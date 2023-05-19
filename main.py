from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, ChatTypeFilter
import sqlite3, json
from config import TOKEN
import api

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


########################################################
# Установка адреса DAO
@dp.message_handler(commands=['set'], state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_set(message: types.Message, state: FSMContext):
    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    for user in chat_admins:
        if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):
            await message.answer("Пожалуйста, введите адрес DAO ответным сообщением")
            await States.AddDAOAddress.set()


########################################################
# Показ списка DAOs, новости которых публикуются в этой группе
@dp.message_handler(commands="list", state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_inline_url(message: types.Message):

    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    for user in chat_admins:
        if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):
    
            # Получение всех DAOs, которые были настроены в этой группе 
            all_addresses = cursor.execute(f"SELECT dao_address FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
            addresses = list(item[0] for item in all_addresses)

            # Создание кнопок с DAOs
            buttons = []
            for item in addresses:
                buttons.append(types.InlineKeyboardButton(text=api.daoAddressInfo(item)[0], url = f"https://dev-ton-vote.netlify.app/{item}")) # https://dev-ton-vote-cache.herokuapp.com/dao/{item}

            # Добавление кнопок к сообщению
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await message.answer("Кнопки-ссылки", reply_markup=keyboard)


########################################################
# Удаление адреса DAO
@dp.message_handler(commands=['remove'], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def start(message: types.Message):
    
    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    for user in chat_admins:
        if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):

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
async def process_callback_button(callback: types.CallbackQuery):
    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(callback['message']['chat']['id'])
    for user in chat_admins:
        if (user['status'] == 'administrator' and user['user']['id'] == callback.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == callback.from_user.id):

            # Получаем данные из Inline кнопки
            button_data = callback.data

            # Обрабатываем выбор пользователя в соответствии с данными из кнопки
            if button_data == "button1":
                await callback.answer("Вы выбрали Кнопку 1")
            elif button_data == "button2":
                await callback.answer("Вы выбрали Кнопку 2")
            elif button_data == "button3":
                await callback.answer("Вы выбрали Кнопку 3")


########################################################
# Редактирование адреса DAO
@dp.message_handler(commands=['remove'], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def start(message: types.Message):
    
    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    for user in chat_admins:
        if (user['status'] == 'administrator' and user['user']['id'] == message.from_user.id) or (user['status'] == 'creator' and user['user']['id'] == message.from_user.id):
        
            buttons = [
                InlineKeyboardButton(text="Кнопка 1", callback_data="button1"),
                InlineKeyboardButton(text="Кнопка 2", callback_data="button2"),
                InlineKeyboardButton(text="Кнопка 3", callback_data="button3")
            ]

            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await message.answer("Кнопки-ссылки", reply_markup=keyboard)


########################################################
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
                if api.daoAddressInfo(dao_address) is None:   
                    await message.answer("DAO с таким адресом не существует, попробуйте другой адрес."), await state.finish()
                elif not cursor.execute(f"SELECT dao_address FROM DAOs  WHERE group_id == '{group_id}' AND dao_address == '{dao_address}'").fetchall():
                    await message.answer(f"Вы ввели следующий адрес: {dao_address}"), await state.finish()
                    cursor.execute(f"INSERT INTO DAOs (dao_address, group_id) VALUES ('{dao_address}', '{group_id}')"), conn.commit() # Добавление в базу данных адрес DAO
                else:
                    await message.answer("DAO с таким адресом уже существует."), await state.finish()

########################################################
if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)