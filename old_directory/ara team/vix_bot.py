from slack_sdk.webhook import WebhookClient
import yfinance as yf
import pandas as pd
from datetime import datetime
from datetime import timedelta
vix_bot_url="https://hooks.slack.com/services/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" #
webhook=WebhookClient(vix_bot_url)
tickers = ['SPY','QQQ', '^VIX','SVXY', 'VXX', "SVIX",'ZIVB','IWM']
tickers.sort()
end_date = pd.Timestamp.now()
vix = yf.download("^VIX", start="1988-01-01", end=(datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d"))['Close']
vix_levels=vix.quantile([0,.2,.4,.6,.8,.9,1]).reset_index(name='levels')
vix_levels.rename(columns={'index':'quintile'},inplace=True)

data = yf.download(tickers, start="1988-01-01", end=(datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d"))['Close']

data['VIX']=pd.qcut(data['^VIX'],5,[1,2,3,4,5])
lastest_bucket=data['VIX'].iloc[-1]
lastest_vix=data['^VIX'].iloc[-1]

def days_returns(datas, aggregate=1, vix_bucket=3):
    vix_buckets=datas['VIX']
    del datas['VIX']

    returns = datas.pct_change(aggregate)
    returns['VIX']=vix_buckets
    returns=returns.loc[returns['VIX']==vix_bucket]
    del returns['VIX']

    if 'VXX' in returns.columns and 'UVXY' in returns.columns:
        returns.loc[returns['VXX'].isna(),'VXX']=returns.loc[returns['VXX'].isna(),'UVXY'] / 1.5
    
    latest=datas.iloc[-1]
    latest.name="Latest"
    avg_returns=pd.Series()
    std_dev=pd.Series()
    win_rate=pd.Series()
    lose_rate=pd.Series()
    average_positive_return=pd.Series()
    average_negative_return=pd.Series()
    var_ret=pd.DataFrame()
    for i in returns:
        return_i=returns[i].dropna()
        avg_returns.loc[i]=return_i.mean()
        std_dev.loc[i]=return_i.std()
        win_rate.loc[i] = (return_i > 0).mean()
        lose_rate.loc[i] = (return_i < 0).mean()
        average_positive_return[i]=return_i.loc[return_i>0].mean()
        average_negative_return[i]=return_i.loc[return_i<0].mean()
        var_ret[i]=(return_i.quantile([.01, .025,.05,.1,.9,.95,.975, .99])*100).round(2)

    avg_returns.name=str(aggregate)+'_Returns'
    std_dev.name=str(aggregate)+'_STD'
    win_rate.name=str(aggregate)+"_Win Rate"
    lose_rate.name=str(aggregate)+"_Lose Rate"
    average_positive_return.name=str(aggregate)+'_Positive Return'
    average_negative_return.name=str(aggregate)+'_Negative Return'
    combined_analysis=pd.concat([latest, avg_returns, std_dev, win_rate, lose_rate, average_positive_return, average_negative_return],axis=1)
    combined_analysis.reset_index(inplace=True)
    combined_analysis.rename(columns={'index':'Symbol'}, inplace=True)
    combined_analysis.sort_values('Symbol', inplace=True)
    var_ret.columns=str(aggregate)+'_'+var_ret.columns
    return combined_analysis,var_ret

def std_dev_offset(datas, vix_bucket=3): # TODO upgrade this based on vix bucket

    vix_analysis_1, var_1=days_returns(datas.copy(), aggregate=1, vix_bucket=vix_bucket)
    vix_analysis_3, var_3=days_returns(datas.copy(), aggregate=3, vix_bucket=vix_bucket)
    vix_analysis_5, var_5=days_returns(datas.copy(), aggregate=5, vix_bucket=vix_bucket)

    #TODO build bollinger bands.
    #TODO assign different sentiment and shocks to ecnomic news and global economy news.
    #TODO shock and economic news. here.
    #TODO UVXY GAP up 3 STD entry.
    del vix_analysis_3['Latest']
    del vix_analysis_5['Latest']
    del vix_analysis_3['Symbol']
    del vix_analysis_5['Symbol']
    combined_analysis=pd.concat([vix_analysis_1, vix_analysis_3, vix_analysis_5],axis=1)
    var=pd.concat([var_1, var_3, var_5],axis=1)
    return combined_analysis, var

#     #TODO build bollinger bands.
#     #TODO assign different sentiment and shocks to ecnomic news and global economy news.
#     #TODO shock and economic news. here.
#     #TODO UVXY GAP up 3 STD entry.


vix_products= yf.download(tickers, start="1988-01-01", end=(datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d"))['Close']

vix_products.index=vix_products.index.astype(str)
# vix_products=pd.concat([vix_products,(vix_products.pct_change()*100).round(2)] , axis=1) # ,(vix_products.pct_change(3)*100).round(2)
# webhook.send(text="Market Levels: \n"+vix_products.tail(12).to_markdown()) # recent prices
webhook.send(text="Market Daily Returns: \n"+(vix_products.pct_change()*100).round(2).tail(12).to_markdown()) # recent returns
webhook.send(text="Market 5-Day Returns: \n"+(vix_products.pct_change(5)*100).round(2).tail(12).to_markdown()) # recent returns
# webhook.send(text="Market 10-Day Returns: \n"+(vix_products.pct_change(10)*100).round(2).tail(12).to_markdown()) # recent returns
# webhook.send(text="Market 21-Day Returns: \n"+(vix_products.pct_change(21)*100).round(2).tail(12).to_markdown()) # recent returns
webhook.send(text="\n        VIX Lagging Quintile: \n"+vix_levels.to_markdown(index=False)+"\n VIX latest bucket: "+str(round(lastest_vix,2))+' | '+str(lastest_bucket))


SPX_Data= yf.download(['SPY','^VIX'], start="1979-12-31", end=(datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d"))['Close'].dropna()
# SPX_Data['VIX']=pd.qcut(SPX_Data['^VIX'],5,[1,2,3,4,5])
historical_m=SPX_Data.resample('M').ffill().copy()
# vix_data=historical_m['VIX']
# del historical_m['VIX']
returns_m=historical_m.pct_change().dropna()
# del returns_m['^VIX']
# returns_m['VIX']=vix_data
returns_m.reset_index('Date', inplace=True)
returns_m['Month']=returns_m['Date'].dt.strftime('%m')
returns_m['Win Rate']=returns_m['SPY']>0
std_months=returns_m.groupby('Month', as_index=False)['SPY'].std()
returns_m=returns_m.groupby('Month', as_index=False)[['SPY','Win Rate']].mean()
returns_m['STD']=std_months['SPY'].copy()
returns_m['Z-Score']=returns_m['SPY']/returns_m['STD']
returns_m['Lose Rate']=1-returns_m['Win Rate']
returns_m[returns_m.columns[1:]]=returns_m[returns_m.columns[1:]].round(4)*100
returns_m=returns_m[['Month','Win Rate','Lose Rate','SPY','STD','Z-Score']]
webhook.send(text="Monthly Returns Seasonality: \n"+(returns_m.to_markdown())) # recent returns




try:
    analysis_0,var_0=std_dev_offset(datas=data.copy(), vix_bucket=lastest_bucket-1)
except:
    pass
analysis_1,var_1=std_dev_offset(datas=data.copy(), vix_bucket=lastest_bucket)
try:
    analysis_2,var_2=std_dev_offset(datas=data.copy(), vix_bucket=lastest_bucket+1)
except:
    pass


# All in level is post ret or +1 std
def send_webhook(df, var, aggregate=1, vix_bucket=2):
    try:
        df=df.loc[df['Symbol']!='^VIX']
        var=var.loc[df['Symbol']!='^VIX']
    except:
        pass
    webhook.send(text='-'*100+'\n'+"*Date: "+datetime.now().strftime("%m/%d/%Y")+'    X Day: '+str(aggregate)+'   Vix Bucket: '+str(vix_bucket) +'*\n'+\
                  'Symbol:          '+df['Symbol'].to_string(index=False).replace('\n','  |  ') + '\n' + \
                  '*Latest:             '+ (df['Latest']).round(2).to_string(index=False).replace('\n',' | ') + '*\n' + \
                  '-1STD Returns:'+ ((df[str(aggregate)+'_Returns']-df[str(aggregate)+'_STD'])*100).round(2).to_string(index=False).replace('\n',' | ') + '\n' + \
                  'Expect Return: '+ ((df[str(aggregate)+'_Returns']*100)).round(2).to_string(index=False).replace('\n','  |  ') + '\n' + \
                  '+1STD Returns:'+ ((df[str(aggregate)+'_Returns']+df[str(aggregate)+'_STD'])*100).round(2).to_string(index=False).replace('\n','  |  ') + '\n' + \
                  '1STD Returns:   '+ ((df[str(aggregate)+'_STD'])*100).round(2).to_string(index=False).replace('\n','  |  ') + '\n' + \
                  '*Expect Level: '+ (df['Latest']*(1+df[str(aggregate)+'_Returns'])).round(2).to_string(index=False).replace('\n',' | ') + '*\n' + \
                  '-2STD Level:  '+ (df['Latest']*(1+df[str(aggregate)+'_Returns']-2*df[str(aggregate)+'_STD'])).round(2).to_string(index=False).replace('\n',' | ') + '\n' + \
                  '*-1STD Level:  '+ (df['Latest']*(1+df[str(aggregate)+'_Returns']-df[str(aggregate)+'_STD'])).round(2).to_string(index=False).replace('\n',' | ') + '*\n' + \
                  '*+1STD Level: '+ (df['Latest']*(1+df[str(aggregate)+'_Returns']+df[str(aggregate)+'_STD'])).round(2).to_string(index=False).replace('\n',' | ') + '*\n' + \
                  '+2STD Level: '+ (df['Latest']*(1+df[str(aggregate)+'_Returns']+2*df[str(aggregate)+'_STD'])).round(2).to_string(index=False).replace('\n',' | ') + '\n' + \
                  'Negative Ret: '+ (df[str(aggregate)+'_Negative Return']*100).round(2).to_string(index=False).replace('\n',' | ') + '\n' + \
                  '*Negative Lvl: '+ (df['Latest']*(1+df[str(aggregate)+'_Negative Return'])).round(2).to_string(index=False).replace('\n',' | ') + '*\n' + \
                  '*Positive Lvl:  '+ (df['Latest']*(1+df[str(aggregate)+'_Positive Return'])).round(2).to_string(index=False).replace('\n',' | ') + '*\n' + \
                  'Positive Ret:   '+ (df[str(aggregate)+'_Positive Return']*100).round(2).to_string(index=False).replace('\n','  |  ') + '\n' + \
                  '*Win Rate:     '+ (df[str(aggregate)+'_Win Rate']*100).round(2).to_string(index=False).replace('\n',' | ') + '*\n' + \
                  '*Lose Rate:     '+ (df[str(aggregate)+'_Lose Rate']*100).round(2).to_string(index=False).replace('\n',' | ') + '*\n'
             )
    quantile_returns=var[[str(aggregate)+'_'+i for i in tickers]] 
    qunatile_levels=(quantile_returns/100+1).mul(analysis_1['Latest'].to_numpy(), axis=1) .round(2)
    webhook.send(text='Quantile Returns: \n'+quantile_returns.to_markdown() + '\n'+'-'*100)
    webhook.send(text='Quantile Levels: \n'+qunatile_levels.to_markdown() + '\n'+'-'*100)
    # webhook.send(text='-'*100)

if not analysis_0.dropna().empty:
    send_webhook(analysis_0, var_0, 1, vix_bucket=lastest_bucket-1)
    send_webhook(analysis_0, var_0, 3, vix_bucket=lastest_bucket-1)
    send_webhook(analysis_0, var_0, 5, vix_bucket=lastest_bucket-1)

send_webhook(analysis_1, var_1, 1, vix_bucket=lastest_bucket)
send_webhook(analysis_1, var_1, 3, vix_bucket=lastest_bucket)
send_webhook(analysis_1, var_1, 5, vix_bucket=lastest_bucket)

if not analysis_2.dropna().empty:
    send_webhook(analysis_2, var_2, 1, vix_bucket=lastest_bucket+1)
    send_webhook(analysis_2, var_2, 3, vix_bucket=lastest_bucket+1)
    send_webhook(analysis_2, var_2, 5, vix_bucket=lastest_bucket+1)

# send_webhook(analysis_3, var_3, 1, vix_bucket=3)
# # send_webhook(analysis_3, var_3, 3, vix_bucket=3) 
# send_webhook(analysis_3, var_3, 5, vix_bucket=3)

# send_webhook(analysis_4, var_4, 1, vix_bucket=4)
# # send_webhook(analysis_4, var_4, 3, vix_bucket=4) 
# send_webhook(analysis_4, var_4, 5, vix_bucket=4)

# send_webhook(analysis_5, var_5, 1, vix_bucket=5)
# send_webhook(analysis_5, var_5, 3, vix_bucket=5)
# send_webhook(analysis_5, var_5, 5, vix_bucket=5)

# send_webhook(analysis_6, var_6, 5, vix_bucket=6)

# analysis_2mo=std_dev_offset(lookback=2)


spy_original=yf.download('SPY', start="1988-01-01", end=(datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d"))
spy_original['Prev_Close']=spy_original['Close'].shift()
spy_original['Returns']=spy_original['Close'].pct_change()
spy_original['Open_Green']=spy_original['Open'] > spy_original['Prev_Close']
spy_original['Green Day']=spy_original['Returns']>0
spy_original.dropna(inplace=True)

matrix = pd.crosstab(spy_original['Open_Green'], spy_original['Green Day'])
probability_space=matrix / spy_original.shape[0]
webhook.send(text="Prob of Red Green: Green Day\n"+(probability_space.round(4)*100).to_markdown()) # recent returns
# Display the result
print(matrix)