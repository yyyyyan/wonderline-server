"""
Implementations of users APIs' business logics.
"""
import functools
import logging
from typing import Dict, List, Optional, Callable, Union, Tuple

from flask_login import login_user, current_user, logout_user
from wonderline_app.api.common.enums import AccessLevel, SortType, SearchSortType
from wonderline_app.core.api_responses.api_errors import APIError, APIError404, APIError500, APIError401, APIError409
from wonderline_app.core.api_responses.api_feedbacks import APIFeedback201
from wonderline_app.core.image_service import ImageSize, upload_encoded_image, DEFAULT_AVATAR_URL
from wonderline_app.core.api_responses.response import Response, Error, Feedback
from wonderline_app.db.cassandra.exceptions import TripNotFound, CommentNotFound, PhotoNotFound
from wonderline_app.db.cassandra.models import AlbumsByUser, TripsByUser, HighlightsByUser, MentionsByUser, Trip, \
    PhotosByTrip, CommentsByPhoto, Photo, Comment, create_and_return_new_trip, ReducedPhoto, delete_photos
from wonderline_app.db.postgres.exceptions import UserNotFound, UserPasswordIncorrect, UserTokenInvalid, \
    UserTokenExpired
from wonderline_app.db.postgres.models import User
from wonderline_app.utils import get_current_timestamp, construct_location, infer_country_from_location, get_uuid

DEFAULT_AVATAR = "https://img2.pngio.com/united-states-avatar-organization-information-png-512x512px-user-avatar-png-820_512.jpg"

LOGGER = logging.getLogger(__name__)


def handle_request(func: Callable, *args, **kwargs) -> Union[Dict, Tuple[Dict, int]]:
    """
    Handle API requests.
    """
    LOGGER.info(f"Handling function {func.__name__}")
    response = Response()
    for arg_key, arg_value in kwargs.items():
        # TODO: handle the case where the value is too long to print
        LOGGER.info(f"Receive arguments: key: {arg_key}, type: {type(arg_key)}, value: {str(arg_value)[:500]} ...")
    try:
        func_response = func(*args, **kwargs)
    except APIError as exp:
        response.add_error(Error(code=exp.code, message=exp.message))
    except Exception as e:
        LOGGER.exception(e)
        response.add_error(APIError500(e))
    else:
        if isinstance(func_response, tuple):  # (payload, feedback)
            response.payload = func_response[0]
            response.add_feedback(func_response[1])
        else:
            response.payload = func_response
    if response.has_errors:
        return response.to_dict(), response.errors[0].code  # TODO: multiple errors
    if response.has_feedbacks:
        return response.to_dict(), response.feedbacks[0].code  # TODO: multiple errors
    return response.to_dict()


def verify_user_token(user_token: str):
    """Verify whether the user token is valid"""
    if user_token is None:
        raise APIError401(message="user token is None")
    if not len(user_token):
        raise APIError401(message="user token is empty")
    LOGGER.info(f"Verifying user token... got {user_token}")
    if current_user.is_anonymous:
        raise APIError401(message="Anonymous user can\'t access the resources")
    else:
        try:
            current_user.verify_auth_token(user_token)
        except UserTokenInvalid:
            raise APIError401(message="user token is invalid")
        except UserTokenExpired:
            raise APIError401(message="user token has expired")


