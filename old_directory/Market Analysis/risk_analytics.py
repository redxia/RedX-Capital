import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

market_dir=r"C:\RedXCapital\Dividends\Data\Market Data"

sp500=pd.read_csv(market_dir+"\SPY.csv")
sp500=yf.download('SPY')
sp500['Maxdrawdown_2yr']=sp500['Adj Close'] / sp500['Adj Close'].rolling(21*12, min_periods=21).max() -1
sp500['yoy_returns']=sp500['Adj Close'].pct_change(252)
#sp500.loc[sp500['yoy_returns']>.5,:]


sp500['Maxdrawdown_2yr'].quantile(.15) # 16.82%
sp500['Maxdrawdown_2yr'].quantile(.10) # 23.2%
sp500['Maxdrawdown_2yr'].quantile(.05) # 32.84%
sp500['Maxdrawdown_2yr'].quantile(.025) # 39.39%
sp500['Maxdrawdown_2yr'].quantile(.01) # 43.6%
sp500['Maxdrawdown_2yr'].min() # 55.19

sp500.loc[sp500['yoy_returns']<0,'yoy_returns'].quantile(.15) # 27.14
sp500.loc[sp500['yoy_returns']<0,'yoy_returns'].quantile(.10) # 33.73
sp500.loc[sp500['yoy_returns']<0,'yoy_returns'].quantile(.05) # 37.7
sp500.loc[sp500['yoy_returns']<0,'yoy_returns'].quantile(.025) # 40.26
sp500.loc[sp500['yoy_returns']<0,'yoy_returns'].quantile(.01) # 43%
sp500.loc[sp500['yoy_returns']<0,'yoy_returns'].min() # 46.54%

# CVaR
sp500.loc[sp500['Maxdrawdown_2yr']<sp500['Maxdrawdown_2yr'].quantile(.10),'Maxdrawdown_2yr'].mean() #33.68%
sp500.loc[sp500['Maxdrawdown_2yr']<sp500['Maxdrawdown_2yr'].quantile(.05),'Maxdrawdown_2yr'].mean() #39.85%
sp500.loc[sp500['Maxdrawdown_2yr']<sp500['Maxdrawdown_2yr'].quantile(.025),'Maxdrawdown_2yr'].mean() #43.63
sp500.loc[sp500['Maxdrawdown_2yr']<sp500['Maxdrawdown_2yr'].quantile(.01),'Maxdrawdown_2yr'].mean() #46.98%

# room for drawdown
min_stats=sp500.iloc[-100:].min() # recent 4-5 months
print(min_stats)
min_stats['Maxdrawdown_2yr']-sp500['Maxdrawdown_2yr'].quantile(.025)
min_stats['Maxdrawdown_2yr']-sp500.loc[sp500['Maxdrawdown_2yr']<sp500['Maxdrawdown_2yr'].quantile(.025),'Maxdrawdown_2yr'].mean() 
min_stats['yoy_returns']-sp500.loc[sp500['yoy_returns']<0,'yoy_returns'].quantile(.025)

min_stats['Maxdrawdown_2yr']-sp500['Maxdrawdown_2yr'].quantile(.005)
min_stats['Maxdrawdown_2yr']-sp500.loc[sp500['Maxdrawdown_2yr']<sp500['Maxdrawdown_2yr'].quantile(.005),'Maxdrawdown_2yr'].mean() 
min_stats['yoy_returns']-sp500.loc[sp500['yoy_returns']<0,'yoy_returns'].quantile(.005)

sp500.plot(x='Date',y='Maxdrawdown_2yr', figsize=(16,12)) # plot the max_drawdown
sp500.iloc[-252*10:].plot(x='Date',y='Maxdrawdown_2yr', figsize=(16,12)) # plot the max_drawdown
sp500.plot(x='Date',y='yoy_returns', figsize=(16,12)) # plot the max_drawdown