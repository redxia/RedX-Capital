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
    return RSI, RSI.iloc[-1:,] # could return the last few rsi to look at

# look back is the rsi period. interval is the timing. 30 stands for hourly
def get_RSI_AlphaRisk(data, tickers, interval=30, look_back=14, moving_alpha_risk=252):
    rsi = dict((x,[]) for x in tickers)
    rsi_last = dict((x,[]) for x in tickers)
    alphas = dict((x,[]) for x in tickers)
    alphas_last = dict((x,[]) for x in tickers)
    risks = dict((x,[]) for x in tickers)
    risks_last = dict((x,[]) for x in tickers)
    df_combine = dict((x,[]) for x in tickers)
    df_combine_last = dict((x,[]) for x in tickers)

    for i in tickers:
        temp = pd.DataFrame(
            data[i]['Adj Close'],
            index=pd.to_datetime(data[i]['Date']), 
            columns=[i]
            )
        temp.index = temp.index.rename('Date')
        temp = temp.between_time('9:30','16:00')
        if interval==60:
            temp = temp[temp.index.minute == interval / 2]
            if ((temp.index.to_series().diff()[-1] == pd.Timedelta('0 days 01:00:00')) or \
                (temp.index.to_series().diff()[-1] == pd.Timedelta('0 days 18:00:00')) or \
                (temp.index.to_series().diff()[-1] == pd.Timedelta('2 days 18:00:00'))) and \
                ((temp.index.to_series()[-1].strftime('%Y-%m-%d') == datetime.today().strftime('%Y-%m-%d')) or \
                 (temp.index.to_series()[-1].strftime('%Y-%m-%d') == (datetime.today()-timedelta(days=2)).strftime('%Y-%m-%d')) or \
                 (temp.index.to_series()[-1].strftime('%Y-%m-%d') == (datetime.today()-timedelta(days=3)).strftime('%Y-%m-%d'))):
                rsi[i], rsi_last[i] = RSI(look_back, temp)
                risks[i] = (temp.pct_change().rolling(moving_alpha_risk).std() * (14 * 252)**.5 * 100) # annualizing
                risks_last[i] = (temp.pct_change().rolling(moving_alpha_risk).std() * (14 * 252)**.5 * 100).iloc[-1:,]

                alpha = ((temp.rolling(moving_alpha_risk).quantile(.925) / temp - 1) + \
                         (temp.rolling(moving_alpha_risk).min() / temp - 1)) * 100
                alphas[i] = alpha
                alphas_last[i] = alpha.iloc[-1:,]
            else:
                rsi[i], rsi_last[i] = pd.Series(), pd.Series()
                alphas[i], alphas_last[i] = pd.Series(), pd.Series()
                risks[i], risks_last[i] = pd.Series(), pd.Series()
        elif interval==30:
            temp = temp[np.logical_or(temp.index.minute == interval, temp.index.minute == 0)]
            # 18:00:00 takes care of missing day close data, aka the 4:00PM
            if ((temp.index.to_series().diff()[-1] == pd.Timedelta('0 days 00:30:00')) or \
                (temp.index.to_series().diff()[-1] == pd.Timedelta('0 days 17:30:00')) or \
                (temp.index.to_series().diff()[-1] == pd.Timedelta('0 days 18:00:00')) or \
                (temp.index.to_series().diff()[-1] == pd.Timedelta('2 days 17:30:00')) or \
                (temp.index.to_series().diff()[-1] == pd.Timedelta('2 days 18:00:00'))) and \
                ((temp.index.to_series()[-1].strftime('%Y-%m-%d') == datetime.today().strftime('%Y-%m-%d')) or \
                 (temp.index.to_series()[-1].strftime('%Y-%m-%d') == (datetime.today()-timedelta(days=2)).strftime('%Y-%m-%d')) or \
                 (temp.index.to_series()[-1].strftime('%Y-%m-%d') == (datetime.today()-timedelta(days=3)).strftime('%Y-%m-%d'))):
                rsi[i], rsi_last[i] = RSI(look_back, temp)
                risks[i] = (temp.pct_change().rolling(moving_alpha_risk).std() * (14 * 252)**.5 * 100) # annualizing
                risks_last[i] = (temp.pct_change().rolling(moving_alpha_risk).std() * (14 * 252)**.5 * 100).iloc[-1:,]

                alpha = ((temp.rolling(moving_alpha_risk).quantile(.95) / temp - 1) + \
                         (temp.rolling(moving_alpha_risk).min() / temp - 1)) * 100
                alphas[i] = alpha
                alphas_last[i] = alpha.iloc[-1:,]
            else:
                rsi[i], rsi_last[i] = pd.Series(), pd.Series()
                alphas[i], alphas_last[i] = pd.Series(), pd.Series()
                risks[i], risks_last[i] = pd.Series(), pd.Series()
        rsi[i]['alpha'] = alphas[i]
        rsi[i]['risk'] = risks[i]
        rsi[i].columns = ['rsi','alpha','risk']
        df_combine[i] = rsi[i]
        rsi_last[i]['alpha'] = alphas_last[i]
        rsi_last[i]['risk'] = risks_last[i]
        rsi_last[i].columns = ['rsi','alpha','risk']
        df_combine_last[i] = rsi_last[i]
    return df_combine, df_combine_last

