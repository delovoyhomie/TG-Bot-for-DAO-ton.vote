from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, ChatTypeFilter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import sqlite3, json
from config import TOKEN
import api


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Установка соединения с базой данных
conn = sqlite3.connect('C:/1. MY FILES/1. PROGRAMMING/3. TON/4. TgBot/TG-Bot-for-DAO-ton.vote/database.db')  # Подставьте имя вашей базы данных или путь к ней
cursor = conn.cursor() # Создание курсора

scheduler = AsyncIOScheduler() 

class States(StatesGroup):  
    AddDAOAddress = State()
    SetNewAddress = State()
    waitingRemove = State()
    removeDAOAddress = State()



########################################################
# Приветственная команда для группы
@dp.message_handler(commands=['start'], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_start(message: types.Message, state: FSMContext):

    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)

    admins = []
    for user in chat_admins:
        if user['status'] == 'administrator' or user['status'] == 'creator':
            admins.append(user['user']['id'])

    if message.from_user.id in admins:
        await message.answer("Привет! это публичка... ")
    else:
        await message.delete()


# Приветственная команда для личных сообщений с ботом
@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Инструкция: ")



########################################################
# Установка адреса DAO
@dp.message_handler(commands=['set'], state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_set(message: types.Message, state: FSMContext):

    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)

    admins = []
    for user in chat_admins:
        if user['status'] == 'administrator' or user['status'] == 'creator':
            admins.append(user['user']['id'])

    if message.from_user.id in admins:
        await message.answer("Пожалуйста, введите адрес DAO ответным сообщением")
        await States.AddDAOAddress.set()
    else:
        await message.delete()



