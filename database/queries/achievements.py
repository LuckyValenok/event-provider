from database.models import Achievement
from ..base import DBSession


def get_achievement_by_id(session: DBSession, aid: int) -> Achievement:
    return session.query(Achievement).filter(Achievement.id == aid).one()


def get_achievements(session: DBSession) -> list[Achievement]:
    return session.query(Achievement).all()
