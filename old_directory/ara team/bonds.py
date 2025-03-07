import os
import fredapi
import yfinance as yf
import pandas as pd
from datetime import timedelta
import utilities
# from rpy2.robjects.packages import importr
# from rpy2.robjects import pandas2ri
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
# pandas2ri.activate()
fredapi_key=os.environ.get("fredapi_key")
from slack_sdk.webhook import WebhookClient

url=r"https://hooks.slack.com/services/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" #ara team
webhook=WebhookClient(url)

tlt=yf.download('TLT', auto_adjust=True,actions=True, period='max', progress=False)[['Close']]
#tlt.to_csv(r"Data\TLT.csv")
# tlt.reset_index(inplace=True) #to get the date
# stats=importr('stats')
fred=fredapi.Fred(api_key=fredapi_key)

# list of relevant data series to for loop the download
t20yr=fred.get_series_latest_release('DGS20')
tlt=utilities.add_to_df(t20yr, 't20yr', tlt, interpolation=True)
fed_funds=fred.get_series('DFF') #.tail(1)[0]#fred.get_series_latest_release('FEDFUNDS')
# print('\n')
# print('Latest Fed Fund Rate')
# print('Fed Funds Rate',fed_funds,'\n')
# latest_ffund=pd.Series([fed_funds.tail(1)[0]], index=[(fed_funds.index[-1]+timedelta(days=32)).replace(day=1)])
# latest_ffund=pd.Series([fed_funds.tail(1)[0]], index=[utilities.next_business(utilities.last_business())])

# fed_funds=fed_funds.append(latest_ffund)


tlt=utilities.add_to_df(fed_funds, 'fedfunds', tlt, interpolation=True)
tlt.loc[tlt.shape[0]-1, 'fedfunds']=fed_funds.tail(1)[0]
tlt['fedfunds']=tlt['fedfunds'].interpolate()
t2yr=fred.get_series_latest_release('DGS2')
tlt=utilities.add_to_df(t2yr, 't2yr', tlt, interpolation=True)
t10yr=fred.get_series_latest_release('DGS10')
tlt=utilities.add_to_df(t10yr, 't10yr', tlt, interpolation=True)
tlt=tlt.ffill()
tlt=tlt.bfill()
tlt['t10yr_t2yr']=tlt['t10yr']-tlt['t2yr']

fedfund_rate=fred.get_series('DFF').tail(1)[0]
# print('Latest ffunds used: \n', fed_funds.tail(1)[0],'\n')
tlt['Date']=tlt['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
del tlt['Close']
webhook.send(text='Latest Yield Curve: \n' + tlt.tail(5).to_markdown()+"\n Uninversion bad forecast.") #TODO run the analysis with sp500
# print(,'\n')

# print('Predicted Fed Funds Rate: ',fedfund_rate)


#TODO find the r-squared for these models - maybe run it in r.