from sqlalchemy import Column, Integer, ForeignKey
from .basemodel import BaseModel


class OrgRateUser(BaseModel):
    __tablename__ = 'user_rate'

    org_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)