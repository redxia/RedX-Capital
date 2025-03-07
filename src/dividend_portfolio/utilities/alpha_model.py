import pandas as pd
# import os
# os.environ["R_HOME"] = r"C:\Program Files\R\R-4.2.1"
# os.environ["PATH"]   = r"C:\Program Files\R\R-4.2.1\bin\x64" + ";" + os.environ["PATH"]
# import rpy2
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import os
from datetime import datetime
import numpy as np
stock_path=r"C:\RedXCapital\Dividends\Data\Symbol"
market_path=r"C:\RedXCapital\Dividends\Data\Market Data"
#TODO beta is actually 3 months

pandas2ri.activate()

stats=importr('stats')
forecast=importr('forecast')

def ar_model(variable):
    model=stats.ar(variable.dropna().values, order_max=10)
    predicted=forecast.forecast_ar(model,h=11)
    return predicted[3].mean() # average predicted

def systemic_model(df):
    beta_mkt=ar_model(df['Mkt_Beta_3mo'])
    beta_mom=ar_model(df['Mom_Beta_3mo'])
    beta_vol=ar_model(df['Vol_Beta_3mo'])
    beta_qual=ar_model(df['Qual_Beta_3mo'])
    return [beta_mkt, beta_mom, beta_vol, beta_qual]# run the multi linear regression then apply the r^2 capping    

