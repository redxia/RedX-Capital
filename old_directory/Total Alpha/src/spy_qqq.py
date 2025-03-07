import pandas as pd
import yfinance as yf
from datetime import datetime
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
import os
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from pypfopt import EfficientFrontier
import numpy as np
from datetime import timedelta
import time

def rolling_ols(df : pd.DataFrame, y : str, x : str= "SPY"):
    print(y)
    ols_df=df[[x, y]]
    ols_df=sm.add_constant(ols_df)
    model = RollingOLS(endog=ols_df[y], exog=ols_df[['const', x]], window=21*4)
    fit = model.fit()
    results=fit.params
    results.columns=['alpha','beta']
    results['Symbol']=y
    results['alpha'] = results['alpha'] * 252
    return results

api_key=os.environ.get("polygon_api")
async def get_market_cap(session, ticker : str='AAPL'):
    url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apikey={api_key}"
    params = {"apiKey": os.environ.get("polygon_api")}
    async with session.get(url) as response:
        # response = requests.get(url, params=params)
        if response.status == 200:
            data =await response.json()
            time.sleep(0.05)
            market_cap = data.get("results", {}).get("market_cap")
            return market_cap
    return 0

def get_qqq():
    qqq=pd.read_csv(r"https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/0?audienceType=Investor&action=download&ticker=QQQ")
    qqq.rename(columns={'Holding Ticker':'Ticker'}, inplace=True)
    qqq['Ticker']=qqq['Ticker'].str.strip()
    qqq['MarketValue']=qqq['MarketValue'].str.replace(",",'').astype(float)
    qqq['Shares/Par Value']=qqq['Shares/Par Value'].str.replace(",",'').astype(float)
    qqq=qqq.loc[qqq['Ticker']!='GOOG',:]
    return qqq

def get_spy():
    spy=pd.read_excel(r"https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx", skiprows=4).dropna()
    spy=spy.loc[spy['Ticker']!='GOOG',:]
    return spy

async def concat_spy_qqq():
    # try:
    qqq=get_qqq()
    spy=get_spy()
    # except:
    #     return
    not_in_spy=qqq.loc[~qqq['Ticker'].isin(spy['Ticker'].to_list())]

    tickers=spy['Ticker'].to_list()
    try:
        tickers.remove('-')
    except:
        pass
    tickers.extend(not_in_spy['Ticker'].to_list())

    connector=aiohttp.TCPConnector(limit = 60)
    async with aiohttp.ClientSession(connector=connector) as session:
        task = [get_market_cap(session, ticker) for ticker in tickers]
        market_cap=await asyncio.gather(*task)

    total_index=pd.DataFrame({"Tickers":tickers,'Market Cap':market_cap})
    total_index['Weight']=total_index['Market Cap'] / total_index['Market Cap'].sum()
    total_index.sort_values('Weight', ascending=False, inplace=True)
    total_index.sort_values('Tickers', ascending=True, inplace=True)
    total_index['Tickers']=total_index['Tickers'].str.replace(".",'-')
    # minus 2 + 5

    ticker_spy=total_index['Tickers'].to_list()
    ticker_spy.append('SPY')
    today=datetime.now()
    data=yf.download(ticker_spy, start=(today-timedelta(days=365*10)).strftime("%Y-%m-%d"),end=(today+timedelta(days=1)).strftime("%Y-%m-%d"))
    returns=data['Close'].pct_change().dropna(axis=1, how='all')
  
    def process_ticker(ticker):
        try:
            return rolling_ols(returns, ticker)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            return None
        
    alpha_beta_matrix=pd.DataFrame()
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_ticker, total_index['Tickers'].to_list())
    alpha_beta_matrix = pd.concat([result for result in results if result is not None])

    alpha_beta_matrix=alpha_beta_matrix.reset_index(names='Date')
    alpha_beta_matrix['Exp Ret']=alpha_beta_matrix['alpha'] + alpha_beta_matrix['beta'] * 0.12

    alpha=alpha_beta_matrix.pivot_table(values='alpha', columns='Symbol', index='Date')
    alpha=alpha.clip(lower=alpha.quantile(0.025),upper=alpha.quantile(0.975), axis=1)
    # alpha.plot(figsize=(16,14), legend=False)

    latest_alpha=alpha.T.iloc[:,-1].reset_index()
    latest_alpha.columns=['Tickers','alpha']
    total_index=total_index.merge(latest_alpha, on='Tickers', how='left')

    # alpha[latest_alpha.index].plot(figsize=(16,12), legend=False)

    beta=alpha_beta_matrix.pivot_table(values='beta', columns='Symbol', index='Date')
    beta=beta.clip(lower=beta.quantile(0.025),upper=beta.quantile(0.975), axis=1)
    # beta.plot(figsize=(16,14), legend=False)

    # latest_beta=beta.iloc[-1,:]
    # latest_beta.sort_values(ascending=False, inplace=True)
    # latest_beta=latest_beta[latest_beta>.7]
    
    latest_beta=beta.T.iloc[:,-1].reset_index()
    latest_beta.columns=['Tickers','beta']
    total_index=total_index.merge(latest_beta, on='Tickers', how='left')

    exp_ret=alpha_beta_matrix.pivot_table(values='Exp Ret', columns='Symbol', index='Date')
    exp_ret=exp_ret.clip(lower=exp_ret.quantile(0.025),upper=exp_ret.quantile(0.975), axis=1)
    # exp_ret.plot(figsize=(16,14), legend=False)
    
    latest_exp_return=exp_ret.T.iloc[:,-1].reset_index()
    latest_exp_return.columns=['Tickers','mu']
    total_index=total_index.merge(latest_exp_return, on='Tickers', how='left')

    return total_index, returns, alpha_beta_matrix, alpha, exp_ret, beta
    

