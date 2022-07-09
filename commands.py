from abc import ABC, abstractmethod

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from controller import Controller
from data.keyboards import profile_inline_keyboard, keyboards_by_status_event_and_by_rank
from enums.ranks import Rank
from enums.steps import Step
from models import User, Interest, Achievement, LocalGroup
from models.basemodel import BaseModel


class Command(ABC):
    @abstractmethod
    async def execute(self, controller: Controller, user: User, message: Message):
        pass

    @abstractmethod
    def can_execute(self, user: User, message: Message) -> bool:
        pass


class GetMyEventsCommand(Command, ABC):
    async def execute(self, controller: Controller, user: User, message: Message):
        events = controller.get_events_by_user(
            user.id) if user.rank == Rank.ORGANIZER else controller.get_events_by_user_without_finished(user.id)
        if len(events) == 0:
            await message.answer('В данный момент у вас нет мероприятий')
        else:
            for event in events:
                str_event = f'⭐️Название: {event.name}\n'
                if user.rank is not Rank.USER:
                    str_event += f'├    ID: {event.id}\n'
                str_event += f'├    Описание: {event.description if event.description is not None else "отсутствует"}\n' \
                             f'└    Дата: {event.date if event.date is not None else "не назначена"}'

                try:
                    keyboard = keyboards_by_status_event_and_by_rank[event.status][user.rank](event)
                except KeyError:
                    keyboard = None
                if event.lat is not None and event.lng is not None:
                    await message.answer_location(event.lat, event.lng)
                await message.answer(str_event, reply_markup=keyboard)

    def can_execute(self, user: User, message: Message) -> bool:
        return (user.rank == Rank.USER or
                user.rank == Rank.MODER or
                user.rank == Rank.ORGANIZER) and 'мои мероприятия' in message.text.lower()


class GetAllEventsCommand(Command, ABC):
    async def execute(self, controller: Controller, user: User, message: Message):
        events = controller.get_events_not_participate_user(user.id)
        if len(events) == 0:
            await message.answer('В данный момент нет активных мероприятий')
        else:
            for event in events:
                keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton('Записаться на мероприятие', callback_data=f'tp_{event.id}'))
                if event.lat is not None and event.lng is not None:
                    await message.answer_location(event.lat, event.lng)
                await message.answer(f'⭐️Название: {event.name}\n'
                                     f'├    Описание: {event.description if event.description is not None else "отсутствует"}\n'
                                     f'└    Дата: {event.date if event.date is not None else "не назначена"}',
                                     reply_markup=keyboard)

    def can_execute(self, user: User, message: Message) -> bool:
        return (user.rank == Rank.USER or
                user.rank == Rank.MODER) and 'все мероприятия' in message.text.lower()


class AddSomethingCommand(Command, ABC):
    rank: Rank
    step: Step
    name: str

    def __init__(self, rank, step, name, _type):
        self.rank = rank
        self.step = step
        self.name = name
        self._type = _type

    async def execute(self, controller: Controller, user: User, message: Message):
        controller.set_step_to_user(user, self.step)
        await message.answer(f'Ввведите {self._type} нового {self.name}')

    def can_execute(self, user: User, message: Message) -> bool:
        return user.rank == self.rank and f'добавить {self.name}' in message.text.lower()


class ManageSomethingCommand(Command, ABC):
    name: str
    model: BaseModel

    def __init__(self, name, model):
        self.name = name
        self.model = model

    async def execute(self, controller: Controller, user: User, message: Message):
        entities = controller.get_entities_by_model(self.model)
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
    async def execute(self, controller: Controller, user: User, message: Message):
        text = f'🦔{user.first_name} {user.middle_name} {user.last_name}\n' \
               f'├ Номер телефона: {user.phone}\n' \
               f'├ Почта: {user.email}\n' \
               f'├ Ваши группы: {", ".join([group.name for group in user.groups]) if len(user.groups) != 0 else "отсутствуют"}\n' \
               f'└ Ваши интересы {", ".join([interest.name for interest in user.interests]) if len(user.interests) != 0 else "отсутствуют"}'
        await message.answer(text, reply_markup=profile_inline_keyboard)
        # TODO: ВЫВОД ДОСТИЖЕНИЙ

    def can_execute(self, user: User, message: Message) -> bool:
        return 'мой профиль' in message.text.lower()


class UnknownCommand(Command, ABC):
    async def execute(self, controller: Controller, user: User, message: Message):
        await message.answer('Неизвестная команда')

    def can_execute(self, user: User, message: Message) -> bool:
        return True


commands = [GetMyEventsCommand(),
            GetAllEventsCommand(),
            GetMyProfileCommand(),
            ManageSomethingCommand('Интересы', Interest),
            ManageSomethingCommand('Группы', LocalGroup),
            ManageSomethingCommand('Достижения', Achievement),
            AddSomethingCommand(Rank.ADMIN, Step.NEW_ORGANIZER_ID, 'организатора', 'ID'),
            AddSomethingCommand(Rank.ORGANIZER, Step.NEW_MODER_ID, 'модератора', 'ID'),
            AddSomethingCommand(Rank.ORGANIZER, Step.EVENT_NAME, 'мероприятие', 'название')]
unknown_command = UnknownCommand()


def get_command(user, message) -> Command:
    for command in commands:
        if message.text is not None and command.can_execute(user, message):
            return command

    return unknown_command
