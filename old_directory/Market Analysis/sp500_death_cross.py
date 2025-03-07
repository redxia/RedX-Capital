# This is four hours version. can look at 2 hours.
# %load_ext autoreload
# %autoreload 2
import os
import pandas as pd
import yfinance as yf

sp500=yf.download('SPY', auto_adjust=True,actions=True, period='max', progress=False)[['Close','Volume','Dividends']]
sp500.reset_index(inplace=True)


print('\n \n \n', "MACD Cross 6_13_30: \n")
sp500['MA_6']=sp500['Close'].rolling(6).mean()
sp500['MA_13']=sp500['Close'].rolling(13).mean()
sp500['MA6_MA13']=sp500['MA_6']-sp500['MA_13']

print('MACD Cross and crosses the 30day MA. \n')

if sp500['MA_6'].iloc[-1]>sp500['MA_13'].iloc[-1]:
    print('MACD Bull Cross!: \n',sp500[['Date','MA6_MA13']].tail(21),'\n')
else:
    print('MACD Bear Cross!: \n',sp500[['Date','MA6_MA13']].tail(21),'\n')

print("5th percentile",sp500['MA6_MA13'].quantile(.05))    
print("10th percentile",sp500['MA6_MA13'].quantile(.1))    
print('Summary Statistics\n',sp500['MA6_MA13'].describe())
print("90th percentile",sp500['MA6_MA13'].quantile(.9))
print("95th percentile",sp500['MA6_MA13'].quantile(.95),'\n')
sp500.iloc[-(252*10):].plot(x='Date',y='MA6_MA13')

sp500['MA30']=sp500['Close'].rolling(30).mean()

print(sp500[['Date','Close','MA_6','MA_13','MA6_MA13','MA30']].tail())

if sp500['MA_6'].iloc[-1]<sp500['MA_13'].iloc[-1]:
    print('Death Cross runs beta neutral/negative portfolio if Close < MA30 and momentum MA6_13 is negative')
else:
    print('bull Cross runs beta positive portfolio if Close > MA30 and momentum MA6_13 is positive') 

print('\n \n \n', "Death Cross 11_126_30: \n")
sp500['MA_11']=sp500['Close'].rolling(11).mean()
sp500['MA_126']=sp500['Close'].rolling(126).mean()
sp500['MA11_MA126']=sp500['MA_11']-sp500['MA_126']

print('Bull/Bear Cross and crosses the 30day MA. \n')

if sp500['MA_11'].iloc[-1]>sp500['MA_126'].iloc[-1]:
    print('Bull Cross!: \n',sp500[['Date','MA11_MA126']].tail(21),'\n')
else:
    print('Bear Cross!: \n',sp500[['Date','MA11_MA126']].tail(21),'\n')

print("5th percentile",sp500['MA11_MA126'].quantile(.05))    
print("10th percentile",sp500['MA11_MA126'].quantile(.1))    
print('Summary Statistics\n',sp500['MA11_MA126'].describe())
print("90th percentile",sp500['MA11_MA126'].quantile(.9))
print("95th percentile",sp500['MA11_MA126'].quantile(.95),'\n')
sp500.iloc[-(252*10):].plot(x='Date',y='MA11_MA126')

sp500['MA30']=sp500['Close'].rolling(30).mean()

print(sp500[['Date','Close','MA_11','MA_126','MA11_MA126','MA30']].tail())

if sp500['MA_11'].iloc[-1]<sp500['MA_126'].iloc[-1]:
    print('Death Cross runs beta neutral/negative portfolio if Close < MA30 or MA126 and momentum MA11_126 is negative')
else:
    print('bull Cross runs beta positive portfolio if Close > MA30 or MA126 and momentum MA11_126 is positive') 


