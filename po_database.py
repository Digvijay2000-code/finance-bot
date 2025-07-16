from aiogram.types import ParseMode
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from datetime import datetime
from functions import filter_camps, user_identification, days_between
from classes import finance_keyboard, coy_keyboard
from async_functions import send_message
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

def setup(dp:Dispatcher):
    dp.register_message_handler(po_database, commands='po_database')
    dp.register_message_handler(cancel, commands='cancel')
    dp.register_message_handler(camp_database, commands = ['hq', 'hmct', 'kranji', 'khatib', 'mandai','alpha', 'charlie', 'ltc'])


async def cancel(m:types.Message):
    await m.answer(
        '*Going back to main page*',
        reply_markup=finance_keyboard(),
        parse_mode=types.ParseMode.MARKDOWN
    )


async def po_database(m:types.Message):
    await types.ChatActions.typing()
    await m.answer(f'Counting POs....🤓')
    await types.ChatActions.typing()
    identity = user_identification(m.from_user.id)
    if identity == "Finance Team":
        #This message consolidates all the outstanding PO
        today = datetime.today()
        today1 = str(datetime.strftime(today, "%d-%m-%Y"))
        camps=['HQ', 'HMCT', 'KRANJI', 'KHATIB', 'MANDAI','ALPHA', 'CHARLIE', 'LTC']
        string = f'----caa {today1}----\n\n'
        for i in camps:
            data = filter_camps(i)
            alert_counter = 0
            hazard_counter = 0
            skull_counter = 0
            #counts the number of alerts
            for x in range(data.shape[0]):
                await types.ChatActions.typing()
                date = datetime.strptime(str(data.iloc[x,4]),"%Y-%m-%d")
                days_to_deadline = int(days_between(date, today))
                if days_to_deadline >10:
                    pass
                elif days_to_deadline >= 7:
                    alert_counter += 1
                elif days_to_deadline >= 1:
                    hazard_counter += 1
                elif days_to_deadline <= 0:
                    skull_counter += 1
            text = f'{i}: {data.shape[0]}\n🚨: {alert_counter}\n⚠️: {hazard_counter}\n💀: {skull_counter}\n\n'
            string += text
        await m.answer(f'These are the number of current POs opened at the moment in the Battalion 🫡')
        await bot.send_message(m.chat.id, md.text(string), parse_mode=ParseMode.MARKDOWN)
        await m.reply(f'Which camp database would you like to access?\n\nOr /cancel to go back to main keyboard', reply_markup=coy_keyboard())
    else:
        await m.answer(f'Oops you do not have the finance rights 😳 Please contact the finance team for assistance. Give them your Telegram ID: {m.from_user.id}')

#For the PO Database
async def camp_database(m: types.Message):
    identity = user_identification(m.from_user.id)
    await types.ChatActions.typing()
    
    if identity == "Finance Team":
        if m.text == "/hq":
            coy = "HQ"
        elif m.text == "/mandai":
            coy = "MANDAI"
        elif m.text == "/charlie":
            coy = "CHARLIE"
        elif m.text == "/alpha":
            coy = "ALPHA"
        elif m.text == "/hmct":
            coy = "HMCT"
        elif m.text == "/kranji":
            coy = "KRANJI"
        elif m.text == "/ltc":
            coy = "LTC"
        elif m.text == "/khatib":
            coy = "KHATIB"
        data = filter_camps(coy)
        try:
            if data.shape[0] > 0:
                await m.answer(f'These are the POs for {coy} ⬇️')
                today = datetime.today()
                for i in range(data.shape[0]):
                    date = datetime.strptime(str(data.iloc[i,4]),"%Y-%m-%d")
                    days_to_deadline = int(days_between(date, today))
                #need to check out the metric of what shud be considered urgent and when shud they be alerted right away
                    if days_to_deadline >10:
                        alert = ""
                    elif days_to_deadline >= 7:
                        alert = "🚨"
                    elif days_to_deadline >= 3:
                        alert = "⚠️"
                    elif days_to_deadline <= 0:
                        alert = "💀"
            #Below are the codes that creates messages for each PO and sends it out to the user
                    await bot.send_message(m.from_user.id, md.text(
                            md.text(f'PO number: {data.iloc[i,0]}'),
                            md.text(f'Title: {data.iloc[i,1]}'),
                            md.text(f'Deadline Date to Handup: {date.strftime("%d %B %Y")} {alert}'),
                            sep='\n'
                        ), parse_mode=ParseMode.MARKDOWN)
                await m.reply(f'Choose what do you want to do next!', reply_markup=finance_keyboard())
            else:
                await m.answer(f'There are no outstanding POs for {coy}', reply_markup=finance_keyboard())
        except Exception as err:
            await m.reply(f'ERROR MESSAGE: {err}\n\n Please inform the Finance Team about this error, sorry for the inconvience caused😞')
    else:
        await m.reply('Oops looks you do not have access to this part of the bot')

