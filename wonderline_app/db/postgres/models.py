"""
PostgreSQL ORM.
"""
from typing import Dict, Any

from sqlalchemy import Column, TEXT, ForeignKey, TIMESTAMP, VARCHAR, INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from wonderline_app.db.postgres.init import db_session, mymetadata


class Custom:
    def _to_camel(self, var_name):
        return ''.join(word.title() if i != 0 else word for i, word in enumerate(var_name.split('_')))

    """Some custom logic here!"""

    def to_dict(self) -> Dict[str, Any]:
        """Serializes only column data."""
        return {self._to_camel(c.name): getattr(self, c.name) for c in self.__table__.columns}


Base = declarative_base(cls=Custom, metadata=mymetadata)


class User(Base):
    """Sqlalchemy User model"""
    __tablename__ = '_user'
    query = db_session.query_property()

    id = Column(TEXT, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False)
    access_level = Column(VARCHAR(255))
    avatar_src = Column(TEXT)
    signature = Column(TEXT)
    profile_lq_src = Column(TEXT)
    profile_src = Column(TEXT)
    follower_nb = Column(INTEGER, default=0)
    followers = relationship('Followed', primaryjoin='User.id==Followed.from_id')
    followees = relationship('Following', primaryjoin='User.id==Following.from_id')


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
