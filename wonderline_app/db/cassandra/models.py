"""
Cassandra ORM.
"""
from __future__ import annotations

import logging
from typing import List, Dict, Type

from cassandra.cqlengine import columns
from cassandra.cqlengine.columns import UserDefinedType
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.usertype import UserType

from wonderline_app.db.cassandra.exceptions import PhotoNotFound, TripNotFound, CommentNotFound
from wonderline_app.db.postgres.exceptions import UserNotFound
from wonderline_app.db.postgres.models import User
from wonderline_app.utils import convert_date_to_timestamp

LOGGER = logging.getLogger(__name__)

# mapping from camel case to snake case
SORTING_MAPPING = {
    'createTime': 'create_time'
}


def get_filtered_models(cls: Type[Model], primary_key: str, id_value: str, sort_by: str = 'create_time', nb: int = 3,
                        access_level=None, start_index=0) -> List[Model]:
    sort_by = SORTING_MAPPING[sort_by]
    models = cls.objects(getattr(cls, primary_key) == id_value).order_by(sort_by).limit(start_index + nb)
    if access_level is not None:
        models = [model for model in models if model.access_level == access_level]
    return models[start_index:start_index + nb]


class Reply(UserType):
    __type_name__ = 'reply'

    reply_id = columns.Text()
    user = columns.Text()
    create_time = columns.DateTime()
    content = columns.Text()
    liked_nb = columns.SmallInt()

    def to_dict(self) -> Dict:
        return {
            "id": self.reply_id,
            "user": User.get_user_attributes_or_none(user_id=self.user, reduced=True),
            "createTime": convert_date_to_timestamp(self.create_time),
            "content": self.content,
            "likedNb": self.liked_nb
        }

    def __hash__(self):
        return id(self.reply_id)


