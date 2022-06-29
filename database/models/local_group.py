from sqlalchemy import Column, VARCHAR

from .base import BaseModel


class LocalGroup(BaseModel):
    __tablename__ = 'local_group'

    name = Column(VARCHAR(255), nullable=False)
