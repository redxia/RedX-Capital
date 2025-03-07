import math
import polygon
client=polygon.RESTClient('LBoNgqc59G4RKRZsQVNCyfOsf3C2CTjd')
import numpy as np
from datetime import datetime
from datetime import timedelta
import yfinance as yf
import pandas as pd
def norm_cdf(x):
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def black_scholes(S, K, r, t, sigma, option_type):
    d1 = (math.log(S/K) + (r + sigma**2/2)*t) / (sigma*math.sqrt(t))
    d2 = d1 - sigma*math.sqrt(t)
    
    if option_type == "Call" or option_type=='C':
        option_price = S*norm_cdf(d1) - K*math.exp(-r*t)*norm_cdf(d2)
    elif option_type == "Put" or option_type=='P':
        option_price = K*math.exp(-r*t)*norm_cdf(-d2) - S*norm_cdf(-d1)
    else:
        raise ValueError("Invalid option type")
    
    return option_price

def bs_spread_price(K_1, K_2, sigma_1, sigma_2, S, r, t, option_type):
    option_1=black_scholes(S, K_1, r, t, sigma_1, option_type)
    option_2=black_scholes(S, K_2, r, t, sigma_2, option_type)
    print(f"Option 1 with strike: {K_1:.1f} Price: {option_1:.2f}")
    print(f"Option 2 with strike: {K_2:.1f} Price {option_2:.2f}")
    print("Spread Price: {:.3f}".format(option_1-option_2), )
    return option_1-option_2

def volatility(ticker, look_back=365):
    # Define the stock ticker symbol and time period
    now=datetime.now()
    end_date = now
    start_date = end_date - timedelta(days=look_back)
    # Get the historical stock price data from Polygon
    resp = client.get_aggs(ticker, 1, "day", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    # Extract the closing prices from the response data
    prices = [day.close for day in resp]
    # Calculate the logarithmic returns
    returns = [(prices[i+1]-prices[i])/prices[i] for i in range(len(prices)-1)]
    # Calculate the historical volatility as the standard deviation of the log returns
    volatility = np.std(returns) * math.sqrt(252)
    return volatility

def intraday_range(ticker):
    # Define the date range for the intraday data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Get the intraday price data for the stock
    data = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)

    # Calculate the intraday range as the difference between the high and low prices
    intraday_range = data["High"] - data["Low"]
    high_low_range=pd.DataFrame({"Dates":data.index,"Intraday range":intraday_range.values, "Rolling Avg 21":intraday_range.rolling(21).mean().values, 'Rolling STD 21':intraday_range.rolling(21).std().values,"Rolling STD 21 Lower":intraday_range.rolling(21).mean().values-intraday_range.rolling(21).std().values,"Rolling STD 21 Upper":intraday_range.rolling(21).mean().values+intraday_range.rolling(21).std().values})
    print(high_low_range.tail(15))
    
    #print(intraday_range.rolling_mean().tail(25))
    # Print the intraday range
    print(f"Intraday range Mean for {ticker} over the past year: {high_low_range['Intraday range'].mean():.2f}\nIntraday range STD over the past year {high_low_range['Intraday range'].std():.2f}")
    
    
