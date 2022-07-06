from enum import Enum, unique


@unique
class Rank(Enum):
    USER = 1
    MODER = 2
    ORGANIZER = 3
    ADMIN = 4
