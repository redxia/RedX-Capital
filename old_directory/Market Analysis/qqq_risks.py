import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


QQQ=yf.download('QQQ')
QQQ['Maxdrawdown_2yr']=QQQ['Adj Close'] / QQQ['Adj Close'].rolling(21*24, min_periods=21).max() -1
QQQ['yoy_returns']=QQQ['Adj Close'].pct_change(252)
#QQQ.loc[QQQ['yoy_returns']>.5,:]


QQQ['Maxdrawdown_2yr'].quantile(.15) # 16.82%
QQQ['Maxdrawdown_2yr'].quantile(.10) # 23.2%
QQQ['Maxdrawdown_2yr'].quantile(.05) # 32.84%
QQQ['Maxdrawdown_2yr'].quantile(.025) # 39.39%
QQQ['Maxdrawdown_2yr'].quantile(.01) # 43.6%
QQQ['Maxdrawdown_2yr'].min() # 55.19

QQQ.loc[QQQ['yoy_returns']<0,'yoy_returns'].quantile(.15) # 27.14
QQQ.loc[QQQ['yoy_returns']<0,'yoy_returns'].quantile(.10) # 33.73
QQQ.loc[QQQ['yoy_returns']<0,'yoy_returns'].quantile(.05) # 37.7
QQQ.loc[QQQ['yoy_returns']<0,'yoy_returns'].quantile(.025) # 40.26
QQQ.loc[QQQ['yoy_returns']<0,'yoy_returns'].quantile(.01) # 43%
QQQ.loc[QQQ['yoy_returns']<0,'yoy_returns'].min() # 46.54%

# CVaR
QQQ.loc[QQQ['Maxdrawdown_2yr']<QQQ['Maxdrawdown_2yr'].quantile(.10),'Maxdrawdown_2yr'].mean() #33.68%
QQQ.loc[QQQ['Maxdrawdown_2yr']<QQQ['Maxdrawdown_2yr'].quantile(.05),'Maxdrawdown_2yr'].mean() #39.85%
QQQ.loc[QQQ['Maxdrawdown_2yr']<QQQ['Maxdrawdown_2yr'].quantile(.025),'Maxdrawdown_2yr'].mean() #43.63
QQQ.loc[QQQ['Maxdrawdown_2yr']<QQQ['Maxdrawdown_2yr'].quantile(.01),'Maxdrawdown_2yr'].mean() #46.98%

# room for drawdown
min_stats=QQQ.iloc[-100:].min() # recent 4-5 months
print(min_stats)
min_stats['Maxdrawdown_2yr']-QQQ['Maxdrawdown_2yr'].quantile(.025)
min_stats['Maxdrawdown_2yr']-QQQ.loc[QQQ['Maxdrawdown_2yr']<QQQ['Maxdrawdown_2yr'].quantile(.025),'Maxdrawdown_2yr'].mean() 
min_stats['yoy_returns']-QQQ.loc[QQQ['yoy_returns']<0,'yoy_returns'].quantile(.025)

min_stats['Maxdrawdown_2yr']-QQQ['Maxdrawdown_2yr'].quantile(.005)
min_stats['Maxdrawdown_2yr']-QQQ.loc[QQQ['Maxdrawdown_2yr']<QQQ['Maxdrawdown_2yr'].quantile(.005),'Maxdrawdown_2yr'].mean() 
min_stats['yoy_returns']-QQQ.loc[QQQ['yoy_returns']<0,'yoy_returns'].quantile(.005)

QQQ.plot(x='Date',y='Maxdrawdown_2yr', figsize=(16,12)) # plot the max_drawdown
QQQ.iloc[-252*10:].plot(x='Date',y='Maxdrawdown_2yr', figsize=(16,12)) # plot the max_drawdown
QQQ.plot(x='Date',y='yoy_returns', figsize=(16,12)) # plot the max_drawdown