import pandas as pd
import yfinance as yf
from datetime import timedelta
from datetime import datetime

# gets the 
def get_ETF(interval):
    start = (datetime.now() - timedelta(366)).strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(1)).strftime("%Y-%m-%d")
    tickers = pd.read_csv('etfs.csv')['Symbol'].to_list()
    df = yf.download(tickers=tickers, start=start, end=end, interval=interval)
    return df


def RSI(n, df, less_threshold, more_threshold):
    delta = df.diff()
    dUp, dDown = delta.copy(), delta.copy()
    dUp[dUp < 0] = 0
    dDown[dDown > 0] = 0
    RollUp = dUp.rolling(n).mean()
    RollDown = dDown.rolling(n).mean().abs()
    RS = RollUp / RollDown
    RSI = 100 - 100 / (RS + 1)
    return RSI, RSI.iloc[-1,][RSI.iloc[-1,] < less_threshold], RSI.iloc[-1,][RSI.iloc[-1,] > more_threshold]