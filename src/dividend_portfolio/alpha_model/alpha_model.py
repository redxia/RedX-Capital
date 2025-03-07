import pandas as pd
import numpy as np
from utilities import utilities

def adjusted_sharpe(vix_adj_returns):
    win_rate=pd.DataFrame(index=vix_adj_returns.columns, columns=['Positive_Returns','Win_Rate','Negative_Returns'])

    for column in vix_adj_returns:
        win_rate.loc[column,'Win_Rate']=(vix_adj_returns[column].dropna()>0).mean()
        win_rate.loc[column,'Positive_Returns']=(vix_adj_returns.loc[vix_adj_returns[column].gt(0), column]).mean()
        win_rate.loc[column,'Negative_Returns']=(vix_adj_returns.loc[vix_adj_returns[column].lt(0), column]).mean()

    win_rate['Lose_Rate']=(1-win_rate['Win_Rate'])

    win_rate['Adj Sharpe']=(win_rate['Win_Rate'] * win_rate['Positive_Returns']) / (win_rate['Lose_Rate'] * win_rate['Negative_Returns'].abs()) - 1
        
    # win_rate.sort_values('Adj Sharpe',ascending=False, inplace=True)
    return win_rate

def expected_returns():
    exp_returns=utilities.read_config_file("expected_return.jsonc")
    exp_returns['SPY']
    pass

