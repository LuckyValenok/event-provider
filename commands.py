import datetime
from abc import ABC, abstractmethod

from aiogram.types import Message

from database.base import DBSession
from database.models import User
from database.queries.users import get_events_by_user
from enums.ranks import Rank
from enums.steps import Step


class Command(ABC):
    @abstractmethod
    async def execute(self, db_session: DBSession, user: User, message: Message):
        pass

    @abstractmethod
    def can_execute(self, user: User, message: Message) -> bool:
        pass


class GetMyEventsCommand(Command, ABC):
    async def execute(self, db_session: DBSession, user: User, message: Message):
        events = get_events_by_user(db_session, user.id)
        current_timestamp = datetime.datetime.now().timestamp()
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

            await message.answer(str_event)

    def can_execute(self, user: User, message: Message) -> bool:
        return (user.rank == Rank.USER or
                user.rank == Rank.MODER or
                user.rank == Rank.ORGANIZER) and 'мои мероприятия' in message.text.lower()


class AddSomethingCommand(Command, ABC):
    rank: Rank
    step: Step
    name: str

    def __init__(self, rank, step, name):
        self.rank = rank
        self.step = step
        self.name = name

    async def execute(self, db_session: DBSession, user: User, message: Message):
        user.step = self.step
        db_session.commit_session()
        await message.answer(f'Ввведите ID нового {self.name}')

    def can_execute(self, user: User, message: Message) -> bool:
        return user.rank == self.rank and f'добавить {self.name}' in message.text.lower()


class UnknownCommand(Command, ABC):
    async def execute(self, db_session: DBSession, user: User, message: Message):
        await message.answer('Неизвестная команда')

    def can_execute(self, user: User, message: Message) -> bool:
        return True


# UnknownCommand нужно оставлять последней
commands = [GetMyEventsCommand(),
            AddSomethingCommand(Rank.ADMIN, Step.ENTER_NEW_MANAGER_ID, 'менеджера'),
            AddSomethingCommand(Rank.MANAGER, Step.ENTER_NEW_ORGANIZER_ID, 'организатора'),
            AddSomethingCommand(Rank.ORGANIZER, Step.ENTER_NEW_EVENT_NAME, 'мероприятие'),
            UnknownCommand()]


def get_command(user, message) -> Command:
    for command in commands:
        if command.can_execute(user, message):
            return command
