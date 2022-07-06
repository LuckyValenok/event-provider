import logging

from aiogram import Bot, Dispatcher, executor, types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from callbacks import get_callback
from commands import get_command
from data import config
from data.keyboards import keyboards_by_rank
from database.base import DBSession
from database.models.user import User
from database.queries import users
from datainputs import get_data_input
from enums.ranks import Rank
from enums.steps import Step

engine = create_engine(f'sqlite:///{config.DATABASE_NAME}', echo=True)
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
        db_session.add_model(
            model=User(id=message.from_user.id, rank=Rank.USER, step=Step.ENTER_FIRST_NAME))
        db_session.commit_session()
        await message.answer(f'Привет, {message.from_user.first_name}. Я бот, помогающий в организации/проведении '
                             f'мероприятий'
                             f'\n\n'
                             f'Пожалуйста, напиши свое имя')


@dp.message_handler(commands=['menu'])
async def send_menu(message: types.Message):
    user = users.get_user_by_id(db_session, message.from_user.id)

    if user.step != Step.NONE:
        await message.answer('Для начала завершите предыдущее действие, пожалуйста')
    else:
        await message.answer('Буп', reply_markup=keyboards_by_rank[user.rank])


@dp.message_handler()
async def send_other(message: types.Message):
    user = users.get_user_by_id(db_session, message.from_user.id)
    data_input = get_data_input(user, message)
    if data_input is not None:
        await message.answer(data_input.input(db_session, user, message))
        return
    command = get_command(user, message)
    if command is not None:
        await command.execute(db_session, user, message)


@dp.callback_query_handler()
async def process_callback(query: types.CallbackQuery):
    user = users.get_user_by_id(db_session, query.from_user.id)
    callback = get_callback(user, query)
    if callback is not None:
        await callback.callback(db_session, user, query)
    else:
        await query.answer()


if __name__ == '__main__':
    executor.start_polling(dp)
