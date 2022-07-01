from aiogram.types import ReplyKeyboardMarkup

from enums.ranks import Rank

keyboards_by_rank = {
    Rank.USER: ReplyKeyboardMarkup(resize_keyboard=True).add(*['Все мероприятия', 'Мои мероприятия', 'Настройки']),
    Rank.MODER: ReplyKeyboardMarkup(resize_keyboard=True).add(*['Все мероприятия', 'Мои мероприятия', 'Настройки']),
    Rank.ORGANIZER: ReplyKeyboardMarkup(resize_keyboard=True).add(*['Мои мероприятия', 'Статистика', 'Настройки']),
    Rank.MANAGER: ReplyKeyboardMarkup(resize_keyboard=True).add(*['Добавить организатора', 'Статистика']),
    Rank.ADMIN: ReplyKeyboardMarkup(resize_keyboard=True).add(*['Добавить менеджера', 'Статистика'])
}
