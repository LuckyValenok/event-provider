from abc import ABC, abstractmethod

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.exc import NoResultFound

from database.base import DBSession
from database.models import User, Interest, Achievement, LocalGroup, UserInterests, UserGroups, EventEditors
from database.models.base import BaseModel
from database.queries import events
from database.queries.events import get_event_by_id
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


class TakePartCallback(Callback, ABC):
    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()

        eid = int(query.data.split('_')[-1])
        try:
            event = get_event_by_id(db_session, eid)
            if user in event.users:
                await query.message.answer("Вы уже принимаете участие в мероприятии.")
            else:
                event.users.append(user)
                db_session.commit_session()

                await query.message.answer('Поздравляем, Вы принимаете участие в мероприятии!')
        except NoResultFound:
            await query.message.answer('Такого мероприятия нет')

        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('tp_') and (user.rank is Rank.USER or user.rank is Rank.MODER)


class ManageUserAttachmentCallback(Callback, ABC):
    def __init__(self, name, name_remove_form, model, relation_model, relation_column, _lambda):
        self.name = name
        self.name_remove_form = name_remove_form
        self.model = model
        self.relation_model = relation_model
        self.relation_column = relation_column
        self._lambda = _lambda

    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()

        de_attach = query.data.startswith('de')

        if query.data.endswith(self.model.__tablename__):
            entities = db_session.query(self.model).filter(
                self.model.id.not_in(db_session.query(self.relation_model).with_entities(self.relation_column).filter(
                    self.relation_model.user_id == user.id))).all() if not de_attach else db_session.query(
                self.model).filter(self.relation_model.user_id == user.id).all()
            if len(entities) == 0:
                await query.message.answer('Тут пусто')
            else:
                keyboard = InlineKeyboardMarkup()
                for entity in entities:
                    keyboard.add(InlineKeyboardButton(entity.name,
                                                      callback_data=query.data + '_' + str(entity.id)))
                await query.message.answer(f'Доступные {self.name.lower()}:', reply_markup=keyboard)
        else:
            try:
                eid = int(query.data.split('_')[-1])
                entity = db_session.query(self.model).filter(self.model.id == eid).one()
                self._lambda(user, entity, not de_attach)
                db_session.commit_session()

                await query.message.answer(
                    f'{entity.name} успешно {"добавлен в " + self.name.lower() if not de_attach else "удален из " + self.name_remove_form.lower()}')
            except ValueError / NoResultFound:
                await query.message.answer(f'{self.name} с этим названием отсутствуют')

        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('att_' + self.model.__tablename__) or query.data.startswith(
            'deatt_' + self.model.__tablename__)


class GetAttendentStatisticsCallback(Callback, ABC):
    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        eid = int(query.data.split('_')[-1])
        await query.answer()
        await query.message.answer(
            f"В мероприятии участвовал(-и) {events.get_count_visited(db_session, eid)} человек(-а).")
        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('atst_') and user.rank is Rank.ORGANIZER


class UserFeedbackCallback(Callback, ABC):
    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()
        await query.message.answer('Оставьте свой отзыв :)')
        await query.message.delete()
        eid = int(query.data.split('_')[-1])
        db_session.add_model(EventEditors(event_id=eid, user_id=user.id))
        user.step = Step.ENTER_FEEDBACK_TEXT
        db_session.commit_session()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('feb_') and (user.rank is Rank.USER or user.rank is Rank.MODER)


class FeedbackStatisticsCallback(Callback, ABC):
    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        eid = int(query.data.split('_')[-1])
        await query.answer()
        # await query.message.answer()
        await query.message.delete()
        # TODO: Тут вывод отзывов

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('fbst_') and user.rank is Rank.ORGANIZER


callbacks = [TakePartCallback(),
             UserFeedbackCallback(),
             ManageSomethingCallback(None, User, 'change', Step.ENTER_FIRST_NAME, 'Напиши свое имя'),
             ManageUserAttachmentCallback('Интересы', 'Интересов', Interest, UserInterests, UserInterests.interest_id,
                                          lambda u, i, a: u.interests.append(i) if a else u.interests.remove(i)),
             ManageUserAttachmentCallback('Группы', 'Групп', LocalGroup, UserGroups, UserGroups.group_id,
                                          lambda u, g, a: u.groups.append(g) if a else u.groups.remove(g)),
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
             GetAttendentStatisticsCallback(),
             FeedbackStatisticsCallback(),
             UnknownCallback()]


def get_callback(user, query) -> Callback:
    for callback in callbacks:
        if callback.can_callback(user, query):
            return callback
