import yfinance as yf
import pandas as pd
from datetime import datetime

# Define the ticker symbol for VIX
ticker_symbol = "^VIX"

# Define the start and end dates for the desired 2-year period
end_date = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))
start_date = end_date - pd.DateOffset(years=2)

# Fetch the historical data for VIX
vix_data = yf.download(ticker_symbol, period='max')

# Calculate the quintiles for the VIX values
quintiles = vix_data['Close'].quantile([0, 0.2, 0.4, 0.6, 0.8, 1])

# Initialize a dictionary to store the counts of days in each quintile
quintile_counts = {'Quintile 1': 0, 'Quintile 2': 0, 'Quintile 3': 0, 'Quintile 4': 0, 'Quintile 5': 0}

# Initialize a dictionary to store the counts of days in each quintile range
quintile_range_counts = [0,0,0,0,0]

# Iterate through the VIX data to count days in each quintile range
for i in range(len(quintiles) - 1):
        lower_bound = quintiles.iloc[i]
        upper_bound = quintiles.iloc[i + 1]
        for k in vix_data.iloc[-(252*2):]['Close']:
            if lower_bound <= k < upper_bound:
                quintile_range_counts[i] += 1
                
quintiles=quintiles.reset_index().iloc[:-1]
quintiles['Counts2yr']=quintile_range_counts
quintiles['Prob2yr']=quintiles['Counts2yr']/(252*2)

