import time
import numpy as np
import yfinance as yf
import statsmodels.api as sm
import pandas as pd
from utilities import utilities
from datetime import datetime
from datetime import timedelta
from excel import excel
from sklearn import linear_model
from datetime import datetime
import requests
import os
import json
import time
import pandas.io.formats.excel
pandas.io.formats.excel.ExcelFormatter.header_style=None

beta_hedges=utilities.read_config_file("beta_hedge.jsonc")
leverage_hedge=utilities.read_config_file("leverage_hedge.jsonc")
expect_spy_ret=utilities.read_config_file("expected_return.jsonc")
api_key=os.environ.get('polygon_api')
class_group=utilities.read_config_file('ClassGroups.jsonc')
start_time=datetime.now()

def beta_results(df1, df2):
    model=linear_model.LinearRegression(fit_intercept=True)
    model_results=model.fit(df2.to_numpy().reshape(-1,1),df1.to_numpy().reshape(-1,1))
    beta=model_results.coef_[0][0]
    alpha=model_results.intercept_[0]
    return beta, alpha

def risk_exposures(positions, lookback=1): # amount of years to look back
    positionals_bool=(positions['Symbol'].isna()) & (positions['Right']=='S')

    positions['Symbol']=positions['Symbol'].ffill()
    for idx, row in positions.loc[positionals_bool].iterrows():
        if row['Class Group']!='Total':
            positions.loc[idx, 'Beta_Hedge']=beta_hedges[row['Class Group']]

    hedge_df=positions[['Beta_Hedge','Class Group','Market Value']].dropna()

    # unique_tickers=positions.loc[(positions['Right']!='P') & (positions['Right']!='C'),'Class Group'].unique().tolist()
    # unique_tickers.remove('Total')
    unique_tickers=pd.unique(hedge_df[['Beta_Hedge','Class Group']].values.ravel()).tolist()

    historical=yf.download(unique_tickers,start=(start_time-timedelta(days=365*lookback+6)).strftime("%Y-%m-%d"), end=utilities.next_business().strftime('%Y-%m-%d'))['Close']
    returns=historical.pct_change().iloc[1:]

    for idx, row in hedge_df[['Class Group','Beta_Hedge']].iterrows():
        historical_returns=returns[[row['Class Group'], row['Beta_Hedge']]].dropna().iloc[-(21*4):]
        hedge_df.loc[idx,'Beta']=beta_results(df1=historical_returns[row['Class Group']], df2=historical_returns[row['Beta_Hedge']])[0]
        class_group[row['Class Group']][row['Beta_Hedge']]=hedge_df.loc[idx,'Beta']
        
    with open ('ClassGroups.jsonc', 'w') as outfile:
        json.dump(class_group, outfile, indent=4)

    total_mv=hedge_df.groupby('Beta_Hedge', as_index=False)['Market Value'].sum()
    hedge_df=hedge_df.merge(total_mv[['Beta_Hedge','Market Value']], on='Beta_Hedge', how='left')
    hedge_df['Weights']=hedge_df['Market Value_x'] / hedge_df['Market Value_y']
    hedge_df['Exposure']=hedge_df['Beta'] * hedge_df['Weights']
    
    del hedge_df['Market Value_y']
    hedge_df.rename(columns={'Market Value_x':'Market Value'}, inplace=True)
    
    hedge_df['Underlying Exposure'] = hedge_df['Market Value'] * hedge_df['Beta']
    hedge_df['Portfolio Weights']=hedge_df['Market Value'] / hedge_df['Market Value'].sum()  #TODO run the sp 500 beta
    hedge_df.sort_values(['Beta_Hedge','Underlying Exposure','Class Group'], ascending=False, inplace=True)
    total=hedge_df.sum()
    
    total_exposures=hedge_df.groupby('Beta_Hedge', as_index=False)['Market Value','Weights','Exposure','Underlying Exposure'].sum()
    total_exposures['Weights']=total_exposures['Market Value'] / total_exposures['Market Value'].sum()
    total_exposures.sort_values('Underlying Exposure', inplace=True, ascending=False)
    

    hedge_df=pd.concat([total_exposures, hedge_df])
    
    sort_df=pd.DataFrame()
    for i in total_exposures['Beta_Hedge']:
        class_group_subset=hedge_df.loc[hedge_df['Beta_Hedge']==i,:] #.sort_values('Underlying Exposure', ascending=False)
        sort_df=pd.concat([sort_df,class_group_subset])
        
    hedge_df=sort_df.copy()
    hedge_df.reset_index(drop=True, inplace=True)
    polygon_date=utilities.last_business(utilities.next_business()).strftime('%Y-%m-%d')  if datetime.now().hour>=16 else utilities.last_business().strftime('%Y-%m-%d') 
    
    for idx, row in hedge_df.iterrows():
        if row['Beta_Hedge']=='QQQ':
            value=2.97
            ticker='TQQQ'
        elif row['Beta_Hedge']=='SPY':
            value=3.97
            ticker='SPYU'
        elif row['Beta_Hedge']=='TLT':
            value=2.97
            ticker="TMF"
        else:
            ticker=row['Beta_Hedge']
            value=1
        hedge_df.loc[idx, 'Leverage Hedge']=hedge_df.loc[idx,'Underlying Exposure'] / value
        close_price=requests.get("https://api.polygon.io/v1/open-close/"+ticker+"/"+polygon_date+"?adjusted=true&apiKey="+api_key).json()['close']
        hedge_df.loc[idx,'Leverage Shares']=(hedge_df.loc[idx,'Leverage Hedge'] / close_price).round(0)
        
        
    # hedge_df.loc[hedge_df['Leverage Hedge'].isna(),'Leverage Hedge']=hedge_df.loc[hedge_df['Leverage Hedge'].isna(),'Underlying Exposure']
    hedge_df=hedge_df[['Beta_Hedge','Class Group','Market Value','Beta','Weights','Exposure','Underlying Exposure','Leverage Hedge','Leverage Shares','Portfolio Weights']]
    total['Leverage Hedge']=np.nan
    total['Leverage Shares']=np.nan
    total=total[['Beta_Hedge','Class Group','Market Value','Beta','Weights','Exposure','Underlying Exposure','Leverage Hedge','Leverage Shares','Portfolio Weights']]
    total['Beta_Hedge']='Total'
    total['Class Group']=np.nan
    total['Beta']=np.nan
    total['Weights']=np.nan
    total['Exposure']=np.nan
    
    hedge_df.loc['Total']=total
    
    return hedge_df, returns

