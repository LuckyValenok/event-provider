from aiogram.types import ReplyKeyboardMarkup

from enums.ranks import Rank

keyboards_by_rank = {
    Rank.USER: ReplyKeyboardMarkup(resize_keyboard=True).add(*['Все мероприятия', 'Мои мероприятия', 'Настройки'])
}
