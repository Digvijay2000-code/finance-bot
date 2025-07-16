from aiogram import Dispatcher, types
from functions import user_identification, filter_camps, days_between
from datetime import datetime
from classes import finance_keyboard
from async_functions import reminder_text
from config import BASEROW_PASSWORD, BASEROW_USERNAME, BOT_TOKEN
from aiogram.types import ParseMode
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types

bot = Bot(token=BOT_TOKEN)

def setup(dp:Dispatcher):
    dp.register_message_handler(start, commands='start')
    dp.register_message_handler(baserow_cred, commands='baserow_cred')

async def start(m:types.Message):
    #To show that the bot is working by showing the "Typing" status at the top
    await types.ChatActions.typing()
    await m.answer(f'Hi {m.from_user.first_name}')
    today = datetime.today()
    today1 = str(datetime.strftime(today, "%d-%m-%Y"))
    #calling the reminder_text function that is declared below
    identity = user_identification(m.from_user.id)
    if identity == 'Finance Team':
        try:
            await types.ChatActions.typing()
            data = filter_camps("HQ")
            alert_counter = 0
            hazard_counter = 0
            skull_counter = 0
            #counts the number of alerts
            string = f'----caa {today1}----\n\n'
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
            text = f'HQ: {data.shape[0]}\n🚨: {alert_counter}\n⚠️: {hazard_counter}\n💀: {skull_counter}\n\n'
            string += text
            await bot.send_message(m.chat.id, md.text(string), parse_mode=ParseMode.MARKDOWN)
            await reminder_text(m.from_user.id)
        except Exception as err:
            await m.reply(f'Something went wrong! Contact the finance team for assistance\n\nError Code:{err}')
        await m.answer(f'Choose what do you want to do today 😄', reply_markup=finance_keyboard())
    elif identity == 'Not Found':
        today = datetime.today()
        today1 = str(datetime.strftime(today, "%d-%m-%Y"))
        camps=['HQ', 'HMCT', 'KRANJI', 'KHATIB', 'MANDAI','ALPHA', 'CHARLIE', 'LTC']
        string = f'----caa {today1}----\n\n'
        for i in camps:
            await types.ChatActions.typing()
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
        await m.answer(f'/start again to refresh the figures 😄')
    else:
        try:
            await types.ChatActions.typing()
            data = filter_camps(identity)
            alert_counter = 0
            hazard_counter = 0
            skull_counter = 0
            #counts the number of alerts
            string = f'----caa {today1}----\n\n'
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
            text = f'{identity}: {data.shape[0]}\n🚨: {alert_counter}\n⚠️: {hazard_counter}\n💀: {skull_counter}\n\n'
            string += text
            await bot.send_message(m.chat.id, md.text(string), parse_mode=ParseMode.MARKDOWN)
            await types.ChatActions.typing()
            await reminder_text(m.from_user.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
            markup.add("/send_invoice")
            await m.answer(f'Click on the button "/send_invoice" to send the invoice over to the finance team', reply_markup=markup)
        except Exception as err:
            await m.reply(f'Something went wrong! Contact the finance team for assistance\n\nError Code:{err}')
        await m.answer(f'Any queries please feel free to approach the 1 TPT HQ S4 BR Finance Team')

async def baserow_cred(m: types.Message):
    await types.ChatActions.typing()
    identity = user_identification(m.from_user.id)
    if identity == 'Finance Team':
        await m.reply(f'Username: {BASEROW_USERNAME} \nPassword: {BASEROW_PASSWORD}', reply_markup=finance_keyboard())
    else:
        m.answer(f'Oops looks like you do not have access to this')
