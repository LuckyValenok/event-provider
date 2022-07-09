from sqlalchemy import Column, VARCHAR, ForeignKey, Integer, TIMESTAMP, Float, Enum
from sqlalchemy.orm import relation

from enums.status_attendion import StatusAttendion
from enums.status_event import StatusEvent
from models import User, Interest, LocalGroup
from .basemodel import BaseModel


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
    status_attendion = Column(Enum(StatusAttendion), nullable=True, index=True)


class EventFeedbacks(BaseModel):
    __tablename__ = 'event_feedbacks'

    event_id = Column(Integer, ForeignKey('event.id', ondelete='CASCADE'), nullable=False, index=True)
    fb_text = Column(VARCHAR(255), nullable=True)


class EventEditors(BaseModel):
    __tablename__ = 'event_editors'

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('event.id', ondelete='CASCADE'), nullable=False, index=True)


class EventCodes(BaseModel):
    __tablename__ = 'event_codes'

    event_id = Column(Integer, ForeignKey('event.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    code = Column(VARCHAR(8), nullable=False, index=True)


class Event(BaseModel):
    __tablename__ = 'event'

    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(255), nullable=True)
    date = Column(TIMESTAMP, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    status = Column(Enum(StatusEvent), nullable=True)

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

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_date(self, date):
        self.date = date

    def set_location(self, location):
        self.lat = location.latitude
        self.lng = location.longitude
