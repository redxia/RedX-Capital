from datetime import datetime
import time
import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier
from utilities import utilities
from excel import excel
import pandas.io.formats.excel
pandas.io.formats.excel.ExcelFormatter.header_style=None

alpha_model_dir=r"C:\RedXCapital\Dividends\Data\Alpha Model"
risk_model_dir=r"C:\RedXCapital\Dividends\Data\Risk Model"
portfolio_model_dir=r"C:\RedXCapital\Dividends\Data\Portfolio Model"

def summary_sheet(date=datetime.now().strftime("%Y%m%d")):
    summary=pd.DataFrame([[np.nan]*5]*25)
    summary.iloc[1,2]="Date"
    summary.iloc[1,4]=date
    summary.iloc[3,2]="Cost Basis" # margin
    summary.iloc[3,4]=0
    summary.iloc[4,2]="NMV"
    summary.iloc[4,4]=0
    summary.iloc[5,2]="Total PnL"
    summary.iloc[5,4]=0 # Cost Basis - NMV
    
    summary.iloc[7,2]="Margin"
    summary.iloc[7,4]=0
    summary.iloc[8,2]="GMV"
    summary.iloc[8,4]=0
    summary.iloc[9,2]="Margin/GMV" # requirement
    summary.iloc[9,4]=0
    summary.iloc[10,2]="VaR" # Portfolio VaR 90%, 95, 99 move tabs
    summary.iloc[10,4]=0 # do 90 first
    summary.iloc[11,3]="   21VaR90" # Portfolio VaR 90%, 95, 99 move tabs
    summary.iloc[11,4]=0
    summary.iloc[12,3]="   21ES90%" #90%, 95, 99 #TODO This is probably better.  Learn to hedge this out
    summary.iloc[12,4]=0
    summary.iloc[13,3]="   21 Max Drawdown 90%" #90%, 95, 99 
    summary.iloc[13,4]=0
    summary.iloc[14,2]="   Net Market Dollar Delta"
    summary.iloc[14,4]=0
    summary.iloc[15,2]="Beta VaR" # Portfolio VaR 90%, 95, 99 move tabs
    summary.iloc[15,4]=0 # do 90 first
    summary.iloc[16,3]="   Beta 21VaR90" # Portfolio VaR 90%, 95, 99 move tabs # show the market move scenario
    summary.iloc[16,4]=0
    summary.iloc[17,2]="   Beta 21ES90%" #90%, 95, 99
    summary.iloc[17,4]=0
    summary.iloc[18,2]="   Beta 21 Max Drawdown 90%" #90%, 95, 99
    summary.iloc[18,4]=0
    summary.iloc[19,2]="Net Market Beta"
    summary.iloc[19,4]=0
    return summary

def run_optimizations(portfolio_value, date=datetime.now().strftime("%Y%m%d"), target_beta=.5,option_hedge_delta=.5):
    prev_day=utilities.last_business(datetime.strptime(date,'%Y%m%d')).strftime('%Y%m%d')

    alpha_model=pd.read_csv(alpha_model_dir+'\\'+'alpha_model_'+date+'.csv')
    alpha_model.sort_values('Symbol', inplace=True, ignore_index=True)
    risk_model=pd.read_csv(risk_model_dir+'\\'+'risk_model_'+date+'.csv',index_col=0)
    bounds=pd.read_excel('master_file.xlsx', sheet_name='Bounds')
    alpha_model=alpha_model.merge(bounds, on='Symbol', how='left')
    alpha_model['alpha']=alpha_model['alpha']*alpha_model['Leverage Factor']
    weight_bounds=alpha_model[['Lower','Upper']] #  convert this to a tuple list.
    wgt_bounds=list(weight_bounds.itertuples(index=False, name=None))
    # wgt_bounds.extend([(0.14,.15),(0.14,.15)])
    
    
    mu=alpha_model['alpha']
    # mu=mu.append(pd.Series([.17,.17]), ignore_index=True)
    ef=EfficientFrontier(mu,risk_model, weight_bounds=wgt_bounds)
    ef.tickers=alpha_model['Symbol']
    ef.efficient_risk(5)
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
