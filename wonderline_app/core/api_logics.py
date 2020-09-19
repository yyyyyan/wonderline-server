"""
Implementations of users APIs' business logics.
"""
import logging
from typing import Dict, List, Optional, Callable, Union, Tuple

from wonderline_app.api.common.enums import AccessLevel
from wonderline_app.core.api_exceptions import APIError, APIError404, APIError500, APIError401
from wonderline_app.core.response import Response, Error
from wonderline_app.db.cassandra.exceptions import TripNotFound, CommentNotFound, PhotoNotFound
from wonderline_app.db.cassandra.models import AlbumsByUser, TripsByUser, HighlightsByUser, MentionsByUser, Trip, \
    PhotosByTrip, CommentsByPhoto, Photo, Comment
from wonderline_app.db.postgres.models import User

LOGGER = logging.getLogger(__name__)


def handle_request(func: Callable, *args, **kwargs) -> Union[Dict, Tuple[Dict, int]]:
    """
    Handle API requests.
    """
    response = Response()
    for arg_key, arg_value in kwargs.items():
        LOGGER.info(f"Receive arguments: key: {arg_key}, type: {type(arg_key)}, value: {arg_value}")
    user_token = kwargs.pop("user_token")
    try:
        verify_user_token(user_token=user_token, **kwargs)
        payload = func(*args, **kwargs)
    except APIError as exp:
        response.add_error(Error(code=exp.code, message=exp.message))
    except Exception as e:
        LOGGER.exception(e)
        response.add_error(APIError500(e))
    else:
        response.payload = payload
    if len(response.errors):
        return response.to_dict(), response.errors[0].code  # TODO: multiple errors
    return response.to_dict()


def verify_user_token(user_token, **kwargs):
    """Verify whether the user token is valid"""
    # TODO: implement the function
    if not user_token:
        raise APIError401(message="user token is None")


def get_user(user_id: str) -> Optional[User]:
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


def get_user_complete_attributes(user_id: str, followers_sort_type: str = "createTime", follower_nb: int = 6) -> Dict:
    """Get user's complete attributes including followers reduced attributes."""
    user = get_user(user_id=user_id)
    LOGGER.info(f"Getting complete user information for {user_id}")
    return user.get_complete_attributes(
        follower_nb=follower_nb,
        sort_by=followers_sort_type,
        start_index=0
    )


def get_user_followers(user_id: str, sort_type: str = "creteTime", nb: int = 50, start_index: int = 0) -> List:
    """Get user's followers with reduced attributes"""
    user = get_user(user_id=user_id)
    LOGGER.info(f"Getting followers for {user_id}")
    return user.get_followers_with_reduced_attributes(
        follower_nb=nb,
        sort_by=sort_type,
        start_index=start_index
    )


def get_albums_by_user(user_id: str, sort_type: str = "creteTime", nb: int = 3, start_index: int = 0,
                       access_level: str = AccessLevel.everyone.name)->List[Dict]:
    """Get all the albums for the user."""
    user = get_user(user_id=user_id)
    if user:
        LOGGER.info(f"Getting albums for user {user_id}")
        return AlbumsByUser.get_albums(
            user_id=user_id,
            sort_by=sort_type,
            nb=nb,
            access_level=access_level,
            start_index=start_index)


def get_trips_by_user(user_id: str, sort_type: str = "creteTime", nb: int = 3, start_index: int = 0,
                      access_level: str = AccessLevel.everyone.name)->List[Dict]:
    """Get all the trips for the user."""
    user = get_user(user_id=user_id)
    if user:
        LOGGER.info(f"Getting trips for user {user_id}")
        return TripsByUser.get_trips(
            user_id=user_id,
            sort_by=sort_type,
            nb=nb,
            access_level=access_level,
            start_index=start_index)


def get_highlights_by_user(user_id: str, sort_type: str = "creteTime", nb: int = 3, start_index: int = 0,
                           access_level: str = AccessLevel.everyone.name)->List[Dict]:
    """Get all the highlights for the user."""
    user = get_user(user_id=user_id)
    if user:
        LOGGER.info(f"Getting highlights for user {user_id}")
        return HighlightsByUser.get_highlights(
            user_id=user_id,
            sort_by=sort_type,
            nb=nb,
            access_level=access_level,
            start_index=start_index)


def get_mentions_by_user(user_id: str, sort_type: str = "creteTime", nb: int = 12, start_index: int = 0,
                         access_level: str = AccessLevel.everyone.name)->List[Dict]:
    """Get all the mentions for the user."""
    user = get_user(user_id=user_id)
    if user:
        LOGGER.info(f"Getting mentions for user {user_id}")
        return MentionsByUser.get_mentions(
            user_id=user_id,
            sort_by=sort_type,
            nb=nb,
            access_level=access_level,
            start_index=start_index)


def get_complete_trip(trip_id: str, users_sort_type: str = "createTime", user_nb: int = 6) -> Dict:
    """Get complete attributes for the trip."""
    trip = get_trip(trip_id=trip_id)
    LOGGER.info(f"Getting complete trip information for {trip_id}")
    return trip.get_complete_attributes(
        users_sort_type=users_sort_type,
        user_nb=user_nb,
    )


def get_users_by_trip(trip_id: str, sort_type: str = "creteTime", nb: int = 12, start_index: int = 0) -> List[Dict]:
    """Get all the users for a trip."""
    trip = get_trip(trip_id=trip_id)
    if trip:
        LOGGER.info(f"Getting users for trip {trip_id}")
        return trip.get_users(
            users_sort_type=sort_type,
            user_nb=nb,
            start_index=start_index)


def get_photos_by_trip(trip_id: str, sort_type: str = "creteTime", nb: int = 12, start_index: int = 0,
                       access_level: str = AccessLevel.everyone.name) -> List[Dict]:
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


def get_replies_by_comment(trip_id: str, photo_id: str, comment_id: str, sort_type: str = "creteTime", nb: int = 3,
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
