from abc import ABC, abstractmethod

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.exc import NoResultFound

from database.base import DBSession
from database.models import User, Interest, Achievement, LocalGroup, UserInterests, UserGroups
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


class AttachSomethingToUserCallback(Callback, ABC):
    def __init__(self, name, model, relation_model, relation_column, _lambda):
        self.name = name
        self.model = model
        self.relation_model = relation_model
        self.relation_column = relation_column
        self._lambda = _lambda

    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()

        if query.data.endswith(self.model.__tablename__):
            entities = db_session.execute(
                f'SELECT * FROM {self.model.__tablename__} WHERE id NOT IN (SELECT {self.relation_column} FROM {self.relation_model.__tablename__} WHERE user_id={user.id})')
            keyboard = InlineKeyboardMarkup()
            has_result = False
            for entity in entities:
                has_result = True
                keyboard.add(InlineKeyboardButton(entity['name'],
                                                  callback_data='att_' + self.model.__tablename__ + "_" + str(
                                                      entity['id'])))
            if has_result:
                await query.message.answer(f'Доступные {self.name.lower()}:', reply_markup=keyboard)
            else:
                await query.message.answer(f'Пока отсутствуют или вы выбрали уже все доступные {self.name.lower()}')
        else:
            try:
                eid = int(query.data.split('_')[-1])
                entity = db_session.query(self.model).filter(self.model.id == eid).one()
                self._lambda(user, entity)
                db_session.commit_session()

                await query.message.answer(f'{entity.name} успешно добавлен в {self.name.lower()}')
            except ValueError / NoResultFound:
                await query.message.answer(f'{self.name} с этим названием отсутствуют')

        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('att_' + self.model.__tablename__)


callbacks = [ManageSomethingCallback(None, User, 'change', Step.ENTER_FIRST_NAME, 'Напиши свое имя'),
             AttachSomethingToUserCallback('Интересы', Interest, UserInterests, 'interest_id',
                                           lambda u, i: u.interests.append(i)),
             AttachSomethingToUserCallback('Группы', LocalGroup, UserGroups, 'group_id',
                                           lambda u, g: u.groups.append(g)),
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
