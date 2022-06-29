from ..base import DBSession
from database.models import User


def get_user_by_id(session: DBSession, eid: int) -> User:
    user = session.query(User).filter(User.id == eid).one()

    return user


def has_user_by_id(session: DBSession, eid: int) -> bool:
    return session.query(User).filter(User.id == eid).one_or_none() is not None
