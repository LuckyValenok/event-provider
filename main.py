import logging

from aiogram import Bot, Dispatcher, executor, types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data import config
from data.commands import get_command
from data.keyboards import keyboards_by_rank
from database.base import DBSession
from database.models.user import User
from database.queries import users
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
    if user.step == Step.ENTER_FIRST_NAME:
        user.first_name = message.text
        user.step = Step.ENTER_MIDDLE_NAME
        db_session.commit_session()
        await message.answer('Теперь введите отчество')
    elif user.step == Step.ENTER_MIDDLE_NAME:
        user.middle_name = message.text
        user.step = Step.ENTER_LAST_NAME
        db_session.commit_session()
        await message.answer('Теперь введите фамилию')
    elif user.step == Step.ENTER_LAST_NAME:
        user.last_name = message.text
        user.step = Step.ENTER_PHONE
        db_session.commit_session()
        await message.answer(f'Приятно познакомиться, {user.first_name} {user.middle_name} {user.last_name}'
                             f'\n\n'
                             f'Пожалуйста, введите ваш номер телефона')
    elif user.step == Step.ENTER_PHONE:
        user.phone = message.text
        user.step = Step.ENTER_EMAIL
        db_session.commit_session()
        await message.answer('Остался последний шаг! Введите e-mail')
    elif user.step == Step.ENTER_EMAIL:
        user.email = message.text
        user.step = Step.NONE
        db_session.commit_session()
        await message.answer('Вы успешно авторизованы', reply_markup=keyboards_by_rank[user.rank])
    else:
        command = get_command(user, message.text)
        await message.answer(command.execute(db_session, user, message.text))


if __name__ == '__main__':
    executor.start_polling(dp)
