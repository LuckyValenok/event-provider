from sqlalchemy import Column, VARCHAR, BLOB, Integer, ForeignKey

from .basemodel import BaseModel


class Achievement(BaseModel):
    __tablename__ = 'achievement'

    name = Column(VARCHAR(255), nullable=False, index=True)
    image = Column(BLOB, nullable=True)
    creator = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=True, index=True)


class UserAchievement(BaseModel):
    __tablename__ = 'achievement_to_user'
    org_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
