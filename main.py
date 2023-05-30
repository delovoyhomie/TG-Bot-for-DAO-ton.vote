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

# Establishing a connection to the database
conn = sqlite3.connect('TG-Bot-for-DAO-ton.vote/database.db')  # Provide the name of your database or its path.
cursor = conn.cursor() # Create a cursor

scheduler = AsyncIOScheduler() 

class States(StatesGroup):  
    AddDAOAddress = State()
    SetNewAddress = State()
    waitingRemove = State()
    removeDAOAddress = State()



########################################################
# Welcome message for the group
@dp.message_handler(commands=['start'], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_start(message: types.Message, state: FSMContext):

    # Check for administrator or group creator
    chat_admins = await bot.get_chat_administrators(message.chat.id)

    admins = []
    for user in chat_admins:
        if user['status'] == 'administrator' or user['status'] == 'creator':
            admins.append(user['user']['id'])

    if message.from_user.id in admins:
        await message.answer("Greetings!\n\nI assist in keeping you updated on proposals of DAOs you're interested in by automatically sending notifications directly into this chat.\n\nHere are the main commands you can use with me:\n\n/set - this is the first command you'll use to start working with me. With it, you set the DAO address that you can find on your DAO's page below the title line. After setting, I will start sending you notifications about new proposals for this DAO.\n\n/list - this command allows you to see a list of all DAOs for which you're receiving proposal notifications in this chat.\n\n/remove - if you've decided that you no longer want to receive notifications about proposals for a certain DAO, you can remove it from your list.")
    else:
        await message.delete()


# Welcome message for personal messages with the bot
@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Greetings!\n\nI was created to operate in groups, assisting the entire team in keeping track of new DAO proposals. To start using me in your group, follow these steps:\n\n1) Add me to the group where you want to receive DAO notifications.\n2) Appoint me as an administrator in this group. This is necessary for me to correctly process commands and manage notifications.\n3) Grant me the right to delete messages. This will enable me to properly handle the commands that you and other group members will send.\n\nAfter completing these steps, you will be able to use all the same commands, but now within the group. This will allow all group members to stay updated on the latest proposals for the DAOs that interest you.\n\nIf you encounter any problems or have questions during the setup process, contact my creator - @delovoyslava, he's always ready to help!")



