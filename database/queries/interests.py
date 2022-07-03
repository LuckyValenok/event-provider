from database.models import Interest
from ..base import DBSession


def get_interest_by_id(session: DBSession, iid: int) -> Interest:
    return session.query(Interest).filter(Interest.id == iid).one()


def get_interests(session: DBSession) -> list[Interest]:
    return session.query(Interest).all()
