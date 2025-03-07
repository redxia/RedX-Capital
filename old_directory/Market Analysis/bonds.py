import os
import fredapi
import yfinance as yf
import pandas as pd
from datetime import timedelta
from utilities import utilities
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pandas2ri.activate()
fredapi_key=os.environ.get("fredapi_key")
from slack_sdk.webhook import WebhookClient

url=r"https://hooks.slack.com/services/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" #ara team
webhook=WebhookClient(url)

# tlt=yf.download('TLT', auto_adjust=True,actions=True, period='max', progress=False)[['Close','Volume','Dividends']]
#tlt.to_csv(r"Data\TLT.csv")
# tlt.reset_index(inplace=True) #to get the date
stats=importr('stats')
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
del tlt['Volume']
del tlt['Dividends']
webhook.send(text='Latest Yield Curve: \n' + tlt.tail(5).to_markdown())
# print(,'\n')

# print('Predicted Fed Funds Rate: ',fedfund_rate)

#t2yr_model=stats.lm('t2yr~fedfunds', data=tlt)
# t2yr_model=stats.lm('t2yr~fedfunds', data=tlt.iloc[(-252*2):])
# t2yr_model=stats.lm('t2yr~fedfunds', data=tlt)
# t2yr_pred=t2yr_model[0][1]*fedfund_rate+t2yr_model[0][0]
# print('Fed Funds to t2yr Model\n','Intercept: ',t2yr_model[0].round(2)[0],'  Beta: ',t2yr_model[0].round(2)[1],'\n')
# print('Fed Funds & t2yr correlation: \n',tlt[['fedfunds','t2yr']].corr().round(4),'\n')
# print('Predicted t2yr: ', t2yr_pred.round(2))
# t10yr_model=stats.lm('t10yr~t2yr', data=tlt.iloc[int(-252*1.5):])
# t10yr_pred=t10yr_model[0][0]+t10yr_model[0][1]*t2yr_pred
# print('t2yr to t10yr Model\n','Intercept: ',t10yr_model[0].round(2)[0],'  Beta: ',t10yr_model[0].round(2)[1], '\n')
# print('t2yr & t10yr correlation: \n',tlt.iloc[int(-252*1.5):][['t10yr','t2yr']].corr().round(4),'\n')
# print('Predicted t10yr: ', t10yr_pred.round(2))

# tlt.reset_index(inplace=True)
# tlt['index']=tlt['index']+1
# t2yr_detrend=stats.lm('t2yr~index', data=tlt) # save the detrend to back out #TODO maybe dont need al this
# t2yr_detrend_pred=t2yr_pred-(t2yr_detrend[0][0]+t2yr_detrend[0][1]*(tlt.shape[0]+1))
# tlt['t2yr_detrend']=t2yr_detrend[1]
# t10yr_detrend=stats.lm('t10yr~index', data=tlt)
# tlt['t10yr_detrend']=t10yr_detrend[1]
# t10yr_model=stats.lm('t10yr_detrend~t2yr_detrend', data=tlt.iloc[(-252*2):])
# t10yr_detrend_pred=t10yr_model[0][0]+t10yr_model[0][1]*t2yr_detrend_pred #TODO lower ir use this. aka ir cuts
# #t10yr_detrend_pred=t10yr_model[0][0]+.6*t2yr_detrend_pred #higher ir use this
# t10yr_pred=t10yr_detrend_pred+t10yr_detrend[0][0]+t10yr_detrend[0][1]*(tlt.shape[0]+1)


t20yr_model=stats.lm('t20yr~t10yr', data=tlt.iloc[int((-252*1.5)):])
t20yr_pred=t10yr_pred*t20yr_model[0][1]+t20yr_model[0][0]
# print('t10yr to t20yr Model\n','Intercept: ',t20yr_model[0].round(2)[0],'  Beta: ',t20yr_model[0].round(2)[1],'\n')
# print('t10yr & t20yr correlation: \n',tlt.iloc[int(-252*1.5):][['t10yr','t20yr']].corr().round(4),'\n')
# print('Predicted t20yr: ', t20yr_pred.round(2))
tlt_model=stats.lm('Close~t20yr', data=tlt.iloc[int(-252*1.5):]) # last two years
tlt_pred=t20yr_pred*tlt_model[0][1]+tlt_model[0][0]
# print('t20yr to TLT Model\n','Intercept: ',tlt_model[0].round(2)[0],'  Beta: ',tlt_model[0].round(2)[1], '\n')
# print('t20yr & TLT correlation: \n',tlt.iloc[int(-252*1.5):][['t10yr','t20yr']].corr().round(4),'\n')
# print('Predicted TLT Price: ',tlt_pred.round(2)) # 105-92 confidence level

#TODO find the r-squared for these models - maybe run it in r.