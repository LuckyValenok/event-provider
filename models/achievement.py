from sqlalchemy import Column, VARCHAR, BLOB, Integer, ForeignKey

from .basemodel import BaseModel


class Achievement(BaseModel):
    __tablename__ = 'achievement'

    name = Column(VARCHAR(255), nullable=False, index=True)
    image = Column(BLOB, nullable=True)
    creator = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=True, index=True)


class OrganizerToUserAchievement(BaseModel):
    __tablename__ = 'organizer_to_user_achievement'

    organizer_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
