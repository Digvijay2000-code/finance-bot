from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, ReplyKeyboardRemove
import aiogram.utils.markdown as md
import logging
from aiogram import Bot, Dispatcher, types
from functions import submit_po, user_identification, po_close, deadline_extend
from classes import ExtendDeadline, finance_keyboard, Open_PO, Close_PO, open_close_keyboard, confirmation_keyboard, COY_keyboard
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

def setup(dp:Dispatcher):
    dp.register_message_handler(po_management, commands = 'po_management')
    dp.register_message_handler(cancel_open, commands = 'cancel', state=Open_PO.all_states)
    dp.register_message_handler(cancel_close, commands = 'cancel', state=Close_PO.all_states)
    dp.register_message_handler(cancel_deadline, commands = 'cancel', state=ExtendDeadline.all_states)
    #add po
    dp.register_message_handler(close_po, commands= 'close_po')
    dp.register_message_handler(closing_confirmation, state=Close_PO.PO)
    dp.register_message_handler(closing_po, state=Close_PO.response)
    #open po
    dp.register_message_handler(add_po, commands='add_po')
    dp.register_message_handler(open_po, state=Open_PO.PO)
    dp.register_message_handler(open_title, state=Open_PO.Title_name)
    dp.register_message_handler(open_coy, state=Open_PO.Coy)
    dp.register_message_handler(opening_confirmation, state=Open_PO.response)
    #extend deadline
    dp.register_message_handler(extend_deadline, commands='extend_deadline')
    dp.register_message_handler(extend_po, state = ExtendDeadline.PO)
    dp.register_message_handler(extend_days, state=ExtendDeadline.Days)
    dp.register_message_handler(extend_confirmation, state=ExtendDeadline.response)

async def extend_deadline(m:types.Message):
    await ExtendDeadline.PO.set()
    await m.answer(f'May I have PO number to extend the deadline date?', reply_markup=ReplyKeyboardRemove())

async def extend_po(m:types.Message, state:FSMContext):
    if len(m.text) != 10:
        await types.ChatActions.typing()
        await m.answer(f'❌PO must be 10 characters❌ please try again\n\n/cancel to stop the submission')
        await ExtendDeadline.PO.set()
    else:
        async with state.proxy() as data:
            data['PO'] = m.text
        await ExtendDeadline.Days.set()
        await m.answer(f'How many days do you want to extend it by?')

async def extend_days(m:types.Message, state:FSMContext):
    #update deadline date by using the function
    async with state.proxy() as data:
        data['Days'] = int(m.text)
    await ExtendDeadline.response.set()
    await m.answer(f'Please confirm that you want to proceed with extending the deadline for this PO', reply_markup=confirmation_keyboard())

async def extend_confirmation(m:types.Message, state:FSMContext):
    if m.text == "✅":
        await types.ChatActions.typing()
        await m.answer(f'Updating Baserow....')
        try:
            await types.ChatActions.typing()
            async with state.proxy() as data:
                po = data['PO']
                days = data['Days']
            extend = deadline_extend(po, days)
            await m.answer(f'Successfully updated deadline🔥', reply_markup=finance_keyboard())
            await state.finish()
        except Exception as err:
            await m.answer(f'ERROR CODE: {err}\n\nPlease inform the Finance Team about this error, sorry for the inconvience caused😞')
            await state.finish()

async def po_management(m:types.Message):
    identity = user_identification(m.from_user.id)
    if identity == "Finance Team":
        await types.ChatActions.typing()
        await m.answer(f'Do you want to Add PO or Close POs or extend the deadline?', reply_markup=open_close_keyboard())
    else:
        await m.answer(f'Oops looks you do not have access to this part of the bot')

async def cancel_open(m:types.Message, state:FSMContext):
    await m.answer(
        '*Submission Cancelled.*',
        reply_markup=finance_keyboard(),
        parse_mode=types.ParseMode.MARKDOWN
    )
    await state.finish()

async def cancel_deadline(m:types.Message, state:FSMContext):
    await m.answer(
        '*Submission Cancelled.*',
        reply_markup=finance_keyboard(),
        parse_mode=types.ParseMode.MARKDOWN
    )
    await state.finish()


