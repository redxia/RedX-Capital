import pandas as pd
import yfinance as yf
import os
from datetime import datetime
import time
from statsmodels.regression.rolling import RollingOLS
import pandas_ta as pta
import statsmodels.api as sm
from datetime import timedelta
import numpy as np
stock_path=r"C:\RedXCapital\Dividends\Data\Symbol"
market_path=r"C:\RedXCapital\Dividends\Data\Market Data"

def rolling_ols(df1,df2,window):
    df2.rename(columns={'Returns':"Mkt_Ret"}, inplace=True)
    beta=df1.merge(df2[["Date","Mkt_Ret"]],on="Date",how='left')
    beta['Returns']=beta['Returns'].astype(float)
    beta['Mkt_Ret']=beta['Mkt_Ret'].astype(float) 
    
    beta_model=RollingOLS(endog=beta['Returns'].values, exog=sm.add_constant(beta['Mkt_Ret']), window=window, missing="drop", min_nobs=5, expanding=True)        
    beta_fit=beta_model.fit()
    return beta_fit.params['Mkt_Ret'].values, beta_fit.rsquared.values

def rolling_hedge_ratio(df1,df2,window):
    df1.rename(columns={'Returns':"Mkt_Ret"}, inplace=True)
    beta=df1.merge(df2[["Date","Returns"]],on="Date",how='left')
    beta['Returns']=beta['Returns'].astype(float)
    beta['Mkt_Ret']=beta['Mkt_Ret'].astype(float) 
    
    beta_model=RollingOLS(endog=beta['Returns'].values, exog=sm.add_constant(beta['Mkt_Ret']), window=window, missing="drop", min_nobs=5, expanding=True)        
    beta_fit=beta_model.fit()
    return beta_fit.params['Mkt_Ret'].values, beta_fit.rsquared.values

def rolling_multiOLS(df1,df2,window):
    df2.rename(columns={'Returns':"Mkt_Ret"}, inplace=True)
    beta=df1.merge(df2[["Date","Mkt_Ret"]],on="Date",how='left')
    beta['Returns']=beta['Returns'].astype(float)
    beta['Mkt_Ret']=beta['Mkt_Ret'].astype(float)

    momentum=pd.read_csv(market_path+'\\'+'MTUM.csv')
    momentum.rename(columns={'Returns':'Mom_Ret'}, inplace=True)
    volatility=pd.read_csv(market_path+'\\'+'USMV.csv')
    volatility.rename(columns={'Returns':"Vol_Ret"}, inplace=True)
    quality=pd.read_csv(market_path+'\\'+'QUAL.csv')    
    quality.rename(columns={'Returns':'Qual_Ret'},inplace=True)

    beta=beta.merge(momentum[['Date','Mom_Ret']], on='Date',how='left')
    beta=beta.merge(volatility[['Date','Vol_Ret']], on='Date',how='left')
    beta=beta.merge(quality[['Date','Qual_Ret']], on='Date',how='left')
    beta_model=RollingOLS(endog=beta['Returns'].values, exog=sm.add_constant(beta[['Mkt_Ret','Mom_Ret','Vol_Ret','Qual_Ret']]), window=window, missing="drop", min_nobs=5, expanding=True)
    beta_fit=beta_model.fit()
    beta_parameters=beta_fit.params
    beta_parameters.rename(columns={'const':'alpha'}, inplace=True)
    return beta_parameters,beta_fit.rsquared.values

def rolling_delta(df1,df2,window):
    df1.rename(columns={'Close':"Mkt_Close"}, inplace=True)
    beta=df1.merge(df2[["Date","Close"]],on="Date",how='left')
    beta['Close']=beta['Close'].astype(float)
    beta['Mkt_Close']=beta['Mkt_Close'].astype(float) 
    
    beta_model=RollingOLS(endog=beta['Close'].values, exog=sm.add_constant(beta['Mkt_Close']), window=window, missing="drop", min_nobs=5, expanding=True)        
    beta_fit=beta_model.fit()
    return beta_fit.params['Mkt_Close'].values, beta_fit.rsquared.values

