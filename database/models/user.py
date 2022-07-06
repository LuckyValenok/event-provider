from sqlalchemy import Column, VARCHAR, Integer, ForeignKey, Enum
from sqlalchemy.orm import relation

from enums.ranks import Rank
from enums.steps import Step
from .achievement import Achievement
from .base import BaseModel
from .interest import Interest
from .local_group import LocalGroup


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


class User(BaseModel):
    __tablename__ = 'user'

    BaseModel.id = Column(Integer, nullable=False, unique=True, primary_key=True)
    first_name = Column(VARCHAR(255), nullable=True)
    middle_name = Column(VARCHAR(255), nullable=True)
    last_name = Column(VARCHAR(255), nullable=True)
    email = Column(VARCHAR(255), nullable=True, unique=True)
    phone = Column(VARCHAR(255), nullable=True, unique=True)
    rank = Column(Enum(Rank), nullable=False)
    step = Column(Enum(Step), nullable=False)

    achievements = relation(
        Achievement,
        secondary=UserAchievements.__tablename__
    )
    interests = relation(
        Interest,
        secondary=UserInterests.__tablename__
    )
    groups = relation(
        LocalGroup,
        secondary=UserGroups.__tablename__
    )

    def set_first_name(self, name):
        self.first_name = name

    def set_middle_name(self, name):
        self.middle_name = name

    def set_last_name(self, name):
        self.last_name = name

    def set_email(self, email):
        self.email = email

    def set_phone(self, phone):
        self.phone = phone
