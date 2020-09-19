"""
PostgreSQL ORM.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

from sqlalchemy import Column, TEXT, ForeignKey, TIMESTAMP, VARCHAR, INTEGER, desc, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from wonderline_app.db.postgres.exceptions import UserNotFound
from wonderline_app.db.postgres.init import db_session, postgres_meta_data
from wonderline_app.utils import convert_date_to_timestamp

LOGGER = logging.getLogger(__name__)


class Custom:
    """Some custom logic here!"""

    def to_dict(self) -> Dict[str, Any]:
        """Serializes only column data."""
        return {k: v for k, v in self.__dict__.items() if k != 'query' and not k.startswith('_')}


Base = declarative_base(cls=Custom, metadata=postgres_meta_data)


class User(Base):
    """Sqlalchemy User model"""
    __tablename__ = '_user'

    __reduced_keys = ['id', 'name', 'accessLevel', 'avatarSrc']

    query = db_session.query_property()

    id = Column(TEXT, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    createTime = Column("create_time", TIMESTAMP, nullable=False)
    accessLevel = Column("access_level", VARCHAR(255))
    avatarSrc = Column("avatar_src", TEXT)
    signature = Column(TEXT)
    profileLqSrc = Column("profile_lq_src", TEXT)
    profileSrc = Column("profile_src", TEXT)
    followerNb = Column("follower_nb", INTEGER, default=0)
    followers = relationship("Followed", primaryjoin='User.id==Followed.from_id')
    followees = relationship("Following", primaryjoin='User.id==Following.from_id')

    def __str__(self):
        return repr(self.to_dict)

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
    def get_users_by_ids(cls, user_ids: List[str], sort_by: str = "createTime", sort_desc: bool = True,
                         start_index: int = 0,
                         user_nb: int = 6) -> List[User]:
        if user_ids is None or not len(user_ids):
            return []
        if sort_desc:
            sort_order = desc
        else:
            sort_order = asc
        return cls.query.filter(cls.id.in_(user_ids)). \
            order_by(sort_order(getattr(User, sort_by))). \
            slice(start_index, start_index + user_nb). \
            all()

    def to_reduced_dict(self) -> Dict:
        user_info_mapping = super().to_dict()
        return {k: user_info_mapping[k] for k in self.__reduced_keys}

    def to_dict(self) -> Dict:
        user_dict = super().to_dict()
        user_dict['createTime'] = convert_date_to_timestamp(user_dict['createTime'])
        return user_dict

    def get_complete_attributes(self, follower_nb: int, sort_by: str, start_index: int) -> Dict:
        """The returned dictionary contains the information about followers"""
        user_dict = self.to_dict()
        user_dict['followers'] = self.get_followers_with_reduced_attributes(
            follower_nb=follower_nb,
            sort_by=sort_by,
            start_index=start_index)
        return user_dict

    def get_followers(self, follower_nb: int, sort_by: str = "createTime", start_index: int = 0) -> List[User]:
        return User.query. \
            join(Followed, User.id == Followed.to_id). \
            filter(Followed.from_id == self.id). \
            order_by(desc(getattr(User, sort_by))). \
            slice(start_index, start_index + follower_nb). \
            all()

    def get_followers_with_reduced_attributes(self, follower_nb: int, sort_by: str = "createTime",
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
