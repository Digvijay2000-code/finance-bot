from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from enum import Enum, unique
from functions import filter_camps
#classes

@unique
class CoyNames(Enum):
    HQ = "/hq"
    HMCT = "/hmct"
    KHATIB = "/khatib"
    KRANJI = "/kranji"
    ALPHA = "/alpha"
    CHARLIE = "/charlie"
    MANDAI = "/mandai"
    LTC = "/ltc"

#Classes are declared here for gathering various information from the users. The sequence of which the information is collected is in sequence declared here
    #1) PO_details class which are used for adding the details of the purchase order into Baserow
class Open_PO(StatesGroup):
    PO = State()
    Title_name = State()
    Coy = State()
    response = State()

    #2) Team_management class is for adding and removing the members that are given the access to the bot which is stored in baserow

class ADD_MEMBER(StatesGroup):
    telegram_id = State()
    coy = State()

class REMOVE_MEMBER(StatesGroup):
    telegram_id = State()

    #3) Close_PO class is closing the PO status on baserow
class Close_PO(StatesGroup):
    PO = State()
    response = State()

    #4) Reminder class to get the bot to move in sequence
class Reminder(StatesGroup):
    reminder = State()

class Invoice(StatesGroup):
    Invoice = State()

class ExtendDeadline(StatesGroup):
    PO = State()
    Days = State()
    response= State()

#keyboards
def finance_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("/po_database")
    markup.add("/po_management")
    markup.add("/team_management")
    markup.add("/reminder")
    markup.add("/baserow_cred")
    markup.add("/send_invoice")
    return markup

def coy_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    for i in CoyNames:
        markup.add(i.value)
    return markup

def COY_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    for i in CoyNames:
        name = str(i.value)
        new_name = name.lstrip("/").upper()
        markup.add(new_name)
    return markup

def open_close_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    markup.add('/add_po')
    markup.add('/close_po')
    markup.add('/extend_deadline')
    return markup

def team_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    markup.add('/add_member')
    markup.add('/remove_member')
    return markup


def confirmation_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    markup.add("✅")
    markup.add("❌")
    return markup

def po_keyboard(camp):
    camp_po = filter_camps(camp)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in camp_po['PO']:
        markup.add(str(i))
    return markup

def start_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    markup.add("/start")
    markup.add("/send_invoice")
    return markup

def start_keyboard1():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    markup.add("/start")
    return markup