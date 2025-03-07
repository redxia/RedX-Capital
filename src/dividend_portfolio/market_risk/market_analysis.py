import pandas as pd
import numpy as np
import yfinance as yf
from utilities import utilities
historical=yf.download(['SPY','QQQ','^VIX','SVIX','ZVOL'], start='1990-01-01', end=utilities.next_business().strftime("%Y-%m-%d"))

def daily_returns(ticker='SPY'): #historical
    # historical=vix_adj_returns.copy()
    historical_daily=historical.copy()
    max_drawdown=historical_daily['Close'][ticker]/historical_daily['Close'][ticker].cummax() - 1
    max_drawup=historical_daily['Close'][ticker]/historical_daily['Low'][ticker].rolling(200).mean() - 1
    returns=historical_daily['Close'].pct_change()
    returns['VIX']=pd.qcut(historical_daily['Close']['^VIX'],5,[1,2,3,4,5])
    vix_cut=returns['VIX'].iloc[-1]
    vix_adj=returns['VIX']==vix_cut
    yoy_returns=historical_daily['Close'][ticker].pct_change(252)
    
    daily_return=pd.concat([historical['Close'][[ticker,'^VIX']],returns[[ticker,'^VIX','VIX']], yoy_returns, max_drawdown, max_drawup], axis=1)
    daily_return.columns=[ticker,'VIX','Daily Ret','VIX Ret','VIX Bucket','YoY Returns','Max Drawdown','Max Drawup 1yr']
    daily_return.reset_index(names='Date', inplace=True)
    daily_return.dropna(subset=ticker,inplace=True)
    daily_return['Date']=daily_return['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    daily_return.sort_values('Date', ascending=False, inplace=True)
    return daily_return

def monthly_returns(ticker='SPY'): 
    historical_m=historical.copy()['Close']
    # historical_m['Close']['VIX']
    historical_m['VIX']=pd.qcut(historical_m['^VIX'],5,[1,2,3,4,5])
    vix_cut=historical_m['VIX'].iloc[-1]
    vix_adj=historical_m['VIX']==vix_cut
    
    historical_m=historical_m.resample('M').ffill()
    vix_buckets=historical_m['VIX']
    del historical_m['VIX']  
    
    historical_high=historical.copy()['Close']
    historical_high=historical_high.resample('M').ffill()
    
    historical_low=historical.copy()['Close']
    historical_low=historical_low.resample('M').ffill()
    
    max_drawdown=historical_low[ticker]/historical_high[ticker].cummax() - 1
    max_drawup=historical_high[ticker]/historical_low[ticker].rolling(10).mean() - 1
    
    monthly_returns=historical_m.pct_change()
    monthly_returns['VIX']=vix_buckets
    yoy_returns=historical_m[ticker].pct_change(12)
    
    returns=pd.concat([historical_m[[ticker,'^VIX']],monthly_returns[[ticker,'^VIX','VIX']], yoy_returns, max_drawdown, max_drawup], axis=1)
    returns.columns=[ticker,'VIX','Monthly Ret','VIX Ret','VIX Bucket','YoY Returns','Max Drawdown','Max Drawup 1yr']
    returns.reset_index(names='Date', inplace=True)
    returns.dropna(subset=ticker,inplace=True)
    returns['Month']=returns['Date'].apply(lambda x: x.strftime('%m'))
    returns['Date']=returns['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    returns.sort_values('Date', ascending=False, inplace=True)
    return returns

def yearly_returns(ticker='SPY'): # historical
    historical_y=historical.copy()['Close']
    historical_y['VIX']=pd.qcut(historical_y['^VIX'],5,[1,2,3,4,5])
    vix_cut=historical_y['VIX'].iloc[-1]
    vix_adj=historical_y['VIX']==vix_cut
    
    historical_y=historical_y.resample('Y').ffill()
    vix_buckets=historical_y['VIX']
    del historical_y['VIX']  
    
    historical_high=historical.copy()['Close']
    historical_high=historical_high.resample('Y').ffill()
    
    historical_low=historical.copy()['Close']
    historical_low=historical_low.resample('Y').ffill()
    
    max_drawdown=historical_low[ticker]/historical_high[ticker].cummax() - 1
    max_drawup=historical_high[ticker]/historical_low[ticker].rolling(1).mean() - 1
    
    yearly_returns=historical_y.pct_change()
    yearly_returns['VIX']=vix_buckets
        
    returns=pd.concat([historical_y[[ticker,'^VIX']],yearly_returns[[ticker,'^VIX','VIX']], max_drawdown, max_drawup], axis=1)
    returns.columns=[ticker,'VIX','Yearly Ret','VIX Ret','VIX Bucket','Max Drawdown','Max Drawup 1yr']
    returns.reset_index(names='Date', inplace=True)
    returns.dropna(subset=ticker, inplace=True)
    returns['Date']=returns['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    returns.sort_values('Date', ascending=False, inplace=True)
    return returns

def daily_svix_returns(): #historical
    # historical=vix_adj_returns.copy()
    historical_daily=historical.copy()
    max_drawdown=historical_daily['Close']['SVIX']/historical_daily['Close']['SVIX'].cummax() - 1
    max_drawup=historical_daily['Close']['SVIX']/historical_daily['Low']['SVIX'].rolling(252).min() - 1
    returns=historical_daily['Close'].pct_change()
    returns['VIX']=pd.qcut(historical_daily['Close']['^VIX'],5,[1,2,3,4,5])
    vix_cut=returns['VIX'].iloc[-1]
    vix_adj=returns['VIX']==vix_cut
    yoy_returns=historical_daily['Close']['SVIX'].pct_change(252)
    
    daily_return=pd.concat([historical_daily['Close'][['SVIX','^VIX']],returns[['SVIX','^VIX','VIX']], yoy_returns, max_drawdown, max_drawup], axis=1)
    daily_return.columns=['SVIX','VIX','Daily Ret','VIX Ret','VIX Bucket','YoY Returns','Max Drawdown','Max Drawup 1yr']
    daily_return.reset_index(names='Date', inplace=True)
    daily_return.dropna(subset='SVIX', inplace=True)
    daily_return['Date']=daily_return['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    daily_return.sort_values('Date', ascending=False, inplace=True)
    return daily_return

def daily_ZVOL_returns(): #historical
    # historical=vix_adj_returns.copy()
    historical_daily=historical.copy()
    max_drawdown=historical_daily['Close']['ZVOL']/historical_daily['Close']['ZVOL'].cummax() - 1
    max_drawup=historical_daily['Close']['ZVOL']/historical_daily['Low']['ZVOL'].rolling(252).min() - 1
    returns=historical_daily['Close'].pct_change()
    returns['VIX']=pd.qcut(historical_daily['Close']['^VIX'],5,[1,2,3,4,5])
    vix_cut=returns['VIX'].iloc[-1]
    vix_adj=returns['VIX']==vix_cut
    yoy_returns=historical_daily['Close']['ZVOL'].pct_change(252)
    
    daily_return=pd.concat([historical_daily['Close'][['ZVOL','^VIX']],returns[['ZVOL','^VIX','VIX']], yoy_returns, max_drawdown, max_drawup], axis=1)
    daily_return.columns=['ZVOL','VIX','Daily Ret','VIX Ret','VIX Bucket','YoY Returns','Max Drawdown','Max Drawup 1yr']
    daily_return.reset_index(names='Date', inplace=True)
    daily_return.dropna(subset='ZVOL', inplace=True)
    daily_return['Date']=daily_return['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    daily_return.sort_values('Date', ascending=False, inplace=True)
    return daily_return