import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def calculate_zbti(data):
    # Calculate advances and declines
    data['Advances'] = (data['Adj Close'] > data['Adj Close'].shift(1)).astype(int)
    data['Declines'] = (data['Adj Close'] < data['Adj Close'].shift(1)).astype(int)

    # Calculate 10-day moving sums of advances and declines
    data['Advances_10d'] = data['Advances'].rolling(window=10).sum()
    data['Declines_10d'] = data['Declines'].rolling(window=10).sum()

    # Calculate Zweig Breadth Thrust Indicator
    data['ZBTI'] = data['Advances_10d'] / (data['Advances_10d'] + data['Declines_10d'])

    return data

# Download S&P 500 data
symbol = '^GSPC'
start_date = '1970-01-01'
end_date = '2023-04-16'

sp500_data = yf.download(symbol, start=start_date, end=end_date)

def calculate_forward_returns(data, periods):
    for period in periods:
        data[f'Forward_Return_{period}M'] = data['Adj Close'].shift(-period * 21) / data['Adj Close'] - 1
    return data

# Define forward-looking periods in months
forward_periods = [1, 2, 3, 6, 9, 12]

# Calculate forward-looking returns
sp500_data = calculate_forward_returns(sp500_data, forward_periods)

# Print results
print(sp500_data.tail(15))


# Calculate Zweig Breadth Thrust Indicator
sp500_data = calculate_zbti(sp500_data)

# Plot S&P 500 levels and ZBTI
subset_data=sp500_data.tail(252*2)

fig, ax1 = plt.subplots(figsize=(14, 7))

ax1.set_xlabel('Date')
ax1.set_ylabel('S&P 500 Levels', color='tab:blue')
ax1.plot(subset_data.index, subset_data['Adj Close'], color='tab:blue', label='S&P 500')
ax1.tick_params(axis='y', labelcolor='tab:blue')

ax2 = ax1.twinx()
ax2.set_ylabel('Zweig Breadth Thrust Indicator', color='tab:red')
ax2.plot(subset_data.index, subset_data['ZBTI'], color='tab:red', label='ZBTI')
ax2.tick_params(axis='y', labelcolor='tab:red')

fig.tight_layout()
plt.show()

#Alpaca version

from getpass import getpass
import os
import numpy as np
from datetime import datetime
from datetime import timedelta
import pandas as pd
from alpaca_trade_api.rest import REST, TimeFrame
import yfinance as yf
# sp500_constituents=pd.read_excel("https://www.ssga.com/us/en/intermediary/etfs/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx", skiprows=4).dropna()

# russel_1000_constituents=pd.read_csv('https://www.ishares.com/us/products/239707/ishares-russell-1000-etf/1467271812596.ajax?fileType=csv&fileName=IWB_holdings&dataType=fund', skiprows=9).iloc[:-5]

alpaca = REST('AKA1ZXH153SHLVTVE2ZF', 'T5pwBCOzcBK7xDyi7xc2wVcSFtXagNz9DitVSiA3', 'https://api.alpaca.markets')
assets = alpaca.list_assets()

symbols = []
# sp500_constituents=sp500_constituents.loc[sp500_constituents['Ticker']!='CASH_USD',:]
# russel_1000_constituents=russel_1000_constituents.loc[~russel_1000_constituents['Ticker'].isin(['CR WI','RXO WI']),:]

# symbols = sp500_constituents['Ticker'].to_list()
# symbols = russel_1000_constituents['Ticker'].to_list()

for asset in assets:
    if asset.exchange == 'NYSE' and asset.status == 'active':
        symbols.append(asset.symbol)


symbols

today=datetime.now().strftime("%Y-%m-%d")
bars_a = alpaca.get_bars(symbols, TimeFrame.Day, "2007-01-01", today).df
# bars = yf.download(symbols, start="2007-01-01", end=today)
# bars = bars[['Adj Close']].rename(columns={'Adj Close': 'close'})

bars=bars_a
bars['pct_change'] = bars['close'].pct_change()
bars['sign'] = np.sign(bars['pct_change'])
print(bars)

df = bars.groupby(by = ['timestamp', 'sign'])['sign'].count().to_frame('count').reset_index()
df = pd.pivot_table(df, values = 'count', index=['timestamp'], columns = 'sign')
df = df.rename(columns={1.0: "advancers", 0.0: "unchanged", -1.0: "decliners"})

df['percent_advancing'] = df['advancers'] / (df['advancers'] + df['decliners'])
df['ema'] = df['percent_advancing'].ewm(span=10, adjust=False).mean() #less than 40 and more than 60 signal

