"""
Cassandra ORM (all the components except the comments).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from cassandra.cqlengine import columns
from cassandra.cqlengine.columns import UserDefinedType
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.usertype import UserType
from cassandra.cqlengine.query import LWTException

from wonderline_app.api.common.enums import SortType, AccessLevel, TripStatus
from wonderline_app.core.image_service import remove_image_by_url
from wonderline_app.db.cassandra.comments import CommentsByPhoto
from wonderline_app.db.cassandra.utils import get_filtered_models
from wonderline_app.db.cassandra.exceptions import PhotoNotFound, TripNotFound
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

    hasLiked: bool = False

    def to_dict(self) -> Dict:
        return {
            "reducedPhoto": self.to_reduced_photo_dict(),
            "hqSrc": self.high_quality_src,
            "likedUsers": [u.to_reduced_dict() for u in self.liked_users],
            "mentionedUsers": [u.to_reduced_dict() for u in self.mentioned_users],
            "commentNb": self.comment_nb,
            "comments": [c.to_dict() for c in self.comments],
            "hasLiked": self.hasLiked,
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
        photo.hasLiked = current_user_id in self.liked_users
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
