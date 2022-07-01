from abc import ABC, abstractmethod

from database.queries.users import get_events_by_user
from enums.ranks import Rank
from enums.steps import Step


class Command(ABC):
    @abstractmethod
    def execute(self, db_session, user, text) -> str:
        pass

    @abstractmethod
    def can_execute(self, user, text) -> bool:
        pass


class GetMyEventsCommand(Command, ABC):
    def execute(self, db_session, user, text) -> str:
        events = get_events_by_user(db_session, user.id)
        return f'{events}'

    def can_execute(self, user, text) -> bool:
        return user.rank == Rank.USER and 'мои мероприятия' in text.lower()


class AddManagerCommand(Command, ABC):
    def execute(self, db_session, user, text) -> str:
        user.step = Step.ENTER_NEW_MANAGER_ID
        db_session.commit_session()
        return 'Ввведите ID нового менеджера'

    def can_execute(self, user, text) -> bool:
        return user.rank == Rank.ADMIN and 'добавить менеджера' in text.lower()


class UnknownCommand(Command, ABC):
    def execute(self, db_session, user, text) -> str:
        return 'Неизвестная команда'

    def can_execute(self, user, text) -> bool:
        return True


# UnknownCommand нужно оставлять последней
commands = [GetMyEventsCommand(), AddManagerCommand(), UnknownCommand()]


def get_command(user, text) -> Command:
    for command in commands:
        if command.can_execute(user, text):
            return command