async def cancel_close(m:types.Message, state:FSMContext):
    await m.answer(
        '*Submission Cancelled.*',
        reply_markup=finance_keyboard(),
        parse_mode=types.ParseMode.MARKDOWN
    )
    await state.finish()

async def close_po(m: types.Message):
    await Close_PO.PO.set()
    await m.answer(f'What is the PO number to be closed? Must be 10 characters (Eg: OA300052312)\n\n/cancel to stop the submission')

async def closing_confirmation(m:types.Message, state:FSMContext):
    if len(m.text) != 10:
        await types.ChatActions.typing()
        await m.answer(f'❌PO must be 10 characters❌ please try again\n\n/cancel to stop the submission')
        await Close_PO.PO.set()
    else:
        async with state.proxy() as data:
            data['PO'] = m.text
        await Close_PO.response.set()
        await m.reply(f'Are you sure you want to close this PO?👀\n\n', reply_markup=confirmation_keyboard())

async def closing_po(m:types.Message, state:FSMContext):
    if m.text == "✅":
        await types.ChatActions.typing()
        async with state.proxy() as data:
            try:
                closed = po_close(data['PO'])
                await state.finish()
                await m.reply(f'Successfully closed!🔥', reply_markup=finance_keyboard())
            except Exception as err:
                await m.reply(f'ERROR MESSAGE: {err}\n\n Please inform the Finance Team about this error, sorry for the inconvience caused😞', reply_markup=finance_keyboard())
                await state.finish()
    else:
        await types.ChatActions.typing()
        current_state = await state.get_state()
        if current_state is None:
            return
        logging.info('Cancelling...%r', current_state)
        await state.finish()
        await m.reply(f'Cancelled Submission!', reply_markup=finance_keyboard())


async def add_po(m:types.Message):
    await types.ChatActions.typing()
    await Open_PO.PO.set()
    await m.answer(f'What is the PO number to be added? Must be 10 characters (Eg: OA300052312)\n\n/cancel to stop the submission')

async def open_po(m:types.Message, state:FSMContext):
    if len(m.text) != 10:
        await types.ChatActions.typing()
        await m.answer(f'❌PO must be 10 characters❌ please try again\n\n/cancel to stop the submission')
        await Open_PO.PO.set()
    else:
        await types.ChatActions.typing()
        async with state.proxy() as data:
            data['PO'] = m.text
        await Open_PO.Title_name.set()
        await m.answer(f'What is the title of the PO?\n\n/cancel to stop the submission')

async def open_title(m:types.Message, state:FSMContext):
    await types.ChatActions.typing()
    async with state.proxy() as data:
        data['Title'] = m.text
    await Open_PO.Coy.set()
    await m.answer(f'Which coy is this for?\n\n/cancel to stop the submission', reply_markup=COY_keyboard())

async def open_coy(m:types.Message, state:FSMContext):
    await types.ChatActions.typing()
    try:
        async with state.proxy() as data:
            data['Coy'] = m.text
            await bot.send_message(
                m.chat.id, 
                md.text(
                    md.text('Following inputs have been made:'),
                    md.text('PO Number: ', md.code(data['PO'])),
                    md.text('Title: ', md.code(data['Title'])),
                    md.text('Coy: ', md.code(data['Coy'])),
                sep = '\n',
            ),
            parse_mode = ParseMode.MARKDOWN,
            )
        await Open_PO.response.set()
        await m.answer(f'Do you confirm these inputs?', reply_markup=confirmation_keyboard())
    except Exception as err:
        await m.answer(f'ERROR CODE: {err}. Please contact the coder', reply_markup=finance_keyboard())
        await state.finish()

async def opening_confirmation(m:types.Message, state:FSMContext):
    if m.text == "✅":
        await types.ChatActions.typing()
        async with state.proxy() as data:
            try:
                submitted_data = submit_po(data['PO'], data['Title'], data['Coy'])
                await state.finish()
                await m.reply(f'Successfully posted 🔥', reply_markup=finance_keyboard())
            except Exception as err:
                await m.reply(f'ERROR CODE: {err}😵‍💫 please contact the coder!')
    else:
        await types.ChatActions.typing()
        current_state = await state.get_state()
        if current_state is None:
            return
        logging.info('Cancelling...%r', current_state)
        await state.finish()
        await m.reply(f'Cancelled submission....', reply_markup= finance_keyboard())