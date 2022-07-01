from abc import ABC, abstractmethod

from enums.steps import Step


class DataInput(ABC):
    from_step: Step
    to_step: Step

    def __init__(self, from_step, to_step):
        self.from_step = from_step
        self.to_step = to_step

    @abstractmethod
    def abstract_input(self, db_session, user, text) -> str:
        pass

    def input(self, db_session, user, text) -> str:
        answer = self.abstract_input(db_session, user, text)
        user.step = self.to_step
        db_session.commit_session()
        return answer

    @abstractmethod
    def can_input(self, user, text) -> bool:
        pass


class FirstNameInput(DataInput, ABC):
    def abstract_input(self, db_session, user, text) -> str:
        user.first_name = text
        return 'Теперь введите отчество'

    def can_input(self, user, text) -> bool:
        return True


class MiddleNameInput(DataInput, ABC):
    def abstract_input(self, db_session, user, text) -> str:
        user.middle_name = text
        return 'Теперь введите фамилию'

    def can_input(self, user, text) -> bool:
        return True


class LastNameInput(DataInput, ABC):
    def abstract_input(self, db_session, user, text) -> str:
        user.last_name = text
        return f'Приятно познакомиться, {user.first_name} {user.middle_name} {user.last_name}\n\nПожалуйста, введите ' \
               f'ваш номер телефона '

    def can_input(self, user, text) -> bool:
        return True


class PhoneInput(DataInput, ABC):
    def abstract_input(self, db_session, user, text) -> str:
        user.phone = text
        return 'Остался последний шаг! Введите e-mail'

    def can_input(self, user, text) -> bool:
        return True


class EmailInput(DataInput, ABC):
    def abstract_input(self, db_session, user, text) -> str:
        user.email = text
        return 'Вы успешно авторизованы'

    def can_input(self, user, text) -> bool:
        return True


data_inputs = [FirstNameInput(Step.ENTER_FIRST_NAME, Step.ENTER_MIDDLE_NAME),
               MiddleNameInput(Step.ENTER_MIDDLE_NAME, Step.ENTER_LAST_NAME),
               LastNameInput(Step.ENTER_LAST_NAME, Step.ENTER_PHONE),
               PhoneInput(Step.ENTER_PHONE, Step.ENTER_EMAIL),
               EmailInput(Step.ENTER_EMAIL, Step.NONE)]


def get_data_input(user, text):
    for data_input in data_inputs:
        if user.step == data_input.from_step and data_input.can_input(user, text):
            return data_input
    return None