class ReducedPhoto(UserType):
    __type_name__ = "reduced_photo"

    photo_id = columns.Text()
    trip_id = columns.Text()
    owner = columns.Text()
    access_level = columns.Text()
    status = columns.Text()
    location = columns.Text()
    country = columns.Text()
    create_time = columns.DateTime()
    upload_time = columns.DateTime()
    width = columns.SmallInt()
    height = columns.SmallInt()
    low_quality_src = columns.Text()
    src = columns.Text()
    liked_nb = columns.SmallInt()

    def to_dict(self) -> Dict:
        return {
            "id": self.photo_id,
            "tripId": self.trip_id,
            "user": User.get_user_attributes_or_none(user_id=self.owner, reduced=True),
            "accessLevel": self.access_level,
            "status": self.status,
            "location": self.location,
            "country": self.country,
            "createTime": convert_date_to_timestamp(self.create_time),
            "uploadTime": convert_date_to_timestamp(self.upload_time),
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
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    user = columns.Text(primary_key=True, clustering_order="DESC")
    content = columns.Text()
    liked_nb = columns.SmallInt()
    reply_nb = columns.SmallInt()
    replies = columns.Set(UserDefinedType(Reply))

    def to_dict(self) -> Dict:
        return {
            "id": self.comment_id,
            "createTime": convert_date_to_timestamp(self.create_time),
            "user": self.user,
            "content": self.content,
            "likedNb": self.liked_nb,
            "replyNb": self.reply_nb,
            "replies": [reply.to_dict() for reply in self.replies]
        }

    def get_filtered_replies_objects(self, sort_by: str = "creteTime", nb: int = 6,
                                     start_index: int = 0) -> List[Reply]:
        sort_by = SORTING_MAPPING[sort_by]
        self.replies = list(self.replies)
        self.replies.sort(key=lambda x: getattr(x, sort_by))
        return self.replies[start_index:start_index + nb]

    def get_replies(self, sort_by: str = "creteTime", nb: int = 6, start_index: int = 0) -> List[Dict]:
        replies = self.get_filtered_replies_objects(sort_by=sort_by, nb=nb, start_index=start_index)
        return [r.to_dict() for r in replies]

    @classmethod
    def get_comment(cls, comment_id: str) -> Comment:
        try:
            return cls.get(comment_id=comment_id)
        except DoesNotExist:
            raise CommentNotFound(f"Comment {comment_id} is not found")


class CommentsByPhoto(Model):
    __table_name__ = "comments_by_photo"

    photo_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    comment_id = columns.Text(primary_key=True, clustering_order="DESC")
    user = columns.Text()
    content = columns.Text()
    liked_nb = columns.SmallInt()
    reply_nb = columns.SmallInt()
    replies = columns.Set(UserDefinedType(Reply))

    def to_dict(self) -> Dict:
        return {
            "id": self.comment_id,
            "createTime": convert_date_to_timestamp(self.create_time),
            "user": User.get_user_attributes_or_none(user_id=self.user, reduced=True),
            "content": self.content,
            "likedNb": self.liked_nb,
            "replyNb": self.reply_nb,
            "replies": [reply.to_dict() for reply in self.replies]
        }

    def get_filtered_replies_objects(self, sort_by: str = "creteTime", nb: int = 6,
                                     start_index: int = 0) -> List[Reply]:
        sort_by = SORTING_MAPPING[sort_by]
        self.replies = list(self.replies)
        self.replies.sort(key=lambda x: getattr(x, sort_by))
        return self.replies[start_index:start_index + nb]

    def get_replies_objects(self, sort_by: str = "creteTime", nb: int = 6, start_index: int = 0) -> List[Reply]:
        replies = self.get_filtered_replies_objects(sort_by=sort_by, nb=nb, start_index=start_index)
        return replies

    @classmethod
    def get_comments_objects(cls, photo_id: str, sort_by: str = "createTime", nb: int = 6) \
            -> List[CommentsByPhoto]:
        try:
            comments = cls.objects(photo_id=photo_id)
        except DoesNotExist:
            raise CommentNotFound(f"Comments with photo_id {photo_id} is not found")
        else:
            for comment in comments:
                comment.replies = comment.get_replies_objects(
                    sort_by=sort_by,
                    nb=nb,
                    start_index=0
                )
        return comments

    @classmethod
    def get_comments(cls, photo_id: str, sort_by: str = "createTime", nb: int = 6) -> List[Dict]:
        comments = cls.get_comments_objects(
            photo_id=photo_id,
            sort_by=sort_by,
            nb=nb
        )
        return [comment.to_dict() for comment in comments]


class Photo(Model):
    __table_name__ = "photo"

    photo_id = columns.Text(primary_key=True)
    trip_id = columns.Text()
    owner = columns.Text()
    access_level = columns.Text()
    status = columns.Text()
    location = columns.Text()
    country = columns.Text()
    create_time = columns.DateTime()
    upload_time = columns.DateTime()
    width = columns.SmallInt()
    height = columns.SmallInt()
    low_quality_src = columns.Text()
    src = columns.Text()
    liked_nb = columns.SmallInt()
    high_quality_src = columns.Text()
    liked_users = columns.Set(columns.Text())
    mentioned_users = columns.Set(columns.Text())
    comment_nb = columns.SmallInt()
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
            "createTime": convert_date_to_timestamp(self.create_time),
            "uploadTime": convert_date_to_timestamp(self.upload_time),
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

    def get_mentioned_users_info(self, sort_by: str, nb: int = -1) -> List[User]:
        mentioned_users = []
        for uid in self.mentioned_users:
            try:
                user = User.get(user_id=uid)
            except UserNotFound:
                user = None
            mentioned_users.append(user)
        mentioned_users.sort(key=lambda x: getattr(x, sort_by))
        return mentioned_users[:nb]

    def get_photo_information(self, photo_id: str, liked_users_sort_by: str = 'createTime', liked_user_nb: int = 6,
                              comments_sort_by: str = "createTime",
                              comment_nb: int = 6) -> Dict:
        photo = Photo.get_photo_by_photo_id(photo_id=photo_id)
        photo.liked_users = self.get_liked_users_info(sort_by=liked_users_sort_by, nb=liked_user_nb)
        photo.mentioned_users = self.get_mentioned_users_info(sort_by='createTime')
        photo.comments = CommentsByPhoto.get_comments_objects(
            photo_id=photo_id,
            sort_by=comments_sort_by,
            nb=comment_nb)
        return photo.to_dict()


class Trip(Model):
    __table_name__ = "trip"

    trip_id = columns.Text(primary_key=True)
    access_level = columns.Text()
    status = columns.Text()
    name = columns.Text()
    description = columns.Text()
    users = columns.Set(columns.Text())
    create_time = columns.DateTime()
    begin_time = columns.DateTime()
    end_time = columns.DateTime()
    photo_nb = columns.SmallInt()
    cover_photo = UserDefinedType(ReducedPhoto)
    liked_nb = columns.SmallInt()
    shared_nb = columns.SmallInt()
    saved_nb = columns.SmallInt()

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
            "accessLevel": self.access_level,
            "status": self.status,
            "name": self.name,
            "description": self.description,
            "users": [u.to_reduced_dict() for u in self.users],
            "createTime": convert_date_to_timestamp(self.create_time),
            "beginTime": convert_date_to_timestamp(self.begin_time),
            "endTime": convert_date_to_timestamp(self.end_time),
            "photoNb": self.photo_nb,
            "coverPhoto": self.cover_photo.to_dict()
        }

    @classmethod
    def get_trip_by_trip_id(cls, trip_id: str) -> Trip:
        try:
            return cls.get(trip_id=trip_id)
        except DoesNotExist:
            LOGGER.warning(f"Trip {trip_id} is not found.")
            raise TripNotFound(f"Trip {trip_id} is not found in Cassandra database.")

    def get_complete_attributes(self, users_sort_type, user_nb) -> Dict:
        self.users = User.get_users_by_ids(user_ids=self.users, sort_by=users_sort_type, user_nb=user_nb,
                                           start_index=0, sort_desc=False)
        return self.to_dict()

    def get_users(self, users_sort_type, user_nb, start_index) -> List[Dict]:
        users = User.get_users_by_ids(user_ids=self.users, sort_by=users_sort_type, user_nb=user_nb,
                                      start_index=start_index, sort_desc=False)
        return [u.to_reduced_dict() for u in users]


