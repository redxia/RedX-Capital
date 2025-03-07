import pandas as pd
import numpy as np
from utilities import utilities
from datetime import datetime

# start_time=datetime.now()
# date=utilities.last_business(utilities.next_business()).strftime("%Y%m%d") if start_time.hour>16 else utilities.last_business().strftime("%Y%m%d")
# positions=pd.read_excel(r"C:\RedXCapital\Dividends\Data\Position\ibkr_pos_"+date+".xlsx")
# start_date=start_time-timedelta(days=365*2)


# historical=yf.download(positions.loc[positions['Symbol'].notna(),'Symbol'].to_list(),start=(start_time-timedelta(days=365*2+6)).strftime("%Y-%m-%d"), end=utilities.next_business().strftime('%Y-%m-%d'))
# #TODO use vix buckets
# # historical.reset_index(inplace=True)
# returns=historical['Adj Close'].pct_change(5)
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
today=datetime.today()
date=utilities.last_business(utilities.next_business()).strftime("%Y%m%d") if today.hour>=16 else utilities.last_business().strftime("%Y%m%d")

def create_summary(risk_exposure, dividend, alpha, current_positions, portfolio_var, liquidity_df, account_summary, spx_daily, spx_monthly, spx_yearly, svix_daily):
#region summary
    summary=pd.DataFrame([[np.nan]*5]*60)
    summary.iloc[1,2]='RedX'
    summary.iloc[1,4]='Summary Report'
    # summary.iloc[2,4]='Summary Report'
    summary.iloc[3,2]='Report Date'
    summary.iloc[3,4]=date
    
    summary.iloc[5,2]='Risk Based Loss'
    summary.iloc[5,4]=current_positions.loc[current_positions['Class Group']=='Total',"Max Loss"].values[0]
    
    summary.iloc[7,2]='SPY'
    summary.iloc[7,4]=spx_daily['SPY'].iloc[0].round(2)
    summary.iloc[8,2]='VIX'
    summary.iloc[8,4]=spx_daily['VIX'].iloc[0].round(2)
    summary.iloc[9,2]='VIX Bucket'
    vix_quantile=spx_daily['VIX'].quantile([0, .2, .4, .6, .8, 1])
    summary.iloc[9,4]=str(vix_quantile.iloc[spx_daily['VIX Bucket'].dropna().iloc[0]-1].round(2)) +' ' + str(spx_daily['VIX Bucket'].dropna().iloc[0]) + ' ' +str(vix_quantile.iloc[spx_daily['VIX Bucket'].dropna().iloc[0]].round(2))
    summary.iloc[10,2]='SPY 5DRet'
    summary.iloc[10,4]=alpha.loc[alpha['Symbol']=='SPY','5DRet'].round(4).values[0]
    summary.iloc[11,2]='SPY 5VaR90'
    summary.iloc[11,4]=alpha.loc[alpha['Symbol']=='SPY','5VaR95'].round(4).values[0]
    summary.iloc[12,2]='SPY 5VaR10'
    summary.iloc[12,4]=alpha.loc[alpha['Symbol']=='SPY','5VaR05'].round(4).values[0]        
    summary.iloc[13,2]='SPY 21DRet'
    summary.iloc[13,4]=alpha.loc[alpha['Symbol']=='SPY','21DRet'].round(4).values[0] #TODO number of consectuive green days or Red and the positive returns amount or negative
    summary.iloc[14,2]='SPY MTD'
    summary.iloc[14,4]=spx_monthly['Monthly Ret'].iloc[0].round(4)
    summary.iloc[15,2]='SPY 3moRet'
    summary.iloc[15,4]=alpha.loc[alpha['Symbol']=='SPY','3mo'].round(4).values[0]    
    summary.iloc[16,2]='SPY YTD'
    summary.iloc[16,4]=spx_yearly['Yearly Ret'].iloc[0].round(4)
    summary.iloc[17,2]='SPY Max Drawdown'
    summary.iloc[17,4]=spx_daily['Max Drawdown'].iloc[0].round(4)
    summary.iloc[18,2]='SPY Max Drawdown Qunatile'
    summary.iloc[18,4]=spx_daily['Max Drawdown'].quantile([0, .2, .4, .6, .8, 1]).round(4).to_string().replace('\n','\t')
    summary.iloc[19,2]='SPY Max Drawup 1yr'
    summary.iloc[19,4]=spx_daily['Max Drawup 1yr'].iloc[0].round(4)
    summary.iloc[20,2]='SPY Max Drawup 1yr Quantile'
    summary.iloc[20,4]=spx_daily['Max Drawup 1yr'].quantile([0, .2, .4, .6, .8, 1]).round(4).to_string().replace('\n','\t')
    summary.iloc[21,2]='SVIX'
    summary.iloc[21,4]=svix_daily['SVIX'].iloc[0].round(2)
    summary.iloc[22,2]='SVIX 5DRet'
    try:
        summary.iloc[22,4]=alpha.loc[alpha['Symbol']=='SVIX','5DRet'].round(4).values[0]
    except:
        summary.iloc[22,4]=0
    summary.iloc[23,2]='SVIX 5VaR95'
    try:
        summary.iloc[23,4]=alpha.loc[alpha['Symbol']=='SVIX','5VaR95'].round(4).values[0]
    except:
        summary.iloc[23,4]=0
    summary.iloc[24,2]='SVIX 5VaR05'
    try:
        summary.iloc[24,4]=alpha.loc[alpha['Symbol']=='SVIX','5VaR05'].round(4).values[0]        
    except:
        summary.iloc[24,4]=0
    summary.iloc[25,2]='SVIX Max Drawdown'
    summary.iloc[25,4]=svix_daily['Max Drawdown'].iloc[0].round(4)
    summary.iloc[27,2]='SPY Market Value' #TODO make this 
    summary.iloc[27,4]=risk_exposure.loc[(risk_exposure['Beta_Hedge']=='SPY') & (risk_exposure['Class Group'].isna()),'Market Value'].round(0).values[0] #TODO break this down with their respective hedges. in a new column
    summary.iloc[28,2]='SPY Beta'
    summary.iloc[28,4]=risk_exposure.loc[(risk_exposure['Beta_Hedge']=='SPY') & (risk_exposure['Class Group'].isna()),'Exposure'].round(2).values[0]
    summary.iloc[29,2]='QQQ Market Value'
    summary.iloc[29,4]=risk_exposure.loc[(risk_exposure['Beta_Hedge']=='QQQ') & (risk_exposure['Class Group'].isna()),'Market Value'].round(0).values[0]
    summary.iloc[30,2]='QQQ Beta'
    summary.iloc[30,4]=risk_exposure.loc[(risk_exposure['Beta_Hedge']=='QQQ') & (risk_exposure['Class Group'].isna()),'Exposure'].round(2).values[0]    
    summary.iloc[31,2]='Total Underlying Exposure'
    summary.iloc[31,4]=risk_exposure.loc[(risk_exposure['Beta_Hedge']=='Total') & (risk_exposure['Class Group'].isna()),'Underlying Exposure'].round(0).values[0]

    summary.iloc[33,2]='Long Market Value'
    summary.iloc[33,4]=current_positions.loc[current_positions['Symbol'].isna() & current_positions['Market Value'].gt(0),"Market Value"].sum()
    summary.iloc[34,2]='Short Market Value'
    summary.iloc[34,4]=current_positions.loc[current_positions['Symbol'].isna() & current_positions['Market Value'].lt(0),"Market Value"].sum() # TODO delta
    summary.iloc[35,2]='Net Market Value'
    summary.iloc[35,4]=current_positions.loc[current_positions['Symbol'].isna(),"Market Value"].sum()
    summary.iloc[36,2]='Gross Market Value'
    summary.iloc[36,4]=current_positions.loc[current_positions['Symbol'].isna(),"Market Value"].abs().sum()    
    
    summary.iloc[38,2]='Portfolio VaR 95'
    summary.iloc[38,4]=portfolio_var["Total PnL"].iloc[1]
    summary.iloc[39,2]='Portfolio VaR 95 Ret'
    summary.iloc[39,4]=portfolio_var["Portfolio Return"].iloc[1,1]
    summary.iloc[40,2]='Portfolio VaR 05'
    summary.iloc[40,4]=portfolio_var["Total PnL"].iloc[-2]    
    summary.iloc[41,2]='Portfolio VaR 05 Ret'
    summary.iloc[41,4]=portfolio_var["Portfolio Return"].iloc[-2,1]
    summary.iloc[42,3]='Liquidity'
    summary.iloc[42,4]=liquidity_df['Liquidity Model'].sum()
        
    summary.iloc[44,2]='Monthly Income' #TODO filter by lmv
    summary.iloc[44,4]=dividend.loc['Total',"Monthly Income"].round(0)
    summary.iloc[45,2]='Annual Income'
    summary.iloc[45,4]=dividend.loc['Total',"Annual Income"].round(0)
    summary.iloc[46,2]='Dividend Yield'
    summary.iloc[46,4]=dividend.loc['Total',"Dividend Yield"].round(3)

    summary.iloc[48,2]='Maintenance Margin'
    summary.iloc[48,4]=account_summary['MaintMarginReq'].sum()    
    summary.iloc[49,2]='Equity'
    summary.iloc[49,4]=account_summary['NetLiquidation'].sum()
    summary.iloc[50,2]='Leverage'
    summary.iloc[50,4]=current_positions.loc[current_positions['Symbol'].isna(),"Market Value"].abs().sum() / account_summary['NetLiquidation'].sum()
    
    return summary
    