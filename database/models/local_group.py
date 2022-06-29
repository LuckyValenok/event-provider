from sqlalchemy import Column, VARCHAR, SMALLINT, Integer, DateTime

from .base import BaseModel


class local_group(BaseModel):
    __tablename__ = 'local_group'

    local_group_id = Column(Integer, nullable=False, unique=True, primary_key=True)
    local_group_name = Column(VARCHAR(255), nullable=False)

