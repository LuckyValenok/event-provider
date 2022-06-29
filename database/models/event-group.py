from sqlalchemy import Integer, Column, ForeignKey

from .base import BaseModel


class event_lg(BaseModel):
    __tablename__ = 'event_lg'

    event_id = Column(Integer, ForeignKey('event.event_id'), nullable=False)
    lg_id = Column(Integer, ForeignKey('local_group.local_group_id', nullable=False))