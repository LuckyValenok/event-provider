from ..base import DBSession
from database.models import User


def get_user_by_id(session: DBSession, eid: int) -> User:
    return session.query(User).filter(User.id == eid).one()


def has_user_by_id(session: DBSession, eid: int) -> bool:
    return session.query(User).filter(User.id == eid).one_or_none() is not None
