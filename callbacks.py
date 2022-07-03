from abc import ABC, abstractmethod

from aiogram.types import CallbackQuery

from database.base import DBSession
from database.models import User, Interest, Achievement, LocalGroup
from database.models.base import BaseModel
from enums.ranks import Rank
from enums.steps import Step


class Callback(ABC):
    @abstractmethod
    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        pass

    @abstractmethod
    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        pass


class UnknownCallback(Callback, ABC):
    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()
        await query.message.answer('Ты куда жмав?')
        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return True


class ManageSomethingCallback(Callback, ABC):
    rank: Rank
    model: BaseModel
    action: str
    step: Step
    message: str

    def __init__(self, rank, model, action, step, message):
        self.rank = rank
        self.model = model
        self.action = action
        self.step = step
        self.message = message

    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()

        user.step = self.step
        db_session.commit_session()

        await query.message.answer(self.message)
        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return (self.rank is None or user.rank == self.rank) and query.data.endswith(
            self.model.__tablename__) and query.data.startswith(self.action)


callbacks = [ManageSomethingCallback(None, User, 'change', Step.ENTER_FIRST_NAME, 'Напиши свое имя'),
             ManageSomethingCallback(Rank.ADMIN, Interest, 'add', Step.ENTER_INTEREST_NAME_FOR_ADD,
                                     'Напишите название нового интереса'),
             ManageSomethingCallback(Rank.ADMIN, Interest, 'remove', Step.ENTER_INTEREST_NAME_FOR_REMOVE,
                                     'Напишите название интереса для удаления'),
             ManageSomethingCallback(Rank.ADMIN, Achievement, 'add', Step.ENTER_ACHIEVEMENT_NAME_FOR_ADD,
                                     'Напишите название нового достижения'),
             ManageSomethingCallback(Rank.ADMIN, Achievement, 'remove', Step.ENTER_ACHIEVEMENT_NAME_FOR_REMOVE,
                                     'Напишите название достижения для удаления'),
             ManageSomethingCallback(Rank.ADMIN, LocalGroup, 'add', Step.ENTER_GROUP_NAME_FOR_ADD,
                                     'Напишите название новой группы'),
             ManageSomethingCallback(Rank.ADMIN, LocalGroup, 'remove', Step.ENTER_GROUP_NAME_FOR_REMOVE,
                                     'Напишите название группы для удаления'),
             UnknownCallback()]


def get_callback(user, query) -> Callback:
    for callback in callbacks:
        if callback.can_callback(user, query):
            return callback