def alpha_model_updater(date=datetime.now().strftime("%Y%m%d")):
    symbols=os.listdir(stock_path)
    dividends=pd.read_excel("master_file.xlsx", sheet_name="Master")

    market_prediction=pd.read_csv(r"C:\RedXCapital\Dividends\Data\Market Daily Predictions\market_prediction_"+date+".csv")
    alpha_model=pd.DataFrame(columns=['Symbol', 'alpha', 'sys_alpha_mkt','sys_alpha_mom','sys_alpha_vol','sys_alpha_qual', 'hedge_ratio','shedge_ratio', 'B_Mkt_Delta','R2_Hedge_3mo','div_yld_use','fwd_div_yld', 'exp_fwd_div_yld','RSI_7','RSI_21','Close','ADV_20','Dollar_ADV_20', 'Maxdrawdown_6mo','Maxdrawup_6mo','Returns_10','Returns_42','Returns_1yr','STD_10','STD_42','STD_1yr','R2_Mkt_3mo','R2_Mom_3mo','R2_Vol_3mo','R2_Qual_3mo','R2_multi_ols_3mo','Maxdrawdown_2yr','Maxdrawup_2yr'])    

    for i in symbols:
        ticker=i.split('.')[0]
        print("Working with Stock: ", ticker)
        historical=pd.read_csv(stock_path+'\\'+i)
        historical_betas=systemic_model(historical)
        sector_symbol=dividends.loc[dividends['Symbol']==ticker,'Sector ETF'].values[0] 
        # TODO maybe predict the future of R2 too since that is depended
        # TODO predict future alpha also
        mkt_ret=market_prediction.loc[market_prediction['Symbol']==sector_symbol,'Ret_11'].values[0]
        mom_ret=market_prediction.loc[market_prediction['Symbol']=='MTUM','Ret_11'].values[0]
        vol_ret=market_prediction.loc[market_prediction['Symbol']=='USMV','Ret_11'].values[0]
        qual_ret=market_prediction.loc[market_prediction['Symbol']=='QUAL','Ret_11'].values[0]

        r_squared=historical[['R2_Mkt_3mo','R2_Mom_3mo','R2_Vol_3mo','R2_Qual_3mo']].iloc[-1].to_list()
        max_index=r_squared.index(max(r_squared))
        max_rsq=r_squared.pop(r_squared.index(max(r_squared)))
        second_max=(max_rsq+max(r_squared))/2
        r_squared=[k / second_max for k in r_squared]
        if max_index==0:
            mkt_risk=historical_betas[0]*mkt_ret
            mom_risk=historical_betas[1]*mom_ret*r_squared[0]
            vol_risk=historical_betas[2]*vol_ret*r_squared[1]
            qual_risk=historical_betas[3]*qual_ret*r_squared[2]
        elif max_index==1:
            mkt_risk=historical_betas[0]*mkt_ret*r_squared[0]
            mom_risk=historical_betas[1]*mom_ret
            vol_risk=historical_betas[2]*vol_ret*r_squared[1]
            qual_risk=historical_betas[3]*qual_ret*r_squared[2]
        elif max_index==2:
            mkt_risk=historical_betas[0]*mkt_ret*r_squared[0]
            mom_risk=historical_betas[1]*mom_ret*r_squared[1]
            vol_risk=historical_betas[2]*vol_ret
            qual_risk=historical_betas[3]*qual_ret*r_squared[2]
        elif max_index==3:
            mkt_risk=historical_betas[0]*mkt_ret*r_squared[0]
            mom_risk=historical_betas[1]*mom_ret*r_squared[1]
            vol_risk=historical_betas[2]*vol_ret*r_squared[2]                        
            qual_risk=historical_betas[3]*qual_ret

        exp_ret=((historical['alpha'].iloc[-1]+1)**21-1)+ mkt_risk+mom_risk+vol_risk+qual_risk + (135/historical['RSI_7'].iloc[-1] - 3 )/ 12.5
        # alpha + sysmteic risk + rsi bias adjustment
        #TODO add the expense ratio

        if (historical.loc[:,'Dividends']==0).all(): #historical
            exp_div=0
        elif dividends.loc[dividends['Symbol']==ticker,'Dividend Use'].values[0]=='CUR':
            exp_div=historical.loc[:,'Dividends'].replace(0, np.nan).dropna().iloc[-1:].values[0]
        elif dividends.loc[dividends['Symbol']==ticker,'Dividend Use'].values[0]=='MA6':
            exp_div=historical.loc[:,'Dividends'].replace(0, np.nan).dropna().iloc[-6:].mean()

        if dividends.loc[dividends['Symbol']==ticker,'Div Frequency'].values[0]=='Y':
            div_adjustment=1
        elif dividends.loc[dividends['Symbol']==ticker,'Div Frequency'].values[0]=='BY':
            div_adjustment=1/2
        elif dividends.loc[dividends['Symbol']==ticker,'Div Frequency'].values[0]=='Q':
            div_adjustment=(1/4)
        elif dividends.loc[dividends['Symbol']==ticker,'Div Frequency'].values[0]=='M':
            div_adjustment=(1/12)
        else:
            div_adjustment=1 #TODO compouding so it adds a small biase to monthly. and add percenrage monthly
        exp_div=exp_div/div_adjustment

        exp_div_yld=exp_div / historical['Close'].iloc[-1]

        if dividends.loc[dividends['Symbol']==ticker,'Qualifying Dividends'].values[0]=='Y':
            tax_rate=.2
        elif dividends.loc[dividends['Symbol']==ticker,'Qualifying Dividends'].values[0]=='N':
            tax_rate=.37 # TODO only apply tax rate if it is positive

        total_return=(exp_ret+exp_div_yld)*(1-tax_rate) - dividends.loc[dividends['Symbol']==ticker,'Expense Ratio'].values[0]
        index=symbols.index(ticker+'.csv')
        alpha_model.loc[index, 'Symbol']=ticker
        alpha_model.loc[index, 'alpha']=total_return
        alpha_model.loc[index, 'sys_alpha_mkt']=mkt_risk
        alpha_model.loc[index, 'sys_alpha_mom']=mom_risk
        alpha_model.loc[index, 'sys_alpha_vol']=vol_risk
        alpha_model.loc[index, 'sys_alpha_qual']=qual_risk
        alpha_model.loc[index, 'beta_mkt']=historical['B_Mkt_3mo'].iloc[-1]
        alpha_model.loc[index, 'div_yld_use']=exp_div_yld-dividends.loc[dividends['Symbol']==ticker,'Expense Ratio'].values[0]
        if not (historical.loc[:,'Dividends']==0).all():
            alpha_model.loc[index, 'fwd_div_yld']= ((1-tax_rate)*historical.loc[:,'Dividends'].replace(0, np.nan).dropna().iloc[-1:].values[0] / div_adjustment) / historical['Close'].iloc[-1]  - dividends.loc[dividends['Symbol']==ticker,'Expense Ratio'].values[0]
            alpha_model.loc[index, 'exp_fwd_div_yld']= ((1-tax_rate)*exp_div_yld)  - dividends.loc[dividends['Symbol']==ticker,'Expense Ratio'].values[0]
        else:
            alpha_model.loc[index, 'fwd_div_yld']=0
            alpha_model.loc[index, 'exp_fwd_div_yld']=0
        alpha_model.loc[index, 'hedge_ratio']= historical['B_Hedge_3mo'].iloc[-1]
        alpha_model.loc[index, 'shedge_ratio']= historical['B_SHedge_3mo'].iloc[-1]
        alpha_model.loc[index, 'B_Mkt_Delta']= historical['B_Mkt_Delta'].iloc[-1]
        alpha_model.loc[index, 'R2_Hedge_3mo']= historical['R2_Hedge_3mo'].iloc[-1]
        alpha_model.loc[index, 'RSI_7']= historical['RSI_7'].iloc[-1]
        alpha_model.loc[index, 'RSI_21']= historical['RSI_21'].iloc[-1]
        alpha_model.loc[index, 'Close']= historical['Close'].iloc[-1]
        alpha_model.loc[index, 'ADV_20']= historical['ADV_20'].iloc[-1]
        alpha_model.loc[index, 'Dollar_ADV_20']= historical['Dollar_ADV_20'].iloc[-1]
        alpha_model.loc[index, 'Maxdrawdown_6mo']= (historical['Close'] / historical['Close'].rolling(21*6, min_periods=21*3).max() - 1).iloc[-1]
        alpha_model.loc[index, 'Maxdrawup_6mo']= (historical['Close'] / historical['Close'].rolling(21*6, min_periods=21*3).min()   - 1).iloc[-1]        
        # alpha_model.loc[index, 'Maxdrawup_6mo']= (historical['Close'].rolling(21*6, min_periods=21*3).max()/ historical['Close'].rolling(21*6, min_periods=21*3).min()   - 1).iloc[-1]        
        alpha_model.loc[index, 'Maxdrawdown_2yr']= (historical['Close'].rolling(252).min() / historical['Close'].rolling(252).max() - 1).iloc[-1]
        alpha_model.loc[index, 'Maxdrawup_2yr']= (historical['Close'].rolling(21*6, min_periods=21*3).max() / historical['Close'].rolling(252).max()  - 1).iloc[-1]
        alpha_model.loc[index, ['R2_Mkt_3mo','R2_Mom_3mo','R2_Vol_3mo','R2_Qual_3mo']]=historical[['R2_Mkt_3mo','R2_Mom_3mo','R2_Vol_3mo','R2_Qual_3mo']].iloc[-1].to_list()
        alpha_model.loc[index, 'R2_multi_ols_3mo']=historical['R2_multi_ols_3mo'].iloc[-1]
        alpha_model.loc[index, ['Returns_10','Returns_42','Returns_1yr','STD_10','STD_42','STD_1yr']]=historical[['Returns_10','Returns_42','Returns_1yr','STD_10','STD_42','STD_1yr']].iloc[-1].to_list()
        if historical.loc[historical['Dividends']!=0,'Dividends'].empty:
            alpha_model.loc[index,'last_dvd']=0
        else:
            alpha_model.loc[index,'last_dvd']=historical.loc[historical['Dividends']!=0,'Dividends'].values[-1]

    alpha_model.sort_values('alpha', inplace=True, ascending=False)
    alpha_model.to_csv(r"C:\RedXCapital\Dividends\Data\Alpha Model\alpha_model_"+date+".csv", index=False)        
    return