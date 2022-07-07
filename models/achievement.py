from sqlalchemy import Column, VARCHAR

from .basemodel import BaseModel


class Achievement(BaseModel):
    __tablename__ = 'achievement'

    name = Column(VARCHAR(255), nullable=False, index=True)
