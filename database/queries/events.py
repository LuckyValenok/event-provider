import random
import string

from sqlalchemy import and_

from database.base import DBSession
from database.models import Event, User, EventUsers, EventEditors, EventFeedbacks
from database.models.event import EventCodes
from enums.ranks import Rank
from enums.status_attendion import StatusAttendion


def get_event_by_id(session: DBSession, eid: int) -> Event:
    return session.query(Event).filter(Event.id == eid).one()


def get_events_by_user(session: DBSession, uid: int):
    return session.query(Event).filter(Event.users.any(User.id == uid)).all()


def get_events_not_participate_user(session: DBSession, uid: int):
    return session.query(Event).filter(~Event.users.any(User.id == uid)).all()


# Вариант с подсчётом количества пришедших
def get_count_visited(session: DBSession, eid: int) -> int:
    return len(session.query(Event).filter(
        and_(Event.id == eid, EventUsers.status_attendion == StatusAttendion.ARRIVED,
             User.rank == Rank.USER)).all())


def get_editor_event(session: DBSession, uid: int) -> EventEditors:
    return session.query(EventEditors).filter(EventEditors.user_id == uid).one()


def get_new_code(session: DBSession) -> str:
    code = None
    while code is None or session.query(EventCodes).filter(EventCodes.code == code).count() > 0:
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return code


def get_code_model_by_id(session: DBSession, eid: int, uid: int) -> EventCodes:
    return session.query(EventCodes).filter(and_(EventCodes.event_id == eid, EventCodes.user_id == uid)).one()


def get_feedbacks(session: DBSession, eid: int):
    return session.query(EventFeedbacks).filter(EventFeedbacks.event_id == eid).all()
