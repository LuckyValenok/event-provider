from sqlalchemy import Column, VARCHAR, BLOB

from .basemodel import BaseModel


class Achievement(BaseModel):
    __tablename__ = 'achievement'

    name = Column(VARCHAR(255), nullable=False, index=True)
    image = Column(BLOB, nullable=True)
