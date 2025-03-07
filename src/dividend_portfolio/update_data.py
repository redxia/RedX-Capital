# Aim to have this program update the data at 6pm
import yfinance as yf
import pandas as pd
import sys
from utilities import utilities
import time
from utilities import market_model
from data_pipeline import data_update
from utilities import alpha_model
from utilities import risk_model
import os
from ibkr import ibkr
import pandas.io.formats.excel
pandas.io.formats.excel.ExcelFormatter.header_style=None
#TODO beta is actually 3 months
stock_path=r"C:\RedXCapital\Dividends\Data\Symbol"
market_path=r"C:\RedXCapital\Dividends\Data\Market Data"

#TODO move all these function to the utility folder
if sys.argv[1]=="Daily": # update the data updater to work for market stuff too.
    if not utilities.business_day():
        sys.exit()    
    data_update.data_updater(market_path)
    time.sleep(3.5)
    data_update.data_updater(stock_path) 
    time.sleep(3.5)
    try:
        ibkr.download_positions()
    except:
        pass
    time.sleep(3.5)
    # market_model.market_model() # market predictions
    time.sleep(3.5)
    # alpha_model.alpha_model_updater() #string arg %Y%m%d
    time.sleep(3.5)
    # risk_model.risk_model_updater() #string arg %Y%m%d

if sys.argv[1]=="Monthly": #TODO once a month check if the stock switches buckets SPY,QQQ, VALUE/Size R^2
    market=[i.split('.')[0] for i in os.listdir(market_path)]
    for ticker in market:
        data_update.download_data(ticker, market_path) 

    symbols=[i.split('.')[0] for i in os.listdir(stock_path)]
    for ticker in symbols:
        data_update.download_data(ticker, stock_path) 
    
    time.sleep(3.5)
    data_update.data_updater(market_path)
    time.sleep(3.5)
    data_update.data_updater(stock_path) 
    time.sleep(2)
    # market_model.market_model() # market predictions
    time.sleep(3.5)
    # alpha_model.alpha_model_updater() #string arg %Y%m%d
    time.sleep(3.5)
    # risk_model.risk_model_updater() #string arg %Y%m%d    

