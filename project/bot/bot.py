import asyncio
import aiogram
import os
from aiogram import Bot, Dispatcher, types, enums
from aiogram.types import Message, Video, Audio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from project.backend.message_handler import MessageHandler
from project.db.models import TgUsers
from project.backend.session import get_session
from sqlalchemy import delete, exists, select, update, desc

token = '7162903479:AAFh3Qs7EmEFDGxdmpCDp1Pl5AYIvfzZ37Q'
# token = '5577625193:AAGBtQsZAaBKJk9nUSUUJGfwuMZDfk89Gv8'
bot = Bot(token)
dp = Dispatcher()



@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    user = message.chat.id

    session = await get_session()
    exist_query = select(exists().where(TgUsers.tg_user == user))
    exist = await session.scalar(exist_query)

    if not exist:
        session = await get_session()
        user_id = await MessageHandler.new_user()

        query = TgUsers(tg_user=user, back_user=user_id)
        session.add(query)
        await session.commit()

    await message.answer(f'Привет! Я бот-помощник по документации Yandex Cloud! Задай мне вопрос, а я постараюсь найти на него ответ.')


@dp.message()
async def message_handler(message: Message) -> None:
    await bot_handler(message)


async def bot_handler(message: Message) -> None:

    b = []
    b.append([InlineKeyboardButton(text="Оценить", callback_data=f"estimate")])
    b.append([InlineKeyboardButton(text="Начать новую тему", callback_data=f"new_chat")])
    markup = InlineKeyboardMarkup(inline_keyboard=b)

    session = await get_session()
    user = message.chat.id
    user_id_query = select(TgUsers).where(TgUsers.tg_user == user)
    user_id = (await session.execute(user_id_query)).scalar().back_user
    
    text = await MessageHandler.new_message(user_id, message.text)
    await bot.send_message(chat_id=message.chat.id,
                           text=str(text).replace(',', '\n'),
                           reply_markup=markup)
    for i in range (5):
        try:
            await bot.edit_message_reply_markup(
                chat_id = message.chat.id,
                message_id =message.message_id - i,
                )
        except:
            pass

@dp.callback_query(lambda c: c.data == "estimate")
async def estimate_handler(callback_query: types.CallbackQuery):
    b = []
    b1 = InlineKeyboardButton(text="1", callback_data=f"grade 1")
    b2 = InlineKeyboardButton(text="2", callback_data=f"grade 2")
    b3 = InlineKeyboardButton(text="3", callback_data=f"grade 3")
    b4 = InlineKeyboardButton(text="4", callback_data=f"grade 4")
    b5 = InlineKeyboardButton(text="5", callback_data=f"grade 5")
    b.append([b1, b2, b3])
    b.append([b4, b5])
    markup = InlineKeyboardMarkup(inline_keyboard=b)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=markup)


@dp.callback_query(lambda c: c.data == "new_chat")
async def new_chat_handler(callback_query: types.CallbackQuery):
    session = await get_session()
    user = callback_query.message.chat.id
    user_id_query = select(TgUsers).where(TgUsers.tg_user == user)
    user_id = (await session.execute(user_id_query)).scalar().back_user

    mes = await MessageHandler.new_chat(user_id)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,)
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=str(mes))


@dp.callback_query(lambda c: int(list(c.data.split())[1]) > 0)
async def grade_handler(callback_query: types.CallbackQuery):
    grade = int(callback_query.data.split()[1])
    session = await get_session()
    user = callback_query.message.chat.id
    user_id_query = select(TgUsers).where(TgUsers.tg_user == user)
    user_id = (await session.execute(user_id_query)).scalar().back_user

    await MessageHandler.store_grade(user_id, grade)

    b = []
    b.append([InlineKeyboardButton(text="Начать новую тему", callback_data=f"new_chat")])
    markup = InlineKeyboardMarkup(inline_keyboard=b)

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text = callback_query.message.text + '\n\n Спасибо за оценку :)',
        reply_markup=markup)



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
