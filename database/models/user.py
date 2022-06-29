from sqlalchemy import Column, VARCHAR, SMALLINT, Integer

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'

    user_id = Column(Integer, nullable=False, unique=True, primary_key=True)
    first_name = Column(VARCHAR(255), nullable=False)
    middle_name = Column(VARCHAR(255), nullable=False)
    last_name = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    phone = Column(VARCHAR(255), unique=True, nullable=True)
    rank = Column(SMALLINT(), nullable=False)

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'
