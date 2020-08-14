"""
Cassandra ORM.
"""
from cassandra.cqlengine import columns
from cassandra.cqlengine.columns import UserDefinedType
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType

from wonderline_app.utils import convert_date_to_timestamp


class Reply(UserType):
    __type_name__ = 'reply'

    reply_id = columns.Text()
    user_id = columns.Text()
    create_time = columns.DateTime()
    content = columns.Text()
    liked_nb = columns.SmallInt()

    @property
    def json(self):
        return {
            "reply_id": self.reply_id,
            "user_id": self.user_id,
            "create_time": convert_date_to_timestamp(self.create_time),
            "content": self.content,
            "liked_nb": self.liked_nb
        }


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

    @property
    def json(self):
        return {
            "photo_id": self.photo_id,
            "trip_id": self.trip_id,
            "owner": self.owner,
            "access_level": self.access_level,
            "status": self.status,
            "location": self.location,
            "country": self.country,
            "create_time": convert_date_to_timestamp(self.create_time),
            "upload_time": convert_date_to_timestamp(self.upload_time),
            "width": self.width,
            "height": self.height,
            "low_quality_src": self.low_quality_src,
            "src": self.src,
            "liked_nb": self.liked_nb
        }


class RearrangedPhoto(UserType):
    __type_name__ = "reduced_photo"
    photo = UserDefinedType(ReducedPhoto)
    ratio_type = columns.Text()


class Comment(Model):
    __table_name__ = "comment"

    comment_id = columns.Text(primary_key=True)
    create_time = columns.Date(primary_key=True, clustering_order="DESC")
    user_id = columns.Text(primary_key=True, clustering_order="DESC")
    content = columns.Text()
    liked_nb = columns.SmallInt()
    reply_nb = columns.SmallInt()
    replies = columns.Set(UserDefinedType(Reply))

    @property
    def json(self):
        return {
            "comment_id": self.comment_id,
            "create_time": convert_date_to_timestamp(self.create_time),
            "user_id": self.user_id,
            "content": self.content,
            "liked_nb": self.liked_nb,
            "reply_nb": self.reply_nb,
            "replies": [reply.json() for reply in self.replies]
        }


class CommentsByPhoto(Model):
    __table_name__ = "comments_by_photo"

    photo_id = columns.Text(primary_key=True)
    create_time = columns.Date(primary_key=True, clustering_order="DESC")
    comment_id = columns.Text(primary_key=True, clustering_order="DESC")
    user_id = columns.Text()
    content = columns.Text()
    liked_nb = columns.SmallInt()
    reply_nb = columns.SmallInt()
    replies = columns.Set(UserDefinedType(Reply))

    @property
    def json(self):
        return {
            "photo_id": self.photo_id,
            "create_time": convert_date_to_timestamp(self.create_time),
            "comment_id": self.comment_id,
            "user_id": self.user_id,
            "content": self.content,
            "liked_nb": self.liked_nb,
            "reply_nb": self.reply_nb,
            "replies": [reply.json() for reply in self.replies]
        }


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

    @property
    def json(self):
        return {
            **self.reduced_photo_json,
            "high_quality_src": self.high_quality_src,
            "liked_users": self.liked_users,
            "mentioned_users": self.mentioned_users,
            "comment_nb": self.comment_nb,
            "comments": list(self.comments)
        }

    @property
    def reduced_photo_json(self):
        return {
            "photo_id": self.photo_id,
            "trip_id": self.trip_id,
            "owner": self.owner,
            "access_level": self.access_level,
            "status": self.status,
            "location": self.location,
            "country": self.country,
            "create_time": convert_date_to_timestamp(self.create_time),
            "upload_time": convert_date_to_timestamp(self.upload_time),
            "width": self.width,
            "height": self.height,
            "low_quality_src": self.low_quality_src,
            "src": self.src,
            "liked_nb": self.liked_nb
        }


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

    @property
    def json(self):
        return {
            **self.reduced_trip,
            "liked_nb": self.liked_nb,
            "shared_nb": self.shared_nb,
            "saved_nb": self.saved_nb
        }

    @property
    def reduced_trip(self):
        return {
            "trip_id": self.trip_id,
            "access_level": self.access_level,
            "status": self.status,
            "name": self.name,
            "description": self.description,
            "users": list(self.users),
            "create_time": convert_date_to_timestamp(self.create_time),
            "begin_time": convert_date_to_timestamp(self.begin_time),
            "end_time": convert_date_to_timestamp(self.end_time),
            "photo_nb": self.photo_nb,
            "cover_photo": self.cover_photo.json()
        }


class TripsByUser(Model):
    __table_name__ = "trips_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.Date(primary_key=True, clustering_order="DESC")
    trip_id = columns.Text(primary_key=True, clustering_order="DESC")
    access_level = columns.Text()
    name = columns.Text()
    description = columns.Text()
    users = columns.Set(columns.Text())
    begin_time = columns.DateTime()
    end_time = columns.DateTime()
    photo_nb = columns.SmallInt()
    cover_photo = columns.Text()

    @property
    def json(self):
        return {
            "user_id": self.user_id,
            "create_time": convert_date_to_timestamp(self.create_time),
            "trip_id": self.trip_id,
            "access_level": self.access_level,
            "name": self.name,
            "description": self.description,
            "users": list(self.users),
            "begin_time": convert_date_to_timestamp(self.begin_time),
            "end_time": convert_date_to_timestamp(self.end_time),
            "photo_nb": self.photo_nb,
            "cover_photo": self.cover_photo.json()
        }


class PhotosByTrip(Model):
    __table_name__ = "photos_by_trip"

    trip_id = columns.Text(primary_key=True)
    create_time = columns.Date(primary_key=True, clustering_order="DESC")
    photo_id = columns.Text(primary_key=True, clustering_order="DESC")
    owner = columns.Text()
    access_level = columns.Text()
    location = columns.Text()
    country = columns.Text()
    upload_time = columns.DateTime()
    width = columns.SmallInt()
    height = columns.SmallInt()
    low_quality_src = columns.Text()
    src = columns.Text()
    liked_nb = columns.SmallInt()

    @property
    def json(self):
        return {
            "trip_id": self.trip_id,
            "create_time": convert_date_to_timestamp(self.create_time),
            "photo_id": self.photo_id,
            "owner": self.owner,
            "access_level": self.access_level,
            "location": self.location,
            "country": self.country,
            "upload_time": convert_date_to_timestamp(self.upload_time),
            "width": self.width,
            "height": self.height,
            "low_quality_src": self.low_quality_src,
            "src": self.src,
            "liked_nb": self.liked_nb
        }


class AlbumsByUser(Model):
    __table_name__ = "albums_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order='DESC')
    album_id = columns.Text(primary_key=True, clustering_order='DESC')
    access_level = columns.Text()
    cover_photos = columns.Set(UserDefinedType(RearrangedPhoto))


class MentionsByUser(Model):
    __table_name__ = "mentions_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    mention_id = columns.Text(primary_key=True, clustering_order="DESC")
    access_level = columns.Text()
    photo = UserDefinedType(ReducedPhoto)


class HighlightsByUser(Model):
    __table_name__ = "highlights_by_user"

    user_id = columns.Text(primary_key=True)
    create_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    highlight_id = columns.Text(primary_key=True, clustering_order="DESC")
    access_level = columns.Text()
    cover_photo = UserDefinedType(ReducedPhoto)
    description = columns.Text()


