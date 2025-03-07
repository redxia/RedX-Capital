import time
import yfinance as yf
import pandas as pd
from utilities import utilities
from datetime import datetime
from datetime import timedelta
from excel import excel
import pandas.io.formats.excel
pandas.io.formats.excel.ExcelFormatter.header_style=None

start_time=datetime.now()

def liquidity_model(positions, lookback=.25): # amount of years to look back
    # positions=utilities.read_position_file() 
    
    positionals_bool=(positions['Symbol'].isna()) & (positions['Right']=='S')
    liquidity=positions.loc[positionals_bool,['Class Group','Market Value','Quantity','Close Price']]

    unique_tickers=liquidity['Class Group'].tolist()
    
    historical=yf.download(unique_tickers,start=(start_time-timedelta(days=365*lookback+6)).strftime("%Y-%m-%d"), end=utilities.next_business().strftime('%Y-%m-%d'))[['Close','Volume']]
    adv_20=historical['Volume'].iloc[-20:].mean(skipna=True, numeric_only=True)
    adv_20=adv_20.reset_index()
    adv_20.columns=['Class Group','ADV 20']
    
    liquidity=liquidity.merge(adv_20, on='Class Group', how='left')
    liquidity['Weight']=liquidity['Market Value'] / liquidity['Market Value'].sum()
    liquidity['Dollar ADV 20'] = liquidity['ADV 20'] * liquidity['Close Price']
    
    liquidity['Liquidity']=liquidity['Quantity'] / liquidity['ADV 20']
    liquidity['Liquidity']=liquidity['Liquidity'].apply(lambda x: max(0,x))
    
    liquidity['Liquidity Model']=(liquidity['Liquidity'] - 1).clip(0) * 0.15 * liquidity['Market Value'].abs()
    liquidity['Quantity Diff']=liquidity['ADV 20'] - liquidity['Quantity']
    
    liquidity=liquidity[['Class Group','Quantity','ADV 20','Close Price','Weight','Market Value','Dollar ADV 20','Liquidity','Liquidity Model', 'Quantity Diff']]
    liquidity.sort_values('Liquidity', ascending=False, inplace=True)
    
    return liquidity
