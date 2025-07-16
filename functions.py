from enum import Enum, unique
import requests
import pandas as pd
from datetime import datetime, timedelta
from baserow import baserow
from config import BASEROW_TOKEN, BOT_ACCESS_TABLE, PO_TABLE

api_url = "https://api.baserow.io/api/database/rows/table/"
HEADERS = {"Authorization": f'Token {BASEROW_TOKEN}'}
HEADERS_JSON = {"Authorization": f'Token {BASEROW_TOKEN}', "Content-Type": "application/json"}

@unique
class FinanceTeamField(Enum):
    ID = "Telegram User ID"
    USER = "Type of User"

@unique
class USER(Enum):
    ID = "Telegram User ID"
    TYPE = "Type of User"

@unique
class PO_details(Enum):
    PO = "PO"
    TITLE = "Title"
    COY = "Coy"
    STATUS = "Status"

#fsidfjdsof
#for user database
@unique
class USERcamps(Enum):
    FINANCE_TEAM = 112796
    MANDAI = 112797
    KRANJI = 112798
    CHARLIE = 112799
    ALPHA = 112800
    HMCT = 112801
    LTC = 112802
    KHATIB = 112803

#for purchase order database
@unique
class POcamps(Enum):
    HQ = 111931
    MANDAI = 111934
    KRANJI = 111932
    CHARLIE = 112783
    ALPHA = 112782
    HMCT = 112784
    LTC = 112785
    KHATIB = 111933

@unique
class HolidaysSG(Enum):
    New_year = datetime.strptime("01/01/2022", "%d/%m/%Y")
    CNY = datetime.strptime("01/02/2022", "%d/%m/%Y")
    CNY_2 = datetime.strptime("02/02/2022", "%d/%m/%Y")
    Good_Friday = datetime.strptime("15/04/2022", "%d/%m/%Y")
    Labour_day = datetime.strptime("02/05/2022", "%d/%m/%Y")
    Eid = datetime.strptime("03/05/2022", "%d/%m/%Y")
    Vesak = datetime.strptime("16/05/2022", "%d/%m/%Y")
    Eid_al_adha = datetime.strptime("10/07/2022", "%d/%m/%Y")
    Eid_al_adha_2 = datetime.strptime("11/07/2022", "%d/%m/%Y")
    NDP = datetime.strptime("09/07/2022", "%d/%m/%Y")
    Diwali = datetime.strptime("24/10/2022", "%d/%m/%Y")
    Christmas_day = datetime.strptime("26/12/2022", "%d/%m/%Y")

#date function
def date_calculate(date, num_of_days):
    #convert the date into a usable format to calculate
    #d1 = datetime.strptime(date, "%Y-%m-%d")
    #add the number of days we want
    d2 = date + timedelta(days=num_of_days)
    #creating a list of holiday dates for the whole year using the HolidaysSG class
    hol = []
    for holiday in HolidaysSG:
        hol.append(holiday.value)
    #while loop to iterate through the list to make sure all of the dates are covered
    i = 0
    while i < 12:
        if hol[i] == d2:
            d2 = d2 - timedelta(days=1)
            i = 0
            #weekend checker
            if d2.strftime('%A') == "Saturday":
                d2 = d2 - timedelta(days=1)
            elif d2.strftime('%A') == "Sunday":
                d2 = d2 - timedelta(days=2)
            else:
                pass
        else:
            i+=1
            pass
    return d2

#identifying who the user is and the access that is permitted
def user_identification(user_id):
    results = requests.get(f'{api_url}{BOT_ACCESS_TABLE}/?user_field_names=true',headers=HEADERS).json()
    try:
        for r in results['results']:
            if int(user_id) == int(r[USER.ID.value]):
                type = r[USER.TYPE.value]['value']
                break
        return type
    except:
        type = "Not Found"
        return type


# creating a list of users to send out to
def userinfo():
    results = requests.get(f'{api_url}{BOT_ACCESS_TABLE}/?user_field_names=true',headers=HEADERS).json()
    try:
        #creating a list of users for us to use in main.py to send out to all of the users
        user_id = []
        for r in results['results']:
            user_id.append(int(r[USER.ID.value]))
        return user_id
    except Exception as err:
        print(f'Error: {err}')

# creating a list of users to send out to
def reminder_userinfo():
    results = requests.get(f'{api_url}{BOT_ACCESS_TABLE}/?user_field_names=true',headers=HEADERS).json()
    try:
        #creating a list of users for us to use in main.py to send out to all of the users
        user_id = []
        for r in results['results']:
            #check whether the user is HQ or not
            if r[USER.TYPE.value]['value'] != "Finance Team":
                user_id.append(int(r[USER.ID.value]))
        return user_id
    except Exception as err:
        print(f'Error: {err}')

