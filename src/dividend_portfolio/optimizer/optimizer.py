from datetime import datetime
import time
import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier
from pypfopt import EfficientSemivariance
from utilities import utilities
from excel import excel
import pandas.io.formats.excel
pandas.io.formats.excel.ExcelFormatter.header_style=None
from alpha_model import alpha_model
from risk_model import risk_exposures
import yfinance as yf

weight_bounds=pd.DataFrame.from_records(utilities.read_config_file("bounds.jsonc")).T
spy_exp_ret=utilities.read_config_file('expected_return.jsonc')['SPY']

today=datetime.today()
end_of_year=datetime(today.year, 12, 31)
total_days_in_year = (end_of_year - datetime(today.year, 1, 1)).days + 1
days_left = (end_of_year - today).days + 1
percentage_left=days_left / total_days_in_year

def optimize_semivariance(portfolio_value, dividend):
    target_tickers=weight_bounds.index.to_list()
    wgt_bounds=list(weight_bounds.itertuples(index=False, name=None))
    mvo_df=pd.DataFrame({"Symbol":target_tickers,'Lower Bounds':weight_bounds[0],'Upper Bounds':weight_bounds[1]})
    target_tickers.append('QQQ')
    target_tickers.append('SPY')
    target_tickers.append('^VIX')
    historical=yf.download(target_tickers ,start="1989-01-01", end=utilities.next_business().strftime('%Y-%m-%d'))['Close']
    returns=historical.pct_change()

    QQQ_Beta=risk_exposures.beta_results(df1=returns.iloc[-(21*4):,:]['QQQ'], df2=returns.iloc[-(21*4):,:]['SPY'])[0]
    for i in mvo_df['Symbol']: # back fill the data to build covarianx matrix. # Beta fill for expected returns
        historical_returns=returns[[i, 'SPY','QQQ']].dropna().iloc[-(21*4):]
        alpha, spy_beta, qqq_beta=risk_exposures.market_beta(df1=historical_returns[i], df2=historical_returns['SPY'], df3=historical_returns['QQQ']) # alpha is annualized
        mvo_df.loc[mvo_df['Symbol']==i,'Unit SPY Beta'], spy_alpha = risk_exposures.beta_results(df1=historical_returns[i], df2=historical_returns['SPY'])
        mvo_df.loc[mvo_df['Symbol']==i,'Alpha'] = alpha
        mvo_df.loc[mvo_df['Symbol']==i,'SPY Beta'] = spy_beta
        mvo_df.loc[mvo_df['Symbol']==i,'QQQ Beta'] = qqq_beta
        mvo_df.loc[mvo_df['Symbol']==i,'Expected Returns'] = alpha * percentage_left + spy_beta * spy_exp_ret + qqq_beta * spy_exp_ret * QQQ_Beta    
        if i!='SPYU':
            returns.loc[returns[i].isna(),i]= alpha / 252 + spy_beta * returns.loc[returns[i].isna(), 'SPY'] + qqq_beta * returns.loc[returns[i].isna(), 'QQQ'] 
        else:
            returns.loc[returns[i].isna(),i]= 3.98 * returns.loc[returns[i].isna(), 'SPY'] 
    
    returns['VIX']=pd.qcut(historical['^VIX'],5,[1,2,3,4,5])
    latest_vix_cut=returns['VIX'].iloc[-1]
    vix_adj_ret=returns.loc[returns['VIX']==latest_vix_cut,mvo_df['Symbol']].dropna().iloc[-(252*2):,:]
        
    covaraince_matrix=vix_adj_ret.cov()
    mvo_df['Volatility']=np.diag(covaraince_matrix)**0.5  * np.sqrt(252) 
    mvo_df['Avg Downside']=vix_adj_ret[vix_adj_ret<0].mean(axis=0) 
    mvo_df['Downside Std']=vix_adj_ret[vix_adj_ret<0].std(axis=0) 

    # ef=EfficientSemivariance(expected_returns=mvo_df['Expected Returns'].to_numpy(), returns=vix_adj_ret, weight_bounds=wgt_bounds)
    # ef.min_semivariance()
    # SV_Wgt=ef.clean_weights()
    # mvo_df['SV_MVO']=list(SV_Wgt.values())
    # mvo_df['SV_MVO']=mvo_df['SV_MVO'].round(2)
    # print(ef.portfolio_performance(risk_free_rate=0)) # expected returns, semideviation, sortino ratio
    
    # ef=EfficientSemivariance(expected_returns=mvo_df['Expected Returns'].to_numpy(), returns=vix_adj_ret, weight_bounds=wgt_bounds)
    # ef.efficient_risk(max(np.diag(covaraince_matrix)**0.5  * np.sqrt(252)))
    # ER_Wgt=ef.clean_weights()
    # mvo_df['ER_MVO']=list(ER_Wgt.values())
    # print(ef.portfolio_performance(risk_free_rate=0)) # expected returns, semideviation, sortino ratio
    
    ef=EfficientSemivariance(expected_returns=mvo_df['Expected Returns'].to_numpy(), returns=vix_adj_ret, weight_bounds=wgt_bounds) 
    ef.max_quadratic_utility(risk_aversion=1)
    # ef.efficient_return(0.2)
    QU_Wgt=ef.clean_weights()
    print(ef.portfolio_performance(risk_free_rate=0)) # expected returns, semideviation, sortino ratio
    
    mvo_df['EF_QU']=list(QU_Wgt.values())
    mvo_df['EF_QU']=mvo_df['EF_QU'].round(2)
    mvo_df['Portfolio Unit SPY Beta']=mvo_df['EF_QU'] * mvo_df['Unit SPY Beta']
    mvo_df['Portfolio Downside']=mvo_df['EF_QU'] * (mvo_df['Avg Downside'] - mvo_df['Downside Std'])
    mvo_df['Portfolio Alpha']=mvo_df['EF_QU'] * mvo_df['Alpha']
    mvo_df['Portfolio SPY Beta']=mvo_df['EF_QU'] * mvo_df['SPY Beta']
    mvo_df['Portfolio QQQ Beta']=mvo_df['EF_QU'] * mvo_df['QQQ Beta']
    mvo_df['Portfolio Exp Returns']=mvo_df['EF_QU'] * mvo_df['Expected Returns']
    mvo_df['Portfolio Exp Gains']=portfolio_value * mvo_df['Portfolio Exp Returns']
    
    mvo_df=mvo_df.merge(dividend[['Class Group','Quantity','Market Value','Close Price','Weights','Dividend']], left_on='Symbol', right_on='Class Group', how='left').fillna(0)
    del mvo_df['Class Group']
    mvo_df['Target Market Value']=portfolio_value * mvo_df['EF_QU']
    mvo_df['Target Qty'] = mvo_df['Target Market Value'] / mvo_df['Close Price']
    mvo_df['Target Diff MV'] = mvo_df['Target Market Value'] - mvo_df['Market Value']
    mvo_df['Target Diff Qty'] = mvo_df['Target Diff MV'] / mvo_df['Close Price']
    mvo_df['Target Monthly Income'] = mvo_df['Target Qty'] * mvo_df['Dividend']
    mvo_df['Target Annual Income'] = mvo_df['Target Monthly Income'] * 12
    mvo_df.sort_values('Target Diff MV', inplace=True, ascending=False)
    mvo_df.loc['Total']=mvo_df.sum()
    mvo_df.loc['Total',['Symbol', 'Alpha', 'SPY Beta', 'QQQ Beta','Expected Returns','Volatility', 'Avg Downside', 'Downside Std', 'Portfolio Downside']]=np.nan
    
    mvo_df=mvo_df[['Symbol', 'Lower Bounds', 'Upper Bounds', 'EF_QU', 'Portfolio Unit SPY Beta', 'Alpha',
                  'SPY Beta', 'QQQ Beta', 'Expected Returns', 'Portfolio Alpha', 'Portfolio SPY Beta',
                  'Portfolio QQQ Beta', 'Portfolio Exp Returns', 'Portfolio Exp Gains',
                  'Target Market Value', 'Target Diff MV', 'Target Diff Qty', 'Target Monthly Income', 
                  'Target Annual Income','Volatility', 'Avg Downside', 'Downside Std', 'Portfolio Downside']]
    
    #TODO delete UNIT spy beta. Delete Close Price. # delete weights.  delete Market Value delete quantity delete dividend    
    return mvo_df
        

