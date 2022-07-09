from abc import ABC, abstractmethod
from datetime import datetime

from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.exc import NoResultFound

from controller import Controller, get_code_from_photo
from data.keyboards import keyboards_by_rank
from enums.friend_request_status import FriendRequestStatus
from enums.ranks import Rank
from enums.steps import Step
from exceptions import NotFoundObjectError, ObjectAlreadyCreatedError
from models import User, Interest, LocalGroup, OrgRateUser


class DataInput(ABC):
    from_step: Step
    to_step: Step
    can_be_canceled: bool

    def __init__(self, from_step, to_step, can_be_canceled=False):
        self.from_step = from_step
        self.to_step = to_step
        self.can_be_canceled = can_be_canceled

    @abstractmethod
    async def abstract_input(self, controller: Controller, user: User, message: Message):
        pass

    async def input(self, controller: Controller, user: User, message: Message):
        if self.can_be_canceled and message.text is not None and message.text.lower() in 'отмена':
            user.step = Step.NONE
            controller.save()

            await message.answer('Операция успешно отменена', reply_markup=keyboards_by_rank[user.rank])
            return
        user.previous_step = user.step
        user.step = self.to_step
        text = await self.abstract_input(controller, user, message)

        reply_markup = ReplyKeyboardRemove()
        if user.step == Step.NONE:
            reply_markup = keyboards_by_rank[user.rank]
        await message.answer(text, reply_markup=reply_markup)
        controller.save()

    def can_input(self, user: User, message: Message) -> bool:
        return message.text is not None and user.step == self.from_step


class UserDataInput(DataInput, ABC):
    def __init__(self, from_step, second_from_step, to_step, _lambda, next_message):
        super().__init__(from_step, to_step)
        self.second_from_step = second_from_step
        self._lambda = _lambda
        self.next_message = next_message

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        self._lambda(user, message.text)
        if str(user.previous_step).endswith('ONLY'):
            user.step = Step.NONE
            return 'Операция успешно выполнена'
        return self.next_message

    def can_input(self, user: User, message: Message) -> bool:
        return message.text is not None and (user.step == self.from_step or user.step == self.second_from_step)


class EventDataInput(DataInput, ABC):
    def __init__(self, from_step, _lambda):
        super().__init__(from_step, Step.NONE, True)
        self._lambda = _lambda

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        try:
            event_editor = controller.get_editor_event(user.id)
            self._lambda(controller.get_event_by_id(event_editor.event_id), message)

            controller.db_session.delete_model(event_editor)
            controller.save()
            return 'Операция успешно выполнена'
        except NoResultFound:
            if self.from_step == Step.EVENT_NAME:
                controller.create_event(message.text, user)
                return 'Мероприятие успешно создано. Теперь вы можете перейти в его настройки и указать дату, ' \
                       'описание и местоположение '
            return 'Мероприятие не найдено'

    def can_input(self, user: User, message: Message) -> bool:
        return (message.location is not None and user.step == Step.EVENT_LOCATION and user.step == self.from_step) or (
                message.text is not None and user.step == self.from_step)


class AddFriendRequestInput(DataInput, ABC):
    def __init__(self):
        super().__init__(Step.ADD_FRIEND, Step.NONE, True)

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        try:
            uid = int(message.text)
            controller.get_user_by_id(uid)
            controller.add_friend(user.id, uid, FriendRequestStatus.ACCEPTED)
            controller.add_friend(uid, user.id, FriendRequestStatus.WAITING)
            return 'Заявка отправлена!'
        except ValueError / NoResultFound:
            return 'Такого пользователя нет. Попробуйте снова или напишите \'отмена\''


class GiveRatingInput(DataInput, ABC):
    def __init__(self):
        super().__init__(Step.GIVE_RATING, Step.NONE, True)

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        uid = controller.get_rate_editor(user.id)
        amount = int(message.text)
        controller.give_rate(uid.user_id, amount)
        req = controller.db_session.query(OrgRateUser).filter(OrgRateUser.org_id == user.id, OrgRateUser.user_id == uid.user_id).one()
        controller.db_session.delete_model(req)
        return 'Баллы успешно начислены!'

    def can_input(self, user: User, message: Message) -> bool:
        return user.step == Step.GIVE_RATING and message.text is not None


class AppointAsInput(DataInput, ABC):
    rank: Rank
    name: str

    def __init__(self, from_step, to_step, rank, name):
        super().__init__(from_step, to_step, True)
        self.rank = rank
        self.name = name

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        text = message.text
        try:
            uid = int(text)
            try:
                target_user = controller.get_user_by_id(uid)
                target_user.rank = self.rank
                return f'{target_user.first_name} {target_user.middle_name} {target_user.last_name} успешно назначен {self.name}'
            except NoResultFound:
                user.step = self.from_step
                return f'Пользователя с таким ({text}) ID не существует. Попробуйте снова или напишите \'отмена\''
        except ValueError:
            user.step = self.from_step
            return f'{text} - не число. Попробуйте снова или напишите \'отмена\''