#adding members into the Bot_access database
def addmember(tele_id, type):
    #giving ID to the type
    if type == "HQ":
        camp = USERcamps.FINANCE_TEAM.value
    elif type == "KRANJI":
        camp = USERcamps.KRANJI.value
    elif type == "KHATIB":
        camp = USERcamps.KHATIB.value
    elif type == "LTC":
        camp = USERcamps.LTC.value
    elif type == "ALPHA":
        camp = USERcamps.ALPHA.value
    elif type == "CHARLIE":
        camp = USERcamps.CHARLIE.value
    else:
        camp = USERcamps.HMCT.value
    results = requests.post(
    f'{api_url}{BOT_ACCESS_TABLE}/?user_field_names=true',
    headers=HEADERS_JSON,
    json={
        "Telegram User ID": tele_id,
        "Type of User": camp
    }
)

def removemember(tele_id):
    #need to extract the row id first to determine which row to delete
    data = requests.get(f'{api_url}{BOT_ACCESS_TABLE}/?user_field_names=true',headers=HEADERS).json() 
    for i in data['results']:
        user_id = int(i[USER.ID.value])
        if  user_id == int(tele_id):
            row_id = i['id']
            results = requests.delete(f'{api_url}{BOT_ACCESS_TABLE}/{row_id}/',headers=HEADERS)
            break
        else:
            pass

def update_deadline(po:str, num_of_days:int):
    today = datetime.today()
    deadline = date_calculate(today, num_of_days)
    deadline_date = str(datetime.strftime(deadline, "%Y-%m-%d"))
    data = requests.get(f'{api_url}{PO_TABLE}/?user_field_names=true',headers=HEADERS).json() 
    row_id = find_row(po)
    # for i in data['results']:
    #     if i[PO_details.PO.value] == str(po):
    #         row_id = i['id']
    results = requests.patch(f'{api_url}{PO_TABLE}/{row_id}/?user_field_names=true',headers=HEADERS_JSON,json={"Deadline Date": deadline_date})
    return results.json()

def deadline_extend(po:str, num_of_days:int):
    row_id = find_row(po)
    data = requests.get(f'{api_url}{PO_TABLE}/{row_id}/?user_field_names=true', headers=HEADERS).json()
    deadline_date = data['Deadline Date']
    deadline_date1 = datetime.strptime(deadline_date, "%Y-%m-%d")
    deadline_date2 = date_calculate(deadline_date1, num_of_days)
    deadline_date2 = str(datetime.strftime(deadline_date2, "%Y-%m-%d"))
    results = requests.patch(f'{api_url}{PO_TABLE}/{row_id}/?user_field_names=true',headers=HEADERS_JSON,json={"Deadline Date": deadline_date2})
    return results.json()

#filtering function to access the relevant PO details for respective camps
def filter_camps(camp):
    results = requests.get(f'{api_url}{PO_TABLE}/?user_field_names=true', headers=HEADERS).json()
    status = []
    coy = []
    for i in results['results']:
        status.append(i[PO_details.STATUS.value]['value'])
        coy.append(i[PO_details.COY.value]['value'])
    df = pd.DataFrame(results['results'])
    df1=df.drop(columns=['Status', 'id','order', 'Coy'])
    df1['Status'] = status
    df1['Coy'] = coy
    filtered = df1.loc[(df1["Coy"] == camp) & (df1["Status"] == "Open")]
    return filtered

def po_close(po):
    data = requests.get(f'{api_url}{PO_TABLE}/?user_field_names=true', headers=HEADERS).json()
    for i in data['results']:
        if i[PO_details.PO.value] == str(po):
            row_id = i['id']
            res = requests.patch(f'{api_url}{PO_TABLE}/{row_id}/?user_field_names=true',headers=HEADERS_JSON, json={"Status": 97166})
            break
        else:
            pass
    return

#adding PO entries to the database
def submit_po(po, title, coy):
    if coy == "HQ":
        camp = POcamps.HQ.value
    elif type == "KRANJI":
        camp = POcamps.KRANJI.value
    elif type == "KHATIB":
        camp = POcamps.KHATIB.value
    elif type == "LTC":
        camp = POcamps.LTC.value
    elif type == "ALPHA":
        camp = POcamps.ALPHA.value
    elif type == "CHARLIE":
        camp = POcamps.CHARLIE.value
    else:
        camp = POcamps.HMCT.value
    deadline_date = date_calculate(datetime.today(), 19)
    deadline_date = str(datetime.strftime(deadline_date, "%Y-%m-%d"))
    results = requests.post(f'{api_url}{PO_TABLE}/?user_field_names=true',headers=HEADERS_JSON, json={
        "PO": po,
        "Title": title,
        "Coy": camp,
        # it will always be open status when first entering
        "Status": 97165,
        "Deadline Date": deadline_date})
    return results.json()

def days_between(d1:datetime,d2:datetime):
    return (d1-d2).days

def find_row(po:str):
    data = requests.get(f'{api_url}{PO_TABLE}/?user_field_names=true', headers=HEADERS).json()
    for i in data['results']:
        if i[PO_details.PO.value] == str(po):
            row_id = i['id']
    return int(row_id)