def market_beta(df1, df2, df3):
    X = np.column_stack((df2, df3))
    y = df1.to_numpy().reshape(-1,1)
    model=linear_model.LinearRegression(fit_intercept=True)
    model_results=model.fit(X, y)    
    alpha=model_results.intercept_[0]
    spy_beta=model_results.coef_[0][0]
    QQQ_beta=model_results.coef_[0][1]
    return alpha * 252, spy_beta, QQQ_beta

def portfolio_beta(risk_exposure, returns):
    today=datetime.today()
    end_of_year=datetime(today.year, 12, 31)
    total_days_in_year = (end_of_year - datetime(today.year, 1, 1)).days + 1
    days_left = (end_of_year - today).days + 1
    percentage_left=days_left / total_days_in_year
    risk_exposure=risk_exposure.dropna()[['Beta_Hedge','Class Group','Market Value','Portfolio Weights']]
    risk_exposure['QQQ Beta']=np.nan
    risk_exposure['SPY Beta']=np.nan
    QQQ_Beta=beta_results(df1=returns.iloc[-(21*4):,:]['QQQ'], df2=returns.iloc[-(21*4):,:]['SPY'])[0]
    for idx, row in risk_exposure.iterrows(): 
        historical_returns=returns[[row['Class Group'], 'SPY','QQQ']].dropna().iloc[-(21*4):]
        if row['Beta_Hedge']=='QQQ':
            risk_exposure.loc[idx, 'QQQ Beta']=beta_results(df1=historical_returns[row['Class Group']], df2=historical_returns['QQQ'])[0]
            # risk_exposure.loc[idx, 'Net QQQ Beta'] = risk_exposure.loc[idx, 'QQQ Beta'] * risk_exposure.loc[idx, 'Portfolio Weights']
        else:
            risk_exposure.loc[idx, 'SPY Beta'], alpha_spy=beta_results(df1=historical_returns[row['Class Group']], df2=historical_returns['SPY'])
            # risk_exposure.loc[idx, 'Net SPY Beta'] = risk_exposure.loc[idx, 'SPY Beta'] * risk_exposure.loc[idx, 'Portfolio Weights']
            
        risk_exposure.loc[idx, 'SPY Beta'], alpha_spy=beta_results(df1=historical_returns[row['Class Group']], df2=historical_returns['SPY']) # SPY market only
        risk_exposure.loc[idx, 'Wgt SPY Beta'] = risk_exposure.loc[idx, 'SPY Beta'] * risk_exposure.loc[idx, 'Portfolio Weights']
        risk_exposure.loc[idx, 'Exp Ret SPY 5%'] = risk_exposure.loc[idx, 'SPY Beta'] * .05  + percentage_left * alpha_spy * 252 # 5% move
        risk_exposure.loc[idx, 'Exp SPY Gains'] = risk_exposure.loc[idx, 'Exp Ret SPY 5%'] * risk_exposure.loc[idx, 'Portfolio Weights'] * risk_exposure.loc[idx, 'Market Value'] 
        
        
        alpha, spy_beta, qqq_beta=market_beta(df1=historical_returns[row['Class Group']], df2=historical_returns['SPY'], df3=historical_returns['QQQ']) # alpha is annualized
        risk_exposure.loc[idx, 'Alpha']=alpha
        risk_exposure.loc[idx, 'Portfolio SPY Beta']=spy_beta
        risk_exposure.loc[idx, 'Portfolio QQQ Beta']=qqq_beta
        risk_exposure.loc[idx, 'Portfolio Wgt SPY Beta']=spy_beta * risk_exposure.loc[idx, 'Portfolio Weights']
        risk_exposure.loc[idx, 'Portfolio Wgt QQQ Beta']=qqq_beta * risk_exposure.loc[idx, 'Portfolio Weights']
        adj_alpha_ytd= alpha * percentage_left
        risk_exposure.loc[idx, 'Exp Ret 2%']=  alpha / 252 + spy_beta * .02 + qqq_beta * .02 * QQQ_Beta
        risk_exposure.loc[idx, 'Exp Ret 5%']= alpha / 252 * 21 + spy_beta * .05 + qqq_beta * .05 * QQQ_Beta
        risk_exposure.loc[idx, 'Expected Returns Yr']= adj_alpha_ytd + spy_beta * expect_spy_ret['SPY'] + qqq_beta * expect_spy_ret['SPY'] * QQQ_Beta
        risk_exposure.loc[idx, 'Expected 5% Gains'] = (risk_exposure.loc[idx, 'Exp Ret 5%'] * risk_exposure.loc[idx,'Market Value']) 
        
        risk_exposure.loc[idx, 'Expected Gains'] = risk_exposure.loc[idx, 'Expected Returns Yr'] * risk_exposure.loc[idx,'Market Value']
    del risk_exposure['Beta_Hedge']
    risk_exposure.sort_values('Expected Returns Yr', inplace=True, ascending=False)
    risk_exposure.loc['Total']=risk_exposure.sum()
    risk_exposure.loc['Total','Class Group']='Total'
    risk_exposure.loc['Total',['QQQ Beta','SPY Beta','Exp Ret SPY 5%','Alpha','Portfolio SPY Beta','Portfolio QQQ Beta','Exp Ret 2%','Exp Ret 5%','Expected Returns Yr']]=np.nan
    beta_exposures=risk_exposure.copy()
    return beta_exposures