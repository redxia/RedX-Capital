import pandas as pd
import alpaca_trade_api as tradeapi
#import numpy as np
from util import utilities as util
from datetime import datetime
from datetime import timedelta
import time
# %load_ext autoreload
# %autoreload 2

api = tradeapi.REST(
    'AKA1ZXH153SHLVTVE2ZF',
    'T5pwBCOzcBK7xDyi7xc2wVcSFtXagNz9DitVSiA3',
    'https://api.alpaca.markets')

limit = 1000 
interval=15 
look_back= 48 # 15 minutes for 48 nodes. 12 hours.
start_time=(datetime.now()-timedelta(days=14)).strftime('%Y-%m-%d')
# CBSE coinbase exchange


# barset_crypto = api.get_crypto_bars(symbol='ETHUSD', exchanges="CBSE", timeframe="1Hour", limit=limit, start=(datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')) # could exclude limit, use limit to limit the amount of api calls
#region crypto
start=datetime.now()
#tickers_crypto = util.read_tickers('crypto')
end=datetime.now()+timedelta(hours=15)
print("\n\n ETH PRICE 48 Hourly RSI")
while start <= end:
    barset_crypto = api.get_crypto_bars(symbol='ETHUSD', exchanges="CBSE", timeframe="1Hour", start=start_time)
    data_crypto={'ETHUSD':{'Date':[i.t for i in barset_crypto], 'Adj Close':[i.c for i in barset_crypto]}}
    ETH = pd.DataFrame(
    data_crypto['ETHUSD']['Adj Close'],
    index=pd.to_datetime(data_crypto['ETHUSD']['Date'],format="%Y-%m-%d %I:%M%p").strftime("%Y-%m-%d %I:%M %p"), 
    columns=['']
    )
    ETH_RSI, ETH_LAST_RSI=util.RSI(look_back, ETH)
    print(ETH_LAST_RSI, end='')
    time.sleep(3600) # every 30 minutes
#ETH_RSI.plot()


# model_crypto, model_last_crypto = util.get_RSI_AlphaRisk(data_crypto, tickers_crypto, interval=15, look_back=look_back, moving_alpha_risk=look_back)
# #endregion

# model_low_crypto = {k:np.round(v.values[0],2) for k, v in model_last_crypto.items() if ((len(v) != 2))}
# sorted(model_low_crypto.items(), key = lambda x:x[1][1], reverse=True) # RSI, ALPHA, STD

