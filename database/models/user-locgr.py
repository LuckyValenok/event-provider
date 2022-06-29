from sqlalchemy import Integer, Column, ForeignKey

from .base import BaseModel


class user_locgr(BaseModel):
    __tablename__ = 'user-lg'

    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    lg_id = Column(Integer, ForeignKey('local_group.local_group_id'), nullable=False)