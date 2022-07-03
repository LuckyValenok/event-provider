from database.base import DBSession
from database.models import Event, User


def get_events_by_user(session: DBSession, uid: int):
    return session.query(Event).filter(Event.users.any(User.id == uid)).all()


def get_events_not_participate_user(session: DBSession, uid: int):
    return session.query(Event).filter(Event.users.any(User.id != uid)).all()
