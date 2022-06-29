from sqlalchemy import Column, VARCHAR

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    first_name = Column(VARCHAR(255), nullable=False)
    last_name = Column(VARCHAR(255), nullable=False)
    phone = Column(VARCHAR(255), unique=True, nullable=True)

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'
