from sqlalchemy import Column, VARCHAR, SMALLINT, Integer, ForeignKey

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'

    BaseModel.id = Column(Integer, nullable=False, unique=True, primary_key=True)
    first_name = Column(VARCHAR(255), nullable=False)
    middle_name = Column(VARCHAR(255), nullable=False)
    last_name = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), nullable=True, unique=True)
    phone = Column(VARCHAR(255), nullable=True, unique=True)
    rank = Column(SMALLINT(), nullable=False)

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


class UserAchievements(BaseModel):
    __tablename__ = 'user_achievements'

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey('achievement.id', ondelete='CASCADE'), nullable=False, index=True)


class UserInterests(BaseModel):
    __tablename__ = 'user_interests'

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    interest_id = Column(Integer, ForeignKey('interest.id', ondelete='CASCADE'), nullable=False, index=True)


class UserGroups(BaseModel):
    __tablename__ = 'user_groups'

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey('local_group.id', ondelete='CASCADE'), nullable=False, index=True)
