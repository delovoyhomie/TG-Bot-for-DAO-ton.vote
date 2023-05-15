from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, ChatTypeFilter
import sqlite3
from config import TOKEN

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

group_links = []
space_addresses = []

# Установка соединения с базой данных
conn = sqlite3.connect('C:/1. MY FILES/1. PROGRAMMING/3. TON/4. TgBot/for Orbs DAO Python/database.db')  # Подставьте имя вашей базы данных или путь к ней
# Создание курсора
cursor = conn.cursor()


class UserInput(StatesGroup):
    waiting_group_link = State()
    waiting_space_address = State()


@dp.message_handler(Command("start"), ChatTypeFilter(types.ChatType.PRIVATE))
async def cmd_start(message: types.Message):
    await message.reply("Привет! Пожалуйста, введите ссылку на группу:")

    # Устанавливаем состояние ожидания ссылки на группу
    await UserInput.waiting_group_link.set()


@dp.message_handler(state=UserInput.waiting_group_link)
async def process_group_link(message: types.Message, state: FSMContext):
    group_link = message.text
    group_links.append(group_link)
    
    cursor.execute(f"INSERT INTO DATA_DAOS (group_id) VALUES ('{group_link}')")
    conn.commit()

    # Сохраняем ссылку на группу в контексте состояния
    await state.update_data(group_link=group_link)

    # Запрашиваем адрес пространства
    await message.reply("Отлично! Теперь введите адрес пространства:")

    # Устанавливаем состояние ожидания адреса пространства
    await UserInput.waiting_space_address.set()


@dp.message_handler(state=UserInput.waiting_space_address)
async def process_space_address(message: types.Message, state: FSMContext):
    space_address = message.text
    space_addresses.append(space_address)
    # Получаем данные из контекста состояния
    data = await state.get_data()
    group_link = data.get('group_link')

    # Обрабатываем данные или выполняем другие действия с полученными значениями
    await message.reply("Спасибо! Вы ввели ссылку на группу: {}\n"
                        "и адрес пространства: {}".format(group_link, space_address))
    
    # Сбрасываем состояние и очищаем данные из контекста состояния
    await state.finish()


if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
