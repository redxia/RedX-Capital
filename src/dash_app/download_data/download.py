import yfinance as yf
import pandas as pd

def spy_download(): #TODO 10 D 30 D for daily
    spy=yf.download('SPY', start='1994-01-01', progress=False).round(2)
    
    # spy=data.loc[:, (slice(None), 'SPY')]
    spy.columns=spy.columns.get_level_values(0)
    spy['200D_MA']=spy['Close'].rolling(200).mean().round(2)
    spy['200D_EWMA']=spy['Close'].ewm(span=200).mean().round(2)
    
    spy['10D_MA']=spy['Close'].rolling(10).mean().round(2)
    spy['10D_EWMA']=spy['Close'].ewm(span=10).mean().round(2)
      
    spy['30D_MA']=spy['Close'].rolling(30).mean().round(2)
    spy['30D_EWMA']=spy['Close'].ewm(span=30).mean().round(2)
    
    spy['MA_CROSSOVER']=spy['10D_EWMA'] - spy['30D_EWMA']
    
    spy['DIST_200MA'] = spy['Close'] / spy['200D_EWMA'] - 1
    spy['Returns']=spy['Close'].pct_change()
    spy['5D_Ret']=spy['Close'].pct_change(5)
    spy['10D_Ret']=spy['Close'].pct_change(10) #TODO moving average cross average.
    spy['21D_Ret']=spy['Close'].pct_change(21)
    spy['63D_Ret']=spy['Close'].pct_change(21*3) # 3 months
    spy['126D_Ret']=spy['Close'].pct_change(21*6) # 6 months
    spy['189D_Ret']=spy['Close'].pct_change(21*9) # 9 months
    spy['252D_Ret']=spy['Close'].pct_change(252) # 12 months
    
    spy['10D_STD']=spy['Returns'].rolling(10).std() * 252**0.5
    spy['21D_STD']=spy['Returns'].rolling(21).std() * 252**0.5
        
    spy['Drawdown']=spy['Close'] / spy['Close'].cummax() - 1
    
    #TODO year to date performance.
    returns=spy['Returns'].copy()
    returns=returns.reset_index()
    returns['Year']=returns['Date'].dt.year
    returns['Day']=returns.groupby(returns['Year']).cumcount() + 1
    # returns['Day'] = returns['Date'].dt.strftime('%#j').astype(int)

    pivot_df = returns.pivot(index='Day', columns='Year', values='Returns')
    pivot_df.sort_index(ascending=True, inplace=True)

    pivot_df.iloc[:,:-1]=pivot_df.iloc[:,:-1].fillna(0).round(4)
    pivot_df_minus_last=pivot_df.copy().round(4)
    pivot_df_cumulative_nolast=pivot_df_minus_last.apply(lambda x : (1+x).cumprod() -1)
    most_correlated_years=pivot_df_cumulative_nolast.corr().iloc[-1,:].sort_values().iloc[-6:].round(4)
    # print(most_correlated_years)


    pivot_df=pivot_df.fillna(0).round(4)
    pivot_df_cumulative=pivot_df.apply(lambda x : (1+x).cumprod() -1)
    # pivot_df_cumulative[most_correlated_years.index].plot(figsize=(12,12))
    # pivot_df_cumulative_nolast[most_correlated_years.index].tail(20)
    # pivot_df_cumulative[most_correlated_years.index].iloc[20:200,:].round(4).head(30)
    # print(pivot_df_cumulative[most_correlated_years.index])
    spy.reset_index(names='Date', inplace=True)
    spy['Year']=spy['Date'].dt.year
    spy['Day']=spy.groupby(spy['Year']).cumcount() + 1
    return spy, pivot_df, pivot_df_cumulative, most_correlated_years

def vix_downloads():
    data=yf.download(['^VIX3M','^VIX'], start='1994-01-01', progress=False).round(2)
    
    vix=data.loc[:, (slice(None), '^VIX')]['Close']
    vix.columns=vix.columns.get_level_values(0)
    vix.reset_index(names='Date', inplace=True)
    vix['VIX']=pd.qcut(vix['^VIX'],5,[1,2,3,4,5])

    
    vix_3mo=data.loc[:, (slice(None), '^VIX3M')]['Close'].dropna()
    vix_3mo.columns=vix_3mo.columns.get_level_values(0)
    vix_3mo.reset_index(names='Date', inplace=True)
    
    return vix, vix_3mo

