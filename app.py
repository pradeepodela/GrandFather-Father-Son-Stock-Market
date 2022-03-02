import pandas as pd
import numpy as np
from stocks_toolkit import stocks_toolkit
from datetime import date , datetime
from nsetools import Nse
from tradingview_ta import TA_Handler, Interval, Exchange
import pyrebase
import streamlit as st
import pandas as pd

st.title("Stock Analysis")
cfg = {
    'apiKey': "AIzaSyBwRBcKz9DC68UVsMBygkANr_QixS0ZaKA",
    'authDomain': "mypy-19226.firebaseapp.com",
    'databaseURL':'https://mypy-19226-default-rtdb.firebaseio.com/',
    'projectId': "mypy-19226",
    'storageBucket': "mypy-19226.appspot.com",
    'messagingSenderId': "990787705081",
    'appId': "1:990787705081:web:ab15b33b11bbea973dea28",
    'measurementId': "G-298F64SX86"

}


print('configering.....')

firebase = pyrebase.initialize_app(cfg)
print('app configered')
db = firebase.database()
auth = firebase.auth()
Storage = firebase.storage()

nse = Nse()
now = datetime.now()
st = stocks_toolkit()



stron_buy = []
weak_buy = []
sell = []
neutral = []
all_chart_list = {}
coumpines_listed = []
stron_buy_updated = []
weak_buy_updated = []



def get_data(symbol, start_date, end_date):
    """
    Get historical data for a given symbol
    :param symbol:
    :param start_date:
    :param end_date:
    :return:
    """
    data = st.technical_data(symbol,start_date,end_date)
    return data

def top_gainers():
    """
    Get top gainers from NSE
    :return:
    """
    nse = Nse()
    data = nse.get_top_gainers()
    data = pd.DataFrame(data)
    data = data['symbol']
    return data

# data = list(top_gainers())

def top_losers():
    """
    Get top losers from NSE
    :return:
    """
    nse = Nse()
    data = nse.get_top_losers()
    data = pd.DataFrame(data)
    data = data['symbol']
    return data

def get_time():
    """
    Get current time
    :return:
    """
    return now.strftime("%H:%M:%S")

def get_predecation(stock_symbol,interval):
    """
    Get analysis for a given stock
    :param stock_symbol: symbol of the stock
    :param interval: interval of the stock
    :return:
    """
    data = TA_Handler(
        symbol=stock_symbol,
        screener="india",
        exchange="nse",
        interval=interval,
        proxies={'http': 'http://50.114.128.23:3128'} # Uncomment to enable proxy (replace the URL).
        )
    analysis = data.get_analysis().summary
    return analysis

def get_indicator_pred(stock_symbol,interval):
    """
    Get analysis for a given stock
    :param stock_symbol: symbol of the stock
    :param interval: interval of the stock
    :return:
    """
    data = TA_Handler(
        symbol=stock_symbol,
        screener="india",
        exchange="nse",
        interval=interval,
        proxies={'http': 'http://50.114.128.23:3128'} # Uncomment to enable proxy (replace the URL).
    )
    analysis = data.get_analysis().oscillators
    return analysis

# data = get_indicator_pred(stock_symbol='tcs',interval=Interval.INTERVAL_1_WEEK)
# print(data['COMPUTE'])

def get_predecation_moving_avg(stock_symbol,interval):
    """
    Get analysis for a given stock
    :param stock_symbol: symbol of the stock
    :param interval: interval of the stock
    :return:
    """
    data = TA_Handler(
        symbol=stock_symbol,
        screener="india",
        exchange="nse",
        interval=interval,
        proxies={'http': 'http://50.114.128.23:3128'} # Uncomment to enable proxy (replace the URL).
    )
    analysis = data.get_analysis().moving_averages
    return analysis

# data = get_predecation_moving_avg(stock_symbol='tcs',interval=Interval.INTERVAL_1_WEEK)
# print(data['COMPUTE'])