def user_token_required(func):
    """
    Use this decorator when some function needs user token
    E.g.,
        @user_token_required
        def func(**kwargs):
            pass
    **kwargs must contain the parameter `user_token`.

    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        verify_user_token(kwargs.pop('user_token'))
        return func(*args, **kwargs)

    return wrapper


def _get_user(user_id: str) -> Optional[User]:
    """
    Get user object from PostgreSQL given user id.

    :raise APIError404 when user
    """
    user = User.get_user_or_none(user_id=user_id)
    if not user:
        raise APIError404(message=f"User {user_id} is not found")
    return user


def get_trip(trip_id: str) -> Trip:
    """
    Get trip object from Cassandra given trip id.

    :raise APIError404 when trip is not found
    """
    try:
        trip = Trip.get_trip_by_trip_id(trip_id=trip_id)
    except TripNotFound:
        raise APIError404(message=f"Trip {trip_id} is not found")
    else:
        return trip


@user_token_required
def get_user_complete_attributes(user_id: str, followers_sort_type: str = SortType.CREATE_TIME.value,
                                 follower_nb: int = 6) -> Dict:
    """Get user's complete attributes including followers reduced attributes."""
    user = _get_user(user_id=user_id)
    LOGGER.info(f"Getting complete user information for {user_id}")
    res = user.get_complete_attributes(
        follower_nb=follower_nb,
        sort_by=followers_sort_type,
        start_index=0
    )
    return res


@user_token_required
def get_user_followers(user_id: str, sort_type: str = SortType.CREATE_TIME.value, nb: int = 50,
                       start_index: int = 0) -> List:
    """Get user's followers with reduced attributes"""
    user = _get_user(user_id=user_id)
    LOGGER.info(f"Getting followers for {user_id}")
    return user.get_followers_with_reduced_attributes(
        follower_nb=nb,
        sort_by=sort_type,
        start_index=start_index
    )


@user_token_required
def get_albums_by_user(user_id: str, sort_type: str = SortType.CREATE_TIME.value, nb: int = 3, start_index: int = 0,
                       access_level: str = AccessLevel.EVERYONE.value) -> List[Dict]:
    """Get all the albums for the user."""
    user = _get_user(user_id=user_id)
    if user:
        LOGGER.info(f"Getting albums for user {user_id}")
        return AlbumsByUser.get_albums(
            user_id=user_id,
            sort_by=sort_type,
            nb=nb,
            access_level=access_level,
            start_index=start_index)


@user_token_required
def get_trips_by_user(user_id: str, sort_type: str = SortType.CREATE_TIME.value, nb: int = 3, start_index: int = 0,
                      access_level: str = AccessLevel.EVERYONE.value) -> List[Dict]:
    """Get all the trips for the user."""
    user = _get_user(user_id=user_id)
    if user:
        LOGGER.info(f"Getting trips for user {user_id}")
        return TripsByUser.get_trips(
            user_id=user_id,
            sort_by=sort_type,
            nb=nb,
            access_level=access_level,
            start_index=start_index)


@user_token_required
def get_highlights_by_user(user_id: str, sort_type: str = SortType.CREATE_TIME.value, nb: int = 3, start_index: int = 0,
                           access_level: str = AccessLevel.EVERYONE.value) -> List[Dict]:
    """Get all the highlights for the user."""
    user = _get_user(user_id=user_id)
    if user:
        LOGGER.info(f"Getting highlights for user {user_id}")
        return HighlightsByUser.get_highlights(
            user_id=user_id,
            sort_by=sort_type,
            nb=nb,
            access_level=access_level,
            start_index=start_index)


@user_token_required
def get_mentions_by_user(user_id: str, sort_type: str = SortType.CREATE_TIME.value, nb: int = 12, start_index: int = 0,
                         access_level: str = AccessLevel.EVERYONE.value) -> List[Dict]:
    """Get all the mentions for the user."""
    user = _get_user(user_id=user_id)
    if user:
        LOGGER.info(f"Getting mentions for user {user_id}")
        return MentionsByUser.get_mentions(
            user_id=user_id,
            sort_by=sort_type,
            nb=nb,
            access_level=access_level,
            start_index=start_index)


@user_token_required
def get_complete_trip(trip_id: str, users_sort_type: str = SortType.CREATE_TIME.value) -> Dict:
    """Get complete attributes for the trip."""
    trip = get_trip(trip_id=trip_id)
    LOGGER.info(f"Getting complete trip information for {trip_id}")
    return trip.get_complete_attributes(
        users_sort_type=users_sort_type,
        user_nb=None,
    )


