"""
PostgreSQL ORM.
"""
from __future__ import annotations

import logging
import uuid

from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import current_app
from flask_login import UserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from sqlalchemy import Column, TEXT, ForeignKey, TIMESTAMP, VARCHAR, INTEGER, desc, asc, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash

from wonderline_app.api.common.enums import SortType, SearchSortType
from wonderline_app.core.image_service import DEFAULT_AVATAR_URL
from wonderline_app.db.postgres.exceptions import UserNotFound, UserPasswordIncorrect, UserTokenInvalid, \
    UserTokenExpired
from wonderline_app.db.postgres.init import db_session, postgres_meta_data
from wonderline_app.utils import convert_date_to_timestamp_in_expected_unit, edit_distance

LOGGER = logging.getLogger(__name__)


class Custom:
    """Some custom logic here!"""

    def to_dict(self) -> Dict[str, Any]:
        """Serializes only column data."""
        return {k: v for k, v in self.__dict__.items() if k != 'query' and not k.startswith('_')}


Base = declarative_base(cls=Custom, metadata=postgres_meta_data)


class User(Base, UserMixin):
    """Sqlalchemy User model"""
    __tablename__ = '_user'

    __reduced_keys = ['id', 'name', 'accessLevel', 'avatarSrc', 'uniqueName']

    query = db_session.query_property()

    id = Column(TEXT, primary_key=True)
    email = Column(VARCHAR(254), nullable=False)
    password = Column(CHAR(), nullable=False, unique=True)
    name = Column(VARCHAR(255), nullable=False)
    uniqueName = Column("unique_name", VARCHAR(255), nullable=False)
    createTime = Column("create_time", TIMESTAMP, nullable=False)
    accessLevel = Column("access_level", VARCHAR(255), default='everyone')
    avatarSrc = Column("avatar_src", TEXT, default=DEFAULT_AVATAR_URL)
    signature = Column(TEXT)
    profileLqSrc = Column("profile_lq_src", TEXT)
    profileSrc = Column("profile_src", TEXT)
    followerNb = Column("follower_nb", INTEGER, default=0)
    followers = relationship("Followed", primaryjoin='User.id==Followed.from_id')
    followees = relationship("Following", primaryjoin='User.id==Following.from_id')

    def __str__(self):
        return repr(self.to_dict)

    def generate_auth_token(self, expiration=7200):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode("ascii")

    def verify_auth_token(self, token: str):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired as e:
            LOGGER.exception(e)
            raise UserTokenExpired
        except BadSignature as e:
            LOGGER.exception(e)
            raise UserTokenInvalid
        if self.id != data['id']:
            raise UserTokenInvalid

    @classmethod
    def does_user_email_exist(cls, email: str) -> bool:
        return cls.query.filter_by(email=email).first() is not None

    @classmethod
    def does_user_unique_name_exist(cls, unique_name: str) -> bool:
        return cls.query.filter_by(uniqueName=unique_name).first() is not None

    @classmethod
    def create_new_user(cls, email: str, name: str, unique_name: str, password: str, avatar_url: str) -> User:
        user_id = str(uuid.uuid1())
        user = User(
            id=user_id,
            email=email,
            password=generate_password_hash(password, method='sha512'),
            name=name,
            uniqueName=unique_name,
            createTime=datetime.now(),
            avatarSrc=avatar_url
        )
        db_session.add(user)
        db_session.commit()
        LOGGER.info(f"Succeeded to create a new user email:{email}, name: {name}, id: {user_id}")
        return user

    @classmethod
    def get_user_if_valid(cls, email: str, password: str) -> User:
        user = cls.query.filter_by(email=email).first()
        if not user:
            raise UserNotFound
        else:
            if not check_password_hash(user.password, password):
                raise UserPasswordIncorrect
            return user

    @classmethod
    def get(cls, user_id: str, **kwargs) -> User:
        if user_id is None:
            raise ValueError("user_id is expected to a str, got None")
        try:
            return cls.query.filter_by(id=user_id, **kwargs).one()
        except NoResultFound:
            LOGGER.warning(f"User {user_id} is not found from PostgreSQL database.")
            raise UserNotFound(f'User {user_id} is not found')

    @classmethod
    def get_user_or_none(cls, user_id) -> Optional[User]:
        try:
            return User.get(user_id=user_id)
        except UserNotFound:
            return None

    @classmethod
    def get_user_attributes_or_none(cls, user_id, reduced=True, **kwargs) -> Optional[Dict]:
        user = cls.get_user_or_none(user_id=user_id)
        if user:
            if reduced:
                return user.to_reduced_dict()
            return user.get_complete_attributes(**kwargs)
        return None

    @classmethod
    def get_users_by_ids(cls, user_ids: List[str], sort_by: str = SortType.CREATE_TIME.value, sort_desc: bool = True,
                         start_index: int = 0,
                         user_nb: int = 6) -> List[User]:
        if user_ids is None or not len(user_ids):
            return []
        if sort_desc:
            sort_order = desc
        else:
            sort_order = asc
        if user_nb is None:  # when user_nb is None, get all the users starting from start_index
            end_index = None
        else:
            end_index = start_index + user_nb
        return cls.query.filter(cls.id.in_(user_ids)). \
            order_by(sort_order(getattr(User, sort_by))). \
            slice(start_index, end_index). \
            all()

    def to_reduced_dict(self) -> Dict:
        user_info_mapping = super().to_dict()
        return {k: user_info_mapping[k] for k in self.__reduced_keys}

    def to_dict(self) -> Dict:
        user_dict = super().to_dict()
        user_dict['reducedUser'] = {}
        for attr_key in list(user_dict.keys()):
            if attr_key in self.__reduced_keys:
                user_dict['reducedUser'][attr_key] = user_dict[attr_key]
                del user_dict[attr_key]
        user_dict['createTime'] = convert_date_to_timestamp_in_expected_unit(user_dict['createTime'])
        return user_dict

    def get_complete_attributes(self, follower_nb: int, sort_by: str = SortType.CREATE_TIME.value,
                                start_index: int = 0) -> Dict:
        """The returned dictionary contains the information about followers"""
        user_dict = self.to_dict()
        user_dict['followers'] = self.get_followers_with_reduced_attributes(
            follower_nb=follower_nb,
            sort_by=sort_by,
            start_index=start_index)
        user_dict['isFollowedByLoginUser'] = current_user.id in (u.to_id for u in self.followers)
        return user_dict

    def get_followers(self, follower_nb: int, sort_by: str = SortType.CREATE_TIME.value, start_index: int = 0) -> List[
        User]:
        return User.query. \
            join(Followed, User.id == Followed.to_id). \
            filter(Followed.from_id == self.id). \
            order_by(desc(getattr(User, sort_by))). \
            slice(start_index, start_index + follower_nb). \
            all()

    def get_followers_with_reduced_attributes(self, follower_nb: int, sort_by: str = SortType.CREATE_TIME.value,
                                              start_index: int = 0) -> List[Dict]:
        if follower_nb <= 0:
            return []
        if start_index < 0:
            raise ValueError(f"start_index is expected to be non-negative, got {start_index}")
        followers = self.get_followers(
            follower_nb=follower_nb,
            sort_by=sort_by,
            start_index=start_index
        )
        return [follower.to_reduced_dict() for follower in followers]

    @staticmethod
    def search_users(name_query: str, start_index: int = 0, nb: int = 12,
                     sort_type: str = SearchSortType.BEST_MATCH.value) -> List[Dict]:
        if name_query is None or not len(name_query):
            return []
        matched_users = User.query.filter(User.name.ilike(f"%{name_query}%")).all()
        if sort_type == SearchSortType.BEST_MATCH.value:
            matched_users.sort(key=lambda x: edit_distance(word1=name_query, word2=x.name))
        else:
            raise ValueError("Unknown sort_type for searching users")
        if matched_users:
            return [u.to_reduced_dict() for u in matched_users[start_index: start_index + nb]]
        return []


class Following(Base):
    """Sqlalchemy Following model"""
    __tablename__ = 'following'

    query = db_session.query_property()

    from_id = Column(TEXT, ForeignKey('_user.id'), primary_key=True)
    to_id = Column(TEXT, ForeignKey('_user.id'), primary_key=True)
    follow_time = Column(TIMESTAMP, nullable=False)


class Followed(Base):
    """Sqlalchemy Followed model"""
    __tablename__ = 'followed'

    query = db_session.query_property()

    from_id = Column(TEXT, ForeignKey('_user.id'), primary_key=True)
    to_id = Column(TEXT, ForeignKey('_user.id'), primary_key=True)
    follow_time = Column(TIMESTAMP, nullable=False)