def get_indicator_data(stock_symbol,interval):
    """
    Get analysis for a given stock
    :param stock_symbol: symbol of the stock
    :param interval: interval of the stock
    :return:
    """
    data = TA_Handler(
        symbol=stock_symbol,
        screener="india",
        exchange="nse",
        interval=interval,
        proxies={'http': 'http://50.114.128.23:3128'} # Uncomment to enable proxy (replace the URL).
    )
    analysis = data.get_analysis().indicators
    return analysis

def get_basic_info(stock_symbol):
    """
    Get basic information for a given stock
    :param stock_symbol: symbol of the stock
    :return:
    """
    data = TA_Handler(
        symbol=stock_symbol,
        screener="india",
        exchange="nse",
        interval=Interval.INTERVAL_1_DAY,
        proxies={'http': 'http://50.114.128.23:3128'} # Uncomment to enable proxy (replace the URL).
    )
    analysis = data.get_analysis().indicators
    out = {
        'company_name': data.symbol,
        'Exchange': data.exchange,
        'Interval': data.interval,
        'Time': get_time(),
        'Open': analysis['open'],
        'High': analysis['high'],
        'Low': analysis['low'],
        'Close': analysis['close'],
        'Volume': analysis['volume'],
    }
    return out
# data = get_basic_info(stock_symbol='tcs')
# print(data)
# data = get_indicator_data(stock_symbol='tcs',interval=Interval.INTERVAL_1_WEEK)
# print(data)



# 1 get data of top gainers in the market

top_gainers = list(top_gainers())

print('Top gainers')
for num , i in enumerate(top_gainers):
    
    print(num,i)
    if '-' in i:
        i = i.replace('-','_')
        top_gainers[num] = i
    if '&' in i:
        i = i.replace('&','_')
        top_gainers[num] = i

all_stock_codes = nse.get_stock_codes()
for i in all_stock_codes:
    coumpines_listed.append(i)
coumpines_listed.remove('SYMBOL')
# print(coumpines_listed)
# print(len(coumpines_listed))
for num , i in enumerate(coumpines_listed):
    
    print(num,i)
    if '-' in i:
        i = i.replace('-','_')
        coumpines_listed[num] = i


monday_tasks=db.child("data").child("stocks_data").child("Top_gainers_of_week").get()


if str(date.today()) not in dict(monday_tasks.val()):
    for num , n in enumerate(coumpines_listed):
        try:
            p = get_predecation(n,Interval.INTERVAL_1_MONTH)
            all_chart_list.update({n:p})
            if p['RECOMMENDATION'] == 'STRONG_BUY':
                stron_buy.append(n)
                db.child('data').child('stocks_data').child('Top_gainers_of_week').child(date.today()).child('Strong_buy').child(num).set(n)
            elif p['RECOMMENDATION'] == 'BUY':
                weak_buy.append(n)
                db.child('data').child('stocks_data').child('Top_gainers_of_week').child(date.today()).child('Week_buy').child(num).set(n)
            elif p['RECOMMENDATION'] == 'SELL':
                sell.append(n)
            elif p['RECOMMENDATION'] == 'NEUTRAL':
                neutral.append(n)
        except:
            print(f'error processing {n}')
            
        print(num)


    print(
        'Strong Buy',
        len(stron_buy),
        '\n',
        'Weak Buy',
        len(weak_buy),
        '\n',
        'sell',
        len(sell),
        '\n',
        'neutral',
        len(neutral)
    )
    print(
        'Strong Buy',
        stron_buy,
        '\n',
        'Weak Buy',
        weak_buy,
        '\n',
        'sell',
        sell,
        '\n',
        'neutral',
        neutral
    )
else:
    print('already updated')
    monday_tasks=db.child("data").child("stocks_data").child("Top_gainers_of_week").get()
    stockNum = list(dict(monday_tasks.val()[str(date.today())]['Strong_buy']))
    stron_buy = []
    for i in stockNum:
        stron_buy.append(dict(monday_tasks.val()[str(date.today())]['Strong_buy'])[i])
    print('update the data of strong buy')

