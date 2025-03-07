import yfinance as yf
import pandas as pd

from slack_sdk.webhook import WebhookClient
url=r"https://hooks.slack.com/services/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"
webhook=WebhookClient(url)

# Define the tickers
tickers = ['SVXY', 'SPY', 'VXX','UVXY']

# Define the start and end dates
end_date = pd.Timestamp.now()
start_date = end_date - pd.DateOffset(months=6)

# Fetch historical data
data = yf.download(tickers, start=start_date, end=end_date)['Close']

# Calculate daily returns
daily_returns = data.pct_change().dropna()

# Calculate average daily returns
avg_daily_returns = daily_returns.mean()

cov_matrix = daily_returns.cov()

# Calculate the beta for SVXY and VXX relative to SPY
beta_SVXY = cov_matrix.loc['SVXY', 'SPY'] / cov_matrix.loc['SPY', 'SPY']
beta_VXX = cov_matrix.loc['VXX', 'SPY'] / cov_matrix.loc['SPY', 'SPY']
beta_UVXY = cov_matrix.loc['UVXY', 'SPY'] / cov_matrix.loc['SPY', 'SPY']

# Calculate monthly returns
monthly_returns = data.resample('M').ffill().pct_change().dropna()

# Calculate yearly returns
yearly_returns = data.resample('Y').ffill().pct_change().dropna()

# Calculate average monthly returns
avg_monthly_returns = monthly_returns.mean()
avg_yearly_returns = yearly_returns.mean()

# Calculate standard deviation (volatility) for daily and monthly returns
std_dev_daily = daily_returns.std()
std_dev_monthly = monthly_returns.std()
std_dev_yearly = yearly_returns.std()

# Calculate annualized volatility for daily and monthly returns
annualized_volatility_daily = std_dev_daily * (252 ** 0.5)  # Assuming 252 trading days in a year
annualized_volatility_monthly = std_dev_monthly * (12 ** 0.5)  # Assuming 12 months in a year

# Print the results
for ticker in tickers:
    print(f"Ticker: {ticker}")
    print(f"Avg Daily Return: {avg_daily_returns[ticker]*100:.2f}")
    print(f"Daily Standard Deviation: {std_dev_daily[ticker]*100:.2f}")
    # print(f"Geometric Daily Return: {((1+avg_monthly_returns[ticker])**(1/21)-1)*100:.2f}")
    # print(f"Monthsized Daily Return: {((1+avg_daily_returns[ticker])**21-1)*100:.2f}")
    # print(f"Avg Monthly Return: {avg_monthly_returns[ticker]*100:.2f}")
    # print(f"Monthly Standard Deviation: {std_dev_monthly[ticker]*100:.2f}")
    # print(f"Annualized Monthly Volatility: {annualized_volatility_monthly[ticker]*100:.2f}")
    # print(f"Avg Yearly Return: {avg_yearly_returns[ticker]*100:.2f}")
    # print(f"Geometric Monthly Return: {((1+avg_yearly_returns[ticker])**(1/12)-1)*100:.2f}")
    # print(f"Yearly Standard Deviation: {std_dev_yearly[ticker]*100:.2f}")
    print("=" * 40)
    
print(f"Beta of SVXY to SPY: {beta_SVXY:.2f}")
print(f"Beta of VXX to SPY: {beta_VXX:.2f}")
print(f"Beta of UVXY to SPY: {beta_UVXY:.2f}")
corr_matrix = daily_returns.corr()
print(f"Corr Matrix: {corr_matrix}")