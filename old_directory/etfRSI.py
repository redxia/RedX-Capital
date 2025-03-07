import pandas as pd
#%load_ext autoreload
#%autoreload 2
from util import utilities as util

df = util.get_ETF("60m")
df.head()
df = df.rename_axis(columns=['OHLCV','Symbol'])
close = df['Adj Close']
rsi, rsi_low, rsi_high = util.RSI(23, close, 40, 60)
rsi_high
rsi_low

low_rsi = pd.DataFrame(rsi_low[rsi_low<20].index)
tickers = pd.read_csv('etfs.csv')
#tickers.columns=['Ticker','Name']
tickers.head()
low_rsi.merge(tickers, how='left', on='Symbol')

# close = df['Adj Close']
# na = (close / close.shift() - 1).isna().sum()
# na = na[na > 2]
# close = close.drop(columns=na.index.tolist())
# returns = (close / close.shift() - 1).dropna()