
# coding: utf-8

# In[100]:

#Import libraries

import pandas as pd
import requests
import json
import datetime
import os
import shutil
import time
from bs4 import BeautifulSoup, SoupStrainer
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday,     USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay,     USLaborDay, USThanksgivingDay
from pandas.tseries.offsets import BDay
import sys
sys.setrecursionlimit(10000)


# In[101]:

#Query request call
resp = requests.post(
    #This is where Twitch stores its data
    "https://gql.twitch.tv/gql",
    json.dumps(
        {
            #BrowsePage_AllDirectories is the directory page with all the top games listed
            "operationName": "BrowsePage_AllDirectories",
            "variables": {
                #Limit changes the amount of games shown
                "limit": 100,
                "directoryFilters": ["GAMES"],
                "isTagsExperiment": True,
                "tags": [],
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "75fb8eaa6e61d995a4d679dcb78b0d5e485778d1384a6232cba301418923d6b7",
                }
            },
        }
    ),
    #Client-Id can change inhibiting our access
    headers={"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"},
)


# In[102]:

#Parses the data for just the game content
edges = json.loads(resp.content)["data"]["directoriesWithTags"]["edges"]
games = [f["node"] for f in edges]

#New dataframe to store current data
df = pd.DataFrame(columns=["Game", "Views", "Tags"])

#Loop through to add all games
for i in range(0,len(games)):
    df.at[i,"Game"] = games[i]["displayName"]
    df.at[i,"Views"] = games[i]["viewersCount"]
    df.at[i,"Tags"] = [x["tagName"] for x in games[i]["tags"]]

df


# In[103]:

#These are the special trading close dates
class USTradingCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
        USMartinLutherKingJr,
        USPresidentsDay,
        GoodFriday,
        USMemorialDay,
        Holiday('USIndependenceDay', month=7, day=4, observance=nearest_workday),
        USLaborDay,
        USThanksgivingDay,
        Holiday('Christmas', month=12, day=25, observance=nearest_workday)
    ]

#Returns a range of trading dates
def get_trading_close_holidays(year):
    inst = USTradingCalendar()

    return inst.holidays(datetime.datetime(year-1, 12, 31), datetime.datetime(year, 12, 31))

def is_business_day(date):
    return bool(len(pd.bdate_range(date, date))) and (date not in get_trading_close_holidays(date.year))

def is_market_open(date):
    market_open = datetime.datetime(date.year,date.month, date.day,9,30)
    market_close = datetime.datetime(date.year,date.month, date.day,16,1) #Added an extra minute to get closing
    return date >= market_open and date <= market_close


# In[104]:

#Finds times, comes up with naming strings
today = datetime.datetime.now()
yesterday = today - datetime.timedelta(1)
today_file = "Data-AsOf-" + str(today.year) +"-" +str(today.month) +"-"+ str(today.day) + ".h5"
yesterday_file = "Data-AsOf-" + str(yesterday.year) +"-" +str(yesterday.month) +"-"+ str(yesterday.day) +".h5"
full_time_string = str(today.year) +"-" +str(today.month) +"-"+ str(today.day) + "-" + str(today.hour) + "-" + str(today.minute)
date_string = str(today.year) +"-" +str(today.month) +"-"+ str(today.day)
time_string = str(today.hour) + "-" + str(today.minute)


# In[105]:

get_stocks = is_business_day(today) and is_market_open(today)


# In[106]:

if get_stocks:
    
    stocks = ["EA", "ATVI", "TTWO", "AMZN","NTDOY", "UBI.PA", "SNE", "BILI", "NTES", "GAMR", "GME", "NFLX", "NVDA", "AMD"]
    stock_df = pd.DataFrame(columns = ["Stock","Price","Price Change", "Percent Change"])
    #Requests stock pricing for the listed stocks
    for i, stock in zip(range(0,len(stocks)),stocks):

        url = 'https://finance.yahoo.com/quote/' + stock

        session = requests.Session()
        resp = session.get(url)

        #Creates a beautiful soup object, strainer to improve run time
        strainer = SoupStrainer('div', attrs={'id': 'app'})
        soup = BeautifulSoup(resp.content, 'lxml', parse_only=strainer)

        #Price
        for item in soup.findAll('span', attrs={'class':"Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)"}):
            price = item.string

        #Price Change
        for item in soup.findAll('span', attrs={'class': lambda L: L and L.startswith('Trsdu(0.3s) Fw(500) Fz(14px)')}):
            ret = item.string.split(" (")

        #Concats the signs for returns
        if(ret[0][0] == "+"):
            price_change = ret[0][1:]
            percent_change = ret[1][1:-1]
        else:
            price_change = ret[0]
            percent_change = ret[1][:-1]

        #Writes to DF
        stock_df.at[i,"Stock"] = stock
        stock_df.at[i,"Price"] = price
        stock_df.at[i,"Price Change"] = price_change
        stock_df.at[i,"Percent Change"] = percent_change

        time.sleep(0.5)

# In[107]:

#If today's file doesnt exist, copy yesterday's and run
if (not os.path.isfile(today_file)) and os.path.isfile(yesterday_file):
    shutil.copy(yesterday_file, today_file)

#Load H5 file
file = pd.HDFStore(today_file)

#Tries to open datalist, if it doesnt work make a new one
try:
    datalist = file["Datalist"]
except:
    file["Datalist"] = pd.DataFrame(columns=["Date","Time","Twitch","Stock"])
    datalist = file["Datalist"]

#Create current run's row
newdata = pd.DataFrame(columns=["Date","Time","Twitch","Stock"])


if get_stocks:
    newdata.at[0] = [date_string, time_string, "Twitch-" + full_time_string, "Stock-" + full_time_string]
else:
    newdata.at[0] = [date_string, time_string, "Twitch-" + full_time_string, "Market Close"]

#Add new data
file["Datalist"] = datalist.append(newdata, ignore_index = True)
    
file["Twitch-" + full_time_string] = df
if get_stocks:
    file["Stock-" + str(full_time_string)] = stock_df

file.close()