########################################################
# Set the DAO address
@dp.message_handler(commands=['set'], state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_set(message: types.Message, state: FSMContext):

    # Check for administrator or group creator
    chat_admins = await bot.get_chat_administrators(message.chat.id)

    admins = []
    for user in chat_admins:
        if user['status'] == 'administrator' or user['status'] == 'creator':
            admins.append(user['user']['id'])

    if message.from_user.id in admins:
        await message.answer("Please reply with the DAO address.")
        await States.AddDAOAddress.set()
    else:
        await message.delete()



########################################################
# Display a list of DAOs whose news is published in this group
@dp.message_handler(commands="list", state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def cmd_inline_url(message: types.Message):

    # Check for administrator or group creator
    chat_admins = await bot.get_chat_administrators(message.chat.id)

    admins = []
    for user in chat_admins:
        if user['status'] == 'administrator' or user['status'] == 'creator':
            admins.append(user['user']['id'])

    if message.from_user.id in admins:
            # Retrieve all the DAOs that have been set up in this group
            all_addresses = cursor.execute(f"SELECT dao_address FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
            all_names = cursor.execute(f"SELECT name_dao FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
            addresses = list(item[0] for item in all_addresses)
            names = list(item[0] for item in all_names)

            # Check for a non-empty array
            if not all_addresses or not all_names:
                await message.answer("The list is empty. Add a new DAO using the /set command.")
                return 
            
            # Creatе buttons with DAOs
            buttons = []
            for i, item in enumerate(addresses):
                buttons.append(types.InlineKeyboardButton(text=names[i], url = f"https://dev-ton-vote.netlify.app/{item}")) # https://dev-ton-vote-cache.herokuapp.com/dao/{item}

            # Add buttons to message
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            await message.answer("Список DAOs ниже:", reply_markup=keyboard)
    else:
        await message.delete()



########################################################
# Delete the DAO address
@dp.message_handler(commands=['remove'], state='*', chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def start(message: types.Message, state: FSMContext):
    
    # Check for administrator or group creator
    chat_admins = await bot.get_chat_administrators(message.chat.id)

    admins = []
    for user in chat_admins:
        if user['status'] == 'administrator' or user['status'] == 'creator':
            admins.append(user['user']['id'])

    if message.from_user.id in admins:
        # Retrieve the names of all the DAOs that have been set up in this group
        all_addresses = cursor.execute(f"SELECT dao_address FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
        addresses = list(item[0] for item in all_addresses)
        all_names = cursor.execute(f"SELECT name_dao FROM DAOs WHERE group_id == '{message.chat.id}'").fetchall()
        names = list(item[0] for item in all_names)

        # Check for a non-empty array
        if not all_addresses or not all_names:
            await message.answer("The list is empty. Add a new DAO using the /set command.")
            return 

        # Create buttons with DAOs
        buttons = []
        for i in range(len(names)):
            buttons.append(types.InlineKeyboardButton(text=names[i], callback_data = addresses[i])) # https://dev-ton-vote-cache.herokuapp.com/dao/{item}

        await States.removeDAOAddress.set()

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        
        await message.answer("Remove the DAO from the list below:", reply_markup=keyboard)
    else:
        await message.delete()

    
        
# Handling the click on inline buttons
@dp.callback_query_handler(state = States.removeDAOAddress, chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def process_callback_button(callback: types.CallbackQuery, state: FSMContext):

    # Handling the user's selection according to the data from the button

    button_data = callback['data'] # The address of the DAO that needs to be deleted is stored
    name = cursor.execute(f"SELECT name_dao from DAOs WHERE dao_address == '{button_data}'").fetchall()[0][0] # The name of the selected DAO for deletion is stored
    cursor.execute(f"DELETE from DAOs WHERE dao_address == '{button_data}'"), conn.commit() # Delete a row with all the information from the database
    await callback.message.answer(f"You have removed the DAO named *{name}*", parse_mode='MarkdownV2')
    await callback.message.delete()



########################################################
# Related state for setting the DAO address
@dp.message_handler(state = States.AddDAOAddress, chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def handle_message(message: types.Message, state: FSMContext):
    if message.text:
        
        # Check for administrator or group creator
        chat_admins = await bot.get_chat_administrators(message.chat.id)

        admins = []
        for user in chat_admins:
            if user['status'] == 'administrator' or user['status'] == 'creator':
                admins.append(user['user']['id'])

        if message.from_user.id in admins:
            dao_address = message.text
            group_id = message.chat.id
            if api.daoAddressInfo(dao_address) is None:   
                await message.answer("A DAO with such an address does not exist, try a different address."), await state.finish()
            elif not cursor.execute(f"SELECT dao_address FROM DAOs  WHERE group_id == '{group_id}' AND dao_address == '{dao_address}'").fetchall():
                await message.answer(f"You have entered the following address: \n```{dao_address}```", parse_mode='MarkdownV2'), await state.finish()
                cursor.execute(f"INSERT INTO DAOs (dao_address, group_id, name_dao, count_proposals) VALUES ('{dao_address}', '{group_id}', '{api.daoAddressInfo(dao_address)[0]}', '{api.daoAddressInfo(dao_address)[6]}')"), conn.commit() # Add a new row to the database
            else:
                await message.answer("A DAO with such an address already exists."), await state.finish()
        else:
            await message.delete()



# Publish new proposals via the API (/dao)
async def post_new_proposal():

    all_addresses = cursor.execute(f"SELECT dao_address FROM DAOs").fetchall()
    addresses = list(item[0] for item in all_addresses)
    for address in addresses:
        count_proposals_now = api.daoAddressInfo(address)[6] # The number of proposals in the DAO
        count_proposals_bd = cursor.execute(f"SELECT count_proposals FROM DAOs WHERE dao_address == '{address}'").fetchall()[0][0]
        if count_proposals_now != count_proposals_bd:
            cursor.execute(f"UPDATE DAOs SET count_proposals = {count_proposals_now} WHERE dao_address == '{address}'"), conn.commit() # Update the number of proposals
            
            # print(api.daoAddressInfo(address)[7], count_proposals_now - count_proposals_bd, count_proposals_now, count_proposals_bd, address) # For debugging
            
            for i in range(count_proposals_now - count_proposals_bd):
            
                # Publish of information about a new offer in accordance with its number
                proposalAddress = api.daoAddressInfo(address)[7][count_proposals_now - (i + 1)] # request for proposals address

                request = api.proposalAddressInfo(proposalAddress)
                
                try:
                    title = request[0]
                    description = request[1]
                    proposalStartTime = datetime.fromtimestamp(request[3])
                    proposalEndTime = datetime.fromtimestamp(request[4])
                    yes = request[5]
                    no = request[6]
                    abstain = request[7]

                    # For debugging
                    # proposalStartTime = datetime.fromtimestamp(1684677540) 
                    # proposalEndTime = datetime.fromtimestamp(1684677540)
                except:
                    return
                
                
                name_dao = cursor.execute(f"SELECT name_dao FROM DAOs WHERE dao_address == '{address}'").fetchall()[0][0] # Name of the DAO in which this sentence is

                text = f'🔔 New proposal for DAO!\n\n🔵 Voting: {description}\n📜 Proposal: {name_dao}\n\n⏰ Start time: {proposalStartTime}\n🔚 End time: {proposalEndTime}\n\nPlease review the proposal and participate in the voting!'
                chat_id = cursor.execute(f"SELECT group_id FROM DAOs WHERE dao_address == '{address}'").fetchall()[0][0]

                # Create buttons with DAOs
                buttons = [types.InlineKeyboardButton(text=title, url = f"https://dev-ton-vote.netlify.app/{address}/proposal/{proposalAddress}")] # names[i]
                
                # Add Buttons to message
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(*buttons)

                # Publish of a post about the beginning and end of the proposal
                scheduler.add_job(start_proposal, "date", run_date=proposalStartTime, args=(chat_id, title, address, proposalAddress, name_dao, description, proposalEndTime))
                scheduler.add_job(end_proposal, "date", run_date=proposalEndTime, args=(chat_id, title, address, proposalAddress, name_dao, description, yes, no, abstain))

                await bot.send_message(chat_id = chat_id, text = text, reply_markup=keyboard) 
            

# Publish a post at the start of voting
async def start_proposal(chat_id, title, address, proposalAddress, name_dao, description, proposalEndTime):
    text = f'🚀 Voting has begun!\n\n🔵 Voting: {description}\n📜 Proposal: {name_dao}\n\n🔚 End time: {proposalEndTime}\n\nVoting has started! Please review the proposal and participate in the voting!'

    # Create buttons with DAOs
    buttons = [types.InlineKeyboardButton(text=title, url = f"https://dev-ton-vote.netlify.app/{address}/proposal/{proposalAddress}")] # names[i]

    # Add Buttons to message
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    await bot.send_message(chat_id = chat_id, text = text, reply_markup=keyboard) 



# Publish a post at the end of the vote
async def end_proposal(chat_id, title, address, proposalAddress, name_dao, description, yes, no, abstain):
    if (yes is None) and (no is None) and (abstain is None):
        # no votes
        text = f"🏁 Voting has ended!\n\n🔵 Voting: {description}\n📜 Proposal: {name_dao}\n\nUnfortunately, the proposal didn't collect a single vote."
    else:
        # are votes
        text = f'🏁 Voting has ended!\n\n🔵 Voting: {description}\n📜 Proposal: {name_dao}\n\n📊 Results:\n✅ For: {yes}\n❌ Against: {no}\n🤐 Abstain: {abstain}\n\nThank you for participating in the voting!'

    # Create buttons with DAOs
    buttons = [types.InlineKeyboardButton(text=title, url = f"https://dev-ton-vote.netlify.app/{address}/proposal/{proposalAddress}")] # names[i]

    # Add Buttons to message
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    await bot.send_message(chat_id = chat_id, text = text, reply_markup=keyboard) 



# Every day information about the proposal is published, when it started
async def post_info_proposals_daily():
    all_addresses = cursor.execute(f"SELECT dao_address FROM DAOs").fetchall()
    addresses = list(item[0] for item in all_addresses)

    for address in addresses:
        count_proposals_now = api.daoAddressInfo(address)[6] # number of proposals in dao

        for i in range(count_proposals_now):

            # Publication of information about a new offer in accordance with its number
            proposalAddress = api.daoAddressInfo(address)[7][i] # request for proposals address

            try:
                request = api.proposalAddressInfo(proposalAddress)
                title = request[0]
                description = request[1]

                # To check daily notifications
                proposalStartTimeUNIX = request[3]
                proposalEndTimeUNIX = request[4]

                proposalStartTime = datetime.fromtimestamp(request[3])
                proposalEndTime = datetime.fromtimestamp(request[4])
                yes = request[5]
                no = request[6]
                abstain = request[7]
            except:
                return
            
            name_dao = cursor.execute(f"SELECT name_dao FROM DAOs WHERE dao_address == '{address}'").fetchall()[0][0] # Name of DAO


            if (datetime.now().timestamp() > proposalStartTimeUNIX):
                if (yes is None) and (no is None) and (abstain is None):
                    # Proposal started, but no votes
                    text = f"📅 Daily proposal update\n\n🔵 Voting: {description}\n📜 Proposal: {name_dao}\n\n🔚 End time: {proposalEndTime}\n\nThe proposal is active, vote!"
                else:
                    # Proposal started and there are votes
                    text = f"📅 Daily proposal update\n\n🔵 Voting: {description}\n📜 Proposal: {name_dao}\n\n📊 Results:\n✅ For: {yes}\n❌ Against: {no}\n🤐 Abstain: {abstain}\n\n🔚 End time: {proposalEndTime}\n\nThe proposal is active, vote!"
            else:
                # Proposal not active yet
                text = f'📅 Daily proposal update\n\n🔵 Voting: {description}\n📜 Proposal: {name_dao}\n\nWait for the voting to start!'

            
            chat_id = cursor.execute(f"SELECT group_id FROM DAOs WHERE dao_address == '{address}'").fetchall()[0][0]

            # Create buttons with DAOs
            buttons = [types.InlineKeyboardButton(text=title, url = f"https://dev-ton-vote.netlify.app/{address}/proposal/{proposalAddress}")] # names[i]

            # Add Buttons to message
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            await bot.send_message(chat_id = chat_id, text = text, reply_markup=keyboard) 



########################################################
# Bot launch
if __name__ == '__main__':
    scheduler.add_job(post_new_proposal, "interval", minutes = 1) # minutes = 1
    scheduler.add_job(post_info_proposals_daily, "interval", days = 1) # minutes = 1
    scheduler.start()

    # Bot launch
    executor.start_polling(dp, skip_updates=True)
