"""
Cassandra ORM.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from itertools import islice
from typing import List, Dict, Optional, Set
from cassandra.cqlengine import columns
from cassandra.cqlengine.columns import UserDefinedType
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.usertype import UserType
from cassandra.cqlengine.query import LWTException

from wonderline_app.api.common.enums import SortType, AccessLevel, TripStatus
from wonderline_app.core.image_service import remove_image_by_url
from wonderline_app.db.cassandra.utils import SORTING_MAPPING, get_filtered_models
from wonderline_app.db.cassandra.exceptions import PhotoNotFound, TripNotFound, CommentNotFound
from wonderline_app.db.postgres.exceptions import UserNotFound
from wonderline_app.db.postgres.models import User
from wonderline_app.utils import convert_date_to_timestamp_in_expected_unit, get_current_timestamp, get_uuid

LOGGER = logging.getLogger(__name__)


@dataclass
class ReducedTrip:
    trip_id: str
    owner_id: str
    create_time: datetime
    name: str
    users: set = set
    access_level: str = AccessLevel.EVERYONE.value
    status: str = TripStatus.EDITING.value
    description: str = ""
    begin_time: datetime = None
    end_time: datetime = None
    photo_nb: int = 0
    cover_photo: ReducedPhoto = None


@dataclass
class ReplyWithId:
    reply_id: str
    _reply: Reply

    def to_dict(self):
        return {
            "id": self.reply_id,
            **self._reply.to_dict()
        }

    @classmethod
    def create(cls, content: str, user_id: str):
        return cls(
            reply_id=get_uuid(),
            _reply=Reply.create(content, user_id)
        )

    def __getattr__(self, item):
        getattr(self._reply, item)

    @property
    def entities(self):
        return self._reply.entities

    @entities.setter
    def entities(self, value):
        self._reply.entities = value

    @property
    def reply_value(self):
        return self._reply


class Reply(UserType):
    __type_name__ = 'reply'

    user = columns.Text()
    create_time = columns.DateTime()
    content = columns.Text()
    liked_nb = columns.SmallInt(default=0)

    entities: Entities

    def to_dict(self) -> Dict:
        return {
            "user": User.get_user_attributes_or_none(user_id=self.user, reduced=True),
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
            "content": self.content,
            "likedNb": self.liked_nb,
            "hashtags": self.entities.hashtags,
            "mentions": self.entities.mentions,
            "hasLiked": self.entities.hasLiked,
        }

    def __hash__(self):
        return id(self.reply_id)

    @classmethod
    def create(cls, content: str, user_id: str):
        return cls(
            user=user_id,
            create_time=get_current_timestamp(),
            content=content,
            liked_nb=0
        )


class ReducedPhoto(UserType):
    __type_name__ = "reduced_photo"

    photo_id = columns.Text()
    trip_id = columns.Text()
    owner = columns.Text()
    access_level = columns.Text(default=AccessLevel.EVERYONE.value)
    status = columns.Text(default=TripStatus.EDITING.value)
    location = columns.Text()
    country = columns.Text()
    create_time = columns.DateTime()
    upload_time = columns.DateTime()
    width = columns.SmallInt()
    height = columns.SmallInt()
    low_quality_src = columns.Text()
    src = columns.Text()
    liked_nb = columns.SmallInt(default=0)

    def to_dict(self) -> Dict:
        return {
            "id": self.photo_id,
            "tripId": self.trip_id,
            "user": User.get_user_attributes_or_none(user_id=self.owner, reduced=True),
            "accessLevel": self.access_level,
            "status": self.status,
            "location": self.location,
            "country": self.country,
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
            "uploadTime": convert_date_to_timestamp_in_expected_unit(self.upload_time),
            "width": self.width,
            "height": self.height,
            "lqSrc": self.low_quality_src,
            "src": self.src,
            "likedNb": self.liked_nb
        }

    def __hash__(self):
        return id(self.photo_id)


class RearrangedPhoto(UserType):
    __type_name__ = "rearranged_photo"

    photo = UserDefinedType(ReducedPhoto)
    ratio_type = columns.Text()

    def to_dict(self) -> Dict:
        return {
            "photo": self.photo.to_dict(),
            "ratioType": self.ratio_type
        }

    def __hash__(self):
        # https://stackoverflow.com/questions/37011190/typeerror-unhashable-type-usertype-when-creating-a-cassandra-python-driver-mode
        return id(self.photo)


class Comment(Model):
    __table_name__ = "comment"

    comment_id = columns.Text(primary_key=True)
    create_time = columns.DateTime()
    user = columns.Text()
    content = columns.Text()
    liked_nb = columns.SmallInt(default=0)
    reply_nb = columns.SmallInt(default=0)
    replies = columns.Map(columns.Text, UserDefinedType(Reply))

    entities: Entities

    def to_dict(self) -> Dict:
        return {
            "id": self.comment_id,
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
            "user": User.get_user_attributes_or_none(user_id=self.user, reduced=True),
            "content": self.content,
            "likedNb": self.liked_nb,
            "replyNb": self.reply_nb,
            # TODO: self.replies is List[ReplyWithId], ambiguity !
            "replies": [reply.to_dict() for reply in self.replies],
            "hashtags": self.entities.hashtags,
            "mentions": self.entities.mentions,
            "hasLiked": self.entities.hasLiked,
        }

    def get_filtered_replies_objects(self, sort_by: str = "createTime", nb: int = 6,
                                     start_index: int = 0) -> List[ReplyWithId]:
        return CommentUtils.get_filtered_replies_objects(
            replies=self.replies,  # type: ignore
            sort_by=sort_by,
            start_index=start_index,
            nb=nb
        )

    def get_replies_with_ids(
            self,
            current_user_id: str,
            sort_by: str = "createTime",
            nb: int = 6,
            start_index: int = 0
    ):
        replies: List[ReplyWithId] = self.get_filtered_replies_objects(sort_by=sort_by, nb=nb, start_index=start_index)
        for reply in replies:
            reply.entities = EntitiesByComment.get_entities(
                comment_id=str(reply.reply_id),
                current_user_id=current_user_id
            )
        return replies

    def get_replies(
            self,
            current_user_id: str,
            sort_by: str = "createTime",
            nb: int = 6,
            start_index: int = 0,
    ) -> List[Dict]:
        replies = self.get_replies_with_ids(
            current_user_id=current_user_id,
            sort_by=sort_by,
            nb=nb,
            start_index=start_index,
        )
        return [r.to_dict() for r in replies]

    def get_comment_as_dict(self, current_user_id: str):
        self.replies = self.get_replies_with_ids(current_user_id=current_user_id)
        self.entities = EntitiesByComment.get_entities(
            comment_id=str(self.comment_id),
            current_user_id=current_user_id
        )
        return self.to_dict()

    @classmethod
    def get_comment(cls, comment_id: str) -> Comment:
        try:
            return cls.get(comment_id=comment_id)
        except DoesNotExist:
            raise CommentNotFound(f"Comment {comment_id} is not found")

    def add_reply(self, reply: ReplyWithId):
        self.replies[reply.reply_id] = reply.reply_value  # type: ignore
        self.reply_nb += 1
        self.update()

    def update_comment(self, photo_id: str, is_like: bool, current_user_id: str):
        entities_model: EntitiesByComment = EntitiesByComment.get(comment_id=self.comment_id)
        entities = EntitiesByComment.get_entities(comment_id=self.comment_id,  # type: ignore
                                                  current_user_id=current_user_id,
                                                  entities_model=entities_model)
        if (entities.hasLiked and is_like) or (not entities.hasLiked and not is_like):
            return
        elif is_like:
            entities_model.likes.add(current_user_id)  # type: ignore
        else:
            entities_model.likes.remove(current_user_id)  # type: ignore
        self.liked_nb += 1 if is_like else -1
        self.update()
        entities_model.update()
        CommentsByPhoto.get(
            photo_id=photo_id,
            comment_id=self.comment_id
        ).update_comment(is_like=is_like)


class CommentsByPhoto(Model):
    __table_name__ = "comments_by_photo"

    photo_id = columns.Text(primary_key=True)
    create_time = columns.DateTime()
    comment_id = columns.Text(primary_key=True)
    user = columns.Text()
    content = columns.Text()
    liked_nb = columns.SmallInt(default=0)
    reply_nb = columns.SmallInt(default=0)
    replies = columns.Map(columns.Text, UserDefinedType(Reply))

    entities: Entities

    def to_dict(self) -> Dict:
        return {
            "id": self.comment_id,
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
            "user": User.get_user_attributes_or_none(user_id=self.user, reduced=True),
            "content": self.content,
            "likedNb": self.liked_nb,
            "replyNb": self.reply_nb,
            # TODO: self.replies is List[ReplyWithId], ambiguity !
            "replies": [reply.to_dict() for reply in self.replies],
            "hashtags": self.entities.hashtags,
            "mentions": self.entities.mentions,
            "hasLiked": self.entities.hasLiked,
        }

    def get_filtered_replies_objects(self, sort_by: str = "createTime", nb: int = 6,
                                     start_index: int = 0) -> List[ReplyWithId]:
        return CommentUtils.get_filtered_replies_objects(
            replies=self.replies,  # type: ignore
            sort_by=sort_by,
            start_index=start_index,
            nb=nb
        )

    def get_replies_objects(
            self,
            sort_by: str = "createTime",
            nb: int = 6,
            start_index: int = 0,
    ) -> List[ReplyWithId]:
        replies = self.get_filtered_replies_objects(sort_by=sort_by, nb=nb, start_index=start_index)
        return replies

    @classmethod
    def get_comments_objects(
            cls, photo_id: str,
            current_user_id: str,
            nb: int = 6,
            comments_sort_type: str = "default",
            start_index: int = 0,
            replies_sort_by: str = SortType.CREATE_TIME.value,
            reply_nb: int = 6) -> List[CommentsByPhoto]:
        try:
            comments = get_filtered_models(
                cls,
                primary_key="photo_id",
                id_value=photo_id,
                sort_by=None,
                nb=None,
                start_index=0,
            )
        except DoesNotExist:
            raise CommentNotFound(f"Comments with photo_id {photo_id} is not found")
        else:
            comments.sort(
                key=lambda x: (-x.liked_nb, -x.reply_nb, -convert_date_to_timestamp_in_expected_unit(x.create_time)))
            comments = comments[start_index: start_index + nb]
            for comment in comments:
                comment.replies = comment.get_replies_objects(
                    sort_by=replies_sort_by,
                    nb=reply_nb,
                    start_index=0
                )
                comment.entities = EntitiesByComment.get_entities(
                    comment_id=str(comment.comment_id),
                    current_user_id=current_user_id
                )
                for reply in comment.replies:
                    reply.entities = EntitiesByComment.get_entities(
                        comment_id=str(reply.reply_id),
                        current_user_id=current_user_id
                    )
        return comments

    @classmethod
    def get_comments(
            cls,
            photo_id: str,
            current_user_id: str,
            nb: int = 6,
            comments_sort_type: str = "default",  # TODO: handle such sort type
            start_index: int = 0,
            replies_sort_type: str = SortType.CREATE_TIME.value,
            reply_nb: int = 6,
    ) -> List[Dict]:
        comments = cls.get_comments_objects(
            photo_id=photo_id,
            nb=nb,
            comments_sort_type=comments_sort_type,
            start_index=start_index,
            replies_sort_by=replies_sort_type,
            reply_nb=reply_nb,
            current_user_id=current_user_id
        )
        return [comment.to_dict() for comment in comments]

    @classmethod
    def add_reply(cls, photo_id: str, comment_id: str, reply: ReplyWithId):
        comment_to_update: CommentsByPhoto = cls.get(
            photo_id=photo_id,
            comment_id=comment_id,
        )
        comment_to_update.reply_nb += 1
        comment_to_update.replies[reply.reply_id] = reply.reply_value  # type: ignore
        comment_to_update.update()

    def update_comment(self, is_like: bool):
        self.liked_nb += 1 if is_like else -1
        self.update()


class CommentUtils:
    @classmethod
    def add_reply(cls, photo_id: str, comment: Comment, reply_payload: Dict, user_id) -> ReplyWithId:
        content, hashtags, mentions = reply_payload["content"], reply_payload["hashtags"], reply_payload["mentions"]
        # get entities
        hashtags = [Hashtag.from_dict(h) for h in hashtags]
        mentioned_users = [MentionedUser.from_dict(m) for m in mentions]
        # create reply
        new_reply_record = ReplyWithId.create(content=content, user_id=user_id)
        EntitiesByComment.create_one_record(
            comment_id=new_reply_record.reply_id,  # type: ignore
            hashtags=hashtags,
            mentioned_users=mentioned_users,
            likes=set()
        )
        # add reply to two comment tables
        comment.add_reply(reply=new_reply_record)
        CommentsByPhoto.add_reply(
            photo_id=photo_id,
            comment_id=comment.comment_id,  # type: ignore
            reply=new_reply_record
        )
        return new_reply_record

    @classmethod
    def add_comment(cls, photo_id: str, comment: Dict, user_id: str) -> Reply:
        content, hashtags, mentions = comment["content"], comment["hashtags"], comment["mentions"]
        create_time = get_current_timestamp()
        comment_id = get_uuid()
        new_comment_record = Comment.create(
            comment_id=comment_id,
            create_time=create_time,
            user=user_id,
            content=content,
        )
        # get entities
        hashtags = [Hashtag.from_dict(h) for h in hashtags]
        mentioned_users = [MentionedUser.from_dict(m) for m in mentions]
        EntitiesByComment.create_one_record(
            comment_id=comment_id,  # type: ignore
            hashtags=hashtags,
            mentioned_users=mentioned_users,
            likes=set()
        )

        CommentsByPhoto.create(
            photo_id=photo_id,
            create_time=create_time,
            comment_id=comment_id,
            user=user_id,
            content=content,
        )
        return new_comment_record

    @classmethod
    def get_filtered_replies_objects(cls, replies: columns.Map(columns.Text, UserDefinedType(Reply)),
                                     sort_by: str = "createTime", nb: int = 6,
                                     start_index: int = 0) -> List[ReplyWithId]:
        sort_by = SORTING_MAPPING[sort_by]
        return [ReplyWithId(id_, reply) for id_, reply in sorted(
            replies.items(), key=lambda x: getattr(replies[x[0]], sort_by), reverse=True)][  # type: ignore
               start_index: start_index + nb]


class TripUtils:
    @classmethod
    def create_from_reduced_trip(cls, reduced_trip: ReducedTrip, **kwargs):
        try:
            return cls.if_not_exists().create(
                **{k: getattr(reduced_trip, k) for k in vars(reduced_trip).keys()},
                **kwargs)
        except LWTException as exp:
            LOGGER.warning(f"Failed to create new record from reduced trip, trip_id={reduced_trip.trip_id}")
            LOGGER.warning(f"{exp.existing}")
            raise exp


class PhotoUtils:
    @classmethod
    def create_from_reduced_photo(cls, reduced_photo: ReducedPhoto, **kwargs):
        try:
            return cls.if_not_exists().create(
                **{k: getattr(reduced_photo, k) for k in reduced_photo.keys()},
                **kwargs)
        except LWTException as exp:
            LOGGER.warning(f"Failed to create new record from reduced photo, photo_id={reduced_photo.photo_id}")
            LOGGER.warning(f"{exp.existing}")
            raise Exception(f"Failed to create a new record for the class {cls.__name__}")


class Photo(Model, PhotoUtils):
    __table_name__ = "photo"

    photo_id = columns.Text(primary_key=True)
    trip_id = columns.Text()
    owner = columns.Text()
    access_level = columns.Text(default=AccessLevel.EVERYONE.value)
    status = columns.Text(default=TripStatus.EDITING.value)
    location = columns.Text()
    country = columns.Text()
    create_time = columns.DateTime()
    upload_time = columns.DateTime()
    width = columns.SmallInt()
    height = columns.SmallInt()
    low_quality_src = columns.Text()
    src = columns.Text()
    liked_nb = columns.SmallInt(default=0)
    high_quality_src = columns.Text()
    liked_users = columns.Set(columns.Text())
    mentioned_users = columns.Set(columns.Text())
    comment_nb = columns.SmallInt(default=0)
    comments = columns.Set(columns.Text())

    def to_dict(self) -> Dict:
        return {
            "reducedPhoto": self.to_reduced_photo_dict(),
            "hqSrc": self.high_quality_src,
            "likedUsers": [u.to_reduced_dict() for u in self.liked_users],
            "mentionedUsers": [u.to_reduced_dict() for u in self.mentioned_users],
            "commentNb": self.comment_nb,
            "comments": [c.to_dict() for c in self.comments]
        }

    def to_reduced_photo_dict(self) -> Dict:
        return {
            "id": self.photo_id,
            "tripId": self.trip_id,
            "user": User.get_user_attributes_or_none(user_id=self.owner, reduced=True),
            "accessLevel": self.access_level,
            "status": self.status,
            "location": self.location,
            "country": self.country,
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
            "uploadTime": convert_date_to_timestamp_in_expected_unit(self.upload_time),
            "width": self.width,
            "height": self.height,
            "lqSrc": self.low_quality_src,
            "src": self.src,
            "likedNb": self.liked_nb
        }

    @classmethod
    def get_photo_by_photo_id(cls, photo_id: str) -> Photo:
        try:
            return cls.get(photo_id=photo_id)
        except DoesNotExist:
            LOGGER.warning(f"Photo {photo_id} is not found.")
            raise PhotoNotFound(f"Photo {photo_id} is not found in Cassandra database")

    def get_liked_users_info(self, sort_by: str, nb: int) -> List[User]:
        # TODO: when # of liked users is large, the code will be slow !
        # Need to handle the like/unlike in a cache such as Redis
        liked_users = []
        for uid in self.liked_users:
            try:
                user = User.get(user_id=uid)
            except UserNotFound:
                user = None
            liked_users.append(user)
        liked_users.sort(key=lambda x: getattr(x, sort_by))
        return liked_users[:nb]

    def get_mentioned_users_info(self, sort_by: str, nb: int = None) -> List[User]:
        mentioned_users = []
        for uid in self.mentioned_users:
            try:
                user = User.get(user_id=uid)
            except UserNotFound:
                user = None
            mentioned_users.append(user)
        mentioned_users.sort(key=lambda x: getattr(x, sort_by))
        if nb is None:
            return mentioned_users
        return mentioned_users[:nb]

    def get_photo_information(
            self,
            photo_id: str,
            current_user_id: str,
            liked_users_sort_by: str = SortType.CREATE_TIME.value,
            liked_user_nb: int = 6,
            comments_sort_by: str = SortType.CREATE_TIME.value,
            comment_nb: int = 6
    ) -> Dict:
        photo = Photo.get_photo_by_photo_id(photo_id=photo_id)
        photo.liked_users = self.get_liked_users_info(sort_by=liked_users_sort_by, nb=liked_user_nb)
        photo.mentioned_users = self.get_mentioned_users_info(sort_by=SortType.CREATE_TIME.value)
        photo.comments = CommentsByPhoto.get_comments_objects(
            photo_id=photo_id,
            current_user_id=current_user_id,
            replies_sort_by=comments_sort_by,
            reply_nb=comment_nb)
        return photo.to_dict()


class Trip(Model, TripUtils):
    __table_name__ = "trip"

    trip_id = columns.Text(primary_key=True)
    owner_id = columns.Text()
    access_level = columns.Text(default=AccessLevel.EVERYONE.value)
    status = columns.Text(default=TripStatus.EDITING.value)
    name = columns.Text()
    description = columns.Text(default="")
    users = columns.Set(columns.Text())
    create_time = columns.DateTime()
    begin_time = columns.DateTime(default=None)
    end_time = columns.DateTime(default=None)
    photo_nb = columns.SmallInt(default=0)
    cover_photo = UserDefinedType(ReducedPhoto)
    liked_nb = columns.SmallInt(default=0)
    shared_nb = columns.SmallInt(default=0)
    saved_nb = columns.SmallInt(default=0)

    def to_dict(self) -> Dict:
        return {
            "reducedTrip": self.to_reduced_dict(),
            "likedNb": self.liked_nb,
            "sharedNb": self.shared_nb,
            "savedNb": self.saved_nb
        }

    def to_reduced_dict(self) -> Dict:
        return {
            "id": self.trip_id,
            "ownerId": self.owner_id,
            "accessLevel": self.access_level,
            "status": self.status,
            "name": self.name,
            "description": self.description,
            "users": [u.to_reduced_dict() for u in self.users],
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
            "beginTime": convert_date_to_timestamp_in_expected_unit(self.begin_time) if self.begin_time else None,
            "endTime": convert_date_to_timestamp_in_expected_unit(self.end_time) if self.end_time else None,
            "photoNb": self.photo_nb,
            "coverPhoto": self.cover_photo.to_dict() if self.cover_photo else None
        }

    @classmethod
    def get_trip_by_trip_id(cls, trip_id: str) -> Trip:
        try:
            return cls.get(trip_id=trip_id)
        except DoesNotExist:
            LOGGER.warning(f"Trip {trip_id} is not found.")
            raise TripNotFound(f"Trip {trip_id} is not found in Cassandra database.")

    def get_complete_attributes(self, users_sort_type: str, user_nb: int = None) -> Dict:
        self.users = User.get_users_by_ids(user_ids=self.users, sort_by=users_sort_type, start_index=0, user_nb=user_nb,
                                           sort_desc=False)
        return self.to_dict()

    def get_users(self, users_sort_type, start_index: int, user_nb: int = None) -> List[Dict]:
        users = User.get_users_by_ids(user_ids=self.users, sort_by=users_sort_type, user_nb=user_nb,
                                      start_index=start_index, sort_desc=False)
        return [u.to_reduced_dict() for u in users]


class TripsByUser(Model, TripUtils):
    __table_name__ = "trips_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    trip_id = columns.Text(primary_key=True, clustering_order="DESC")
    owner_id = columns.Text()
    access_level = columns.Text(default=AccessLevel.EVERYONE.value)
    status = columns.Text(default=TripStatus.EDITING.value)
    name = columns.Text()
    description = columns.Text(default="")
    users = columns.Set(columns.Text())
    begin_time = columns.DateTime()
    end_time = columns.DateTime()
    photo_nb = columns.SmallInt(default=0)
    cover_photo = columns.Text()

    def to_dict(self) -> Dict:
        return {
            "id": self.trip_id,
            "ownerId": self.owner_id,
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
            "tripTd": self.trip_id,
            "accessLevel": self.access_level,
            "status": self.status,
            "name": self.name,
            "description": self.description,
            "users": [u.to_reduced_dict() for u in self.users],
            "beginTime": convert_date_to_timestamp_in_expected_unit(self.begin_time) if self.begin_time else None,
            "endTime": convert_date_to_timestamp_in_expected_unit(self.end_time) if self.end_time else None,
            "photoNb": self.photo_nb,
            "coverPhoto": self.cover_photo.to_reduced_photo_dict() if self.cover_photo else None
        }

    @classmethod
    def get_trips(cls, user_id: str, sort_by: str = 'create_time', nb: int = 3, access_level=None,
                  start_index=0) -> List[Dict]:
        trips = get_filtered_models(
            cls=cls,
            primary_key='user_id',
            sort_by=sort_by,
            id_value=user_id,
            nb=nb,
            access_level=access_level,
            start_index=start_index)  # trips: List[TripsByUser]
        for trip in trips:
            trip.users = User.get_users_by_ids(user_ids=trip.users, sort_by='nickName', sort_desc=False)
            try:
                trip.cover_photo = Photo.get_photo_by_photo_id(photo_id=str(trip.cover_photo))
            except PhotoNotFound:
                trip.cover_photo = None
        return [trip.to_dict() for trip in trips]


class PhotosByTrip(Model, PhotoUtils):
    __table_name__ = "photos_by_trip"

    trip_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    photo_id = columns.Text(primary_key=True, clustering_order="DESC")
    owner = columns.Text()
    access_level = columns.Text(default=AccessLevel.EVERYONE.value)
    status = columns.Text(default=TripStatus.EDITING.value)
    location = columns.Text()
    country = columns.Text()
    upload_time = columns.DateTime()
    width = columns.SmallInt()
    height = columns.SmallInt()
    low_quality_src = columns.Text()
    src = columns.Text()
    liked_nb = columns.SmallInt(default=0)

    def to_dict(self) -> Dict:
        return {
            "tripId": self.trip_id,
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
            "id": self.photo_id,
            "user": User.get_user_attributes_or_none(user_id=self.owner, reduced=True),
            "accessLevel": self.access_level,
            "status": self.status,
            "location": self.location,
            "country": self.country,
            "uploadTime": convert_date_to_timestamp_in_expected_unit(self.upload_time),
            "width": self.width,
            "height": self.height,
            "lqSrc": self.low_quality_src,
            "src": self.src,
            "likedNb": self.liked_nb
        }

    @classmethod
    def get_filtered_photos(cls, trip_id: str, sort_by: str, access_level: str, start_index: int,
                            nb: int = None) -> List[Dict]:
        photos = get_filtered_models(
            cls=cls,
            primary_key='trip_id',
            sort_by=sort_by,
            id_value=trip_id,
            nb=nb,
            start_index=start_index,
            access_level=access_level)  # photos: List[PhotosByTrip]
        return [photo.to_dict() for photo in photos]


class AlbumsByUser(Model):
    __table_name__ = "albums_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order='DESC')
    album_id = columns.Text(primary_key=True, clustering_order='DESC')
    access_level = columns.Text(default=AccessLevel.EVERYONE.value)
    cover_photos = columns.Set(UserDefinedType(RearrangedPhoto))

    @classmethod
    def get_albums(cls, user_id: str, sort_by: str = 'create_time', nb: int = 3, access_level=None,
                   start_index=0) -> List[Dict]:
        albums = get_filtered_models(
            cls=cls,
            primary_key='user_id',
            id_value=user_id,
            sort_by=sort_by,
            nb=nb,
            access_level=access_level,
            start_index=start_index)  # albums: List[AlbumsByUser]
        for album in albums:
            # convert cover_photos from set to list
            # so that it can be sortable
            album.cover_photos = list(album.cover_photos)
            album.cover_photos.sort(key=lambda x: x.photo.create_time)
        return [album.to_dict() for album in albums]

    def to_dict(self) -> Dict:
        return {
            "id": self.album_id,
            "accessLevel": self.access_level,
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
            "coverPhotos": [photo.to_dict() for photo in self.cover_photos]
        }


class MentionsByUser(Model):
    __table_name__ = "mentions_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    mention_id = columns.Text(primary_key=True, clustering_order="DESC")
    access_level = columns.Text(default=AccessLevel.EVERYONE.value)
    photo = UserDefinedType(ReducedPhoto)

    @classmethod
    def get_mentions(cls, user_id: str, sort_by: str = 'create_time', nb: int = 3, access_level: str = 'everyone',
                     start_index=0) -> List[Dict]:
        mentions = get_filtered_models(
            cls=cls,
            primary_key='user_id',
            id_value=user_id,
            sort_by=sort_by,
            nb=nb,
            access_level=access_level,
            start_index=start_index)  # mentions: List[MentionsByUser]
        return [mention.to_dict() for mention in mentions]

    def to_dict(self) -> Dict:
        return {
            "id": self.mention_id,
            "photo": self.photo.to_dict(),
            "accessLevel": self.access_level,
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time),
        }


class HighlightsByUser(Model):
    __table_name__ = "highlights_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    highlight_id = columns.Text(primary_key=True, clustering_order="DESC")
    access_level = columns.Text(default=AccessLevel.EVERYONE.value)
    cover_photo = columns.Text()
    description = columns.Text(default="")

    @classmethod
    def get_highlights(cls, user_id: str, sort_by: str = 'create_time', nb: int = 3, access_level=None,
                       start_index=0) -> List[Dict]:
        highlights = get_filtered_models(
            cls=cls,
            primary_key='user_id',
            id_value=user_id,
            sort_by=sort_by,
            nb=nb,
            access_level=access_level,
            start_index=start_index)  # highlights: List[HighlightsByUser]
        for highlight in highlights:
            try:
                Photo.get_photo_by_photo_id(photo_id=str(highlight.cover_photo))
            except PhotoNotFound:
                highlight.cover_photo = None
        return [highlight.to_dict() for highlight in highlights]

    def to_dict(self) -> Dict:
        return {
            "id": self.highlight_id,
            "accessLevel": self.access_level,
            "coverPhoto": self.cover_photo.to_dict() if self.cover_photo else None,
            "description": self.description,
            "createTime": convert_date_to_timestamp_in_expected_unit(self.create_time)
        }


class Hashtag(UserType):
    __type_name__ = 'hashtag'

    name = columns.Text()
    start_index = columns.SmallInt()
    end_index = columns.SmallInt()

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "startIndex": self.start_index,
            "endIndex": self.end_index,
        }

    @classmethod
    def from_dict(cls, hashtag_as_dict):
        return cls(
            name=hashtag_as_dict["name"],
            start_index=hashtag_as_dict["startIndex"],
            end_index=hashtag_as_dict["endIndex"],
        )


class MentionedUser(UserType):
    __type_name__ = 'mentioned_user'

    user_id = columns.Text()
    user_unique_name = columns.Text()
    start_index = columns.SmallInt()
    end_index = columns.SmallInt()

    def to_dict(self) -> Dict:
        return {
            "userId": self.user_id,
            "uniqueName": self.user_unique_name,
            "startIndex": self.start_index,
            "endIndex": self.end_index,
        }

    @classmethod
    def from_dict(cls, mention_as_dict):
        return cls(
            user_id=mention_as_dict["userId"],
            user_unique_name=mention_as_dict["uniqueName"],
            start_index=mention_as_dict["startIndex"],
            end_index=mention_as_dict["endIndex"],
        )


@dataclass
class Entities:
    hashtags: List[Dict] = field(default_factory=list)
    mentions: List[Dict] = field(default_factory=list)
    hasLiked: bool = False


class EntitiesByComment(Model):
    __table_name__ = "entities_by_comment"
    comment_id = columns.Text(primary_key=True)
    hashtags = columns.List(UserDefinedType(Hashtag))
    mentioned_users = columns.List(UserDefinedType(MentionedUser))
    likes = columns.Set(columns.Text)

    def to_dict(self) -> Dict:
        return {
            "comment_id": self.comment_id,
            "hashtags": [hashtag.to_dict() for hashtag in self.hashtags],
            "mentioned_users": [user.to_dict() for user in self.mentioned_users],
            "likes": self.likes,
        }

    @classmethod
    def get_entities(cls, comment_id: str, current_user_id: str, entities_model=None) -> Entities:
        if entities_model is None:
            entity_models = get_filtered_models(
                cls,
                primary_key="comment_id",
                id_value=comment_id,
                sort_by=None,
                access_level=None,
                start_index=0,
                nb=None
            )
            if len(entity_models) == 0:
                return Entities()
            entities_model = entity_models[0]
        entity_dict = entities_model.to_dict()
        return Entities(
            hashtags=entity_dict["hashtags"],
            mentions=entity_dict["mentioned_users"],
            hasLiked=current_user_id in entity_dict["likes"],
        )

    @classmethod
    def create_one_record(
            cls,
            comment_id: str,
            hashtags: List[Hashtag],
            mentioned_users: List[MentionedUser],
            likes: Set[str]
    ):
        return EntitiesByComment.create(
            comment_id=comment_id,
            hashtags=hashtags,
            mentioned_users=mentioned_users,
            likes=likes,
        )


def create_and_return_new_trip(owner_id: str, trip_name: str, user_ids: List[str]) -> Optional[Trip]:
    if user_ids is None or not len(user_ids):
        user_ids = [owner_id]
    reduced_trip = ReducedTrip(
        trip_id=get_uuid(),
        owner_id=owner_id,
        create_time=get_current_timestamp(),
        name=trip_name,
        users=set(user_ids)
    )
    new_trip = Trip.create_from_reduced_trip(reduced_trip=reduced_trip)
    for user_id in user_ids:
        TripsByUser.create_from_reduced_trip(reduced_trip=reduced_trip, user_id=user_id)
    return new_trip


def delete_photos(trip_id: str, photo_ids: List[str]):
    # 1. Delete photo in Photo
    # 2. Delete photo in PhotosByTrip
    # 3. Delete images in minio
    if photo_ids is not None and len(photo_ids) > 0:
        for photo_id in photo_ids:
            photo = Photo.get(photo_id=photo_id)
            PhotosByTrip.get(
                trip_id=trip_id,
                photo_id=photo_id,
                create_time=photo.create_time
            ).delete()
            photo.delete()
            remove_image_by_url(photo.high_quality_src)
            remove_image_by_url(photo.src)
            remove_image_by_url(photo.low_quality_src)


def delete_all_about_given_trip(trip_id: str, photo_ids=None):
    # only used for integration test
    trip = Trip.get_trip_by_trip_id(trip_id=trip_id)
    for user_id in trip.users:
        trips_by_user_record = TripsByUser.get(
            user_id=user_id,
            trip_id=trip_id,
            create_time=trip.create_time
        )
        trips_by_user_record.delete()
    delete_photos(trip_id, photo_ids)
    trip.delete()


def delete_db_comment(photo_id: str, comment_id: str):
    # only used for integration test for now
    Comment.get(comment_id=comment_id).delete()
    CommentsByPhoto.get(
        photo_id=photo_id,
        comment_id=comment_id
    ).delete()
    EntitiesByComment.get(comment_id=comment_id).delete()


def delete_db_reply(photo_id: str, comment_id: str, reply_id: str):
    # only used for integration test
    # remove in Comment
    comment = Comment.get(comment_id=comment_id)
    comment.replies[reply_id] = None
    comment.reply_nb -= 1
    comment.update()
    # remove in CommentsByPhoto
    comment_in_comments_by_photo = CommentsByPhoto.get(
        photo_id=photo_id,
        comment_id=comment_id,
    )
    comment_in_comments_by_photo.replies[reply_id] = None
    comment_in_comments_by_photo.reply_nb -= 1
    comment_in_comments_by_photo.update()
    # remove in EntitiesByComment
    EntitiesByComment.get(comment_id=reply_id).delete()
