from abc import ABC, abstractmethod

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.exc import NoResultFound

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


class AttachSomethingCallback(Callback, ABC):
    name: str
    model: BaseModel

    def __init__(self, name, model):
        self.name = name
        self.model = model

    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()

        if query.data.endswith(self.model.__tablename__):
            # TODO: Должно обрабатывать не только интересы
            entities = db_session.query(self.model).filter(Interest not in user.interests).all()
            if len(entities) == 0:
                await query.message.answer(f'{self.name} пока отсутствуют')
            else:
                keyboard = InlineKeyboardMarkup()
                for entity in entities:
                    keyboard.add(InlineKeyboardButton(entity.name,
                                                      callback_data='att_' + self.model.__tablename__ + "_" + str(
                                                          entity.id)))
                await query.message.answer(f'Доступные {self.name.lower()}:',
                                           reply_markup=keyboard)
        else:
            try:
                eid = int(query.data.split('_')[-1])
                entity = db_session.query(self.model).filter(self.model.id == eid).one()
                # TODD: Должно обрабатывать не только интересы
                user.interests.append(entity)
                db_session.commit_session()

                await query.message.answer(f'{entity.name} успешно добавлен в {self.name.lower()}')
            except ValueError / NoResultFound:
                await query.message.answer(f'{self.name} с этим названием отсутствуют')

        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('att_' + self.model.__tablename__)


callbacks = [ManageSomethingCallback(None, User, 'change', Step.ENTER_FIRST_NAME, 'Напиши свое имя'),
             AttachSomethingCallback('Интересы', Interest),
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