def monthly_returns(df): 
    historical_m=df.copy()
    # historical_m['Close']['VIX']
    historical_m.set_index('Date', inplace=True)
    historical_m=historical_m.resample('M').ffill()
    
    monthly_returns=historical_m['Close'].pct_change()
    
    # returns=pd.concat([historical_m[[ticker,'^VIX']],monthly_returns[[ticker,'^VIX','VIX']], yoy_returns, max_drawdown, max_drawup], axis=1)
    returns=monthly_returns # .columns=[ticker,'VIX','Monthly Ret','VIX Ret','VIX Bucket','YoY Returns','Max Drawdown','Max Drawup 1yr']
    returns=returns.reset_index().round({'Close':4})
    returns['Month']=returns['Date'].apply(lambda x: x.strftime('%m'))
    returns['Date']=returns['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    # returns.sort_values('Date', ascending=False, inplace=True)
    return returns

def yearly_returns(df): 
    historical_m=df.copy()
    # historical_m['Close']['VIX']
    historical_m.set_index('Date', inplace=True)
    historical_m=historical_m.resample('Y').ffill()
    
    monthly_returns=historical_m['Close'].pct_change()
    
    # returns=pd.concat([historical_m[[ticker,'^VIX']],monthly_returns[[ticker,'^VIX','VIX']], yoy_returns, max_drawdown, max_drawup], axis=1)
    returns=monthly_returns # .columns=[ticker,'VIX','Monthly Ret','VIX Ret','VIX Bucket','YoY Returns','Max Drawdown','Max Drawup 1yr']
    returns=returns.reset_index()
    returns['Year']=returns['Date'].apply(lambda x: x.strftime('%Y'))
    returns['Date']=returns['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    # returns.sort_values('Date', ascending=False, inplace=True)
    return returns.dropna()

def days_returns(datas, aggregate=1, vix_bucket=3, columns=['Close','^VIX']):
    vix_buckets=datas['VIX']
    del datas['VIX']

    # returns = datas.pct_change(aggregate)
    returns=datas[columns].pct_change(aggregate)
    returns['VIX']=vix_buckets
    returns=returns.loc[returns['VIX']==vix_bucket]
    del returns['VIX']

    if 'VXX' in returns.columns and 'UVXY' in returns.columns:
        returns.loc[returns['VXX'].isna(),'VXX']=returns.loc[returns['VXX'].isna(),'UVXY'] / 1.5
    
    latest=datas[columns].iloc[-1]
    latest.name="Latest"
    avg_returns=pd.Series()
    std_dev=pd.Series()
    win_rate=pd.Series()
    lose_rate=pd.Series()
    average_positive_return=pd.Series()
    average_negative_return=pd.Series()
    qunatile_01=pd.Series()
    qunatile_05=pd.Series()
    qunatile_10=pd.Series()
    qunatile_90=pd.Series()
    qunatile_95=pd.Series()
    qunatile_99=pd.Series()
    for i in returns:
        return_i=returns[i].dropna()
        avg_returns.loc[i]=return_i.mean()
        std_dev.loc[i]=return_i.std()
        win_rate.loc[i] = (return_i > 0).mean()
        lose_rate.loc[i] = (return_i < 0).mean()
        average_positive_return[i]=return_i.loc[return_i>0].mean()
        average_negative_return[i]=return_i.loc[return_i<0].mean()
        qunatile_01[i]=return_i.quantile(.01)
        qunatile_05[i]=return_i.quantile(.05)
        qunatile_10[i]=return_i.quantile(.10)
        qunatile_90[i]=return_i.quantile(.90)
        qunatile_95[i]=return_i.quantile(.95)
        qunatile_99[i]=return_i.quantile(.99)

    qunatile_01.name=str(aggregate)+'_Quantile_01'
    qunatile_05.name=str(aggregate)+'_Quantile_05'
    qunatile_10.name=str(aggregate)+'_Quantile_10'
    qunatile_90.name=str(aggregate)+'_Quantile_90'
    qunatile_95.name=str(aggregate)+'_Quantile_95'
    qunatile_99.name=str(aggregate)+'_Quantile_99'
    avg_returns.name=str(aggregate)+'_Returns'
    std_dev.name=str(aggregate)+'_STD'
    win_rate.name=str(aggregate)+"_Win Rate"
    lose_rate.name=str(aggregate)+"_Lose Rate"
    average_positive_return.name=str(aggregate)+'_Positive Return'
    average_negative_return.name=str(aggregate)+'_Negative Return'
    combined_analysis=pd.concat([latest, avg_returns, std_dev, win_rate, lose_rate, average_positive_return, average_negative_return, qunatile_01, qunatile_05, qunatile_10, qunatile_90, qunatile_95, qunatile_99],axis=1)
    combined_analysis.reset_index(inplace=True)
    combined_analysis.rename(columns={'index':'Symbol'}, inplace=True)
    combined_analysis.sort_values('Symbol', inplace=True)
    return combined_analysis

def std_dev_offset(datas, vix_bucket=3, aggregator=None): # TODO upgrade this based on vix bucket

    if aggregator==None:
        vix_analysis_1=days_returns(datas=datas.copy(), aggregate=1, vix_bucket=vix_bucket)
        vix_analysis_3=days_returns(datas=datas.copy(), aggregate=3, vix_bucket=vix_bucket)
        vix_analysis_5=days_returns(datas=datas.copy(), aggregate=5, vix_bucket=vix_bucket)
        del vix_analysis_3['Latest']
        del vix_analysis_5['Latest']
        del vix_analysis_3['Symbol']
        del vix_analysis_5['Symbol']
        combined_analysis=pd.concat([vix_analysis_1, vix_analysis_3, vix_analysis_5],axis=1).round(4)
        combined_analysis.iloc[:,2:]=combined_analysis.iloc[:,2:] * 100
    else:
        vix_analysis=days_returns(datas=datas.copy(), aggregate=aggregator, vix_bucket=vix_bucket).round(4)
        vix_analysis.iloc[:,2:]=vix_analysis.iloc[:,2:] * 100
        combined_analysis=vix_analysis.copy()
    
    # vix_analysis_1=vix_analysis_1.drop(index=1)
    # vix_analysis_3=vix_analysis_3.drop(index=1)


    # var.iloc[:,2:]=var.iloc[:,2:] * 100
    
    return combined_analysis