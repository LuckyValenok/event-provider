from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

rank_selection_keyboard = InlineKeyboardMarkup()
rank_selection_keyboard.add(InlineKeyboardButton('Пользователь', callback_data='set_user'),
                            InlineKeyboardButton('Организатор', callback_data='set_organizer'))
