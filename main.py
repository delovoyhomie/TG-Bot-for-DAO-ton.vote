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

#################################################################################
@dp.message_handler(Command("start"), ChatTypeFilter(types.ChatType.PRIVATE))
async def start(message: types.Message):
    await message.answer("Привет! это личка... ")

# Класс состояний
class UserInput(StatesGroup):
    waiting_group_link = State()
    waiting_dao_address = State()

@dp.message_handler(Command("set"), ChatTypeFilter(types.ChatType.PRIVATE))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Пожалуйста, введите ссылку на группу:")
    await UserInput.waiting_group_link.set()  # Устанавливаем состояние ожидания ссылки на группу

@dp.message_handler(state=UserInput.waiting_group_link)
async def process_group_link(message: types.Message, state: FSMContext):
    group_link = message.text
    user_id = message.from_user.id
    await state.update_data(group_link=group_link, user_id=user_id) # Сохраняем ссылку на группу в контексте состояния
    await message.answer("Отлично! Теперь введите адрес пространства:") # Запрашиваем адрес пространства
    await UserInput.waiting_dao_address.set() # Устанавливаем состояние ожидания адреса пространства
    
@dp.message_handler(state=UserInput.waiting_dao_address)
async def process_dao_address(message: types.Message, state: FSMContext):
    dao_address = message.text

    # Получаем данные из контекста состояния
    data = await state.get_data()
    group_link = data.get('group_link')
    user_id = data.get('user_id')

    cursor.execute(f"INSERT INTO DATA_DAOS (group_link, dao_address, admin_id) VALUES ('{group_link}', '{dao_address}', '{user_id}')"), conn.commit() # Добавление в БД
    
    # Обрабатываем данные или выполняем другие действия с полученными значениями
    await message.answer("Спасибо! Вы ввели ссылку на группу: {}\n"
                        "и адрес пространства: {}".format(group_link, dao_address))
    
    await state.finish() # Сбрасываем состояние и очищаем данные из контекста состояния


@dp.message_handler(Command("start"), ChatTypeFilter(types.ChatType.PRIVATE))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Пожалуйста, введите ссылку на группу:")
    await UserInput.waiting_group_link.set() # Устанавливаем состояние ожидания ссылки на группу
#################################################################################

@dp.message_handler(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! это публичка... ")

    # Добавление в БД
    cursor.execute(f"UPDATE DATA_DAOS SET group_id = '{message.chat.id}' WHERE admin_id = '{message.from_user.id}'"), conn.commit() # если user.id сопадают, то устанавливается group_id
    address = cursor.execute(f"SELECT dao_address FROM DATA_DAOS WHERE admin_id = '{message.from_user.id}'").fetchall()[0][0]
    proposals = json.dumps(proposal(address)) # Преобразование в json формат из функции в api, принимающей адрес предложения 
    cursor.execute(f"INSERT INTO DATA_DAOS (suggestions) VALUES ('{proposals}')"), conn.commit()


if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
