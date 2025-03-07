#region set up
from utilities import bs_spread
from datetime import datetime
import polygon
import fredapi
import pandas as pd
import os
import numpy as np
import math
from datetime import timedelta
import requests
import py_vollib.black_scholes.implied_volatility as iv
import sys
from datetime import timedelta
fred = fredapi.Fred(api_key=os.environ.get("fredapi_key"))
#688f94bd2d2ed0862a7bb29ce73d495f

# Fetch the latest Federal Funds Rate
fed_funds_rate = fred.get_series('DFF').tail(1)[0]
client=polygon.RESTClient(os.environ.get('polygon_api'))
r=fed_funds_rate/100
#endregion set up

now = datetime.now()
ticker=sys.argv[1]
symbol=client.get_last_quote(ticker)
S=round((symbol.ask_price+symbol.bid_price)/2,2)
print('\n')
print("Stock price for ticker: ", ticker, '=',S,'\n Original Spread')
expiration_date=sys.argv[2]
dte=((datetime.strptime(expiration_date,"%y%m%d")+timedelta(hours=16)) - now).days 
today_dte=(now.hour*60+now.minute) / (24*60)
T=(dte+today_dte)/ 365
option_type=sys.argv[3]
strike_1=float(sys.argv[4])
strike_2=float(sys.argv[5])
sigma_1=float(sys.argv[6])/100
sigma_2=float(sys.argv[7])/100
spread_price=bs_spread.bs_spread_price(strike_1, strike_2, sigma_1, sigma_2, S, r, T, option_type)

print('\n')
bs_spread.intraday_range(ticker)
print('\n')
offset=float(sys.argv[8])
print("Offset price: ", S+offset)
spread_price=bs_spread.bs_spread_price(strike_1, strike_2, sigma_1, sigma_2, S+offset, r, T, option_type)

print('\n')
const_vol=bs_spread.volatility(ticker)
print('With constant volatility. \n')
const_spread_price = bs_spread.bs_spread_price(strike_1, strike_2, const_vol, const_vol, S, r, T, option_type)