import logging

from aiogram import Bot, Dispatcher, executor, types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data import config
from data.keyboards import rank_selection_keyboard
from database.base import DBSession
from database.queries import users

engine = create_engine(f'sqlite:///{config.DATABASE_NAME}')
session_factory = sessionmaker(bind=engine)
db_session = DBSession(session_factory())

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TG_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if users.has_user_by_id(db_session, message.from_user.id):
        await message.answer('Вы уже авторизованы')
    else:

        await message.answer(f'Привет, {message.from_user.first_name}. Я бот, помогающий в организации/проведении '
                             f'мероприятий'
                             f'\n\n'
                             f'Кто вы? Организатор или обычный пользователь?', reply_markup=rank_selection_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)