print('***********************************************************************')

# 2 get the data of the each stock
print('***********************************************************************')
print('Strong Buy Stocka Are :')
print(stron_buy)
print('Total Number of Strong Buy Stocks : ',len(stron_buy))
print(len(stron_buy))
print('***********************************************************************')
i = 0
for p,n in enumerate(stron_buy):
    try:
        i = i + 1
        p = get_predecation(n,Interval.INTERVAL_1_WEEK)
        
        if p['RECOMMENDATION'] == 'STRONG_BUY':
            stron_buy_updated.append(n)
            db.child('data').child('stocks_data').child('Top_gainers_of_week').child('Top_gainers_of_mth').child(date.today()).child('Strong_buy').child(i).set(n)
            print(n,':','Strong Buy')
        elif p['RECOMMENDATION'] == 'BUY':
            weak_buy_updated.append(n)
            db.child('data').child('stocks_data').child('Top_gainers_of_week').child('Top_gainers_of_mth').child(date.today()).child('Week_buy').child(i).set(n)
            print(n,':','Weak Buy')

        
    except:
        print(f'error processing {n}')
        
    
print('uploaded the data')

# 3 seprate them to strong buy and weak buy

stron_buy = []
weak_buy = []
sell = []
neutral = []
all_chart_list = {}
coumpines_listed = []

price_chart = {}
for i in stron_buy:
    data = db.child('data').child('stocks_data').child('Top_gainers').child(date.today()).child(i).get()  # get the data of the stock
    #print('***********************')
    data = data.val()
    price_chart.update({data['company_name']:data['predecations']['RECOMMENDATION']})
    #print(price_chart)

for l in price_chart:
    #print(l)
    if price_chart[l] == 'STRONG_BUY':
        stron_buy.append(l)
    elif price_chart[l] == 'BUY':
        weak_buy.append(l)
    elif price_chart[l] == 'SELL':
        sell.append(l)
    elif price_chart[l] == 'NEUTRAL':
        neutral.append(l)
    else:
        pass

print('Strong Buy',stron_buy,'\n','Weak Buy',weak_buy,'\n','sell',sell,'\n','neutral',neutral)
# all_stock_codes = nse.get_stock_codes()
# for i in all_stock_codes:
#     coumpines_listed.append(i)
# coumpines_listed.remove('SYMBOL')
# print(coumpines_listed)
# print(len(coumpines_listed))
# for num , i in enumerate(coumpines_listed):
    
#     print(num,i)
#     if '-' in i:
#         i = i.replace('-','_')
#         coumpines_listed[num] = i
# for num , n in enumerate(coumpines_listed):
#     p = get_predecation(n,Interval.INTERVAL_1_WEEK)
#     all_chart_list.update({n:p})
#     if p['RECOMMENDATION'] == 'STRONG_BUY':
#         stron_buy.append(n)
#     elif p['RECOMMENDATION'] == 'BUY':
#         weak_buy.append(n)
#     elif p['RECOMMENDATION'] == 'SELL':
#         sell.append(n)
#     elif p['RECOMMENDATION'] == 'NEUTRAL':
#         neutral.append(n)
#     if num == 10:
#         break
    
#     else:
#         pass
#     print(num)


# print(
#     'Strong Buy',
#     len(stron_buy),
#     '\n',
#     'Weak Buy',
#     len(weak_buy),
#     '\n',
#     'sell',
#     len(sell),
#     '\n',
#     'neutral',
#     len(neutral)
# )
# print(
#     'Strong Buy',
#     stron_buy,
#     '\n',
#     'Weak Buy',
#     weak_buy,
#     '\n',
#     'sell',
#     sell,
#     '\n',
#     'neutral',
#     neutral
# )

    

# 4 get the data of the each stock
# 5 arrange them from low to high price of strong buy
