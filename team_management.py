from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from functions import user_identification, addmember, removemember
from classes import finance_keyboard, COY_keyboard, REMOVE_MEMBER, ADD_MEMBER, team_keyboard
from config import BOT_TOKEN
bot = Bot(token=BOT_TOKEN)


def setup(dp:Dispatcher):
    dp.register_message_handler(cancel, commands='cancel',state=[REMOVE_MEMBER, ADD_MEMBER])
    dp.register_message_handler(team_management, commands='team_management')
    #add member
    dp.register_message_handler(add_member, commands= 'add_member')
    dp.register_message_handler(add_tele, state = ADD_MEMBER.telegram_id)
    dp.register_message_handler(add, state = ADD_MEMBER.coy)
    #remove member
    dp.register_message_handler(remove_member, commands= 'remove_member')
    dp.register_message_handler(remove, state = REMOVE_MEMBER.telegram_id)

async def cancel(m:types.Message, state:FSMContext):
    await m.answer(
        '*Submission Cancelled.*',
        reply_markup=finance_keyboard(),
        parse_mode=types.ParseMode.MARKDOWN
    )
    await state.finish()


# conversation flow
# ask whether we are adding or removing
# split the streams
# if adding then COY > TELE ID
# if removing then TELE ID

async def team_management(m:types.Message):
    #authority check
    if user_identification(m.from_user.id) == "Finance Team":
        await types.ChatActions.typing()
        await m.answer(f'Team Management allows you to add and delete existing finance team as well as admins who have access to our bot 🤯 \n\nTake note: Admins are people that are outside of our finance team aka other camps 👀')
        await m.answer(f'Before starting, get the member to send his Telegram ID using ➡️ https://t.me/userinfobot which is necessary for this process')
        await m.answer(f'Are we adding or removing a member?🤔', reply_markup=team_keyboard())
    else:
        await m.answer(f'Oops looks like you are not authorised here🚨👮')

async def remove_member(m:types.Message):
    await types.ChatActions.typing()
    if user_identification(m.from_user.id) == "Finance Team":
        await m.answer(f'May I have the Telegram ID to remove?\n\n', reply_markup=ReplyKeyboardRemove())
        await REMOVE_MEMBER.telegram_id.set()
    else:
        await m.answer(f'Oops looks like you are not authorised here🚨👮')

async def remove(m:types.Message, state:FSMContext):
    await types.ChatActions.typing()
    data_submit = removemember(m.text)
    await state.finish()
    await m.answer(f'So long, bye bye person 🖖', reply_markup=finance_keyboard())
        
async def add_member(m:types.Message):
    await types.ChatActions.typing()
    if user_identification(m.from_user.id) == "Finance Team":
        await m.answer(f'May I know the Telegram ID of this member to add?', reply_markup=ReplyKeyboardRemove())
        await ADD_MEMBER.telegram_id.set()
    else:
        await m.answer(f'Oops looks like you are not authorised here🚨👮')

async def add_tele(m:types.Message, state:FSMContext):
    await types.ChatActions.typing()
    async with state.proxy() as data:
        data["TeleID"] = m.text
    await m.answer(f'Which Coy is this member from?', reply_markup=COY_keyboard())
    await ADD_MEMBER.coy.set()

async def add(m:types.Message, state:FSMContext):
    await types.ChatActions.typing()
    async with state.proxy() as data:
        send_data = addmember(data['TeleID'], m.text)
    await state.finish()
    await m.answer(f'Access granted✅', reply_markup=finance_keyboard())