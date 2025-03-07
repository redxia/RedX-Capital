import pandas as pd
import yfinance as yf
from datetime import timedelta
from datetime import datetime
import numpy as np

indicies_path = '..\data\indicies'
columns = ['Date','Adj Close']

def read_tickers(file='sp100'):
    if file == 'sp100':
        df = pd.read_csv(indicies_path + '\sp100_tickers.csv')['Symbol'].to_list()
    elif file == 'nasdaq':
        df = pd.read_csv(indicies_path + '\sp500_minus_nasdaq.csv')['Symbol'].to_list()
    elif file == 'nyse':
        df = pd.read_csv(indicies_path + '\_nyse100_tickers.csv')['Symbol'].to_list()
    elif file == 'etfs':
        df = pd.read_csv(indicies_path + '\etfs.csv')['Symbol'].to_list()
    elif file == 'sp100_diff':
        df = pd.read_csv(indicies_path + '\sp100_minus_NYSE_NASDAQ.csv')['Symbol'].to_list()
    elif file == 'dji':
        df = pd.read_csv(indicies_path + '\dji_tickers.csv')['Symbol'].to_list()
    elif file == 'sp500':
        df = pd.read_csv(indicies_path + '\sp500_tickers.csv')['Symbol'].to_list()
    elif file == 'russ1k':
        df = pd.read_csv(indicies_path + '\\russ1000_tickers.csv')['Symbol'].to_list()
    elif file == 'sp500_diff':
        df = pd.read_csv(indicies_path + '\sp500_minus_russ1k.csv')['Symbol'].to_list()
    elif file == 'roth':
        df = pd.read_csv(indicies_path + '\Roth.csv')['Symbol'].to_list()
    elif file=='crypto':
        df = pd.read_csv(indicies_path + '\crypto.csv')['Symbol'].to_list()
    return df

def get_close(barset, tickers, limit=1000):
    data = dict((x,dict((y,[]) for y in columns)) for x in tickers)
    for i in tickers:
        if len(barset[i]) >= 300: 
            # enforces full data
            for j in range(len(barset[i])):
                data[i]['Adj Close'].append(barset[i][j].c)
                data[i]['Date'].append(
                    datetime.strptime(
                        barset[i][j].t.strftime(
                            '%Y-%m-%d %H:%M:%S'
                            ), 
                            '%Y-%m-%d %H:%M:%S')
                )
    return data

# Helper function for getting rsi
def RSI(n, df):
    delta = df.diff()
    dUp, dDown = delta.copy(), delta.copy()
    dUp[dUp < 0] = 0
    dDown[dDown > 0] = 0
    RollUp = dUp.rolling(n).mean() # could use EWMA
    RollDown = dDown.rolling(n).mean().abs() # EWMA
    RS = RollUp / RollDown
    RSI = 100 - (100 / (RS + 1.0))
    RSI=pd.concat([df,RSI], axis=1)
    return RSI, RSI.iloc[-1:,] # could return the last few rsi to look at