class TripsByUser(Model):
    __table_name__ = "trips_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    trip_id = columns.Text(primary_key=True, clustering_order="DESC")
    access_level = columns.Text()
    status = columns.Text()
    name = columns.Text()
    description = columns.Text()
    users = columns.Set(columns.Text())
    begin_time = columns.DateTime()
    end_time = columns.DateTime()
    photo_nb = columns.SmallInt()
    cover_photo = columns.Text()

    def to_dict(self) -> Dict:
        return {
            "id": self.trip_id,
            "createTime": convert_date_to_timestamp(self.create_time),
            "tripTd": self.trip_id,
            "accessLevel": self.access_level,
            "status": self.status,
            "name": self.name,
            "description": self.description,
            "users": [u.to_reduced_dict() for u in self.users],
            "beginTime": convert_date_to_timestamp(self.begin_time),
            "endTime": convert_date_to_timestamp(self.end_time),
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
            trip.users = User.get_users_by_ids(user_ids=trip.users, sort_by='name', sort_desc=False)
            try:
                trip.cover_photo = Photo.get_photo_by_photo_id(photo_id=str(trip.cover_photo))
            except PhotoNotFound:
                trip.cover_photo = None
        return [trip.to_dict() for trip in trips]


class PhotosByTrip(Model):
    __table_name__ = "photos_by_trip"

    trip_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    photo_id = columns.Text(primary_key=True, clustering_order="DESC")
    owner = columns.Text()
    access_level = columns.Text()
    status = columns.Text()
    location = columns.Text()
    country = columns.Text()
    upload_time = columns.DateTime()
    width = columns.SmallInt()
    height = columns.SmallInt()
    low_quality_src = columns.Text()
    src = columns.Text()
    liked_nb = columns.SmallInt()

    def to_dict(self) -> Dict:
        return {
            "tripId": self.trip_id,
            "createTime": convert_date_to_timestamp(self.create_time),
            "id": self.photo_id,
            "user": User.get_user_attributes_or_none(user_id=self.owner, reduced=True),
            "accessLevel": self.access_level,
            "status": self.status,
            "location": self.location,
            "country": self.country,
            "uploadTime": convert_date_to_timestamp(self.upload_time),
            "width": self.width,
            "height": self.height,
            "lqSrc": self.low_quality_src,
            "src": self.src,
            "likedNb": self.liked_nb
        }

    @classmethod
    def get_filtered_photos(cls, trip_id: str, sort_by: str, nb: int, start_index: int, access_level: str
                            ) -> List[Dict]:
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
    access_level = columns.Text()
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
            "createTime": convert_date_to_timestamp(self.create_time),
            "coverPhotos": [photo.to_dict() for photo in self.cover_photos]
        }


class MentionsByUser(Model):
    __table_name__ = "mentions_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    mention_id = columns.Text(primary_key=True, clustering_order="DESC")
    access_level = columns.Text()
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
            "createTime": convert_date_to_timestamp(self.create_time),
        }


class HighlightsByUser(Model):
    __table_name__ = "highlights_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    highlight_id = columns.Text(primary_key=True, clustering_order="DESC")
    access_level = columns.Text()
    cover_photo = columns.Text()
    description = columns.Text()

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
            "createTime": convert_date_to_timestamp(self.create_time)
        }
