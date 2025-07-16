from aiogram.dispatcher import FSMContext
import logging
from aiogram import Bot, Dispatcher, types
from functions import user_identification, reminder_userinfo
from classes import Reminder, finance_keyboard, confirmation_keyboard
from async_functions import reminder_text
import asyncio
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
log = logging.getLogger('broadcast')

def setup(dp:Dispatcher):
    dp.register_message_handler(reminder, commands='reminder')
    dp.register_message_handler(sending_out, state=Reminder.reminder)

async def reminder(m:types.Message):
    await types.ChatActions.typing()
    identity = user_identification(m.from_user.id)
    try:
        if identity == "Finance Team":
            await Reminder.reminder.set()
            await m.answer(f'Do want to remind everyone for POs?', reply_markup=confirmation_keyboard())
        else:
            m.answer(f'Oops looks like you are not authorised to send out reminders')
    except Exception as err:  
        m.answer(f'ERROR CODE:{err}. Please contact the code person', reply_markup=finance_keyboard())

async def sending_out(m:types.Message, state:FSMContext):
    await types.ChatActions.typing()
    if m.text == "✅":
        #counting the number of messages that would be sent out
        count = 0
        #extracting the user info from the table 62322
        #only sends to the non-HQ people
        user_list = reminder_userinfo()
        try:
            #first loop for the number of users
            for user_id in user_list:
                #just use the reminder_text function for this use
                if await reminder_text(user_id=user_id):
                    count += 1
            #20 messages per second (Limit: 30 messages per second)
                await asyncio.sleep(.05)
        finally:
            log.info(f'{count} messages are successfully sent out')
            await m.reply(f'{count} messages are sent out', reply_markup=finance_keyboard())
        await state.finish()
    else:
        current_state = await state.get_state()
        markup1 = types.ReplyKeyboardRemove()
        if current_state is None:
            return
        logging.info('Cancelling...%r', current_state)
        await state.finish()
        await m.reply(f'Cancelled Reminder....', reply_markup=finance_keyboard())
