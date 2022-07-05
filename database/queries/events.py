from sqlalchemy import and_

from database.base import DBSession
from database.models import Event, User, EventUsers
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
