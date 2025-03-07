import pandas as pd
import alpaca_trade_api as tradeapi
import numpy as np
from util import utilities as util
from datetime import datetime
from datetime import timedelta
%load_ext autoreload
%autoreload 2

api = tradeapi.REST(
    'AKA1ZXH153SHLVTVE2ZF',
    'T5pwBCOzcBK7xDyi7xc2wVcSFtXagNz9DitVSiA3',
    'https://api.alpaca.markets')

limit = 1000 
interval=15  # 60 for hourly, 30 for every 30 min
# 17 for 2 days and a half for hourly, 34 for 30 min, 21 for a day and a half, 28 days, 42 for 3 days
look_back= 48#42  
# low_rsi = 45
# high_rsi = 60E
moving_alpha_risk = 1080#int(22*1.5) # 22 trading days x 1.5 = 1.5  months


#region crypto
tickers_crypto = util.read_tickers('crypto')
barset_crypto = api.get_crypto_bars(symbol='ETHUSD', exchanges="CBSE", timeframe="15Min", limit=limit, start=(datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d'))
data_crypto={'ETHUSD':{'Date':[i.t for i in barset_crypto], 'Adj Close':[i.c for i in barset_crypto]}}
ETH = pd.DataFrame(
    data_crypto['ETHUSD']['Adj Close'],
    index=pd.to_datetime(data_crypto['ETHUSD']['Date'],format="%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M"), 
    columns=['ETHUSD']
    )
ETH_RSI, ETH_LAST_RSI=util.RSI(look_back, ETH)
ETH_RSI.tail(15)
ETH_RSI.plot()


model_crypto, model_last_crypto = util.get_RSI_AlphaRisk(data_crypto, tickers_crypto, interval=15, look_back=look_back, moving_alpha_risk=look_back)
#endregion

model_low_crypto = {k:np.round(v.values[0],2) for k, v in model_last_crypto.items() if ((len(v) != 2))}
sorted(model_low_crypto.items(), key = lambda x:x[1][1], reverse=True) # RSI, ALPHA, STD


#region roth
tickers_roth = util.read_tickers('roth')
barset_roth = api.get_barset(tickers_roth, timeframe='15Min', limit=limit)
data_roth = util.get_close(barset_roth, tickers_roth, limit)
model_roth, model_last_roth = util.get_RSI_AlphaRisk(data_roth, tickers_roth, interval=interval, look_back=look_back, moving_alpha_risk=moving_alpha_risk)
#endregion

model_low_roth = {k:np.round(v.values[0],2) for k, v in model_last_roth.items() if ((len(v) != 2))}
sorted(model_low_roth.items(), key = lambda x:x[1][1], reverse=True) # RSI, ALPHA, STD

#region ETFS
tickers_etfs = util.read_tickers('etfs')
barset_etfs = api.get_barset(tickers_etfs, timeframe='15Min', limit=limit)
data_etfs = util.get_close(barset_etfs, tickers_etfs, limit)
model_etfs, model_last_etfs = util.get_RSI_AlphaRisk(data_etfs, tickers_etfs, interval=interval, look_back=look_back, moving_alpha_risk=moving_alpha_risk)
# rsi_empty_etfs = {k:v for k, v in rsi_last_etfs.items() if v.values.size == 0}
#endregion ETFS

model_low_etfs = {k:np.round(v.values[0],2) for k, v in model_last_etfs.items() if ((len(v) != 2))}
sorted(model_low_etfs.items(), key = lambda x:x[1][1], reverse=True) # RSI, ALPHA, STD
# model_low_etfs = {k:np.round(v.values[0],2) for k, v in model_last_etfs.items() if ((len(v) != 2) and (v.values[0][0] < 45) and v.values[0][1] > 0)}
# model_high_etfs = {k:np.round(v.values[0],2) for k, v in model_last_etfs.items() if ((len(v) != 2) and (v.values[0][0] > 55) and v.values[0][1] < 0)}

#region others
#region russ1k This will take a long time to run
tickers_russ1k = util.read_tickers('russ1k')
russ1k_seq = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000] # needs to read each sequence into the data
russ1k_data = {}

for i in russ1k_seq:
        print(i)
        russ1k_tick = tickers_russ1k[(i-100):i]
        russ1k_barset = api.get_barset(russ1k_tick, timeframe='15Min', limit=limit)
        russ1k_data.update(util.get_close(russ1k_barset, russ1k_tick, limit))

model_russ1k, model_last_russ1k = util.get_RSI_AlphaRisk(russ1k_data, tickers_russ1k, interval=interval, look_back=look_back, moving_alpha_risk=252)
# rsi_empty_russ1k = {k:v for k, v in rsi_last_russ1k.items() if v.values.size == 0}
#endregion russ1k

#region NASDAQ
tickers_nasdaq = util.read_tickers('nasdaq')
barset_nasdaq = api.get_barset(tickers_nasdaq, timeframe='15Min', limit=limit)
data_nasdaq = util.get_close(barset_nasdaq, tickers_nasdaq, limit)
model_nasdaq, model_last_nasdaq = util.get_RSI_AlphaRisk(data_nasdaq, tickers_nasdaq, interval=interval, look_back=look_back, moving_alpha_risk=252)
# rsi_empty_nasdaq = {k:v for k, v in rsi_last_nasdaq.items() if v.values.size == 0}
#endregion

#region sp500
tickers_sp500_diff = util.read_tickers('sp500_diff')
barset_sp500_diff = api.get_barset(tickers_sp500_diff, timeframe='15Min', limit=limit)
data_sp500_diff = util.get_close(barset_sp500_diff, tickers_sp500_diff, limit)
model_sp500_diff, model_last_sp500_diff = util.get_RSI_AlphaRisk(data_sp500_diff, tickers_sp500_diff, interval=interval, look_back=look_back, moving_alpha_risk=252)
#endregion


#region mean reversion sorts
# Build the alpha models here
#and basic variance model here.
# filters
model_low_etfs = {k:np.round(v.values[0],2) for k, v in model_last_etfs.items() if ((len(v) != 2) and (v.values[0][0] < 45) and v.values[0][1] > 0)}
model_high_etfs = {k:np.round(v.values[0],2) for k, v in model_last_etfs.items() if ((len(v) != 2) and (v.values[0][0] > 55) and v.values[0][1] < 0)}
model_low_russ1k = {k:np.round(v.values[0],2) for k, v in model_last_russ1k.items() if ((len(v) != 2) and (v.values[0][0] < low_rsi) and v.values[0][1] > 10)}
model_high_russ1k = {k:np.round(v.values[0],2) for k, v in model_last_russ1k.items() if ((len(v) != 2) and (v.values[0][0] > high_rsi) and v.values[0][1] < -20)}
model_low_sp500_diff = {k:np.round(v.values[0],2) for k, v in model_last_sp500_diff.items() if ((len(v) != 2) and (v.values[0][0] < 45) and v.values[0][1] > 0)}
model_high_sp500_diff = {k:np.round(v.values[0],2) for k, v in model_last_sp500_diff.items() if ((len(v) != 2) and (v.values[0][0] > 55) and v.values[0][1] < 0)}
model_low_roth = {k:np.round(v.values[0],2) for k, v in model_last_roth.items() if ((len(v) != 2) and (v.values[0][0] < 45) and v.values[0][1] > 0)}
model_high_roth = {k:np.round(v.values[0],2) for k, v in model_last_roth.items() if ((len(v) != 2) and (v.values[0][0] > 55) and v.values[0][1] < 0)}
model_low_nasdaq = {k:np.round(v.values[0],2) for k, v in model_last_nasdaq.items() if ((len(v) != 2) and (v.values[0][0] < 45) and v.values[0][1] > 0)}
model_high_nasdaq = {k:np.round(v.values[0],2) for k, v in model_last_nasdaq.items() if ((len(v) != 2) and (v.values[0][0] > 55) and v.values[0][1] < 0)}
model_low_crypto = {k:np.round(v.values[0],2) for k, v in model_last_crypto.items() if ((len(v) != 2) and (v.values[0][0] < 45) and v.values[0][1] > 0)}
model_high_crypto = {k:np.round(v.values[0],2) for k, v in model_last_crypto.items() if ((len(v) != 2) and (v.values[0][0] > 55) and v.values[0][1] < 0)}

# Sorted by the alphas
sorted(model_low_etfs.items(), key = lambda x:x[1][1], reverse=True)
sorted(model_low_russ1k.items(), key = lambda x:x[1][1], reverse=True)
sorted(model_low_sp500_diff.items(), key = lambda x:x[1][1], reverse=True)
sorted(model_low_nasdaq.items(), key = lambda x:x[1][1], reverse=True)
sorted(model_low_roth.items(), key = lambda x:x[1][1], reverse=True)
sorted(model_low_crypto.items(), key = lambda x:x[1][1], reverse=True)

sorted(model_high_etfs.items(), key = lambda x:x[1][1], reverse=False)
sorted(model_high_russ1k.items(), key = lambda x:x[1][1], reverse=False) 
sorted(model_high_sp500_diff.items(), key = lambda x:x[1][1], reverse=False) 
sorted(model_high_nasdaq.items(), key = lambda x:x[1][1], reverse=False) 
sorted(model_high_roth.items(), key = lambda x:x[1][1], reverse=False) 
sorted(model_high_crypto.items(), key = lambda x:x[1][1], reverse=False) 

# sort by volatility
sorted(model_low_etfs.items(), key = lambda x:x[1][2], reverse=True)
sorted(model_low_russ1k.items(), key = lambda x:x[1][2], reverse=True)
sorted(model_low_sp500_diff.items(), key = lambda x:x[1][2], reverse=True)
sorted(model_low_nasdaq.items(), key = lambda x:x[1][2], reverse=True)
sorted(model_low_roth.items(), key = lambda x:x[1][2], reverse=True)

sorted(model_high_etfs.items(), key = lambda x:x[1][2], reverse=True)
sorted(model_high_russ1k.items(), key = lambda x:x[1][2], reverse=True) 
sorted(model_high_sp500_diff.items(), key = lambda x:x[1][2], reverse=True) 
sorted(model_high_nasdaq.items(), key = lambda x:x[1][2], reverse=True) 
sorted(model_high_roth.items(), key = lambda x:x[1][2], reverse=True) 
#endregion mean reversion sorts

#endregion others