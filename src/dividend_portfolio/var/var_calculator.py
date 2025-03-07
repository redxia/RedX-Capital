import pandas as pd
import numpy as np
from utilities import utilities
from datetime import datetime
from datetime import timedelta
import yfinance as yf

start_time=datetime.now()
# date=utilities.last_business(utilities.next_business()).strftime("%Y%m%d") if start_time.hour>16 else utilities.last_business().strftime("%Y%m%d")
# positions=pd.read_excel(r"C:\RedXCapital\Dividends\Data\Position\ibkr_pos_"+date+".xlsx")
# start_date=start_time-timedelta(days=365*2)

#TODO portfolio 5 day return. maybe show the historical

def var_calculator(positions, risk_exposure): #TODO make this as parametric var
    # positions=current_positions.copy()
    # risk_exposure
    # unique_tickers=positions.loc[(positions['Right']=='S') | positions['Right'].isna(),'Class Group'].unique().tolist()
    unique_tickers=pd.unique(risk_exposure[['Beta_Hedge','Class Group']].dropna().values.ravel()).tolist()
    unique_tickers.extend(['^VIX'])
    # unique_tickers.remove('Total')
    historical=yf.download(unique_tickers,start="1989-01-01", end=utilities.next_business().strftime('%Y-%m-%d'))['Close']
    
    portfolio=risk_exposure.loc[:,['Beta_Hedge','Class Group','Beta','Market Value']].dropna()
    systematic_tickers=(portfolio['Beta_Hedge']=='QQQ') | (portfolio['Beta_Hedge']=='SPY')
    returns=historical.pct_change(1)
    
    for idx, row in portfolio.iterrows(): # Historical fill
        returns.loc[returns[row['Class Group']].isna(),row['Class Group']] = returns.loc[returns[row['Class Group']].isna(),row['Beta_Hedge']] * row['Beta'] 
    
    # remove_vix=list(returns.columns)
    # returns[]
    adjusted_returns_5d=returns.add(1).rolling(5).apply(np.prod, raw=True).sub(1)
    adjusted_returns_5d['VIX']=pd.qcut(historical['^VIX'],5,[1,2,3,4,5])
    vix_cut=adjusted_returns_5d['VIX'].iloc[-1]
    adjusted_returns_5d=adjusted_returns_5d.loc[adjusted_returns_5d['VIX']==vix_cut,:]
    del adjusted_returns_5d['VIX']
    
    vix_adj_returns=historical.copy()
        
    for idx, row in portfolio.loc[systematic_tickers].iterrows(): # Historical fill
        adjusted_returns_5d[row['Class Group']+' PnL Sys']=adjusted_returns_5d[row['Class Group']].dropna() * row['Market Value']
    
    Spnl_tickers=[i for i in adjusted_returns_5d.columns if 'PnL Sys' in i]
    adjusted_returns_5d['Systematic PnL']=adjusted_returns_5d[Spnl_tickers].dropna().sum(axis=1)
    
    sz = adjusted_returns_5d['Systematic PnL'].dropna().size-1
    adjusted_returns_5d.loc[adjusted_returns_5d['Systematic PnL'].notna(),'Systematic Percentile'] = adjusted_returns_5d['Systematic PnL'].dropna().rank(method='max').apply(lambda x: (x-1)/sz)
    
    sys_quantile_1=adjusted_returns_5d.loc[(adjusted_returns_5d['Systematic Percentile']-0.01).abs().idxmin()]
    sys_quantile_2=adjusted_returns_5d.loc[(adjusted_returns_5d['Systematic Percentile']-0.05).abs().idxmin()]
    sys_quantile_3=adjusted_returns_5d.loc[(adjusted_returns_5d['Systematic Percentile']-0.1).abs().idxmin()]
    sys_quantile_4=adjusted_returns_5d.loc[(adjusted_returns_5d['Systematic Percentile']-0.9).abs().idxmin()]
    sys_quantile_5=adjusted_returns_5d.loc[(adjusted_returns_5d['Systematic Percentile']-0.95).abs().idxmin()]
    sys_quantile_6=adjusted_returns_5d.loc[(adjusted_returns_5d['Systematic Percentile']-0.99).abs().idxmin()]
    systematic_var=pd.concat([sys_quantile_1,sys_quantile_2,sys_quantile_3,sys_quantile_4,sys_quantile_5,sys_quantile_6], axis=1).T.reset_index(names='Sys Date')
    systematic_columns=[i for i in systematic_var.columns if 'QQQ'==i or 'SPY'==i or '^VIX'==i or ('PnL ' not in i and ' PnL' in i) or 'Percentile' in i or 'Date' in i]
    # systematic_columns.extend(['Sys Date'])
    # systematic_var=systematic_var[['Sys Date','QQQ','SPY','^VIX','Systematic PnL','Portfolio Return']]
    systematic_var=systematic_var[systematic_columns]
    systematic_var['Portfolio Return']=systematic_var['Systematic PnL'] / positions.loc[positions['Class Group']=='Total','Market Value'].values[0]
    systematic_var['Sys Date']=systematic_var['Sys Date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    non_systemmatic=~systematic_tickers
    for idx, row in portfolio.loc[non_systemmatic].iterrows(): # Historical fill
        adjusted_returns_5d[row['Class Group']+' PnL NSys']=adjusted_returns_5d[row['Class Group']].dropna() * row['Market Value']
    NSpnl_tickers=[i for i in adjusted_returns_5d.columns if 'PnL NSys' in i]
    
    adjusted_returns_5d['NSystematic PnL']=adjusted_returns_5d.loc[adjusted_returns_5d['Systematic PnL'].notna(),NSpnl_tickers].sum(axis=1)
    
    adjusted_returns_5d['Total PnL']=adjusted_returns_5d['Systematic PnL'] + adjusted_returns_5d['NSystematic PnL']
    
    sz = adjusted_returns_5d['Total PnL'].dropna().size-1
    adjusted_returns_5d.loc[adjusted_returns_5d['Total PnL'].notna(),'Total Percentile'] = adjusted_returns_5d['Total PnL'].dropna().rank(method='max').apply(lambda x: (x-1)/sz)
    
    nsys_quantile_1=adjusted_returns_5d.loc[(adjusted_returns_5d['Total Percentile']-0.01).abs().idxmin()]
    nsys_quantile_2=adjusted_returns_5d.loc[(adjusted_returns_5d['Total Percentile']-0.05).abs().idxmin()]
    nsys_quantile_3=adjusted_returns_5d.loc[(adjusted_returns_5d['Total Percentile']-0.1).abs().idxmin()]
    nsys_quantile_4=adjusted_returns_5d.loc[(adjusted_returns_5d['Total Percentile']-0.9).abs().idxmin()]
    nsys_quantile_5=adjusted_returns_5d.loc[(adjusted_returns_5d['Total Percentile']-0.95).abs().idxmin()]
    nsys_quantile_6=adjusted_returns_5d.loc[(adjusted_returns_5d['Total Percentile']-0.99).abs().idxmin()]
    nsystematic_var=pd.concat([nsys_quantile_1,nsys_quantile_2,nsys_quantile_3,nsys_quantile_4,nsys_quantile_5,nsys_quantile_6], axis=1).T.reset_index(names='NSys Date')
    nsystematic_columns=[i for i in nsystematic_var.columns if (' Sys' not in i) and (i not in portfolio.loc[systematic_tickers,'Class Group'].to_list())]
    nsystematic_var=nsystematic_var[nsystematic_columns]
    nsystematic_var['Portfolio Return']=nsystematic_var['Total PnL'] / positions.loc[positions['Class Group']=='Total','Market Value'].values[0]
    nsystematic_var['NSys Date']=nsystematic_var['NSys Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    
    portfolio_var=pd.concat([systematic_var,nsystematic_var], axis=1)
    portfolio_var['VIX Cut']=vix_cut #TODO signle name VaR.
    
    return portfolio_var, vix_adj_returns
    
    
    
#     adjusted_returns_5d.loc[adjusted_returns_5d['Systematic PnL'].round(0)==adjusted_returns_5d['Systematic PnL'].quantile(.01).round(0)]
#     adjusted_returns_5d.loc[adjusted_returns_5d['Systematic PnL'].round(0)==adjusted_returns_5d['Systematic PnL'].quantile(.05).round(0)]
#     adjusted_returns_5d.loc[np.isclose(adjusted_returns_5d['Systematic PnL'].round(0),adjusted_returns_5d['Systematic PnL'].quantile(.05).round(0), rtol=.01)]
#     adjusted_returns_5d.loc[adjusted_returns_5d['Systematic PnL'].round(0)==adjusted_returns_5d['Systematic PnL'].quantile(.1).round(0)]
#     adjusted_returns_5d.loc[adjusted_returns_5d['Systematic PnL'].round(0)==adjusted_returns_5d['Systematic PnL'].quantile(.9).round(0)]
#     adjusted_returns_5d.loc[adjusted_returns_5d['Systematic PnL'].round(0)==adjusted_returns_5d['Systematic PnL'].quantile(.95).round(0)]
#     adjusted_returns_5d.loc[adjusted_returns_5d['Systematic PnL'].round(0)==adjusted_returns_5d['Systematic PnL'].quantile(.99).round(0)]
#     # adjusted_returns_5d['Systematic PnL'].quantile(0.1)
#     var_arrays=adjusted_returns_5d['Systematic PnL'].quantile([0.01, 0.05, 0.1, 0.9, 0.95, 0.99])
#     risk_exposure=risk_exposure.loc[risk_exposure['Beta_Hedge']!='Total',:]
    
    
# #TODO use vix buckets
# # historical.reset_index(inplace=True)
    
# del returns['TOTAL']

# class_groups=utilities.read_config_file("ClassGroups.jsonc")

# for idx, row in positions.iterrows():
#     if row['Class Group'] !='Total':
#         try:
#             positions.loc[idx,'Adjustment Factor']=list(class_groups[row['Class Group']].values())[0]
#         except:
#             positions.loc[idx,'Adjustment Factor']=list(class_groups[row['Class Group']].values())[0]

# positions['Symbol']=positions['Symbol'].ffill()
# positions['Effective Delta']=positions['Dollar Delta'] * positions['Adjustment Factor'] #TODO run the regression eventually instead of this
# returns.quantile([0.05,0.95])
# portfolio_returns=pd.DataFrame(index=returns.index)
# del returns['TOTAL']
# for idx, row in positions.loc[positions['Right'].notna(),['Class Group','Symbol','Effective Delta']].iterrows():
#     if row['Symbol']!='Total':
#         portfolio_returns[row['Class Group']]=row['Effective Delta']*returns[row['Symbol']]

# portfolio_returns=pd.concat([portfolio_returns,portfolio_returns.sum(axis=1)], axis=1)
# portforlio_var=portfolio_returns.sum(axis=1).quantile([0.05,0.1,0.9,.95])
# print(portforlio_var)
# print(portfolio_returns.sort_values(0)) #TODO need to get the return series returns.


# import time
# import numpy as np
# import yfinance as yf
# import statsmodels.api as sm
# import pandas as pd
# from utilities import utilities
# from datetime import datetime
# from datetime import timedelta
# from excel import excel
# from sklearn import linear_model
# import pandas.io.formats.excel
# pandas.io.formats.excel.ExcelFormatter.header_style=None

# beta_hedges=utilities.read_config_file("beta_hedge.jsonc")
# leverage_hedge=utilities.read_config_file("leverage_hedge.jsonc")

# start_time=datetime.now()

# def beta_results(df1, df2):
#     model=linear_model.LinearRegression(fit_intercept=True)
#     model_results=model.fit(df2.to_numpy().reshape(-1,1),df1.to_numpy().reshape(-1,1))
#     beta=model_results.coef_[0][0]
#     # beta_fit=sm.OLS(df1,exog=sm.add_constant(df2)).fit()
#     # beta=beta_fit.params.iloc[1]
#     return beta

# def risk_exposures(writer, positions, lookback=2): # amount of years to look back
#     # positions=utilities.read_position_file() 
    
#     positionals_bool=(positions['Symbol'].isna()) & (positions['Right']=='S')

#     positions['Symbol']=positions['Symbol'].ffill()
#     unique_tickers=positions.loc[(positions['Right']!='P') & (positions['Right']!='C'),'Class Group'].unique().tolist()
#     unique_tickers.remove('Total')

#     historical=yf.download(unique_tickers,start=(start_time-timedelta(days=365*lookback+6)).strftime("%Y-%m-%d"), end=start_time.strftime('%Y-%m-%d'))['Close']
#     returns=historical.pct_change().iloc[1:]

#     for idx, row in positions.loc[positionals_bool].iterrows():
#         if row['Class Group']!='Total':
#             positions.loc[idx, 'Beta_Hedge']=beta_hedges[row['Class Group']]
            

#     hedge_df=positions[['Beta_Hedge','Class Group','Market Value']].dropna()

#     for idx, row in hedge_df[['Class Group','Beta_Hedge']].iterrows():
#         historical_returns=returns[[row['Class Group'], row['Beta_Hedge']]].dropna()
#         hedge_df.loc[idx,'Beta']=beta_results(df1=historical_returns[row['Class Group']], df2=historical_returns[row['Beta_Hedge']])
        


#     total_mv=hedge_df.groupby('Beta_Hedge', as_index=False)['Market Value'].sum()
#     hedge_df=hedge_df.merge(total_mv[['Beta_Hedge','Market Value']], on='Beta_Hedge', how='left')
#     hedge_df['Weights']=hedge_df['Market Value_x'] / hedge_df['Market Value_y']
#     hedge_df['Exposure']=hedge_df['Beta'] * hedge_df['Weights']
    
#     del hedge_df['Market Value_y']
#     hedge_df.rename(columns={'Market Value_x':'Market Value'}, inplace=True)
    
#     hedge_df['Underlying Exposure'] = hedge_df['Market Value'] * hedge_df['Beta']
#     hedge_df['Portfolio Weights']=hedge_df['Market Value'] / hedge_df['Market Value'].sum()  #TODO run the sp 500 beta
#     hedge_df.sort_values(['Beta_Hedge','Underlying Exposure','Class Group'], ascending=False, inplace=True)
#     total=hedge_df.sum()
    
#     total_exposures=hedge_df.groupby('Beta_Hedge', as_index=False)['Market Value','Weights','Exposure','Underlying Exposure'].sum()
#     total_exposures['Weights']=total_exposures['Market Value'] / total_exposures['Market Value'].sum()
#     total_exposures.sort_values('Underlying Exposure', inplace=True, ascending=False)
    

#     hedge_df=pd.concat([hedge_df,total_exposures])
    
#     sort_df=pd.DataFrame()
#     for i in total_exposures['Beta_Hedge']:
#         class_group_subset=hedge_df.loc[hedge_df['Beta_Hedge']==i,:] #.sort_values('Underlying Exposure', ascending=False)
#         sort_df=pd.concat([sort_df,class_group_subset])
        
#     hedge_df=sort_df
        
#     for key, value in leverage_hedge.items():
#         hedge_df.loc[hedge_df['Beta_Hedge']==key,'Leverage Hedge']=hedge_df.loc[hedge_df['Beta_Hedge']==key,'Underlying Exposure'] / value
#     hedge_df.loc[hedge_df['Leverage Hedge'].isna(),'Leverage Hedge']=hedge_df.loc[hedge_df['Leverage Hedge'].isna(),'Underlying Exposure']
#     hedge_df=hedge_df[['Beta_Hedge','Class Group','Market Value','Beta','Weights','Exposure','Underlying Exposure','Leverage Hedge','Portfolio Weights']]
#     total['Leverage Hedge']=np.nan
#     total=total[['Beta_Hedge','Class Group','Market Value','Beta','Weights','Exposure','Underlying Exposure','Leverage Hedge','Portfolio Weights']]
#     total['Beta_Hedge']='Total'
#     total['Class Group']=np.nan
#     total['Beta']=np.nan
#     total['Weights']=np.nan
#     total['Exposure']=np.nan
    
#     hedge_df.loc['Total']=total
    
    
        
    
#     # writer=pd.ExcelWriter(directory, engine='xlsxwriter')
#     # positions_original.to_excel(writer, sheet_name='Current Portfolio', index=False)
#     hedge_df.to_excel(writer, sheet_name='Risk Exposures', index=False)
#     # summary_original.to_excel(writer, sheet_name='Account Summary', index=False)
#     # writer=excel.sheet_adj(writer,'Current Portfolio')
#     # writer=excel.sheet_adj(writer,'Account Summary')
#     writer=excel.sheet_adj(writer,'Risk Exposures',num_row=hedge_df.shape[0]+1)
#     # writer.save()
#     # writer.close()
#     # time.sleep(2)
#     # excel.auto_size_wrksht(directory, list(writer.sheets.keys()))
#     return hedge_df, writer