class ManageSomethingDataInput(DataInput, ABC):
    def __init__(self, from_step, to_step, name, model, model_column, _lambda):
        super().__init__(from_step, to_step, True)
        self.name = name
        self.model = model
        self.model_column = model_column
        self._lambda = _lambda
        self.removing = str(from_step).endswith('REMOVE')

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        new_name = message.text
        try:
            controller.manage_something_model(self.model, self.model_column,
                                              new_name, self._lambda, self.removing)
            return 'Операция успешно выполнена'
        except NotFoundObjectError:
            user.step = self.from_step
            return 'Такого объекта нет. Попробуйте снова или напишите \'отмена\''
        except ObjectAlreadyCreatedError:
            user.step = self.from_step
            return f'Уже существует {self.name.lower()} с данным названием. Попробуйте снова или напишите \'отмена\''


class FeedbackToEventInput(DataInput, ABC):
    def __init__(self):
        super().__init__(Step.FEEDBACK_TEXT, Step.NONE, True)

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        controller.add_feedback_to_event(user, message.text)
        return 'Отзыв отправлен!'


class MarkPresentInput(DataInput, ABC):
    def __init__(self):
        super().__init__(Step.VERIFICATION_PRESENT, Step.NONE, True)

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        if message.text is not None:
            code = message.text
        else:
            photo = message.photo[-1]

            await photo.download(destination_file=f'{photo.file_id}.jpg')

            code = get_code_from_photo(f'{photo.file_id}.jpg')
            if code is None:
                user.step = Step.VERIFICATION_PRESENT
                return 'Произошла ошибка при распознавании QR-кода. Попробуйте снова или напишите \'отмена\''

        try:
            controller.mark_presents(user, code)

            return 'Пользователь успешно отмечен'
        except NoResultFound as e:
            user.step = Step.VERIFICATION_PRESENT
            return f'Произошла ошибка ({e.code}). Попробуйте снова или напишите \'отмена\''

    def can_input(self, user, message: Message) -> bool:
        return (message.text is not None or len(message.photo) != 0) and user.step == self.from_step


data_inputs = [
    UserDataInput(Step.FIRST_NAME, Step.FIRST_NAME_ONLY, Step.MIDDLE_NAME, lambda u, t: u.set_first_name(t),
                  'Теперь введите отчество'),
    UserDataInput(Step.MIDDLE_NAME, Step.MIDDLE_NAME_ONLY, Step.LAST_NAME, lambda u, t: u.set_middle_name(t),
                  'Теперь введите фамилию'),
    UserDataInput(Step.LAST_NAME, Step.LAST_NAME_ONLY, Step.PHONE, lambda u, t: u.set_last_name(t),
                  'Пожалуйста, введите ваш номер телефона'),
    UserDataInput(Step.PHONE, Step.PHONE_ONLY, Step.EMAIL, lambda u, t: u.set_phone(t),
                  'Остался последний шаг! Введите e-mail'),
    UserDataInput(Step.EMAIL, Step.EMAIL_ONLY, Step.NONE, lambda u, t: u.set_email(t), 'Вы успешно авторизованы'),
    EventDataInput(Step.EVENT_NAME, lambda e, m: e.set_name(m.text)),
    EventDataInput(Step.EVENT_DESCRIPTION, lambda e, m: e.set_description(m.text)),
    EventDataInput(Step.EVENT_LOCATION, lambda e, m: e.set_location(m.location)),
    EventDataInput(Step.EVENT_DATE, lambda e, m: e.set_date(datetime.strptime(m.text, "%d.%m.%Y %H:%M"))),
    FeedbackToEventInput(),
    MarkPresentInput(),
    AddFriendRequestInput(),
    AppointAsInput(Step.NEW_ORGANIZER_ID, Step.NONE, Rank.ORGANIZER, 'организатором'),
    AppointAsInput(Step.NEW_MODER_ID, Step.NONE, Rank.MODER, 'модератором'),
    ManageSomethingDataInput(Step.INTEREST_NAME_FOR_ADD, Step.NONE, 'Интерес', Interest, Interest.name,
                             lambda n: Interest(name=n)),
    ManageSomethingDataInput(Step.INTEREST_NAME_FOR_REMOVE, Step.NONE, 'Интерес', Interest,
                             Interest.name, None),
    ManageSomethingDataInput(Step.GROUP_NAME_FOR_ADD, Step.NONE, 'Группа', LocalGroup, LocalGroup.name,
                             lambda n: LocalGroup(name=n)),
    ManageSomethingDataInput(Step.GROUP_NAME_FOR_REMOVE, Step.NONE, 'Группа', LocalGroup,
                             LocalGroup.name, None),
    GiveRatingInput()
]


def get_data_input(user, message):
    for data_input in data_inputs:
        if data_input.can_input(user, message):
            return data_input
    return None
