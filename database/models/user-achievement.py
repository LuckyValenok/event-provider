from sqlalchemy import Integer, Column, ForeignKey

from .base import BaseModel


class user_achievement(BaseModel):
    __tablename__ = 'user-achievement'

    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievement.achievement_id'), nullable=False)

