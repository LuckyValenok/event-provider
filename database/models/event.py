from sqlalchemy import Column, VARCHAR, DateTime, ForeignKey, Integer

from .base import BaseModel


class Event(BaseModel):
    __tablename__ = 'event'

    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(255), nullable=False)
    date = Column(DateTime, nullable=False)


class EventGroups(BaseModel):
    __tablename__ = 'event_groups'

    event_id = Column(Integer, ForeignKey('event.id', ondelete='CASCADE'), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey('local_group.id', ondelete='CASCADE'), nullable=False, index=True)


class EventInterests(BaseModel):
    __tablename__ = 'event_interests'

    event_id = Column(Integer, ForeignKey('event.id', ondelete='CASCADE'), nullable=False, index=True)
    interest_id = Column(Integer, ForeignKey('interest.id', ondelete='CASCADE'), nullable=False, index=True)


class EventUsers(BaseModel):
    __tablename__ = 'event_users'

    event_id = Column(Integer, ForeignKey('event.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
