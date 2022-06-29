from sqlalchemy import Integer, Column, ForeignKey

from .base import BaseModel


class event_user(BaseModel):
    __tablename__ = 'event_user'

    event_id = Column(Integer, ForeignKey('event.event_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)