########################################################
# Показ списка DAOs, новости которых публикуются в этой группе
@dp.message_handler(commands="list", state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_inline_url(message: types.Message):

    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)

    admins = []
    for user in chat_admins:
        if user['status'] == 'administrator' or user['status'] == 'creator':
            admins.append(user['user']['id'])

    if message.from_user.id in admins:
            # Получение всех DAOs, которые были настроены в этой группе 
            all_addresses = cursor.execute(f"SELECT dao_address FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
            all_names = cursor.execute(f"SELECT name_dao FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
            addresses = list(item[0] for item in all_addresses)
            names = list(item[0] for item in all_names)

            # Проверка на не пустой массив
            if not all_addresses or not all_names:
                await message.answer("Список пуст. Добавьте новый DAO по команде /set")
                return 
            
            # Создание кнопок с DAOs
            buttons = []
            for i, item in enumerate(addresses):
                buttons.append(types.InlineKeyboardButton(text=names[i], url = f"https://dev-ton-vote.netlify.app/{item}")) # https://dev-ton-vote-cache.herokuapp.com/dao/{item}

            # Добавление кнопок к сообщению
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await message.answer("Список DAOs ниже:", reply_markup=keyboard)
    else:
        await message.delete()



########################################################
# Удаление адреса DAO
@dp.message_handler(commands=['remove'], state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def start(message: types.Message, state: FSMContext):
    
    # Проверка на администратора или создателя группы
    chat_admins = await bot.get_chat_administrators(message.chat.id)

    admins = []
    for user in chat_admins:
        if user['status'] == 'administrator' or user['status'] == 'creator':
            admins.append(user['user']['id'])

    if message.from_user.id in admins:
        # Получение имён всех DAOs, которые были настроены в этой группе 
        all_addresses = cursor.execute(f"SELECT dao_address FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
        addresses = list(item[0] for item in all_addresses)
        all_names = cursor.execute(f"SELECT name_dao FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
        names = list(item[0] for item in all_names)

        # Проверка на не пустой массив
        if not all_addresses or not all_names:
            await message.answer("Список пуст. Добавьте новый DAO по команде /set")
            return 

        # Создание кнопок с DAOs
        buttons = []
        for i in range(len(names)):
            buttons.append(types.InlineKeyboardButton(text=names[i], callback_data = addresses[i])) # https://dev-ton-vote-cache.herokuapp.com/dao/{item}

        await States.removeDAOAddress.set()

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        
        await message.answer("Удалите DAO из списка ниже:", reply_markup=keyboard)
    else:
        await message.delete()

    
        
# Обрабатывание нажатия на inline кнопки
@dp.callback_query_handler(state = States.removeDAOAddress, chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def process_callback_button(callback: types.CallbackQuery, state: FSMContext):

    # Обрабатываем выбор пользователя в соответствии с данными из кнопки

    button_data = callback['data'] # Хранится адрес DAO, которое нужно удалить 
    name = cursor.execute(f"SELECT name_dao from DAOs WHERE dao_address == '{button_data}'").fetchall()[0][0] # Имя выбранного для удаления DAO
    cursor.execute(f"DELETE from DAOs WHERE dao_address == '{button_data}'"), conn.commit() # Удаление из базы данных строки со всей информацией 
    await callback.message.answer(f"Вы удалили DAO с именем *{name}*", parse_mode='MarkdownV2')
    await callback.message.delete()



########################################################
# Связанное состояние для установки адреса DAO 
@dp.message_handler(state = States.AddDAOAddress, chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def handle_message(message: types.Message, state: FSMContext):
    if message.text:
        
        # Проверка на администратора или создателя группы
        chat_admins = await bot.get_chat_administrators(message.chat.id)

        admins = []
        for user in chat_admins:
            if user['status'] == 'administrator' or user['status'] == 'creator':
                admins.append(user['user']['id'])

        if message.from_user.id in admins:
            dao_address = message.text
            group_id = message.chat.id
            if api.daoAddressInfo(dao_address) is None:   
                await message.answer("DAO с таким адресом не существует, попробуйте другой адрес."), await state.finish()
            elif not cursor.execute(f"SELECT dao_address FROM DAOs  WHERE group_id == '{group_id}' AND dao_address == '{dao_address}'").fetchall():
                await message.answer(f"Вы ввели следующий адрес: \n```{dao_address}```", parse_mode='MarkdownV2'), await state.finish()
                cursor.execute(f"INSERT INTO DAOs (dao_address, group_id, name_dao, count_proposals) VALUES ('{dao_address}', '{group_id}', '{api.daoAddressInfo(dao_address)[0]}', '{api.daoAddressInfo(dao_address)[6]}')"), conn.commit() # Добавление в базу данных новую строчку
            else:
                await message.answer("DAO с таким адресом уже существует."), await state.finish()
        else:
            await message.delete()



# Публикация новых proposals по API (/dao)
async def post_new_proposal():

    all_addresses = cursor.execute(f"SELECT dao_address FROM DAOs").fetchall()
    addresses = list(item[0] for item in all_addresses)
    for address in addresses:
        count_proposals_now = api.daoAddressInfo(address)[6] # количество proposals в dao
        count_proposals_bd = cursor.execute(f"SELECT count_proposals FROM DAOs WHERE dao_address == '{address}'").fetchall()[0][0]
        if count_proposals_now != count_proposals_bd:
            cursor.execute(f"UPDATE DAOs SET count_proposals = {count_proposals_now} WHERE dao_address == '{address}'"), conn.commit()
            
            # print(api.daoAddressInfo(address)[7], count_proposals_now - count_proposals_bd, count_proposals_now, count_proposals_bd, address) # для дебага
            
            for i in range(count_proposals_now - count_proposals_bd):

                # Публикация информации о новом предложении в соответсвии с его номером 
                proposalAddress = api.daoAddressInfo(address)[7][count_proposals_now - (i + 1)] # запрос на адрес proposals

                request = api.proposalAddressInfo(proposalAddress)

                title = json.loads(request[0])['en']
                description = json.loads(request[1])['en']
                proposalStartTime = datetime.fromtimestamp(request[3])
                proposalEndTime = datetime.fromtimestamp(request[4])

                
                name_dao = cursor.execute(f"SELECT name_dao FROM DAOs WHERE dao_address == '{address}'").fetchall()[0][0] # название DAO, в котром это предложение

                text = f'новое предложение from {name_dao}\n {title} \n {description} \n start: {proposalStartTime} \n end: {proposalEndTime}'
                chat_id = cursor.execute(f"SELECT group_id FROM DAOs WHERE dao_address == '{address}'").fetchall()[0][0]

                # Создание кнопок с DAOs
                buttons = [types.InlineKeyboardButton(text=title, url = f"https://dev-ton-vote.netlify.app/proposal{proposalAddress}")] # names[i]

                # Добавление кнопок к сообщению
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(*buttons)

                await bot.send_message(chat_id = chat_id, text = text, reply_markup=keyboard) 
            

########################################################
# Запуск бота
if __name__ == '__main__':
    scheduler.add_job(post_new_proposal, "interval", seconds = 5) # minutes = 1
    scheduler.start()

    # Запуск бота
    executor.start_polling(dp, skip_updates=True)