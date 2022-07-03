from database.models import User
from ..base import DBSession


def get_user_by_id(session: DBSession, uid: int) -> User:
    return session.query(User).filter(User.id == uid).one()


def has_user_by_id(session: DBSession, uid: int) -> bool:
    return session.query(User).filter(User.id == uid).one_or_none() is not None
