from enum import Enum, unique


@unique
class FriendRequestStatus(Enum):
    ACCEPTED = 1,
    WAITING = 2