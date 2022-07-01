from enum import Enum, unique


@unique
class Step(Enum):
    NONE = 0,
    ENTER_FIRST_NAME = 1,
    ENTER_MIDDLE_NAME = 2,
    ENTER_LAST_NAME = 3,
    ENTER_PHONE = 4,
    ENTER_EMAIL = 5,
    ENTER_NEW_MANAGER_ID = 6,
