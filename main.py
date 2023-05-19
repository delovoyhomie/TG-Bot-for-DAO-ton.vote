from aiogram import Bot, Dispatcher, executor, types
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

########################################################
# Приветственная команда для группы
@dp.message_handler(commands=['start'], state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_start(message: types.Message, state: FSMContext):
    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    for user in chat_admins:
        if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):
            await message.answer("Привет! это публичка... ")

# Приветственная команда для личных сообщений
@dp.message_handler(commands=['start'], state='*',  chat_type=types.ChatType.PRIVATE)
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

        
########################################################
if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)