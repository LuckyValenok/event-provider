from abc import ABC, abstractmethod

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.exc import NoResultFound

from controller import Controller
from data.keyboards import change_user_data_keyboard, change_event_data_keyboard
from enums.ranks import Rank
from enums.status_event import StatusEvent
from enums.steps import Step
from models import User, Interest, Achievement, LocalGroup, UserInterests, UserGroups, EventEditors
from models.basemodel import BaseModel


class Callback(ABC):
    @abstractmethod
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        pass

    @abstractmethod
    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        pass


class UnknownCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()
        await query.message.answer('Ты куда жмав?')
        await query.message.delete()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return True


class AcceptFriendRequestCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        fid = query.data.split('_')[-1]
        controller.accept_friend_request(user.id, fid)
        await query.message.answer('Вы приняли заявку в друзья!')

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('acceptreq_') and user.rank == Rank.USER


class DeclineFriendRequestCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        fid = query.data.split('_')[-1]
        controller.decline_friend_request(user.id, fid)
        await query.message.answer('Вы отклонили заявку в друзья.')

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('declinereq_') and user.rank == Rank.USER


class DeleteFriendCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        fid = query.data.split('_')[-1]
        controller.delete_friend(user.id, fid)
        await query.message.answer('Вы удалили этого пользователя из друзей.')

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('deletefr_') and user.rank == Rank.USER


class ChangeDataInEventCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()

        name = None

        _type = query.data.split('_')[-1]
        try:
            eid = int(_type)
            controller.db_session.add_model(EventEditors(event_id=eid, user_id=user.id))
            controller.save()

            await query.message.answer('Пожалуйста, выберите параметр, который Вы хотите изменить.',
                                       reply_markup=change_event_data_keyboard)

        except ValueError:
            if _type in 'name':
                user.step = Step.EVENT_NAME
                name = 'название ивента'
            elif _type in 'description':
                user.step = Step.EVENT_DESCRIPTION
                name = 'описание'
            elif _type in 'date':
                user.step = Step.EVENT_DATE
                name = 'дату'
            elif _type in 'location':
                user.step = Step.EVENT_LOCATION
                name = 'локацию'

            controller.save()
            await query.message.answer(f'Пожалуйста, введите {name}')

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('ech_') and user.rank == Rank.ORGANIZER


class ChangeDataInUserCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()

        name = None

        _type = query.data.split('_')[-1]
        if _type in 'user':
            await query.message.answer('Пожалуйста, выберите, что хотите изменить',
                                       reply_markup=change_user_data_keyboard)
            return
        elif _type in 'firstname':
            user.step = Step.FIRST_NAME_ONLY
            name = 'имя'
        elif _type in 'middlename':
            user.step = Step.MIDDLE_NAME_ONLY
            name = 'отчество'
        elif _type in 'lastname':
            user.step = Step.LAST_NAME_ONLY
            name = 'фамилию'
        elif _type in 'phone':
            user.step = Step.PHONE_ONLY
            name = 'номер телефона'
        elif _type in 'email':
            user.step = Step.EMAIL_ONLY
            name = 'почту'

        controller.save()
        await query.message.answer(f'Пожалуйста, введите {name}')

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('change_user')


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

    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()

        user.step = self.step
        controller.save()

        await query.message.answer(self.message)

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return (self.rank is None or user.rank == self.rank) and query.data.endswith(
            self.model.__tablename__) and query.data.startswith(self.action)


class TakePartCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()

        eid = int(query.data.split('_')[-1])
        try:
            event = controller.get_event_by_id(eid)
            if user in event.users or event.status == StatusEvent.FINISHED:
                await query.message.answer("Вы уже принимаете участие в мероприятии или оно уже завершилось")
            else:
                event.users.append(user)

                await query.message.answer('Поздравляем, Вы принимаете участие в мероприятии!')

                code, output = controller.generate_qr_code(event, user)

                await query.message.answer(f'Ваш код, который вы должны предоставить модератору мероприятия: {code}\n'
                                           f'Или QR-код:')
                try:
                    await query.message.answer_photo(output)
                finally:
                    output.close()

                controller.save()
        except NoResultFound:
            await query.message.answer('Такого мероприятия нет')

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

    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()

        de_attach = query.data.startswith('de')

        if query.data.endswith(self.model.__tablename__):
            entities = controller.get_entities_by_model_with_relationship(user, self.model, self.relation_model,
                                                                          self.relation_column, de_attach)
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
                entity = controller.get_entity_by_model_id(self.model, eid)
                self._lambda(user, entity, not de_attach)
                controller.save()

                await query.message.answer(
                    f'{entity.name} успешно {"добавлен в " + self.name.lower() if not de_attach else "удален из " + self.name_remove_form.lower()}')
            except ValueError / NoResultFound:
                await query.message.answer(f'{self.name} с этим названием отсутствуют')

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('att_' + self.model.__tablename__) or query.data.startswith(
            'deatt_' + self.model.__tablename__)


class GetAttendentStatisticsCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        eid = int(query.data.split('_')[-1])
        await query.answer()
        await query.message.answer(
            f"В мероприятии участвовал(-и) {controller.get_count_visited(eid)} человек(-а).")

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('atst_') and user.rank is Rank.ORGANIZER


class UserFeedbackCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()
        await query.message.answer('Оставьте свой отзыв :)')

        eid = int(query.data.split('_')[-1])
        controller.add_event_editor(eid, user.id)
        user.step = Step.FEEDBACK_TEXT
        controller.save()

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('feb_') and (user.rank is Rank.USER or user.rank is Rank.MODER)


class FeedbackStatisticsCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()

        eid = int(query.data.split('_')[-1])
        messages, neutral_list, negative_list, positive_list = controller.get_feedbacks_statistics(eid)

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

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('fbst_') and user.rank is Rank.ORGANIZER


class CancelEventCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()

        eid = int(query.data.split('_')[-1])
        try:
            event = controller.get_event_by_id(eid)
            if user in event.users and event.status == StatusEvent.UNFINISHED:
                event.users.remove(user)

                controller.remove_code(event, user)

                await query.message.answer('Вы отменили заявку на участие в мероприятии')

                controller.save()
            else:
                await query.message.answer("Вы уже не принимаете участие в этом мероприятии или оно завершилось")
        except NoResultFound:
            await query.message.answer('Такого мероприятия нет')

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('ecan_') and (user.rank is Rank.USER or user.rank is Rank.MODER)


class MarkPresentCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()

        eid = int(query.data.split('_')[-1])
        try:
            event = controller.get_event_by_id(eid)
            if event.status == StatusEvent.UNFINISHED:
                user.step = Step.VERIFICATION_PRESENT

                controller.add_event_editor(event.id, user.id)

                await query.message.answer(
                    'Вам необходимо прислать фото QR-кода, текстовый код для подтверждения или \'отмена\' для отмены '
                    'действия')

                controller.save()
            else:
                await query.message.answer("Мероприятие уже завершилось")
        except NoResultFound:
            await query.message.answer('Такого мероприятия нет')

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('marpr_') and user.rank is Rank.MODER


class EndEventCallback(Callback, ABC):
    async def callback(self, controller: Controller, user: User, query: CallbackQuery):
        await query.answer()

        eid = int(query.data.split('_')[-1])
        try:
            event = controller.get_event_by_id(eid)
            if event.status == StatusEvent.UNFINISHED:
                event.status = StatusEvent.FINISHED
                controller.save()

                for user in controller.get_visited_users(eid):
                    await query.message.bot.send_message(chat_id=user.id, text=f'Мероприятие {event.name} завершено',
                                                         reply_markup=InlineKeyboardMarkup()
                                                         .add(InlineKeyboardButton('Оставить отзыв',
                                                                                   callback_data=f"feb_{event.id}")))

                await query.message.answer('Мероприятие успешно завершено')
            else:
                await query.message.answer('Мероприятие уже завершено')
        except NoResultFound:
            await query.message.answer('Такого мероприятия нет')

    def can_callback(self, user: User, query: CallbackQuery) -> bool:
        return query.data.startswith('ende_') and user.rank is Rank.ORGANIZER


callbacks = [TakePartCallback(),
             UserFeedbackCallback(),
             CancelEventCallback(),
             MarkPresentCallback(),
             ChangeDataInUserCallback(),
             EndEventCallback(),
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
             ChangeDataInEventCallback(),
             AcceptFriendRequestCallback(),
             DeclineFriendRequestCallback(),
             DeleteFriendCallback(),
             UnknownCallback()]


def get_callback(user, query) -> Callback:
    for callback in callbacks:
        if callback.can_callback(user, query):
            return callback
