from sqlalchemy import Column, VARCHAR, SMALLINT, Integer, DateTime

from .base import BaseModel


class event(BaseModel):
    __tablename__ = 'event'

    event_id = Column(Integer, nullable=False, unique=True, primary_key=True)
    event_name = Column(VARCHAR(255), nullable=False)
    event_description = Column(VARCHAR(255), nullable=False)
    event_date = Column(DateTime, nullable=False)