df['10dayadvancers'] = df['advancers'].rolling(window=10).sum()
df['10daydecliners'] = df['decliners'].rolling(window=10).sum()
df['bam'] = df['10dayadvancers'] / df['10daydecliners'] # bigger than 1.97

df['5dayadvancers'] = df['advancers'].rolling(window=5).sum()
df['5daydecliners'] = df['decliners'].rolling(window=5).sum()
df['whaley_percent'] = df['5dayadvancers'] / (df['5dayadvancers'] + df['5daydecliners']) #70% statistically signficant # long months without this signal implies bear
df=df.reset_index()
df['timestamp']=df['timestamp'].dt.tz_localize(None)
df.to_excel("Breaadth_Thrust_Indicator.xlsx", index=False)



import yfinance as yf
import pandas as pd

# Download the Russell 1000 constituents
# russell1000 = pd.read_csv("https://www.ishares.com/us/products/239707/ishares-russell-1000-etf/1467271812596.ajax?fileType=csv&fileName=iwf_holdings&dataType=fund")
russell1000=pd.read_csv('https://www.ishares.com/us/products/239707/ishares-russell-1000-etf/1467271812596.ajax?fileType=csv&fileName=IWB_holdings&dataType=fund', skiprows=9).iloc[:-5]
tickers = russell1000['Ticker'].tolist()

# Define the time period (e.g., 10 trading days)
lookback_period = 10

# Download the historical data for the tickers
data = yf.download(tickers, start="2000-01-01", end="2023-04-17", group_by='ticker')

# Reshape the DataFrame
data = data.stack(level=0).reset_index().rename(columns={'level_1': 'Ticker'})
data.set_index('Date', inplace=True)

# Filter adjusted close prices
adj_close_data = data.pivot_table(values='Adj Close', index=data.index, columns='Ticker')
adj_close_data=adj_close_data.pct_change()
adj_close_data=np.sign(adj_close_data)
adj_close_data=adj_close_data.reset_index()

value_counts = adj_close_data.groupby('Date').apply(lambda x: x.apply(lambda col: col.value_counts(dropna=False).to_dict(), axis=1))#.apply(lambda x: x.sum(), axis=1)

# Create a new DataFrame with the counts
count_df = pd.DataFrame.from_records(value_counts.values.tolist(), index=value_counts.index)
df = count_df.rename(columns={1.0: "advancers", 0.0: "unchanged", -1.0: "decliners"})

df['percent_advancing'] = df['advancers'] / (df['advancers'] + df['decliners'])
df['ema'] = df['percent_advancing'].ewm(span=10, adjust=False).mean() #less than 40 and more than 60 
# Calculate advancing and declining stocks
# Calculate Zweig Breadth Thrust

russell1000_index_data = yf.download('^RUI', start="2000-01-01", end="2023-04-17")
# Create a dual-axis plot
fig, ax1 = plt.subplots()

# Plot the Russell 1000 levels
ax1.set_ylabel('Russell 1000')
ax1.plot(russell1000_index_data.index, russell1000_index_data['Close'], label="Russell 1000", color='tab:blue')
ax1.tick_params(axis='y', labelcolor='tab:blue')

# Create a second y-axis
ax2 = ax1.twinx()
ax2.set_ylabel('Zweig Breadth Thrust')
ax2.plot(russell1000_index_data.index[-1], df['ema'][-1], 'o', label="ZBT", color='tab:red')
ax2.tick_params(axis='y', labelcolor='tab:red')

# Show the plot
plt.title("Zweig Breadth Thrust vs. Russell 1000")
plt.show()

df=df.reset_index()
russell1000_index_data=russell1000_index_data['Adj Close']
russell1000_index_data=russell1000_index_data.reset_index()
russell1000_index_data=russell1000_index_data.merge(df[['Date','ema']], on='Date', how='left')
subset=russell1000_index_data.tail(252*5)

fig, ax1 = plt.subplots(figsize=(14, 7))

ax1.set_xlabel('Date')
ax1.set_ylabel('S&P 500 Levels', color='tab:blue')
ax1.plot(subset.Date, subset['Adj Close'], color='tab:blue', label='Russell 1000')
ax1.tick_params(axis='y', labelcolor='tab:blue')

ax2 = ax1.twinx()
ax2.set_ylabel('Zweig Breadth Thrust Indicator', color='tab:red')
ax2.plot(subset.Date, subset['ema'], color='tab:red', label='ZBTI')
ax2.tick_params(axis='y', labelcolor='tab:red')

# ax2.hlines(.6,0, 1)
# ax2.hlines(.4,0,1)
#$Zweig Breadth Thrust
fig.tight_layout()
plt.show()