import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
pandas2ri.activate()

quantmod=importr('quantmod')

quantmod.getSymbols(r"^GSPC")
forecast=importr('forecast')

import yfinance as yf

sp500=yf.download('^GSPC', auto_adjust=True,actions=True, period='max', progress=False)
sp500_monthly=yf.download('^GSPC', auto_adjust=True,actions=True, period='max', progress=False, interval='1mo')
sp500.to_csv('sp500.csv')
sp500_monthly.to_csv('sp500_Monthly.csv')