def stock_properties(ticker, path, historical=''):
    if path==market_path:
        return
    if type(historical)==str:
        historical=pd.read_csv(path+'\\'+ticker+'.csv')
    dividends=pd.read_excel("master_file.xlsx", sheet_name="Master")
    
    market=pd.read_csv(market_path+'\\'+dividends.loc[dividends['Symbol']==ticker,'Sector ETF'].values[0]+'.csv')
    momentum=pd.read_csv(market_path+'\\'+'MTUM.csv')
    volatility=pd.read_csv(market_path+'\\'+'USMV.csv')
    quality=pd.read_csv(market_path+'\\'+'QUAL.csv')
    hedge=pd.read_csv(market_path+'\\'+dividends.loc[dividends['Symbol']==ticker,'Hedge ETF'].values[0]+'.csv')
    second_hedge=pd.read_csv(market_path+'\\'+dividends.loc[dividends['Symbol']==ticker,'Second Hedge ETF'].values[0]+'.csv')
    
    historical['ADV_20']=historical['Volume'].rolling(20).mean()
    historical['Dollar_ADV_20']=historical['Close']*historical['ADV_20']
    historical['B_Mkt_3mo'],historical['R2_Mkt_3mo']=rolling_ols(historical.copy(),market.copy(), 21*3) # four months of historical data
    historical['B_Mom_3mo'],historical['R2_Mom_3mo']=rolling_ols(historical.copy(),momentum.copy(), 21*3) # four months of historical data
    historical['B_Vol_3mo'],historical['R2_Vol_3mo']=rolling_ols(historical.copy(),volatility.copy(), 21*3) # four months of historical data
    historical['B_Qual_3mo'],historical['R2_Qual_3mo']=rolling_ols(historical.copy(),quality.copy(), 21*3) # four months of historical data
    historical['B_Hedge_3mo'],historical['R2_Hedge_3mo']=rolling_hedge_ratio(historical.copy(),hedge.copy(), 21*3) # four months of historical data
    historical['B_SHedge_3mo'],historical['R2_SHedge_3mo']=rolling_hedge_ratio(historical.copy(),second_hedge.copy(), 21*3) # four months of historical data
    try:
        historical['B_Mkt_1yr'],historical['R2_Mkt_1yr']=rolling_ols(historical.copy(),market.copy(), 21*12) # 1yr of historical data
    except:
        historical['B_Mkt_1yr'],historical['R2_Mkt_1yr']=rolling_ols(historical.copy(),market.copy(), 21) # 1yr of historical data
    try:
        historical['B_Mom_1yr'],historical['R2_Mom_1yr']=rolling_ols(historical.copy(),momentum.copy(), 21*12) # 1yr of historical data
    except:
        historical['B_Mom_1yr'],historical['R2_Mom_1yr']=rolling_ols(historical.copy(),momentum.copy(), 21) # 1yr of historical data
    try:        
        historical['B_Vol_1yr'],historical['R2_Vol_1yr']=rolling_ols(historical.copy(),volatility.copy(), 21*12) # 1yr of historical data
    except:
        historical['B_Vol_1yr'],historical['R2_Vol_1yr']=rolling_ols(historical.copy(),volatility.copy(), 21) # 1yr of historical data
    try:        
        historical['B_Qual_1yr'],historical['R2_Qual_1yr']=rolling_ols(historical.copy(),quality.copy(), 21*12) # 1yr of historical data       
    except:
        historical['B_Qual_1yr'],historical['R2_Qual_1yr']=rolling_ols(historical.copy(),quality.copy(), 21) # 1yr of historical data               
    try:
        historical['B_Hedge_1yr'],historical['R2_Hedge_1yr']=rolling_hedge_ratio(historical.copy(),hedge.copy(), 21*12) # four months of historical data
    except:
        historical['B_Hedge_1yr'],historical['R2_Hedge_1yr']=rolling_hedge_ratio(historical.copy(),hedge.copy(), 21) # four months of historical data        
    try:
        historical['B_Mkt_Delta'],historical['R2_Mkt_Delta']=rolling_delta(historical.copy(),market.copy(), 21*12) # 1yr of historical data # the amount of $ move based on market
    except:
        historical['B_Mkt_Delta'],historical['R2_Mkt_Delta']=rolling_ols(historical.copy(),market.copy(), 21*2) # 6 months of historical data
    historical["RSI_7"]=pta.rsi(historical['Close'], length=7) 
    historical['RSI_21']=pta.rsi(historical['Close'], length=21) 
    historical['AvgRet_10']=historical['Returns'].rolling(10, min_periods=5).mean()
    historical['AvgRet_42']=historical['Returns'].rolling(42, min_periods=5).mean()
    try:
        historical['AvgRet_1yr']=historical['Returns'].rolling(21*12, min_periods=5).mean()
    except:
        historical['AvgRet_1yr']=historical['Returns'].rolling(5, min_periods=5).mean()
    historical['STD_10']=historical['Returns'].rolling(10, min_periods=5).std()
    historical['STD_42']=historical['Returns'].rolling(42, min_periods=5).std()
    historical['STD_1yr']=historical['Returns'].rolling(21*12, min_periods=5).std()
    historical['Returns_10']=historical['Close'].pct_change(10)
    historical['Returns_42']=historical['Close'].pct_change(42)
    try:
        historical['Returns_1yr']=historical['Close'].pct_change(21*12)        
    except:
        historical['Returns_1yr']=historical['Close'].pct_change(21)        

    if historical.shape[0] >= 21*3:
        historical[['alpha','Mkt_Beta_3mo','Mom_Beta_3mo','Vol_Beta_3mo','Qual_Beta_3mo']],historical['R2_multi_ols_3mo']=rolling_multiOLS(historical.copy(),market.copy(), 21*3) # four months of historical data
    else:
        historical[['alpha','Mkt_Beta_3mo','Mom_Beta_3mo','Vol_Beta_3mo','Qual_Beta_3mo']],historical['R2_multi_ols_3mo']=rolling_multiOLS(historical.copy(),market.copy(), 21) # four months of historical data
    try:
        historical[['alpha','Mkt_Beta_1yr','Mom_Beta_1yr','Vol_Beta_1yr','Qual_Beta_1yr']],historical['R2_multi_ols_1yr']=rolling_multiOLS(historical.copy(),market.copy(), 21*12) # four months of historical data
    except:
        historical[['alpha','Mkt_Beta_1yr','Mom_Beta_1yr','Vol_Beta_1yr','Qual_Beta_1yr']],historical['R2_multi_ols_1yr']=rolling_multiOLS(historical.copy(),market.copy(), 21) # four months of historical data
    historical.to_csv(path+'\\'+ticker+'.csv',index=False)
    return historical
