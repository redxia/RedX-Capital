import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import timedelta

ticker='SPY'
end_date=datetime.now()+timedelta(days=1)
start_date='1994-01-01'
stock_data=yf.download(ticker,start=start_date, end=end_date, progress=False)
returns=stock_data.pct_change()['Close']
returns=returns.reset_index()
returns['Year']=returns['Date'].dt.year
returns['Day'] = returns['Date'].dt.strftime('%#j').astype(int)

pivot_df = returns.pivot(index='Day', columns='Year', values='SPY')
pivot_df.sort_index(ascending=True, inplace=True)

pivot_df.iloc[:,:-1]=pivot_df.iloc[:,:-1].fillna(0).round(4)
pivot_df_minus_last=pivot_df.copy().round(4)
pivot_df_cumulative_nolast=pivot_df_minus_last.apply(lambda x : (1+x).cumprod() -1)
most_correlated_years=pivot_df_cumulative_nolast.corr().iloc[-1,:].sort_values().iloc[-6:].round(4)
print(most_correlated_years)


pivot_df=pivot_df.fillna(0).round(4)
pivot_df_cumulative=pivot_df.apply(lambda x : (1+x).cumprod() -1)
pivot_df_cumulative[most_correlated_years.index].plot(figsize=(12,12))
# pivot_df_cumulative_nolast[most_correlated_years.index].tail(20)
pivot_df_cumulative[most_correlated_years.index].iloc[20:200,:].round(4).head(30)
print(pivot_df_cumulative[most_correlated_years.index])