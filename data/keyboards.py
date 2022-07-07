from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from enums.ranks import Rank
from enums.status_event import StatusEvent

keyboards_by_rank = {
    Rank.USER: ReplyKeyboardMarkup(resize_keyboard=True)
        .add('Все мероприятия', 'Мои мероприятия', 'Мой профиль'),
    Rank.MODER: ReplyKeyboardMarkup(resize_keyboard=True)
        .add('Все мероприятия', 'Мои мероприятия', 'Мой профиль'),
    Rank.ORGANIZER: ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        .add('Добавить мероприятие', 'Мои мероприятия', 'Добавить модератора'),
    Rank.ADMIN: ReplyKeyboardMarkup(resize_keyboard=True)
        .add('Интересы', 'Группы', 'Достижения', 'Добавить организатора')
}

keyboards_by_status_event_and_by_rank = {
    StatusEvent.UNFINISHED: {
        Rank.ORGANIZER: lambda e: InlineKeyboardMarkup()
            .add(InlineKeyboardButton('Редактировать мероприятие', callback_data=f"ech_{e.id}_ev")),

        Rank.USER: lambda e: InlineKeyboardMarkup()
            .add(InlineKeyboardButton('Отменить заявку на участие', callback_data=f"ecan_{e.id}")),
        Rank.MODER: lambda e: InlineKeyboardMarkup()
            .row(InlineKeyboardButton('Отменить заявку на участие', callback_data=f"ecan_{e.id}"))
            .row(InlineKeyboardButton('Отметить присутствующих', callback_data=f"marpr_{e.id}")),
    },
    StatusEvent.FINISHED: {
        Rank.ORGANIZER: lambda e: InlineKeyboardMarkup()
            .add(InlineKeyboardButton('Статистика посещения', callback_data=f"atst_{e.id}"),
                 InlineKeyboardButton('Просмотреть отзывы', callback_data=f"fbst_{e.id}")),
        Rank.USER: lambda e: InlineKeyboardMarkup()
            .add(InlineKeyboardButton('Оставить отзыв', callback_data=f"feb_{e.id}")),
        Rank.MODER: lambda e: InlineKeyboardMarkup()
            .add(InlineKeyboardButton('Оставить отзыв', callback_data=f"feb_{e.id}"))
    }
}

profile_inline_keyboard = InlineKeyboardMarkup() \
    .row(InlineKeyboardButton('Изменить анкету', callback_data='change_user')) \
    .row(InlineKeyboardButton('Добавить группу', callback_data='att_local_group'),
         InlineKeyboardButton('Удалить группу', callback_data='deatt_local_group')) \
    .row(InlineKeyboardButton('Добавить интерес', callback_data='att_interest'),
         InlineKeyboardButton('Удалить интерес', callback_data='deatt_interest'))

change_user_data_keyboard = InlineKeyboardMarkup() \
    .row(InlineKeyboardButton('Имя', callback_data='change_user_firstname'),
         InlineKeyboardButton('Отчество', callback_data='change_user_middlename'),
         InlineKeyboardButton('Фамилию', callback_data='change_user_lastname')) \
    .row(InlineKeyboardButton('Телефон', callback_data='change_user_phone'),
         InlineKeyboardButton('Почту', callback_data='change_user_email'))

change_event_data_keyboard = InlineKeyboardMarkup() \
    .row(InlineKeyboardButton('Название', callback_data='ech_change_event_ename'),
         InlineKeyboardButton('Описание', callback_data='ech_change_event_edescription'),
         InlineKeyboardButton('Дата', callback_data='ech_change_event_edata')) \
    .row(InlineKeyboardButton('Локация', callback_data='ech_change_event_elocation'))
