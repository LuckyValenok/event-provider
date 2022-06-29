from sqlalchemy import Column, VARCHAR, SMALLINT, Integer

from .base import BaseModel


class interest(BaseModel):
    __tablename__ = 'interest'

    interest_id = Column(Integer, nullable=False, unique=True, primary_key=True)
    interest_name = Column(VARCHAR(255), nullable=False)

