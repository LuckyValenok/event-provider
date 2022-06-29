from sqlalchemy import Column, VARCHAR, SMALLINT, Integer

from .base import BaseModel


class achievement(BaseModel):
    __tablename__ = 'achievement'

    achievement_id = Column(Integer, nullable=False, unique=True, primary_key=True)
    achievement_name = Column(VARCHAR(255), nullable=False)

