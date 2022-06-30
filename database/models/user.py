from sqlalchemy import Column, VARCHAR, SMALLINT, Integer, ForeignKey
from sqlalchemy.orm import relation

from enums.ranks import Rank
from enums.steps import Step
from .base import BaseModel
from .achievement import Achievement
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
    rank_id = Column(SMALLINT(), nullable=False)
    step_id = Column(Integer, nullable=False)

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

    def rank(self) -> Rank:
        return Rank(self.rank_id)

    def step(self) -> Step:
        return Step(self.step_id)
