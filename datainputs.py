from abc import ABC, abstractmethod

from aiogram.types import Message
from sqlalchemy.exc import NoResultFound

from database.base import DBSession
from database.models import User, Event
from database.queries.users import get_user_by_id
from enums.ranks import Rank
from enums.steps import Step


class DataInput(ABC):
    from_step: Step
    to_step: Step

    def __init__(self, from_step, to_step):
        self.from_step = from_step
        self.to_step = to_step

    @abstractmethod
    def abstract_input(self, db_session: DBSession, user: User, message: Message) -> str:
        pass

    def input(self, db_session: DBSession, user: User, message: Message) -> str:
        user.step = self.to_step
        answer = self.abstract_input(db_session, user, message)
        db_session.commit_session()
        return answer

    @abstractmethod
    def can_input(self, user, message) -> bool:
        pass


class FirstNameInput(DataInput, ABC):
    def abstract_input(self, db_session: DBSession, user: User, message: Message) -> str:
        user.first_name = message.text
        return 'Теперь введите отчество'

    def can_input(self, user, message) -> bool:
        return True


class MiddleNameInput(DataInput, ABC):
    def abstract_input(self, db_session: DBSession, user: User, message: Message) -> str:
        user.middle_name = message.text
        return 'Теперь введите фамилию'

    def can_input(self, user, message) -> bool:
        return True


class LastNameInput(DataInput, ABC):
    def abstract_input(self, db_session: DBSession, user: User, message: Message) -> str:
        user.last_name = message.text
        return f'Приятно познакомиться, {user.first_name} {user.middle_name} {user.last_name}\n\nПожалуйста, введите ' \
               f'ваш номер телефона '

    def can_input(self, user, message) -> bool:
        return True


class PhoneInput(DataInput, ABC):
    def abstract_input(self, db_session: DBSession, user: User, message: Message) -> str:
        user.phone = message.text
        return 'Остался последний шаг! Введите e-mail'

    def can_input(self, user, message) -> bool:
        return True


class EmailInput(DataInput, ABC):
    def abstract_input(self, db_session: DBSession, user: User, message: Message) -> str:
        user.email = message.text
        return 'Вы успешно авторизованы'

    def can_input(self, user, message) -> bool:
        return True


class AppointAsInput(DataInput, ABC):
    rank: Rank
    name: str

    def __init__(self, from_step, to_step, rank, name):
        super().__init__(from_step, to_step)
        self.rank = rank
        self.name = name


    def abstract_input(self, db_session: DBSession, user: User, message: Message) -> str:
        text = message.text
        if 'отмена' in text.lower():
            return 'Операция успешно отменена'
        try:
            uid = int(text)
            try:
                target_user = get_user_by_id(db_session, uid)
                target_user.rank = self.rank
                return f'{target_user.first_name} {target_user.middle_name} {target_user.last_name} успешно назначен ' \
                       f'{self.name}'
            except NoResultFound:
                user.step = self.from_step
                return f'Пользователя с таким ({text}) ID не существует. Попробуйте снова или напишите \'отмена\''
        except ValueError:
            user.step = self.from_step
            return f'{text} - не число. Попробуйте снова или напишите \'отмена\''

    def can_input(self, user, message) -> bool:
        return True


class EventNameInput(DataInput, ABC):
    def abstract_input(self, db_session: DBSession, user: User, message: Message) -> str:
        event = Event(name=message.text)
        event.users.append(user)
        db_session.add_model(event)
        return 'Мероприятие успешно создано. Теперь вы можете перейти в его настройки и указать дату, описание и ' \
               'местоположение '

    def can_input(self, user, text) -> bool:
        return True


data_inputs = [FirstNameInput(Step.ENTER_FIRST_NAME, Step.ENTER_MIDDLE_NAME),
               MiddleNameInput(Step.ENTER_MIDDLE_NAME, Step.ENTER_LAST_NAME),
               LastNameInput(Step.ENTER_LAST_NAME, Step.ENTER_PHONE),
               PhoneInput(Step.ENTER_PHONE, Step.ENTER_EMAIL),
               EmailInput(Step.ENTER_EMAIL, Step.NONE),
               AppointAsInput(Step.ENTER_NEW_MANAGER_ID, Step.NONE, Rank.MANAGER, 'менеджером'),
               EventNameInput(Step.ENTER_NEW_EVENT_NAME, Step.NONE),
               AppointAsInput(Step.ENTER_NEW_ORGANIZER_ID, Step.NONE, Rank.ORGANIZER, 'организатором')]


def get_data_input(user, message):
    for data_input in data_inputs:
        if user.step == data_input.from_step and data_input.can_input(user, message):
            return data_input
    return None