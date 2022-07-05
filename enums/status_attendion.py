from enum import Enum, unique


@unique
class StatusAttendion(Enum):
    ARRIVED = 1,
    NOT_ARRIVED = 2,
