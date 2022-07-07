from abc import ABC, abstractmethod

from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.exc import NoResultFound

from controller import Controller, get_code_from_photo
from data.keyboards import keyboards_by_rank
from enums.ranks import Rank
from enums.steps import Step
from models import User, Interest, Achievement, LocalGroup


class DataInput(ABC):
    from_step: Step
    to_step: Step

    def __init__(self, from_step, to_step):
        self.from_step = from_step
        self.to_step = to_step

    @abstractmethod
    async def abstract_input(self, controller: Controller, user: User, message: Message):
        pass

    async def input(self, controller: Controller, user: User, message: Message):
        user.step = self.to_step
        text = await self.abstract_input(controller, user, message)

        reply_markup = ReplyKeyboardRemove()
        if user.step == Step.NONE:
            reply_markup = keyboards_by_rank[user.rank]
        await message.answer(text, reply_markup=reply_markup)
        controller.save()

    def can_input(self, user, message) -> bool:
        return message.text is not None


class UserDataInput(DataInput, ABC):
    def __init__(self, from_step, to_step, _lambda, next_message):
        super().__init__(from_step, to_step)
        self._lambda = _lambda
        self.next_message = next_message

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        self._lambda(user, message.text)
        return self.next_message


class AppointAsInput(DataInput, ABC):
    rank: Rank
    name: str

    def __init__(self, from_step, to_step, rank, name):
        super().__init__(from_step, to_step)
        self.rank = rank
        self.name = name

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        text = message.text
        if 'отмена' in text.lower():
            return 'Операция успешно отменена'
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


class EventNameInput(DataInput, ABC):
    def __init__(self):
        super().__init__(Step.NEW_EVENT_NAME, Step.NONE)

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        controller.create_event(message.text, user)
        return 'Мероприятие успешно создано. Теперь вы можете перейти в его настройки и указать дату, описание и ' \
               'местоположение '


class ManageSomethingDataInput(DataInput, ABC):
    def __init__(self, from_step, to_step, name, model, model_column, _lambda):
        super().__init__(from_step, to_step)
        self.name = name
        self.model = model
        self.model_column = model_column
        self._lambda = _lambda
        self.removing = str(from_step).endswith('REMOVE')

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        new_name = message.text
        if 'отмена' in new_name.lower():
            return 'Операция успешно отменена'
        return controller.manage_something_model(user, self.from_step, self.name, self.model, self.model_column,
                                                 new_name, self._lambda, self.removing)


class FeedbackToEventInput(DataInput, ABC):
    def __init__(self):
        super().__init__(Step.FEEDBACK_TEXT, Step.NONE)

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        controller.add_feedback_to_event(user, message.text)
        return 'Отзыв отправлен!'


class MarkPresentInput(DataInput, ABC):
    def __init__(self):
        super().__init__(Step.VERIFICATION_PRESENT, Step.NONE)

    async def abstract_input(self, controller: Controller, user: User, message: Message):
        if message.text is not None:
            if 'отмена' in message.text.lower():
                return 'Операция успешно отменена'
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
        return message.text is not None or len(message.photo) != 0


data_inputs = [
    UserDataInput(Step.FIRST_NAME, Step.MIDDLE_NAME, lambda u, t: u.set_first_name(t), 'Теперь введите отчество'),
    UserDataInput(Step.MIDDLE_NAME, Step.LAST_NAME, lambda u, t: u.set_middle_name(t), 'Теперь введите фамилию'),
    UserDataInput(Step.LAST_NAME, Step.PHONE, lambda u, t: u.set_last_name(t),
                  'Пожалуйста, введите ваш номер телефона'),
    UserDataInput(Step.PHONE, Step.EMAIL, lambda u, t: u.set_phone(t), 'Остался последний шаг! Введите e-mail'),
    UserDataInput(Step.EMAIL, Step.NONE, lambda u, t: u.set_email(t), 'Вы успешно авторизованы'),
    EventNameInput(),
    FeedbackToEventInput(),
    MarkPresentInput(),
    AppointAsInput(Step.NEW_ORGANIZER_ID, Step.NONE, Rank.ORGANIZER, 'организатором'),
    ManageSomethingDataInput(Step.INTEREST_NAME_FOR_ADD, Step.NONE, 'Интерес', Interest, Interest.name,
                             lambda n: Interest(name=n)),
    ManageSomethingDataInput(Step.INTEREST_NAME_FOR_REMOVE, Step.NONE, 'Интерес', Interest,
                             Interest.name, None),
    ManageSomethingDataInput(Step.ACHIEVEMENT_NAME_FOR_ADD, Step.NONE, 'Достижение', Achievement,
                             Achievement.name, lambda n: Achievement(name=n)),
    ManageSomethingDataInput(Step.ACHIEVEMENT_NAME_FOR_REMOVE, Step.NONE, 'Достижение', Achievement,
                             Achievement.name, None),
    ManageSomethingDataInput(Step.GROUP_NAME_FOR_ADD, Step.NONE, 'Группа', LocalGroup, LocalGroup.name,
                             lambda n: LocalGroup(name=n)),
    ManageSomethingDataInput(Step.GROUP_NAME_FOR_REMOVE, Step.NONE, 'Группа', LocalGroup,
                             LocalGroup.name, None)]


def get_data_input(user, message):
    for data_input in data_inputs:
        if user.step == data_input.from_step and data_input.can_input(user, message):
            return data_input
    return None
