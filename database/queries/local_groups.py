from database.models import LocalGroup
from ..base import DBSession


def get_group_by_id(session: DBSession, gid: int) -> LocalGroup:
    return session.query(LocalGroup).filter(LocalGroup.id == gid).one()


def get_groups(session: DBSession) -> list[LocalGroup]:
    return session.query(LocalGroup).all()
