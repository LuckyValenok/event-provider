from abc import ABC, abstractmethod

from aiogram.types import CallbackQuery

from database.base import DBSession
from database.models import User, Interest, Achievement, LocalGroup, Event, EventUsers
from database.models.base import BaseModel
from enums.ranks import Rank
from enums.steps import Step
from database.queries import users


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

class TakePartCallback(Callback, ABC):

    def __init__(self, rank, model, action, step, message):
        self.rank = rank
        self.model = model
        self.action = action
        self.step = step
        self.message = message

    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()
        ev_id = query.data.split('_')[1]
        if users.has_user_in_event(ev_id, db_session, query.from_user.id):
            await query.message.answer("Вы уже принимаете участие в мероприятии.")
        else:
            db_session.add_model(
                model=EventUsers(event_id=ev_id, user_id=user.id))
            db_session.commit_session()
            await query.message.answer('Поздравляем, Вы принимаете участие в мероприятии!')
            await query.message.delete()


    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return True



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
             TakePartCallback(Rank.ORGANIZER, Event, 'takepart', None, 'Поздравляем, Вы участвуете в мероприятии!'),
             UnknownCallback()]


def get_callback(user, query) -> Callback:
    for callback in callbacks:
        if callback.can_callback(user, query):
            return callback