@user_token_required
def get_users_by_trip(trip_id: str, sort_type: str = SortType.CREATE_TIME.value, nb: int = 12, start_index: int = 0) -> \
        List[Dict]:
    """Get all the users for a trip."""
    trip = get_trip(trip_id=trip_id)
    if trip:
        LOGGER.info(f"Getting users for trip {trip_id}")
        return trip.get_users(
            users_sort_type=sort_type,
            start_index=start_index,
            user_nb=nb)


@user_token_required
def get_photos_by_trip(trip_id: str, sort_type: str = SortType.CREATE_TIME.value, nb: int = 12, start_index: int = 0,
                       access_level: str = AccessLevel.EVERYONE.value) -> List[Dict]:
    """Get all the photos for the trip."""
    trip = get_trip(trip_id=trip_id)
    if trip:
        LOGGER.info(f"Getting users for trip {trip_id}")
        return PhotosByTrip.get_filtered_photos(
            trip_id=trip_id,
            sort_by=sort_type,
            nb=nb,
            start_index=start_index,
            access_level=access_level)


@user_token_required
def get_photo_details(trip_id: str, photo_id: str, liked_users_sort_type: str,
                      liked_user_nb: int, comments_sort_type: str, comment_nb: int) -> Dict:
    """Get photo complete attributes."""
    trip = get_trip(trip_id=trip_id)
    if trip:
        try:
            photo = Photo.get_photo_by_photo_id(photo_id=photo_id)
            if photo:
                return photo.get_photo_information(
                    photo_id=photo_id,
                    liked_users_sort_by=liked_users_sort_type,
                    liked_user_nb=liked_user_nb,
                    comments_sort_by=comments_sort_type,
                    comment_nb=comment_nb
                )
        except PhotoNotFound as e:
            raise APIError404(message=str(e))


@user_token_required
def get_comments_by_photo(trip_id: str, photo_id: str, replies_sort_type: str, reply_nb: int) -> List[Dict]:
    """Get all the comments for the photo."""
    trip = get_trip(trip_id=trip_id)
    if trip:
        try:
            return CommentsByPhoto.get_comments(
                photo_id=photo_id,
                sort_by=replies_sort_type,
                nb=reply_nb)
        except CommentNotFound as e:
            raise APIError404(message=str(e))


@user_token_required
def get_replies_by_comment(trip_id: str, photo_id: str, comment_id: str, sort_type: str = SortType.CREATE_TIME.value,
                           nb: int = 3,
                           start_index: int = 0) -> List[Dict]:
    """Get all the replies for the comment."""
    trip = get_trip(trip_id=trip_id)
    if trip:
        try:
            photo = Photo.get_photo_by_photo_id(photo_id=photo_id)
            if photo:
                try:
                    comment = Comment.get_comment(comment_id=comment_id)
                    return comment.get_replies(
                        sort_by=sort_type,
                        nb=nb,
                        start_index=start_index)
                except CommentNotFound as e:
                    raise APIError404(message=str(e))
        except PhotoNotFound as e:
            raise APIError404(message=str(e))


def sign_up(email: str,
            user_name: str,
            password: str,
            photo_data: str) -> [Dict, Feedback]:
    if User.does_user_exist(email=email):
        raise APIError409(f"User with email {email} exists, try another email")
    if photo_data is not None:
        avatar_url = upload_encoded_image(image=photo_data, sizes=[ImageSize.AVATAR])[ImageSize.AVATAR.name]
    else:
        avatar_url = DEFAULT_AVATAR_URL
    user = User.create_new_user(email=email, name=user_name, password=password, avatar_url=avatar_url)

    if login_user(user):
        payload = {
            "userToken": user.generate_auth_token(),
            "user": user.get_complete_attributes(follower_nb=0)
        }
        return payload, APIFeedback201(message=f"User {user.email} successfully created")
    else:
        raise APIError500(f"User {email} failed to sign in")


