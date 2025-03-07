%load_ext autoreload
%autoreload 2
#import matplotlib.dates as mdates
#ax.xaxis.set_major_locator(mdates.MonthLocator())
import os
import fredapi
import pandas as pd
from datetime import timedelta
import yfinance as yf
from utilities import utilities
from utilities import market_util
import numpy as np
#import matplotlib.pyplot as plt
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
pandas2ri.activate()

#fig, ax2 = plt.subplots()
stats=importr('stats')
forecast=importr('forecast')
# base=importr('base')
fredapi_key=os.environ.get("fredapi_key")

sp500=yf.download('^GSPC', auto_adjust=True,actions=True, period='max', progress=False)[['Close','Volume','Dividends']]
fred=fredapi.Fred(api_key=fredapi_key)
# list of relevant data series to for loop the download
t10yr_t2yr=fred.get_series_latest_release('T10Y2Y')
sp500=utilities.add_to_df(t10yr_t2yr,'t10yr_t2yr', sp500, interpolation=True)
sp500['Close_ewma']=sp500['Close'].ewm(3).mean()
sp500.dropna(inplace=True)
sp500=market_util.get_returns(sp500,'daily', ewma=True)
t10yr_t2yr_model=stats.ar(sp500['t10yr_t2yr'],order_max=1)
predicted_t10yr_t2yr=forecast.forecast_ar(t10yr_t2yr_model,h=252)
predicted_t10yr_t2yr_adj=(predicted_t10yr_t2yr[3]+predicted_t10yr_t2yr[4][:,0])/2

df_regression=sp500.loc[sp500['returns_12mo'].notna(),['returns_12mo','t10yr_t2yr']].iloc[-(18*21):]
sp500_model=stats.lm('returns_12mo~t10yr_t2yr',data=df_regression)

sp500.to_csv('sp500_t10y_t2y.csv', index=False)


spy=yf.download('SPY', auto_adjust=True,actions=True, period='max', progress=False)[['Close','Volume','Dividends']]
fed_funds=fred.get_series_latest_release('FEDFUNDS')
fed_funds=fed_funds.append(pd.Series([4.25], index=[(fed_funds.index[-1]+timedelta(days=32)).replace(day=1)]))
spy=utilities.add_to_df(fed_funds, 'fedfunds', spy, interpolation=False)

#spy['fedfunds']=spy['fedfunds'].interpolate()
#spy=spy.ffill()
#spy=spy.bfill()
spy['spy_returns']=spy['Close'].pct_change()
spy['spy_returns_3mo']=spy['Close'].pct_change(3)
spy['spy_returns_6mo']=spy['Close'].pct_change(6)
spy['spy_returns_9mo']=spy['Close'].pct_change(9)
spy['spy_returns_12mo']=spy['Close'].pct_change(12)
spy['spy_returns_18mo']=spy['Close'].pct_change(18)
spy['spy_returns_24mo']=spy['Close'].pct_change(24)
spy=spy.dropna()

M1=fred.get_series_latest_release('M1SL')

M1=fred.get_series_latest_release('M1SL')
M1=pd.DataFrame({"Date":M1.index,"M1":M1.values})
M1['Date']=M1['Date']-timedelta(days=1)

sp500_monthly=pd.read_csv("sp500_monthly.csv")
sp500_monthly=sp500_monthly[["Date","Adjusted"]]
sp500_monthly['Date']=pd.to_datetime(sp500_monthly['Date'])

sp500_monthly=sp500_monthly.merge(M1,on="Date", how='left')

M1['Date']=M1['Date']-timedelta(days=1)
sp500_monthly=sp500_monthly.merge(M1,on="Date", how='left')
sp500_monthly.rename(columns={'M1_x':'M1'}, inplace=True)
sp500_monthly.loc[sp500_monthly['M1_y'].notna(),"M1"]=sp500_monthly.loc[sp500_monthly['M1_y'].notna(),"M1_y"]
del sp500_monthly['M1_y']

M1['Date']=M1['Date']-timedelta(days=1)
sp500_monthly=sp500_monthly.merge(M1,on="Date", how='left')
sp500_monthly.rename(columns={'M1_x':'M1'}, inplace=True)
sp500_monthly.loc[sp500_monthly['M1_y'].notna(),"M1"]=sp500_monthly.loc[sp500_monthly['M1_y'].notna(),"M1_y"]
del sp500_monthly['M1_y']

M1['Date']=M1['Date']-timedelta(days=1)
sp500_monthly=sp500_monthly.merge(M1,on="Date", how='left')
sp500_monthly.rename(columns={'M1_x':'M1'}, inplace=True)
sp500_monthly.loc[sp500_monthly['M1_y'].notna(),"M1"]=sp500_monthly.loc[sp500_monthly['M1_y'].notna(),"M1_y"]
del sp500_monthly['M1_y']

sp500_monthly.dropna().to_csv("sp500_m1.csv", index=False)

#yearly
sp500_yearly=pd.read_csv("sp500_yearly.csv")
sp500_yearly=sp500_yearly[["Date","Adjusted"]]
sp500_yearly['Date']=pd.to_datetime(sp500_yearly['Date'])

sp500_yearly=sp500_yearly.merge(M1,on="Date", how='left')

M1['Date']=M1['Date']-timedelta(days=1)
sp500_yearly=sp500_yearly.merge(M1,on="Date", how='left')
sp500_yearly.rename(columns={'M1_x':'M1'}, inplace=True)
sp500_yearly.loc[sp500_yearly['M1_y'].notna(),"M1"]=sp500_yearly.loc[sp500_yearly['M1_y'].notna(),"M1_y"]
del sp500_yearly['M1_y']

M1['Date']=M1['Date']-timedelta(days=1)
sp500_yearly=sp500_yearly.merge(M1,on="Date", how='left')
sp500_yearly.rename(columns={'M1_x':'M1'}, inplace=True)
sp500_yearly.loc[sp500_yearly['M1_y'].notna(),"M1"]=sp500_yearly.loc[sp500_yearly['M1_y'].notna(),"M1_y"]
del sp500_yearly['M1_y']
sp500_yearly.dropna().to_csv("sp500_m1_yearly.csv", index=False)
