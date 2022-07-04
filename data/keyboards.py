from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from enums.ranks import Rank

keyboards_by_rank = {
    Rank.USER: ReplyKeyboardMarkup(resize_keyboard=True).add(*['Все мероприятия', 'Мои мероприятия', 'Мой профиль']),
    Rank.MODER: ReplyKeyboardMarkup(resize_keyboard=True).add(*['Все мероприятия', 'Мои мероприятия', 'Мой профиль']),
    Rank.ORGANIZER: ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
        *['Добавить мероприятие', 'Мои мероприятия', 'Статистика', 'Настройки']),
    Rank.MANAGER: ReplyKeyboardMarkup(resize_keyboard=True).add(*['Добавить организатора', 'Статистика']),
    Rank.ADMIN: ReplyKeyboardMarkup(resize_keyboard=True).add(
        *['Интересы', 'Группы', 'Достижения', 'Добавить менеджера', 'Статистика'])
}

profile_inline_keyboard = InlineKeyboardMarkup()
profile_inline_keyboard.row(InlineKeyboardButton('Изменить анкету', callback_data='change_user'))
profile_inline_keyboard.row(InlineKeyboardButton('Добавить группу', callback_data='att_local_group'),
                            InlineKeyboardButton('Удалить группу', callback_data='deatt_local_group'))
profile_inline_keyboard.row(InlineKeyboardButton('Добавить интерес', callback_data='att_interest'),
                            InlineKeyboardButton('Удалить интерес', callback_data='deatt_interest'))