def sign_in(email: str, password: str) -> Dict:
    try:
        user = User.get_user_if_valid(email=email, password=password)
    except UserNotFound:
        raise APIError404(f"User {email} is not found")
    except UserPasswordIncorrect:
        raise APIError401(f"User {email} failed to login")
    if login_user(user):
        return {
            "userToken": user.generate_auth_token(),
            "user": user.get_complete_attributes(follower_nb=6)
        }
    else:
        raise APIError500(f"User {email} failed to sign in")


@user_token_required
def sign_out():
    if current_user.is_anonymous:
        LOGGER.warning("Anonymous user doesn't need to log out")
    else:
        LOGGER.info(f"Logging out user {current_user.email}")
        if not logout_user():
            APIError500(f"User {current_user} failed to sign out")
    return {}


@user_token_required
def create_new_trip(owner_id: str, trip_name: str, user_ids: List[str], users_sort_type: str):
    new_trip = create_and_return_new_trip(owner_id, trip_name, user_ids)
    if new_trip is not None:
        return new_trip.get_complete_attributes(users_sort_type=users_sort_type, user_nb=None), APIFeedback201(
            message=f"Trip '{trip_name}' successfully created")
    else:
        raise APIError500("Failed to create new trip, please check the server log")


@user_token_required
def update_trip(trip_id: str, name: str, description: str, user_ids: List[str]):
    try:
        trip = Trip.get_trip_by_trip_id(trip_id=trip_id)
    except TripNotFound:
        raise APIError404(message=f"Trip {trip_id} is not found")

    # name, description and user_ids are optional arguments
    # so, when the value is None, no need to update
    attributes_to_update = {}
    if name is not None:
        attributes_to_update['name'] = name
    if description is not None:
        attributes_to_update['description'] = description

    if user_ids is not None:
        old_user_ids = set(trip.users)
        new_user_ids = set(user_ids)
        user_ids_to_add = new_user_ids - old_user_ids
        user_ids_to_update = new_user_ids & old_user_ids
        user_ids_to_delete = old_user_ids - new_user_ids
        attributes_to_update['users'] = new_user_ids
        # update TripsByUser
        for user_id in user_ids_to_add:
            TripsByUser.create(
                user_id=user_id,
                create_time=trip.create_time,
                trip_id=trip_id,
                owner_id=trip.owner_id,
                **attributes_to_update,
            )
        for user_id in user_ids_to_update:
            TripsByUser.get(user_id=user_id, trip_id=trip_id, create_time=trip.create_time).update(
                **attributes_to_update
            )
        for user_id in user_ids_to_delete:
            TripsByUser.get(user_id=user_id, trip_id=trip_id, create_time=trip.create_time).delete()
    # update Trip
    trip.update(**attributes_to_update)
    return trip.get_complete_attributes(users_sort_type=SortType.CREATE_TIME.value, user_nb=None)


@user_token_required
def search_users(query: str, users_sort_type: str = SearchSortType.BEST_MATCH.value, start_index: int = 0,
                 nb: int = 12) -> List[Dict]:
    return User.search_users(
        name_query=query,
        start_index=start_index,
        nb=nb,
        sort_type=users_sort_type
    )


