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
fred = fredapi.Fred(api_key=os.environ.get("fredapi_key"))

# Fetch the latest Federal Funds Rate
fed_funds_rate = fred.get_series('DFF').tail(1)[0]
client=polygon.RESTClient('LBoNgqc59G4RKRZsQVNCyfOsf3C2CTjd')
r=fed_funds_rate/100
#endregion set up

now = datetime.now()
market_close = datetime(now.year, now.month, now.day, 16, 0, 0)
today_dte=int((market_close-now).total_seconds() / 60) / 390
today_dte=int((market_close-now).total_seconds() / 60) / 390
dte=10
VXX=client.get_last_quote('VXX')
SVXY=client.get_last_quote('SVXY')


#region vix
#decay factor Daily .24%
# 5 day -1.19%
# 10 days -2.426%
# 21 days -4.91%

# VXX
expiration_date="230428"
K_1, K_2 = 39, 39.5
sigma_1, sigma_2 = 0.4457, 0.4698
S = round((VXX.bid_price+VXX.ask_price)/2,2)
t = (dte+today_dte)/252
option_type = "Put"
VXX_Vol=bs_spread.volatility('VXX')
print("VXX Volatility: ", round(VXX_Vol,4))
spread_price=bs_spread.bs_spread_price(K_1, K_2, sigma_1, sigma_2, S, r, t, option_type)
spread_price_const_vol=bs_spread.bs_spread_price(K_1, K_2, VXX_Vol, VXX_Vol, S, r, t, option_type)
bs_spread.intraday_range("VXX")

#boost factor Daily .12%
# 5 day .6%
# 10 days 1.213%
# 21 days 2.46%

#SVXY

K_1, K_2 = 68, 68.5
sigma_1, sigma_2 = 0.237, 0.2228
S = round((SVXY.bid_price+SVXY.ask_price)/2,2)
t = (dte + today_dte)/252
option_type = "Call"
SVXY_Vol=bs_spread.volatility('SVXY')
print("SVXY Volatility: ", round(SVXY_Vol,4))
spread_price=bs_spread.bs_spread_price(K_1, K_2, sigma_1, sigma_2, S, r, t, option_type)
spread_price_const_vol=bs_spread.bs_spread_price(K_1, K_2, SVXY_Vol, SVXY_Vol, S, r, t, option_type)
bs_spread.intraday_range("SVXY")
#endregion VIX

expiration_date="230526"
option_type='P'
symbol="QQQ"
strike_1=302
strike_2=302.5
QQQ=client.get_last_quote('QQQ')
S=round((QQQ.ask_price+QQQ.bid_price)/2,2)
dte=(datetime.strptime(expiration_date,"%y%m%d") - now).days 
today_dte=(now.hour*60+now.minute) / (24*60)
T=(dte+today_dte)/ 365

bs_spread.intraday_range("QQQ")
option1_price = client.get_last_trade("O:{symbol}{date}{type}00{strike}".format(symbol=symbol, date=expiration_date, 
                                                                                 type=option_type, strike=str(int(strike_1*1000)))).price
option2_price = client.get_last_trade("O:{symbol}{date}{type}00{strike}".format(symbol=symbol, date=expiration_date, 
                                                                                 type=option_type, strike=str(int(strike_2*1000)))).price

implied_vol1 = iv.implied_volatility(option1_price, S, strike_1, T, r, option_type.lower())
implied_vol1 = .242
implied_vol2 = iv.implied_volatility(option2_price, S, strike_2, T, r, option_type.lower())
implied_vol2 = .241
spread_price=bs_spread.bs_spread_price(strike_1, strike_2, implied_vol1, implied_vol2, S, r, T, option_type)
spread_price=bs_spread.bs_spread_price(strike_1, strike_2, implied_vol1, implied_vol2, S+3, r, T, option_type)

#TODO just write  batch program to enter answer so it will pring it out