from sqlalchemy import Column, VARCHAR

from .basemodel import BaseModel


class Interest(BaseModel):
    __tablename__ = 'interest'

    name = Column(VARCHAR(255), nullable=False, index=True)