@user_token_required
def upload_trip_photos(trip_id: str, original_photos: List[Dict]) -> Tuple[List[Dict], APIFeedback201]:
    # 1. get trip obj from Cassandra DB
    # 2. for each photo:
    #   2.1. generate url
    #   2.2. create photo obj in Cassandra DB
    #   2.3. add it to the table photos_by_trip
    # 3. use the first photo as the cover photo for the trip if it's not set yet
    LOGGER.info(f"Uploading photo for trip {trip_id}")
    trip = get_trip(trip_id=trip_id)
    for original_photo in original_photos:
        size2url = upload_encoded_image(
            image=original_photo['data'],
            sizes=[ImageSize.ORIGINAL, ImageSize.MEDIUM, ImageSize.SMALL])
        location = construct_location(longitude=original_photo['longitude'],
                                      longitude_ref=original_photo['longitudeRef'],
                                      latitude=original_photo['latitude'],
                                      latitude_ref=original_photo['latitudeRef'])
        country = infer_country_from_location(
            longitude=float(original_photo['longitude']),
            latitude=float(original_photo['latitude']))
        reduced_photo = ReducedPhoto(
            photo_id=get_uuid(),
            trip_id=trip_id,
            owner=current_user.id,
            location=location,
            country=country,
            create_time=original_photo['time'],
            upload_time=get_current_timestamp(),
            width=original_photo['width'],
            height=original_photo['height'],
            low_quality_src=size2url[ImageSize.SMALL.name],
            src=size2url[ImageSize.ORIGINAL.name],
            access_level=original_photo['accessLevel']
        )
        Photo.create_from_reduced_photo(
            reduced_photo=reduced_photo,
            high_quality_src=size2url[ImageSize.ORIGINAL.name],
            mentioned_users=original_photo.get("mentionedUserIds", set()),
        )
        PhotosByTrip.create_from_reduced_photo(reduced_photo=reduced_photo)
        if trip.cover_photo is None:
            try:
                trip.update(cover_photo=reduced_photo)
            except Exception as e:
                LOGGER.exception(e)
                raise APIError500(f"Failed to update the cover photo for the trip, trip_id={trip_id}")
            LOGGER.info(f"Update the cover photo for the trip {trip_id} with the photo {reduced_photo.photo_id}")

    return PhotosByTrip.get_filtered_photos(
        trip_id=trip_id,
        sort_by=SortType.CREATE_TIME.value,
        access_level=AccessLevel.EVERYONE.value,
        start_index=0,
        nb=None), APIFeedback201(message=f"Photos are added successfully")


def _update_photo(trip_id: str, photo_id: str, access_level: str, mentioned_users: Optional[List[str]]) -> Photo:
    photo = Photo.get_photo_by_photo_id(photo_id=photo_id)
    if photo:
        attributes_to_update = {}
        if access_level is not None:
            attributes_to_update['access_level'] = access_level
        if mentioned_users is not None:
            attributes_to_update['mentioned_users'] = set(mentioned_users)
        photo.update(**attributes_to_update)
        attributes_to_update.pop('mentioned_users', None)
        if len(attributes_to_update.keys()) > 0:
            photos_by_trip_record = PhotosByTrip.get(
                trip_id=trip_id,
                photo_id=photo_id,
                create_time=photo.create_time
            )
            photos_by_trip_record.update(**attributes_to_update)
    return photo


@user_token_required
def update_trip_photo(trip_id: str, photo_id: str, access_level: str, mentioned_users: Optional[List[str]]):
    trip = get_trip(trip_id=trip_id)
    if trip:
        try:
            photo = _update_photo(trip_id, photo_id, access_level, mentioned_users)
            return photo.get_photo_information(photo_id=photo_id)
        except PhotoNotFound as e:
            raise APIError404(message=str(e))


@user_token_required
def update_trip_photos(trip_id: str, photo_ids: List[str], access_level: str):
    trip = get_trip(trip_id=trip_id)
    updated_photos = []
    if trip:
        for photo_id in photo_ids:
            try:
                updated_photos.append(_update_photo(trip_id, photo_id, access_level, mentioned_users=None))
            except PhotoNotFound as e:
                raise APIError404(message=str(e))
    return [photo.to_reduced_photo_dict() for photo in updated_photos]


@user_token_required
def delete_trip_photos(trip_id: str, photo_ids: List[str]):
    trip = get_trip(trip_id=trip_id)
    if trip:
        delete_photos(trip_id=trip_id, photo_ids=photo_ids)
