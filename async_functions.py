from aiogram.types import ParseMode
import aiogram.utils.markdown as md
import logging
from aiogram import Bot
from aiogram.utils import exceptions
import asyncio
from datetime import datetime
from functions import filter_camps, user_identification, days_between
from config import BOT_TOKEN

log = logging.getLogger('broadcast')
bot = Bot(token=BOT_TOKEN)

#new async function for sending out messages in reminders
async def send_message(user_id: int, text: str, disable_notification:bool = False) -> bool:
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    #to make sure we handle all kinds of errors when sending out the messages
    except exceptions.BotBlocked:
        log.error(f'Target [ID:{user_id}]: blocked by user')
    except exceptions.ChatNotFound:
        log.error(f'Target [ID:{user_id}]: invalid user ID')
    except exceptions.RetryAfter as e:
        log.error(f'Target [ID{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds')
        await asyncio.sleep(e.timeout)
        #recursive
        return await send_message(user_id, text)
    except exceptions.UserDeactivated:
        log.error(f'Target [ID{user_id}]: user is deactivated')
    except exceptions.TelegramAPIError:
        log.exception(f'Target [ID:{user_id}]: failed')
    else:
        log.info(f'Target [ID"{user_id}]: success')
        return True
    return False

async def reminder_text(user_id: int) ->bool:
    identity = user_identification(user_id)
    if identity == "Finance Team":
        data = filter_camps("HQ")
        today = datetime.today()
        urgent_po_counter = 0
        for i in range(data.shape[0]):
                date = datetime.strptime(str(data.iloc[i,4]),"%Y-%m-%d")
                days_to_deadline = int(days_between(date, today))
                #need to check out the metric of what shud be considered urgent and when shud they be alerted right away
                #more than 10 dont care
                if days_to_deadline > 10:
                    pass
                elif days_to_deadline >= 1:
                    urgent_po_counter +=1
                elif days_to_deadline <=0:
                    urgent_po_counter+=1
        #sending the first message of the number of urgent PO numbers
        await send_message(user_id=user_id,text = f'This is a reminder, HQ has {data.shape[0]} open POs of which {urgent_po_counter} POs are urgent! Here are the POs:')
        try:
            for i in range(data.shape[0]):
                date = datetime.strptime(str(data.iloc[i,4]),"%Y-%m-%d")
                days_to_deadline = int(days_between(date, today))
                #need to check out the metric of what shud be considered urgent and when shud they be alerted right away
                if days_to_deadline >10:
                    alert = ""
                elif days_to_deadline >= 7:
                    alert = "🚨"
                elif days_to_deadline >= 1:
                    alert = "⚠️"
                elif days_to_deadline <= 0:
                    alert = "💀"
            #Below are the codes that creates messages for each PO and sends it out to the user
                await bot.send_message(user_id, md.text(
                        md.text(f'PO number: {data.iloc[i,0]}'),
                        md.text(f'Title: {data.iloc[i,1]}'),
                        md.text(f'Deadline Date to Handup: {date.strftime("%d %B %Y")} {alert}'),
                        sep='\n'
                    ), parse_mode=ParseMode.MARKDOWN)
            return True
        except Exception as err:
            await send_message(user_id=user_id,text = f'There are no POs for you!😁 Error Code: {err}')
            return True
    elif identity == "Not Found!":
        await send_message(user_id=user_id, text = f'Hmmm looks like you are not in my database....🤔\n\nContact the finance team for assistance.')
        return False
    else:
        data = filter_camps(identity)
        today = datetime.today()
        urgent_po_counter = 0
        for i in range(data.shape[0]):
                date = datetime.strptime(str(data.iloc[i,4]),"%Y-%m-%d")
                days_to_deadline = int(days_between(date, today))
                #need to check out the metric of what shud be considered urgent and when shud they be alerted right away
                #more than 10 dont care
                if days_to_deadline > 10:
                    pass
                elif days_to_deadline >= 1:
                    urgent_po_counter +=1
                elif days_to_deadline <=0:
                    urgent_po_counter+=1
        await send_message(user_id = user_id, text =f'This is a reminder, you have {data.shape[0]} open POs for {identity} of which {urgent_po_counter} POs are urgent! Here are the POs owed:')
        try:
            for i in range(data.shape[0]):
                date = datetime.strptime(str(data.iloc[i,4]),"%Y-%m-%d")
                days_to_deadline = int(days_between(date, today))
                #need to check out the metric of what shud be considered urgent and when shud they be alerted right away
                if days_to_deadline >10:
                    alert = ""
                elif days_to_deadline >= 7:
                    alert = "🚨"
                elif days_to_deadline >= 1:
                    alert = "⚠️"
                elif days_to_deadline <= 0:
                    alert = "💀"
            #Below are the codes that creates messages for each PO and sends it out to the user
                await bot.send_message(user_id, md.text(
                        md.text(f'PO number: {data.iloc[i,0]}'),
                        md.text(f'Title: {data.iloc[i,1]}'),
                        md.text(f'Deadline Date to Handup: {date.strftime("%d %B %Y")} {alert}'),
                        sep='\n'
                    ), parse_mode=ParseMode.MARKDOWN)
            await send_message(user_id=user_id,text =f'Click /start to refresh PO to the latest figure 😊')
            await send_message(user_id=user_id,text =f'Please ensure that you hand up the invoices upon receiving them to avoid late GR and LOE')
            return True
        except:
            await send_message(user_id=user_id, text=f'There are no POs for you!😁')
            return True


async def sendfile(user_id: int, file_id:str, disable_notification:bool = False) ->bool:
    try:
        await bot.send_document(user_id, document=file_id, disable_notification=disable_notification,)
    #to make sure we handle all kinds of errors when sending out the messages
    except exceptions.BotBlocked:
        log.error(f'Target [ID:{user_id}]: blocked by user')
    except exceptions.ChatNotFound:
        log.error(f'Target [ID:{user_id}]: invalid user ID')
    except exceptions.RetryAfter as e:
        log.error(f'Target [ID{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds')
        await asyncio.sleep(e.timeout)
        #recursive
        await bot.send_document(user_id, document=file_id, disable_notification=disable_notification,)
    except exceptions.UserDeactivated:
        log.error(f'Target [ID{user_id}]: user is deactivated')
    except exceptions.TelegramAPIError:
        log.exception(f'Target [ID:{user_id}]: failed')
    else:
        log.info(f'Target [ID"{user_id}]: success')
        return True
    return False