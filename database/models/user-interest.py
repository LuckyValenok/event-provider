from sqlalchemy import Integer, Column, ForeignKey

from .base import BaseModel


class user_interest(BaseModel):
    __tablename__ = 'user_interest'

    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    interest_id = Column(Integer, ForeignKey('interest.interest_id'), nullable=False)