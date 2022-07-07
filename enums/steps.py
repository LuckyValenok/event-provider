from enum import Enum, unique


@unique
class Step(Enum):
    NONE = 0,
    FIRST_NAME = 1,
    MIDDLE_NAME = 2,
    LAST_NAME = 3,
    PHONE = 4,
    EMAIL = 5,
    NEW_EVENT_NAME = 7,
    NEW_ORGANIZER_ID = 8,
    INTEREST_NAME_FOR_ADD = 9,
    INTEREST_NAME_FOR_REMOVE = 10,
    ACHIEVEMENT_NAME_FOR_ADD = 11,
    ACHIEVEMENT_NAME_FOR_REMOVE = 12,
    GROUP_NAME_FOR_ADD = 13,
    GROUP_NAME_FOR_REMOVE = 14,
    FEEDBACK_TEXT = 15,
    VERIFICATION_PRESENT = 16,
    NEW_MODER_ID = 17,
    FIRST_NAME_ONLY = 18,
    MIDDLE_NAME_ONLY = 19,
    LAST_NAME_ONLY = 20,
    PHONE_ONLY = 21,
    EMAIL_ONLY = 22
