from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, ChatTypeFilter
import sqlite3, json
from config import TOKEN
from api import proposal

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Установка соединения с базой данных
conn = sqlite3.connect('C:/1. MY FILES/1. PROGRAMMING/3. TON/4. TgBot/for Orbs DAO Python/database.db')  # Подставьте имя вашей базы данных или путь к ней
cursor = conn.cursor() # Создание курсора

class States(StatesGroup):
    AddDAOAddress = State()
    SetNewAddress = State()
    waitingRemove = State()
########################################################
# Приветственная команда для группы
@dp.message_handler(commands=['start'], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_start(message: types.Message, state: FSMContext):
    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    for user in chat_admins:
        if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):
            await message.answer("Привет! это публичка... ")

# Приветственная команда для личных сообщений
@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Инструкция: ")

# Установка адреса DAO
@dp.message_handler(commands=['set'], state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_set(message: types.Message, state: FSMContext):
    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    for user in chat_admins:
        if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):
            await message.answer("Пожалуйста, введите адрес DAO ответным сообщением")
            await States.AddDAOAddress.set()

# Связанное состояние для установки адреса DAO 
@dp.message_handler(state = States.AddDAOAddress, chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def handle_message(message: types.Message, state: FSMContext):
    if message.text:
        # Проверка на администратора или создателя группы
        chat_admins = await bot.get_chat_administrators(message.chat.id)
        for user in chat_admins:
            if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):
                dao_address = message.text
                group_id = message.chat.id
                await message.answer(f"Вы ввели следующий адрес: {dao_address}"), await state.finish()
                cursor.execute(f"INSERT INTO DAOs (dao_address, group_id) VALUES ('{dao_address}', '{group_id}')"), conn.commit() # Добавление в базу данных адрес DAO
        
# Редактирование адреса DAO
@dp.message_handler(commands=['reset'], state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_reset(message: types.Message, state: FSMContext):
# Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    for user in chat_admins:
        if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):
            await message.answer("Пожалуйста, введите отредактированный адрес DAO ответным сообщением")
            await States.SetNewAddress.set()

# Связанное состояние для установки нового ареса DAO 
@dp.message_handler(state = States.SetNewAddress, chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def handle_message(message: types.Message, state: FSMContext):
    if message.text:
        # Проверка на администратора или создателя группы
        chat_admins = await bot.get_chat_administrators(message.chat.id)
        for user in chat_admins:
            if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):
                dao_address = message.text
                group_id = message.chat.id
                await message.answer(f"Вы ввели следующий адрес: {dao_address}"), await state.finish()
                cursor.execute(f"UPDATE DAOs SET dao_address = '{dao_address}' WHERE group_id = '{message.chat.id}'"), conn.commit() # если group_id сопадают, то устанавливается новый dao_address

# Показ списка DAOs, новости которых публикуются в этой группе
@dp.message_handler(commands="list")
async def cmd_inline_url(message: types.Message):

    # Получение всех DAOs, которые были настроены в этой группе 
    address = cursor.execute(f"SELECT dao_address FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
    addresses = list(item[0] for item in address)

    # Создание кнопок с DAOs
    buttons = []
    for item in addresses:
        buttons.append(types.InlineKeyboardButton(text=item, url = f"https://dev-ton-vote.netlify.app/{item}")) # https://dev-ton-vote-cache.herokuapp.com/dao/{item}


    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer("Кнопки-ссылки", reply_markup=keyboard)

# Удаление адреса DAO
@dp.message_handler(commands=['remove'], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def start(message: types.Message):
    buttons = [
        InlineKeyboardButton(text="Кнопка 1", callback_data="button1"),
        InlineKeyboardButton(text="Кнопка 2", callback_data="button2"),
        InlineKeyboardButton(text="Кнопка 3", callback_data="button3")
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer("Кнопки-ссылки", reply_markup=keyboard)

# Обрабатывание нажатия на inline кнопки
@dp.callback_query_handler()
async def process_callback_button(callback_query: types.CallbackQuery):
    # Получаем данные из Inline кнопки
    button_data = callback_query.data

    # Обрабатываем выбор пользователя в соответствии с данными из кнопки
    if button_data == "button1":
        await callback_query.answer("Вы выбрали Кнопку 1")
    elif button_data == "button2":
        await callback_query.answer("Вы выбрали Кнопку 2")
    elif button_data == "button3":
        await callback_query.answer("Вы выбрали Кнопку 3")
########################################################

if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)