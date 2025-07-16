from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types, Bot
from aiogram.types import ContentTypes
from functions import filter_camps, find_row, user_identification, userinfo, update_deadline
from classes import finance_keyboard, Invoice, start_keyboard, start_keyboard1
from io import BytesIO
from async_functions import sendfile
import asyncio
from baserow import baserow
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

def setup(dp:Dispatcher):
    dp.register_message_handler(sending_invoice, commands='send_invoice')
    dp.register_message_handler(cancel, commands = 'cancel', state=Invoice.all_states)
    dp.register_message_handler(transmit_invoice, state=Invoice.Invoice, content_types=ContentTypes.DOCUMENT) 

async def cancel(m:types.Message, state:FSMContext):
    if user_identification(m.from_user.id) == "Finance Team":
        await m.answer(
            '*Submission Cancelled.*',
            reply_markup=finance_keyboard(),
            parse_mode=types.ParseMode.MARKDOWN
        )
        await state.finish()
    elif user_identification(m.from_user.id) == "Not Found":
        await m.answer('*Submission Cancelled.*', reply_markup=start_keyboard1(), parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    else:
        await m.answer('*Submission Cancelled.*', reply_markup=start_keyboard(), parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
        
async def sending_invoice(m:types.Message):
    await types.ChatActions.typing()
    await m.answer(f'Prepare your scanned document and just meet these few criteria ⬇️\n1) Document must be in PDF file format (.pdf at the end)\n2) Name the document in this manner, <PO number>_<DDMMYY of when goods/services were received>')
    await m.answer(f'Whenever you are ready, send the document to the Finance Team')
    await m.answer(f'To cancel the submission right now, click here /cancel or simply type it')
    await Invoice.Invoice.set()

async def transmit_invoice(m:types.Message, state:FSMContext):
    await types.ChatActions.typing()
    # check for PO format and PDF file type
    identity = user_identification(m.from_user.id)
    if identity == "Finance Team":
       #check for the length of the document to begin the process
        await types.ChatActions.typing()
        if len(m.document.file_name) == 21:
                po_data = filter_camps("HQ")
                name_check = False
                format_check = False
                for i in po_data['PO']:
                    await types.ChatActions.typing()
                    if m.document.file_name.startswith(i,0,10):
                        name_check = True
                if m.document.file_name.endswith(".pdf", 17, 21):
                    format_check = True
                if name_check and format_check:
                    await types.ChatActions.typing()
                    await m.answer(f'File meets all the requirements ✅ Uploading Invoice Submission....')
            # declaring doc here to set aside for document
                    doc = BytesIO()
            # downloading the document into the doc
                    await m.document.download(destination_file=doc)
                    await types.ChatActions.upload_document()
                    filename = await baserow.upload_file(doc, m.document.file_name)
                    try:
                        if filename:
                            payload = {
                                "Invoices" : [{"name":filename}]
                                        }
                        po = m.document.file_name[0:10]
                        row_id = find_row(po)
                        success = await baserow.update_row(
                            63578, row_id, payload
                            )
                        await types.ChatActions.typing()
                        await m.answer(f'Upload Complete 🔥')
                        await m.answer(f'Informing the Finance Team now of the new submission')
                        user_list = userinfo()
                        message_counter = 0
                        for user_id in user_list:
                            if user_identification(user_id) == "Finance Team":
                                if await sendfile(user_id, file_id=m.document.file_id):
                                    message_counter += 1
                                    await asyncio.sleep(.05)
                        await types.ChatActions.typing()
                        await m.answer(f'{message_counter} message(s) sent out to the Finance Team!')
                        await state.finish()
                        await m.answer(f'Thank you for submitting your invoice! Finance Team will begin GR right away 😇')
                        deadline_extend = update_deadline(m.document.file_name[0:10], 14)
                        await m.answer(f'Please submit the hardcopy to S4 Branch in the next 14 days to close the PO')
                    except Exception as err:
                        await m.answer(f'ERROR CODE: {err}')
                elif format_check == False:
                    await m.answer(f'File is not a PDF. Make sure that it is in PDF format (.pdf) Try again❌')
                elif name_check == False:
                    await m.answer(f'File does not contain valid PO number. Please amend it and send again❌')
                else:
                    await m.answer(f'File does not contain valid PO number and is not in PDF format (.pdf). Please follow the requirements and send again❌')
        else:
            await m.answer(f'Please follow the naming convention 😬 Try amending it and send again')
    else:
        #check for the length of the document to begin the process
        await types.ChatActions.typing()
        if len(m.document.file_name) == 21:
                po_data = filter_camps(user_identification(m.from_user.id))
                name_check = False
                format_check = False
                for i in po_data['PO']:
                    await types.ChatActions.typing()
                    if m.document.file_name.startswith(i,0,10):
                        name_check = True
                if m.document.file_name.endswith(".pdf", 17, 21):
                    format_check = True
                if name_check and format_check:
                    await types.ChatActions.typing()
                    await m.answer(f'File meets all the requirements ✅ Uploading Invoice Submission....')
            # declaring doc here to set aside for document
                    doc = BytesIO()
            # downloading the document into the doc
                    await m.document.download(destination_file=doc)
                    await types.ChatActions.upload_document()
                    filename = await baserow.upload_file(doc, m.document.file_name)
                    try:
                        if filename:
                            payload = {
                                "Invoices" : [{"name":filename}]
                                        }
                        po = m.document.file_name[0:10]
                        row_id = find_row(po)
                        success = await baserow.update_row(
                            63578, row_id, payload
                            )
                        await types.ChatActions.typing()
                        await m.answer(f'Upload Complete 🔥')
                        await m.answer(f'Informing the Finance Team now of the new submission')
                        user_list = userinfo()
                        message_counter = 0
                        for user_id in user_list:
                            if user_identification(user_id) == "Finance Team":
                                if await sendfile(user_id, file_id=m.document.file_id):
                                    message_counter += 1
                                    await asyncio.sleep(.05)
                        await types.ChatActions.typing()
                        await m.answer(f'{message_counter} message(s) sent out to the Finance Team!')
                        await state.finish()
                        await m.answer(f'Thank you for submitting your invoice! Finance Team will begin GR right away 😇')
                        deadline_extend = update_deadline(m.document.file_name[0:10], 14)
                        await m.answer(f'Please submit the hardcopy to S4 Branch in the next 14 days to close the PO')
                    except Exception as err:
                        await m.answer(f'ERROR CODE: {err}')
                elif format_check == False:
                    await m.answer(f'File is not a PDF. Make sure that it is in PDF format (.pdf) Try again❌')
                elif name_check == False:
                    await m.answer(f'File does not contain valid PO number. Please amend it and send again❌')
                else:
                    await m.answer(f'File does not contain valid PO number and is not in PDF format (.pdf). Please follow the requirements and send again❌')
        else:
            await m.answer(f'Please follow the naming convention 😬 Try amending it and send again')
        
        
        
        
        
        # #OA30044831_060722.pdf - 21 characters 
        # # check for PO 
        # # extract the database and compare the PO
        # #declaring the name check and format as false before starting the checks
        # name_check = False
        # format_check = False
        # #name check which is the PO check
        # for i in po_data['PO']:
        #     await types.ChatActions.typing()
        #     if m.document.file_name.startswith(i,0,10):
        #         name_check = True
        # #format check for the file type
        # if m.document.file_name.endswith(".pdf", 17, 21):
        #     format_check = True
        # # for i in po_data["PO"]:
        # #     await types.ChatActions.typing()
        # #     if m.document.file_name.startswith(i,0,10):
        # #         name_check = True
        # #         if m.document.file_name.endswith(".pdf", 17, 21):
        # #             format_check = True
        # #         else:
        # #             format_check = False
        # #     else:
        # #         name_check = False
        # if name_check and format_check:
        #     await types.ChatActions.typing()
        #     await m.answer(f'File meets all the requirements ✅ Uploading Invoice Submission....')
        #     # declaring doc here to set aside for document
        #     doc = BytesIO()
        #     # downloading the document into the doc
        #     await m.document.download(destination_file=doc)
        #     await types.ChatActions.upload_document()
        #     filename = await baserow.upload_file(doc, m.document.file_name)
        #     try:
        #         if filename:
        #             payload = {
        #                 "Invoices" : [{"name":filename}]
        #                 }
        #         po = m.document.file_name[0:10]
        #         row_id = find_row(po)
        #         success = await baserow.update_row(
        #             63578, row_id, payload
        #         )
        #         await types.ChatActions.typing()
        #         await m.answer(f'Upload Complete 🔥')
        #         await m.answer(f'Informing the Finance Team now of the new submission')
        #         user_list = userinfo()
        #         message_counter = 0
        #         for user_id in user_list:
        #             if user_identification(user_id) == "Finance Team":
        #                 if await sendfile(user_id, file_id=m.document.file_id):
        #                     message_counter += 1
        #                 await asyncio.sleep(.05)
        #         await types.ChatActions.typing()
        #         await m.answer(f'{message_counter} message(s) sent out to the Finance Team!')
        #         await state.finish()
        #         await m.answer(f'Thank you for submitting your invoice! Finance Team will begin GR right away 😇')
        #         deadline_extend = update_deadline(m.document.file_name[0:10], 14)
        #         await m.answer(f'Please submit the hardcopy to S4 Branch in the next 14 days to close the PO')
        #     except Exception as err:
        #         await m.answer(f'ERROR CODE: {err}')
        # elif format_check == False:
        #     await m.answer(f'File is not a PDF. Make sure that it is in PDF format (.pdf) Try again❌')
        # elif name_check == False:
        #     await m.answer(f'File does not contain valid PO number. Please amend it and send again❌')
        # else:
        #     await m.answer(f'File does not contain valid PO number and is not in PDF format (.pdf). Please follow the requirements and send again❌')