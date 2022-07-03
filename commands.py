import datetime
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
        current_timestamp = datetime.datetime.now().timestamp()
        str_events = []
        for event in events:
            if event.date is not None and current_timestamp > event.date:
                continue
            str_event = f'⭐️Название: {event.name}\n'
            if user.rank is not Rank.USER:
                str_event += f'├    ID: {event.id}\n'
            str_event += f'├    Описание: {event.description if event.description is not None else "отсутствует"}\n' \
                         f'├    Дата: {event.date if event.date is not None else "не назначена"}\n' \
                         f'└    Координаты места проведения: '
            if event.lat is not None and event.lng is not None:
                str_event += f'{event.lat} {event.lng}'
            else:
                str_event += 'не назначены'

            str_events.append(str_event)

        return '\n\n'.join(str_events)

    def can_execute(self, user, text) -> bool:
        return (user.rank == Rank.USER or
                user.rank == Rank.MODER or
                user.rank == Rank.ORGANIZER) and 'мои мероприятия' in text.lower()


class AddManagerCommand(Command, ABC):
    def execute(self, db_session, user, text) -> str:
        user.step = Step.ENTER_NEW_MANAGER_ID
        db_session.commit_session()
        return 'Ввведите ID нового менеджера'

    def can_execute(self, user, text) -> bool:
        return user.rank == Rank.ADMIN and 'добавить менеджера' in text.lower()


class AddEventCommand(Command, ABC):
    def execute(self, db_session, user, text) -> str:
        user.step = Step.ENTER_NEW_EVENT_NAME
        db_session.commit_session()
        return 'Ввведите название нового мероприятия'

    def can_execute(self, user, text) -> bool:
        return user.rank == Rank.ORGANIZER and 'добавить мероприятие' in text.lower()


class UnknownCommand(Command, ABC):
    def execute(self, db_session, user, text) -> str:
        return 'Неизвестная команда'

    def can_execute(self, user, text) -> bool:
        return True


# UnknownCommand нужно оставлять последней
commands = [GetMyEventsCommand(), AddManagerCommand(), AddEventCommand(), UnknownCommand()]


def get_command(user, text) -> Command:
    for command in commands:
        if command.can_execute(user, text):
            return command
