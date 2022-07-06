from abc import ABC, abstractmethod
from io import BytesIO

import qrcode
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from sqlalchemy.exc import NoResultFound

from database.base import DBSession
from database.models import User, Interest, Achievement, LocalGroup, UserInterests, UserGroups, EventEditors
from database.models.base import BaseModel
from database.models.event import EventCodes
from database.queries import events
from database.queries.events import get_event_by_id, get_new_code, get_code_model_by_id, get_feedbacks
from enums.ranks import Rank
from enums.status_event import StatusEvent
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
            if user in event.users or event.status == StatusEvent.FINISHED:
                await query.message.answer("Вы уже принимаете участие в мероприятии или оно уже завершилось")
            else:
                event.users.append(user)

                await query.message.answer('Поздравляем, Вы принимаете участие в мероприятии!')

                code = get_new_code(db_session)

                db_session.add_model(EventCodes(event_id=event.id, user_id=user.id, code=code))

                img = qrcode.make(code)

                output = BytesIO()
                img.save(output, "PNG")
                output.seek(0)

                await query.message.answer(f'Ваш код, который вы должны предоставить модератору мероприятия: {code}\n'
                                           f'Или QR-код:')
                await query.message.answer_photo(output)
                output.close()

                db_session.commit_session()
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
        user.step = Step.FEEDBACK_TEXT
        db_session.commit_session()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('feb_') and (user.rank is Rank.USER or user.rank is Rank.MODER)


class FeedbackStatisticsCallback(Callback, ABC):
    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()

        tokenizer = RegexTokenizer()
        model = FastTextSocialNetworkModel(tokenizer=tokenizer)

        messages = []

        eid = int(query.data.split('_')[-1])
        for feedback in get_feedbacks(db_session, eid):
            messages.append(str(feedback.fb_text))

        results = model.predict(messages, k=2)
        neutral_list = []
        negative_list = []
        positive_list = []
        for sentiment in results:
            neutral = sentiment.get('neutral')
            negative = sentiment.get('negative')
            positive = sentiment.get('positive')
            if neutral is not None:
                neutral_list.append(sentiment.get('neutral'))
            if negative is not None:
                negative_list.append(sentiment.get('negative'))
            if positive is not None:
                positive_list.append(sentiment.get('positive'))

        if len(messages) != 0:
            neutral = sum(neutral_list)
            negative = sum(negative_list)
            positive = sum(positive_list)
            _max = neutral + negative + positive
            feedbacks = f'Сентимент-анализ:\n' \
                        f'Доля нейтральных отзывов: {neutral / _max:.1%}\n' \
                        f'Доля отрицательных отзывов: {negative / _max:.1%}\n' \
                        f'Доля положительных отзывов: {positive / _max:.1%}\n\n'
            feedbacks += '\n'.join(messages)
        else:
            feedbacks = 'отсутствуют'
        await query.message.answer(f'Отзывы:\n\n{feedbacks}')
        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('fbst_') and user.rank is Rank.ORGANIZER


class CancelEventCallback(Callback, ABC):
    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()

        eid = int(query.data.split('_')[-1])
        try:
            event = get_event_by_id(db_session, eid)
            if user in event.users and event.status == StatusEvent.UNFINISHED:
                event.users.remove(user)

                db_session.delete_model(get_code_model_by_id(db_session, event.id, user.id))

                await query.message.answer('Вы отменили заявку на участие в мероприятии')

                db_session.commit_session()
            else:
                await query.message.answer("Вы уже не принимаете участие в этом мероприятии или оно завершилось")
        except NoResultFound:
            await query.message.answer('Такого мероприятия нет')

        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('ecan_') and (user.rank is Rank.USER or user.rank is Rank.MODER)


class MarkPresentCallback(Callback, ABC):
    async def callback(self, db_session: DBSession, user: User, query: CallbackQuery):
        await query.answer()

        eid = int(query.data.split('_')[-1])
        try:
            event = get_event_by_id(db_session, eid)
            if event.status == StatusEvent.UNFINISHED:
                user.step = Step.VERIFICATION_PRESENT

                db_session.add_model(EventEditors(event_id=event.id, user_id=user.id))

                await query.message.answer(
                    'Вам необходимо прислать фото QR-кода, текстовый код для подтверждения или \'отмена\' для отмены '
                    'действия')

                db_session.commit_session()
            else:
                await query.message.answer("Мероприятие уже завершилось")
        except NoResultFound:
            await query.message.answer('Такого мероприятия нет')

        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('marpr_') and user.rank is Rank.MODER


callbacks = [TakePartCallback(),
             UserFeedbackCallback(),
             CancelEventCallback(),
             MarkPresentCallback(),
             ManageSomethingCallback(None, User, 'change', Step.FIRST_NAME, 'Напиши свое имя'),
             ManageUserAttachmentCallback('Интересы', 'Интересов', Interest, UserInterests, UserInterests.interest_id,
                                          lambda u, i, a: u.interests.append(i) if a else u.interests.remove(i)),
             ManageUserAttachmentCallback('Группы', 'Групп', LocalGroup, UserGroups, UserGroups.group_id,
                                          lambda u, g, a: u.groups.append(g) if a else u.groups.remove(g)),
             ManageSomethingCallback(Rank.ADMIN, Interest, 'add', Step.INTEREST_NAME_FOR_ADD,
                                     'Напишите название нового интереса'),
             ManageSomethingCallback(Rank.ADMIN, Interest, 'remove', Step.INTEREST_NAME_FOR_REMOVE,
                                     'Напишите название интереса для удаления'),
             ManageSomethingCallback(Rank.ADMIN, Achievement, 'add', Step.ACHIEVEMENT_NAME_FOR_ADD,
                                     'Напишите название нового достижения'),
             ManageSomethingCallback(Rank.ADMIN, Achievement, 'remove', Step.ACHIEVEMENT_NAME_FOR_REMOVE,
                                     'Напишите название достижения для удаления'),
             ManageSomethingCallback(Rank.ADMIN, LocalGroup, 'add', Step.GROUP_NAME_FOR_ADD,
                                     'Напишите название новой группы'),
             ManageSomethingCallback(Rank.ADMIN, LocalGroup, 'remove', Step.GROUP_NAME_FOR_REMOVE,
                                     'Напишите название группы для удаления'),
             GetAttendentStatisticsCallback(),
             FeedbackStatisticsCallback(),
             UnknownCallback()]


def get_callback(user, query) -> Callback:
    for callback in callbacks:
        if callback.can_callback(user, query):
            return callback
