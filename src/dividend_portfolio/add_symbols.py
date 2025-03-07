from data_pipeline import data_update
from data_pipeline import data_properties
import os

stock_path=r"C:\RedXCapital\Dividends\Data\Symbol"
market_path=r"C:\RedXCapital\Dividends\Data\Market Data"
path=stock_path
ticker='SPYI'

data_update.download_data(ticker, path)
data_properties.stock_properties(ticker, path)

#TODO alpha model then risk model then run the optimizations