def run_optimizations(portfolio_value, date=datetime.now().strftime("%Y%m%d"), target_beta=.5,option_hedge_delta=.5):
    alpha, cov=alpha_model.optimization_inputs(vix_cut=1)
    alpha.reset_index(names='Symbol', inplace=True)
    weight_bounds=pd.DataFrame.from_records(utilities.read_config_file("bounds.jsonc")).T
    wgt_bounds=list(weight_bounds.itertuples(index=False, name=None))
    alpha.sort_index(inplace=True)
    class_group=utilities.read_config_file("ClassGroups.jsonc")
    weight_bounds.reset_index(names='Symbol', inplace=True)
    weight_bounds['Underlying Symbol']=weight_bounds['Symbol'].apply(lambda x: list(class_group[x].keys())[0])
    weight_bounds.loc[weight_bounds['Symbol']=='ISPY','Underlying Symbol']='ISPY'
    weight_bounds.loc[weight_bounds['Symbol']=='QQQY','Underlying Symbol']='QQQY'
    weight_bounds.loc[weight_bounds['Symbol']=='JEPY','Underlying Symbol']='JEPY'
    weight_bounds.loc[weight_bounds['Symbol']=='FEPI','Underlying Symbol']='FEPI'
    weight_bounds.loc[weight_bounds['Symbol']=='IWMY','Underlying Symbol']='IWMY'
    weight_bounds.loc[weight_bounds['Symbol']=='SVOL','Underlying Symbol']='SVOL'
    weight_bounds.loc[weight_bounds['Symbol']=='TMF','Underlying Symbol']='TMF'
    weight_bounds.loc[weight_bounds['Symbol']=='CRF','Underlying Symbol']='CRF'
    weight_bounds.loc[weight_bounds['Symbol']=='CLM','Underlying Symbol']='CLM'
    weight_bounds=weight_bounds.merge(alpha[['Symbol','Adj Sharpe']], right_on='Symbol', left_on='Underlying Symbol', how='left')
    weight_bounds.set_index('Underlying Symbol', inplace=True)
    weight_bounds['Underlying Symbol']=weight_bounds.index
    cov.reset_index(names='Symbol', inplace=True)
    cov=cov[cov['Symbol'].isin(weight_bounds['Underlying Symbol'])]
    cov=cov.loc[:,cov.columns.isin(weight_bounds['Underlying Symbol'])]
    cov.set_index(weight_bounds['Underlying Symbol'], inplace=True)
    cov=cov*252
    cov=cov.to_numpy()

    mu=weight_bounds['Adj Sharpe'].to_numpy()
    
    # mu=mu.append(pd.Series([.17,.17]), ignore_index=True)
    ef=EfficientSemivariance(mu, cov, weight_bounds=wgt_bounds) # 
    # ef.tickers=weight_bounds['Symbol_x']
    # ef.efficient_risk(0.5)
    # ef.max_sharpe()
    ef.min_semivariance()
    # ef.max_sharpe(0) # todo need to input risk free rate
    weights=ef.clean_weights()
    weights=dict(weights)
    portfolio_model=pd.DataFrame(columns=['Symbol','MVO_Weights'])
    portfolio_model['Symbol']=weights.keys()
    portfolio_model['MVO_Weights']=weights.values()
    portfolio_model['MVO_Weights']=portfolio_model['MVO_Weights'].round(2)

    close_prices=alpha_model[['Symbol','Close']]
    close_prices.set_index('Symbol', inplace=True)
    close_prices=close_prices['Close']
    portfolio_model=portfolio_model.merge(bounds[["Symbol",'Leverage Factor']], on='Symbol',how='left')
    portfolio_model['MVO_Quantity']= ((portfolio_value * portfolio_model['MVO_Weights'].values * portfolio_model['Leverage Factor']) /close_prices.values).round(0)
    portfolio_model['MVO_Mkt_Value']= (portfolio_model['MVO_Quantity'] * close_prices.values ).round(2)
    
    
    
    # portfolio_model['MVO_Mkt_Value']= (portfolio_model['MVO_Quantity'] * close_prices.values).round(2)
    portfolio_model['Close Price']=close_prices.values.round(2)

    print("\nPortfolio Performance (Exp, Vol, Sharpe): \n", ef.portfolio_performance(risk_free_rate=0.0))
    # print(alpha_model) #TODO make a totals columns
    

    portfolio_model=portfolio_model.merge(alpha_model[['Symbol','alpha','div_yld_use','fwd_div_yld','exp_fwd_div_yld','RSI_7','RSI_21','beta_mkt','Maxdrawdown_6mo','Maxdrawup_6mo','R2_multi_ols_3mo','last_dvd','ADV_20','Dollar_ADV_20','hedge_ratio','shedge_ratio', 'B_Mkt_Delta','R2_Hedge_3mo','Maxdrawdown_2yr']], on='Symbol', how='left') # TODO switch lower and upper once stabilized
    portfolio_model['Eff_Beta']=portfolio_model['beta_mkt']*portfolio_model['MVO_Weights']*portfolio_model['Leverage Factor']
    portfolio_model['Maxdrawup_6mo']=portfolio_model['Maxdrawup_6mo']#*portfolio_model['Leverage Factor']
    portfolio_model['Maxdrawdown_6mo']=portfolio_model['Maxdrawdown_6mo']#*portfolio_model['Leverage Factor']
    portfolio_model['Port_Maxdrawdown_6mo']=portfolio_model['Maxdrawdown_6mo']*portfolio_model['MVO_Weights']
    portfolio_model['Port_Maxdrawdup_6mo']=portfolio_model['Maxdrawup_6mo']*portfolio_model['MVO_Weights']
    portfolio_model.drop(columns='Leverage Factor', inplace=True)
    portfolio_model['dvd_income']=portfolio_model['last_dvd']*portfolio_model['MVO_Quantity']
    
    dividends=pd.read_excel('master_file.xlsx', sheet_name='Master')
    hedge_ratio_aggregate=portfolio_model.loc[portfolio_model['MVO_Weights']!=0,['Symbol','hedge_ratio']].merge(dividends[['Symbol','Hedge ETF']], on='Symbol', how='left')
    # shedge_ratio_aggregate=portfolio_model.loc[portfolio_model['MVO_Weights']!=0,['Symbol','shedge_ratio']].merge(dividends[['Symbol','Second Hedge ETF']], on='Symbol', how='left')
    
    hedge_weight=hedge_ratio_aggregate.groupby('Hedge ETF', as_index=False)['hedge_ratio'].sum()
    hedge_ratio_aggregate=hedge_ratio_aggregate.merge(hedge_weight, on='Hedge ETF', how='left')
    hedge_ratio_aggregate['wgt_hedge']=hedge_ratio_aggregate['hedge_ratio_x']/hedge_ratio_aggregate['hedge_ratio_y']
    portfolio_model=portfolio_model.merge(dividends[['Symbol','Hedge ETF']], on='Symbol', how='left')    
    portfolio_model=portfolio_model.merge(hedge_ratio_aggregate[['Symbol','wgt_hedge']], on='Symbol', how='left')      
    portfolio_model.fillna(0,inplace=True)
    portfolio_model['target_beta']=target_beta*portfolio_model['wgt_hedge']
    # portfolio_model['hedge_ratio']=1/portfolio_model['hedge_ratio']
    portfolio_model['Target_Beta_MV']=(portfolio_model['MVO_Mkt_Value']*(1-portfolio_model['target_beta'])/(portfolio_model['target_beta']-portfolio_model['hedge_ratio'])).round(2) 
    portfolio_model['Beta_Neutral_MV']=-(portfolio_model['MVO_Mkt_Value']/portfolio_model['hedge_ratio']).round(2) 


    # shedge_weight=shedge_ratio_aggregate.groupby('Second Hedge ETF', as_index=False)['shedge_ratio'].sum()
    # shedge_ratio_aggregate=shedge_ratio_aggregate.merge(shedge_weight, on='Second Hedge ETF', how='left')
    # shedge_ratio_aggregate['wgt_shedge']=shedge_ratio_aggregate['shedge_ratio_x']/shedge_ratio_aggregate['shedge_ratio_y']
    # portfolio_model=portfolio_model.merge(dividends[['Symbol','Second Hedge ETF']], on='Symbol', how='left')    
    # portfolio_model=portfolio_model.merge(shedge_ratio_aggregate[['Symbol','wgt_shedge']], on='Symbol', how='left')      
    # portfolio_model.fillna(0,inplace=True)
    # portfolio_model['target_beta_s']=target_beta*portfolio_model['wgt_shedge']
    # # portfolio_model['hedge_ratio']=1/portfolio_model['hedge_ratio']
    # portfolio_model['Target_Beta_MV_s']=(portfolio_model['MVO_Mkt_Value']*(1-portfolio_model['target_beta_s'])/(portfolio_model['target_beta_s']-portfolio_model['hedge_ratio'])).round(2) 
    portfolio_model['Beta_Neutral_MV_s']=-(portfolio_model['MVO_Mkt_Value']/portfolio_model['shedge_ratio']).round(2) 
    portfolio_model['Market_Delta']=portfolio_model['B_Mkt_Delta']*portfolio_model['MVO_Quantity']
    portfolio_model['Option_number_hedge']=portfolio_model['Market_Delta']/100/option_hedge_delta
    

    # del portfolio_model['Hedge ETF']
    # del portfolio_model['Second Hedge ETF']
    portfolio_model.sort_values(['MVO_Mkt_Value','Hedge ETF','MVO_Mkt_Value'], ignore_index=True, inplace=True, ascending=False)
    
    portfolio_model.loc[portfolio_model.shape[0],'Symbol']='Total'
    portfolio_model.loc[portfolio_model.shape[0]-1,'Hedge ETF']='Total'
    #portfolio_model.iloc[portfolio_model.shape[0]-1,1:]=portfolio_model.iloc[:-1,1:].sum(numeric_only=True, axis=0)
    portfolio_model.loc[portfolio_model.shape[0]-1,['MVO_Weights', 'MVO_Quantity', 'MVO_Mkt_Value', 'Close Price', 'alpha',       'div_yld_use', 'fwd_div_yld', 'exp_fwd_div_yld', 'RSI_7', 'RSI_21','beta_mkt', 'Maxdrawdown_6mo', 'Maxdrawup_6mo', 'R2_multi_ols_3mo','last_dvd', 'ADV_20', 'Dollar_ADV_20', 'hedge_ratio', 'shedge_ratio','R2_Hedge_3mo', 'Maxdrawdown_2yr', 'Eff_Beta', 'Port_Maxdrawdown_6mo','Port_Maxdrawdup_6mo', 'dvd_income', 'wgt_hedge', 'target_beta', 'Target_Beta_MV', 'Beta_Neutral_MV','Beta_Neutral_MV_s']]=portfolio_model.sum(axis=0)
    portfolio_model.loc[portfolio_model.shape[0]-1,'MVO_Quantity']=np.nan
    portfolio_model.loc[portfolio_model.shape[0]-1,'Close Price']=np.nan

    portfolio_model.loc[portfolio_model.shape[0]-1,'div_yld_use']=np.nan
    portfolio_model.loc[portfolio_model.shape[0]-1,'fwd_div_yld']=np.nan
    portfolio_model.loc[portfolio_model.shape[0]-1,'exp_fwd_div_yld']=np.nan
    portfolio_model['Beta_Neutral_Pct']=portfolio_model['Beta_Neutral_MV']/portfolio_model['MVO_Mkt_Value']
    portfolio_model['Beta_Neutral_s_Pct']=portfolio_model['Beta_Neutral_MV_s']/portfolio_model['MVO_Mkt_Value']
    

    writer=pd.ExcelWriter(portfolio_model_dir+'\\'+"portfolio_model_"+date+".xlsx", engine='xlsxwriter')
    portfolio_model.to_excel(writer, sheet_name='portfolio', index=False)
    writer=excel.sheet_adj(writer,'portfolio')

    writer.save()
    writer.close()

    time.sleep(1)
    # auto_size_wrksht(portfolio_model_dir+'\\'+"portfolio_model_"+date+".xlsx", 'portfolio')


    # portfolio_model.to_csv(portfolio_model_dir+'\\'+"portfolio_model_"+date+".csv", index=False)


