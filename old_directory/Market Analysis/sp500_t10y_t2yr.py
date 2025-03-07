import os
import fredapi
import pandas as pd
from datetime import timedelta
import yfinance as yf
from utilities import utilities
from utilities import market_util
import numpy as np
import seaborn as sns
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
pandas2ri.activate()
print('\n')
#fig, ax2 = plt.subplots()
stats=importr('stats')
forecast=importr('forecast')
base=importr('base')
fredapi_key=os.environ.get("fredapi_key")

sp500=yf.download('^GSPC', auto_adjust=True,actions=True, period='max', progress=False)[['Close','Volume','Dividends']]
fred=fredapi.Fred(api_key=fredapi_key)
# list of relevant data series to for loop the download
t10yr_t2yr=fred.get_series_latest_release('T10Y2Y')
sp500=utilities.add_to_df(t10yr_t2yr,'t10yr_t2yr', sp500, interpolation=True)
sp500['Close_ewma']=sp500['Close'].ewm(3).mean()
sp500.dropna(inplace=True)
sp500=market_util.get_returns(sp500,'daily', ewma=True)
print(sp500[['Date','Close','returns_12mo','t10yr_t2yr']].tail())
t10yr_t2yr_model=stats.ar(sp500['t10yr_t2yr'],order_max=1)
print('t10yr-t2yr Ar(1): ',t10yr_t2yr_model[1],'\n')

predicted_t10yr_t2yr=forecast.forecast_ar(t10yr_t2yr_model,h=252)

predicted_t10yr_t2yr_adj=((predicted_t10yr_t2yr[5][:,0]+predicted_t10yr_t2yr[3])/2).round(4)
print("((predicted_t10yr_t2yr[5][:,0]+predicted_t10yr_t2yr[3])/2).round(4)",'\n')
# predicted_t10yr_t2yr_adj=(predicted_t10yr_t2yr[3]).round(4)
# (predicted_t10yr_t2yr[3]+predicted_t10yr_t2yr[4][:,0])/2 #bear case
print('Average Case t10yr_t2yr: ', predicted_t10yr_t2yr_adj.round(4)[-1], '\n')


#after_2021=sp500['Date']>'2021-01-01'
df_regression=sp500.loc[:,['t10yr_t2yr','returns_12mo']].iloc[-(252*2):,:]
print('Correlation matrix between t10yr-t2yr and 12month returns: \n',df_regression.corr().round(4),'\n')
df_regression=df_regression.loc[df_regression['returns_12mo'].notna(),:]
sp500_model=stats.lm('returns_12mo~t10yr_t2yr',data=df_regression)

print('\n')
print("Linear Regression Model: ",sp500_model[0])
print("Standard residual: ",sp500_model[1].std())
print('Predicted 12mo returns SP500: ',(sp500_model[0][0]+sp500_model[0][1]*predicted_t10yr_t2yr_adj)[-1:].round(4)[0], '\n')

print('\n')
print(sp500['t10yr_t2yr'].iloc[-(252*30):].describe())
sp500['t10yr_t2yr'].append(pd.Series(predicted_t10yr_t2yr_adj)).reset_index(drop=True).plot()




# plot if we are on bottom quadrant that means we should be bullish. if we are extreme top right we should bearish

#sp500.index=sp500['Date']
#sp500=sp500.resample('1M').last() # end of month
#sp500.resample('1M').first() # start of month

# sp500['returns_12mo_adj']=sp500['returns_12mo']*sp500['t10yr_t2yr'].max()/sp500['returns_12mo'].max()
# sp500['t10yr_t2yr_lag12']=sp500['t10yr_t2yr'].shift(12)
# sp500.dropna().plot(x='Date',y=['t10yr_t2yr_lag12','returns_12mo_adj'], figsize=(10,6),  grid=True)
# sp500.dropna().plot(x='Date',y='returns_12mo', figsize=(10,6),  grid=True) # TODO time series prediction on sp500 and t10-t2
# sp500.dropna().plot(x='Date',y=['t10yr_t2yr','returns_12mo'], figsize=(10,6),  grid=True) # past two year the correlation is strong
# sp500.dropna().plot(x='Date',y='returns_12mo', figsize=(10,6),  grid=True)
# sp500.dropna().plot(x='t10yr_t2yr',y='returns_24mo', kind='scatter',s=.75, grid=True,xticks=np.arange(-3, 3, .5), yticks=np.arange(-.5, 1, .1), figsize=(12,8)) # this is useless by itself but maybe with random forest or more dimensions
# sp500.dropna().plot(x='t10yr_t2yr',y='returns_18mo', kind='scatter',s=.75, grid=True,xticks=np.arange(-3, 3, .5), yticks=np.arange(-.5, 1, .1), figsize=(12,8)) # this is useless by itself but maybe with random forest or more dimensions
# sp500.dropna().plot(x='t10yr_t2yr',y='returns_12mo', kind='scatter',s=.75, grid=True,xticks=np.arange(-3, 2.5, 1), yticks=np.arange(-.5, .6, .1), figsize=(12,8)) # this is useless by itself but maybe with random forest or more dimensions, bull bear case is useful for this. # or bucketing

sp500.iloc[-(252*3):].plot(x='t10yr_t2yr',y='returns_12mo', kind='scatter',s=.75, grid=True,xticks=np.arange(-3, 2.5, 1), yticks=np.arange(-.5, .6, .1), figsize=(12,8))# this is useless by itself but maybe with random forest or more dimensions, bull bear case is useful for this. # or bucketing

sns.regplot(x='t10yr_t2yr',y='returns_12mo', data=sp500.iloc[-(252*3):], scatter_kws={'s':2})

# for i in range(1,12*21): #two years ahead
#     print('For lag number: '+str(i)+'\n')
#     sp500['t10yr_t2yr_lag'+str(i)]=sp500['t10yr_t2yr'].shift(i)
#     print('Corr 3mo+lag '+str(i)+':',sp500[['returns_3mo','t10yr_t2yr_lag'+str(i)]].corr().iloc[0,1].round(4))
#     print('Corr 6mo+lag '+str(i)+':',sp500[['returns_6mo','t10yr_t2yr_lag'+str(i)]].corr().iloc[0,1].round(4))
#     print('Corr 9mo+lag '+str(i)+':',sp500[['returns_9mo','t10yr_t2yr_lag'+str(i)]].corr().iloc[0,1].round(4))
#     print('Corr 12mo+lag '+str(i)+':',sp500[['returns_12mo','t10yr_t2yr_lag'+str(i)]].corr().iloc[0,1].round(4))
#     print('Corr 18mo+lag '+str(i)+':',sp500[['returns_18mo','t10yr_t2yr_lag'+str(i)]].corr().iloc[0,1].round(4))
#     print('Corr 24mo+lag '+str(i)+':',sp500[['returns_24mo','t10yr_t2yr_lag'+str(i)]].corr().iloc[0,1].round(4))
#     del sp500['t10yr_t2yr_lag'+str(i)]

# sp500[['returns_24mo','t10yr_t2yr']].corr()
# sp500[['returns_12mo','t10yr_t2yr']].corr()
#sp500[['returns_18mo','t10yr_t2yr']].iloc[-48:].corr()