def alpha(historical, risk_exposure):
    # historical=vix_adj_returns.copy()
    returns=historical.pct_change()
    portfolio=risk_exposure.loc[:,['Beta_Hedge','Class Group','Beta','Market Value']].dropna()
    for idx, row in portfolio.iterrows(): # Historical fill
        returns.loc[returns[row['Class Group']].isna(),row['Class Group']] = returns.loc[returns[row['Class Group']].isna(),row['Beta_Hedge']] * row['Beta'] 
    
    adjusted_returns_5d=returns.add(1).rolling(5).apply(np.prod, raw=True).sub(1).iloc[-1]
    adjusted_returns_10d=returns.add(1).rolling(10).apply(np.prod, raw=True).sub(1).iloc[-1]
    adjusted_returns_21d=returns.add(1).rolling(21).apply(np.prod, raw=True).sub(1).iloc[-1]
    adjusted_returns_3m=returns.add(1).rolling(21*3).apply(np.prod, raw=True).sub(1).iloc[-1]
    adjusted_returns_6m=returns.add(1).rolling(21*6).apply(np.prod, raw=True).sub(1).iloc[-1]
    adjusted_returns_9m=returns.add(1).rolling(21*9).apply(np.prod, raw=True).sub(1).iloc[-1]
    adjusted_returns_1yr=returns.add(1).rolling(252).apply(np.prod, raw=True).sub(1).iloc[-1]
    
    recent_returns=pd.concat([adjusted_returns_5d, adjusted_returns_10d, adjusted_returns_21d, adjusted_returns_3m, adjusted_returns_6m, adjusted_returns_9m, adjusted_returns_1yr], axis=1).reset_index()
    recent_returns.columns=['Symbol','5DRet','10DRet','21DRet','3mo','6mo','9mo','1yr']
    
    monthly_returns=historical.resample('M').ffill().pct_change()
    # for idx, row in portfolio.iterrows(): # Historical fill
    #     monthly_returns[row['Class Group']] = monthly_returns[row['Beta_Hedge']] * row['Beta'] 
    for idx, row in portfolio.iterrows(): # Historical fill
        monthly_returns.loc[monthly_returns[row['Class Group']].isna(),row['Class Group']] = monthly_returns.loc[monthly_returns[row['Class Group']].isna(),row['Beta_Hedge']] * row['Beta']         
    monthly_returns=monthly_returns.iloc[-4:].reset_index(names='Symbol')
    monthly_returns['Symbol']=monthly_returns['Symbol'].apply(lambda x: x.strftime("%Y-%m-%d")) # TODO fix those with nans as YTD back fill
    monthly_returns=monthly_returns.T
    monthly_returns.columns=monthly_returns.iloc[0]
    monthly_returns=monthly_returns.iloc[1:] #.reset_index(names='Symbol')
    
    # monthly=historical.copy()
    # monthly['VIX']=pd.qcut(historical['^VIX'],4,[1,2,3,4])
    # vix_cut=monthly['VIX'].iloc[-1]
    # monthly=monthly.resample('M').ffill()
    # adj_vix=monthly['VIX']==vix_cut
    # del monthly['VIX']
    # monthly_returns=monthly.pct_change()
    # for idx, row in portfolio.iterrows(): # Historical fill
    #     monthly_returns[row['Class Group']] = monthly_returns[row['Beta_Hedge']] * row['Beta'] 
    # # monthly_std=monthly_std.std()    
    # monthly_returns=monthly_returns.loc[adj_vix,:]
    # monthly_std=monthly_returns.std()
        
    yearly_returns=historical.resample('Y').ffill().pct_change()
    # for idx, row in portfolio.iterrows(): # Historical fill
    #     yearly_returns[row['Class Group']] = yearly_returns[row['Beta_Hedge']] * row['Beta'] 
    for idx, row in portfolio.iterrows(): # Historical fill
        yearly_returns.loc[yearly_returns[row['Class Group']].isna(),row['Class Group']] = yearly_returns.loc[yearly_returns[row['Class Group']].isna(),row['Beta_Hedge']] * row['Beta']         
    yearly_returns=yearly_returns.iloc[-3:].reset_index(names='Symbol')
    yearly_returns['Symbol']=yearly_returns['Symbol'].apply(lambda x: x.strftime("%Y-%m-%d")) # TODO fix those with nans as YTD back fill
    yearly_returns=yearly_returns.T
    yearly_returns.columns=yearly_returns.iloc[0]
    yearly_returns=yearly_returns.iloc[1:] #.reset_index(names='Date')
    
    long_returns=pd.concat([monthly_returns,yearly_returns], axis=1).reset_index(drop=True)
    
    historical_returns=pd.concat([recent_returns,long_returns], axis=1)

    returns_21D=returns.add(1).rolling(21).apply(np.prod, raw=True).sub(1)
    returns_5d=returns.add(1).rolling(5).apply(np.prod, raw=True).sub(1)
    
    returns['VIX']=pd.qcut(historical['^VIX'],5,[1,2,3,4,5])
    vix_cut=returns['VIX'].iloc[-1]
    vix_adj=returns['VIX']==vix_cut
    del returns['VIX']
    returns=returns.loc[vix_adj,:] 
    adj_sharpe=adjusted_sharpe(returns.copy()).reset_index(drop=True)
    
    
    returns_5d=returns_5d.loc[vix_adj] 
    returns_21D=returns_21D.loc[vix_adj]
    
    
    alpha_model=pd.concat([historical_returns,adj_sharpe], axis=1)
    #TODO add the maximum drawdown.
    
    for column in returns:
        alpha_model.loc[alpha_model['Symbol']==column,'5VaR99']=returns_5d[column].dropna().quantile(0.01) #TODO need to investiate what is wrong with this var. it is too low
        alpha_model.loc[alpha_model['Symbol']==column,'5VaR95']=returns_5d[column].dropna().quantile(0.05)
        alpha_model.loc[alpha_model['Symbol']==column,'5VaR90']=returns_5d[column].dropna().quantile(0.1)
        alpha_model.loc[alpha_model['Symbol']==column,'5VaR10']=returns_5d[column].dropna().quantile(0.9)
        alpha_model.loc[alpha_model['Symbol']==column,'5VaR05']=returns_5d[column].dropna().quantile(0.95)
        alpha_model.loc[alpha_model['Symbol']==column,'5VaR01']=returns_5d[column].dropna().quantile(0.99)
        alpha_model.loc[alpha_model['Symbol']==column,'5Mean']=returns_5d[column].dropna().mean()
        alpha_model.loc[alpha_model['Symbol']==column,'5STD']=returns_5d[column].dropna().std()
        alpha_model.loc[alpha_model['Symbol']==column,'21Mean']=returns_21D[column].dropna().mean()
        alpha_model.loc[alpha_model['Symbol']==column,'21STD']=returns_21D[column].dropna().std()
        
        # print(returns[column].dropna().quantile([0.01,0.05,0.1, 0.9, 0.95, 0.99]))
    
    alpha_model.sort_values('5DRet', inplace=True, ascending=True)
    
    return alpha_model