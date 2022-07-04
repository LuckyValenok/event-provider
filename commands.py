from abc import ABC, abstractmethod

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from data.keyboards import profile_inline_keyboard
from database.base import DBSession
from database.models import User, Interest, Achievement, LocalGroup
from database.models.base import BaseModel
from database.queries.events import get_events_by_user, get_events_not_participate_user
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
        if len(events) == 0:
            await message.answer('В данный момент у вас нет мероприятий')
        else:
            for event in events:
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
                # TODO: взимодействие с этими мероприятиями
                await message.answer(str_event)

    def can_execute(self, user: User, message: Message) -> bool:
        return (user.rank == Rank.USER or
                user.rank == Rank.MODER or
                user.rank == Rank.ORGANIZER) and 'мои мероприятия' in message.text.lower()


class GetAllEventsCommand(Command, ABC):
    async def execute(self, db_session: DBSession, user: User, message: Message):
        events = get_events_not_participate_user(db_session, user.id)
        if len(events) == 0:
            await message.answer('В данный момент нет активных мероприятий')
        else:
            for event in events:
                str_event = f'⭐️Название: {event.name}\n' \
                            f'├    Описание: {event.description if event.description is not None else "отсутствует"}\n' \
                            f'├    Дата: {event.date if event.date is not None else "не назначена"}\n' \
                            f'└    Координаты места проведения: '
                if event.lat is not None and event.lng is not None:
                    str_event += f'{event.lat} {event.lng}'
                else:
                    str_event += 'не назначены'
                keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton('Записаться на мероприятие', callback_data=f'tp_{event.id}'))
                await message.answer(str_event, reply_markup=keyboard)

    def can_execute(self, user: User, message: Message) -> bool:
        return (user.rank == Rank.USER or
                user.rank == Rank.MODER) and 'все мероприятия' in message.text.lower()


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


class ManageSomethingCommand(Command, ABC):
    name: str
    model: BaseModel

    def __init__(self, name, model):
        self.name = name
        self.model = model

    async def execute(self, db_session: DBSession, user: User, message: Message):
        entities = db_session.query(self.model).all()
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton('Добавить', callback_data='add_' + self.model.__tablename__))
        if len(entities) != 0:
            keyboard.row(InlineKeyboardButton('Удалить', callback_data='remove_' + self.model.__tablename__))
        await message.answer(f'{self.name}: '
                             f'{", ".join([entity.name for entity in entities]) if len(entities) != 0 else "пока отсутствуют"}',
                             reply_markup=keyboard)

    def can_execute(self, user: User, message: Message) -> bool:
        return user.rank == Rank.ADMIN and f'{self.name.lower()}' in message.text.lower()


class GetMyProfileCommand(Command, ABC):
    async def execute(self, db_session: DBSession, user: User, message: Message):
        text = f'🧚{user.first_name} {user.middle_name} {user.last_name}\n' \
               f'├ Номер телефона: {user.phone}\n' \
               f'├ Почта: {user.email}\n' \
               f'├ Ваши группы: {", ".join([group.name for group in user.groups]) if len(user.groups) != 0 else "отсутствуют"}\n' \
               f'└ Ваши интересы {", ".join([interest.name for interest in user.interests]) if len(user.interests) != 0 else "отсутствуют"}'
        await message.answer(text, reply_markup=profile_inline_keyboard)
        # TODO: ВЫВОД ДОСТИЖЕНИЙ

    def can_execute(self, user: User, message: Message) -> bool:
        return 'мой профиль' in message.text.lower()


class UnknownCommand(Command, ABC):
    async def execute(self, db_session: DBSession, user: User, message: Message):
        await message.answer('Неизвестная команда')

    def can_execute(self, user: User, message: Message) -> bool:
        return True


# UnknownCommand нужно оставлять последней
commands = [GetMyEventsCommand(),
            GetAllEventsCommand(),
            GetMyProfileCommand(),
            ManageSomethingCommand('Интересы', Interest),
            ManageSomethingCommand('Группы', LocalGroup),
            ManageSomethingCommand('Достижения', Achievement),
            AddSomethingCommand(Rank.ADMIN, Step.ENTER_NEW_MANAGER_ID, 'менеджера'),
            AddSomethingCommand(Rank.MANAGER, Step.ENTER_NEW_ORGANIZER_ID, 'организатора'),
            AddSomethingCommand(Rank.ORGANIZER, Step.ENTER_NEW_EVENT_NAME, 'мероприятие'),
            UnknownCommand()]


def get_command(user, message) -> Command:
    for command in commands:
        if command.can_execute(user, message):
            return command
