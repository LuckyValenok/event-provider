from sqlalchemy import Column, VARCHAR, ForeignKey, Integer, TIMESTAMP, Float, Enum
from sqlalchemy.orm import relation

from enums.status_attendion import StatusAttendion
from enums.status_event import StatusEvent
from . import User, Interest, LocalGroup
from .base import BaseModel


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
    status_attendion = Column(Enum(StatusAttendion), nullable=False, default=StatusAttendion.NOT_ARRIVED, index=True)

class FeedBack(BaseModel):
    __tablename__ = 'feedback'

    event_id = Column(Integer, ForeignKey('event.id', ondelete='CASCADE'), nullable=False, index=True)
    fb_text = Column(VARCHAR(255), nullable=True)

class Event_FeedBack(BaseModel):
    __tablename__ = 'user-ev'

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('event.id', ondelete='CASCADE'), nullable=False, index=True)




class Event(BaseModel):
    __tablename__ = 'event'

    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(255), nullable=True)
    date = Column(TIMESTAMP, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    status = Column(Enum(StatusEvent), nullable=False, default=StatusEvent.UNFINISHED)

    users = relation(
        User,
        secondary=EventUsers.__tablename__
    )
    interests = relation(
        Interest,
        secondary=EventInterests.__tablename__
    )
    groups = relation(
        LocalGroup,
        secondary=EventGroups.__tablename__
    )
