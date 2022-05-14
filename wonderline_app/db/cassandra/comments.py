"""
Cassandra ORM related to comments.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from cassandra.cqlengine import columns
from cassandra.cqlengine.columns import UserDefinedType
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.usertype import UserType

from wonderline_app.db.postgres.models import User
from wonderline_app.api.common.enums import SortType
from wonderline_app.db.cassandra.exceptions import CommentNotFound, ReplyNotFound
from wonderline_app.db.cassandra.utils import get_filtered_models, SORTING_MAPPING
from wonderline_app.utils import convert_date_to_timestamp_in_expected_unit, get_uuid, get_current_timestamp


@dataclass
class Entities:
    hashtags: List[Dict] = field(default_factory=list)
    mentions: List[Dict] = field(default_factory=list)
    hasLiked: bool = False


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
            reply_nb: int = 6) -> 'List[CommentsByPhoto]':
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
    def get_comment(cls, comment_id: str) -> 'Comment':
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

    @classmethod
    def delete_db_reply(cls, photo_id: str, comment_id: str, reply_id: str):
        # only used for integration test
        # remove in Comment
        comment = Comment.get(comment_id=comment_id)
        if reply_id not in comment.replies:
            raise ReplyNotFound(f"Reply {reply_id} is not found")
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

    @classmethod
    def delete_db_comment(cls, photo_id: str, comment_id: str):
        # only used for integration test for now
        Comment.get(comment_id=comment_id).delete()
        CommentsByPhoto.get(
            photo_id=photo_id,
            comment_id=comment_id
        ).delete()
        EntitiesByComment.get(comment_id=comment_id).delete()

    @classmethod
    def update_reply(cls, photo_id: str, comment_id: str, reply_id: str, is_like: bool,
                     current_user_id: str) -> ReplyWithId:

        comment = Comment.get_comment(comment_id=comment_id)
        entities = EntitiesByComment.get(comment_id=reply_id)
        if (current_user_id in entities.likes and not is_like) or (current_user_id not in entities.likes and is_like):
            if is_like:
                entities.likes.add(current_user_id)
            else:
                entities.likes.remove(current_user_id)
            entities.update()

            like_delta = 1 if is_like else -1

            comment.replies[reply_id].liked_nb += like_delta
            comment.update()

            comment = CommentsByPhoto.get(photo_id=photo_id, comment_id=comment_id)
            comment.replies[reply_id].liked_nb += like_delta
            comment.update()
        reply_with_id = ReplyWithId(reply_id=reply_id, _reply=comment.replies[reply_id])
        reply_with_id.entities = EntitiesByComment.get_entities(
            current_user_id=current_user_id,
            entities_model=entities
        )
        return reply_with_id


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
    def get_entities(cls, current_user_id: str, entities_model=None, comment_id: Optional[str] = None) -> Entities:
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
