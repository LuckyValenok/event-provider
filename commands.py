from abc import ABC, abstractmethod

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from controller import Controller, generate_image_achievements
from data.keyboards import profile_inline_keyboard, keyboards_by_status_event_and_by_rank
from enums.ranks import Rank
from enums.steps import Step
from formatter import plurals
from models import User, Interest, LocalGroup
from models.basemodel import BaseModel


class Command(ABC):
    @abstractmethod
    async def execute(self, controller: Controller, user: User, message: Message):
        pass

    @abstractmethod
    def can_execute(self, user: User, message: Message) -> bool:
        pass


class GetFriendListCommand(Command, ABC):
    async def execute(self, controller: Controller, user: User, message: Message):
        friend_list = controller.get_friend_list(user)
        if len(friend_list) == 0:
            await message.answer("У Вас пока нет друзей.")
        else:
            for friend in friend_list:
                keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton('Удалить из друзей', callback_data=f"deletefr_{friend.friend_id}"))
                await message.answer(friend[0] + " " + friend[1] + " " + friend[2], reply_markup=keyboard)

    def can_execute(self, user: User, message: Message) -> bool:
        return (user.rank == Rank.USER or user.rank == Rank.MODER) and 'мои друзья' in message.text.lower()


class GetFriendRequestListCommand(Command, ABC):
    async def execute(self, controller: Controller, user: User, message: Message):
        requests_list = controller.get_friend_requests(user.id)
        if len(requests_list) == 0:
            await message.answer("У Вас пока нет заявок в друзья.")
        else:
            for request in requests_list:
                keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton('Принять заявку', callback_data=f"acceptreq_{request.friend_id}"),
                    InlineKeyboardButton('Отклонить заявку', callback_data=f"declinereq_{request.friend_id}"))
                await message.answer(request[0] + " " + request[1] + " " + request[2] + " хочет добавить Вас в друзья!",
                                     reply_markup=keyboard)

    def can_execute(self, user: User, message: Message) -> bool:
        return (user.rank == Rank.USER or user.rank == Rank.MODER) and 'мои заявки в друзья' in message.text.lower()


class AddFriendCommand(Command, ABC):
    async def execute(self, controller: Controller, user: User, message: Message):
        user.step = Step.ADD_FRIEND
        controller.save()
        await message.answer("Введите телеграмм-id друга:", reply_markup=ReplyKeyboardRemove())

    def can_execute(self, user: User, message: Message) -> bool:
        return (user.rank == Rank.USER or user.rank == Rank.MODER) and 'добавить друга' in message.text.lower()


class GetMyEventsCommand(Command, ABC):
    async def execute(self, controller: Controller, user: User, message: Message):
        events = controller.get_events_by_user(
            user.id) if user.rank == Rank.ORGANIZER else controller.get_events_by_user_without_finished(user.id)
        if len(events) == 0:
            await message.answer('В данный момент у вас нет мероприятий')
        else:
            for event in events:
                try:
                    keyboard = keyboards_by_status_event_and_by_rank[event.status][user.rank](event)
                except KeyError:
                    keyboard = None
                if event.lat is not None and event.lng is not None:
                    await message.answer_location(event.lat, event.lng)
                await message.answer(str(event), reply_markup=keyboard)

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
                friends = controller.get_friends_on_event(user, event)
                friends_str = f'\n\n{plurals(len(friends), "ваш друг", "ваших друга", "ваших друзей")} на этом мероприятии: {", ".join(f"{friend.first_name} {friend.middle_name} {friend.last_name}" for friend in friends)}' if len(
                    friends) != 0 else ''
                if event.lat is not None and event.lng is not None:
                    await message.answer_location(event.lat, event.lng)
                await message.answer(f'{event}{friends_str}', reply_markup=keyboard)

    def can_execute(self, user: User, message: Message) -> bool:
        return (user.rank == Rank.USER or
                user.rank == Rank.MODER) and 'все мероприятия' in message.text.lower()


class AddSomethingCommand(Command, ABC):
    rank: Rank
    step: Step
    name: str

    def __init__(self, rank, step, name, _type, name_in_message=None):
        self.rank = rank
        self.step = step
        self.name = name
        self._type = _type
        self.name_in_message = name_in_message

    async def execute(self, controller: Controller, user: User, message: Message):
        controller.set_step_to_user(user, self.step)
        await message.answer(
            f'Ввведите {self._type} нового {self.name_in_message if self.name_in_message is not None else self.name}')

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
               f'├ Ваши интересы {", ".join([interest.name for interest in user.interests]) if len(user.interests) != 0 else "отсутствуют"}\n' \
               f'└ Ваш рейтинг: {user.rating}'
        await message.answer(text, reply_markup=profile_inline_keyboard)
        image_achievements = generate_image_achievements(user)
        if image_achievements is not None:
            await message.answer_photo(photo=image_achievements, caption='Ваши достижения')
            image_achievements.close()

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
            GetFriendListCommand(),
            AddFriendCommand(),
            GetFriendRequestListCommand(),
            ManageSomethingCommand('Интересы', Interest),
            ManageSomethingCommand('Группы', LocalGroup),
            AddSomethingCommand(Rank.ADMIN, Step.NEW_ORGANIZER_ID, 'организатора', 'ID'),
            AddSomethingCommand(Rank.ORGANIZER, Step.NEW_MODER_ID, 'модератора', 'ID'),
            AddSomethingCommand(Rank.ORGANIZER, Step.EVENT_NAME, 'мероприятие', 'название'),
            AddSomethingCommand(Rank.ORGANIZER, Step.ACHIEVEMENT_NAME, 'достижение', 'название', 'достижения')]
unknown_command = UnknownCommand()


def get_command(user, message) -> Command:
    for command in commands:
        if message.text is not None and command.can_execute(user, message):
            return command

    return unknown_command
