from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.utils import executor

from callbacks import get_callback
from commands import get_command
from controller import Controller
from data import config
from data.keyboards import keyboards_by_rank
from datainputs import get_data_input
from enums.steps import Step

bot: Bot = Bot(token=config.TG_TOKEN)
dp: Dispatcher = Dispatcher(bot)
controller: Controller = Controller()


@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    if controller.has_user_by_id(message.from_user.id):
        await message.answer('Вы уже авторизованы')
    else:
        controller.add_new_user(message.from_user.id)
        await message.answer(f'Привет, {message.from_user.first_name}. Я бот, помогающий в организации/проведении '
                             f'мероприятий'
                             f'\n\n'
                             f'Пожалуйста, напиши свое имя')


@dp.message_handler(commands=['menu'])
async def send_menu(message: Message):
    user = controller.get_user_by_id(message.from_user.id)

    if user.step != Step.NONE:
        await message.answer('Для начала завершите предыдущее действие, пожалуйста')
    else:
        await message.answer('Буп', reply_markup=keyboards_by_rank[user.rank])


@dp.message_handler(commands=['id'])
async def send_id(message: Message):
    await message.answer(f"Ваш ID: {message.from_user.id}")


@dp.message_handler(content_types=[ContentType.PHOTO, ContentType.TEXT, ContentType.LOCATION])
async def send_other(message: Message):
    user = controller.get_user_by_id(message.from_user.id)
    data_input = get_data_input(user, message)

    if data_input is not None:
        await data_input.input(controller, user, message)
        return
    if user.step != Step.NONE:
        await message.answer('Для начала завершите предыдущее действие, пожалуйста')
        return
    command = get_command(user, message)
    if command is not None:
        await command.execute(controller, user, message)


@dp.callback_query_handler()
async def process_callback(query: CallbackQuery):
    user = controller.get_user_by_id(query.from_user.id)
    if user.step != Step.NONE:
        await query.message.answer('Для начала завершите предыдущее действие, пожалуйста')
        return
    callback = get_callback(user, query)
    if callback is not None:
        await callback.callback(controller, user, query)
    else:
        await query.answer()


def run():
    executor.start_polling(dp)
