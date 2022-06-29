from sqlalchemy import Integer, Column, ForeignKey

from .base import BaseModel


class event_interest(BaseModel):
    __tablename__ = 'event_interest'

    event_id = Column(Integer, ForeignKey('event.event_id'), nullable=False)
    interest_id = Column(Integer, ForeignKey('interest.interest_id'), nullable=False)