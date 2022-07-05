from enum import Enum, unique


@unique
class StatusEvent(Enum):
    UNFINISHED = 1,
    FINISHED = 2,
