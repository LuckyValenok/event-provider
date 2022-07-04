from database.base import DBSession
from database.models import Event, User, EventUsers


def get_events_by_id(session: DBSession, eid: int):
    return session.query(Event).filter(Event.id == eid).one()


def get_events_by_user(session: DBSession, uid: int):
    return session.query(Event).filter(Event.users.any(User.id == uid)).all()


def get_events_not_participate_user(session: DBSession, uid: int):
    return session.query(Event).filter(~Event.users.any(User.id == uid)).all()

# Вариант с человеками
def get_attendance_of_event(event_id, session: DBSession):
    return session.query(EventUsers, User, Event) \
        .filter(EventUsers.user_id == User.id, EventUsers.event_id == Event.id) \
        .with_entities(User.first_name, User.middle_name, User.last_name, Event.name)

# Вариант с подсчётом количества пришедших
def get_count_visited(event_id, session: DBSession) -> int:
    return session.query(EventUsers).filter(EventUsers.event_id == event_id).count()
