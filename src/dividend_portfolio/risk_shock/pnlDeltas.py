import pandas as pd
import jstyleson
import numpy as np
from datetime import datetime
import numpy as np
from excel import excel
import pandas.io.formats.excel
pandas.io.formats.excel.ExcelFormatter.header_style=None
from utilities import utilities
from datetime import timedelta
import fredapi
import os
from black_scholes import black_scholes
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
fred = fredapi.Fred(api_key=os.environ.get("fredapi_key"))
fed_funds_rate = fred.get_series('DFF').tail(1)[0]

def read_config_file(jsonc_config):
    config=open(jsonc_config,'r')
    config_dict=jstyleson.load(config)
    config.close()
    return config_dict

def risk_shock(current_positions):
    positions=current_positions.copy()
    positions['Weight']=positions['Market Value']/positions['Market Value'].sum()

    class_groups=read_config_file('ClassGroups.jsonc')  
    
    # Spot shock
    base_file_columns=positions.columns.to_list()

    percentage_values = [-50, -40, -30, -25, -20, -15, -12.5, -10, -7.5, -5, -3, -2, -1, 1, 2, 3, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50]

    for pct in percentage_values:
        # if pct < 0:
            # positions.loc[positions['Type'] == 'STK', f'{pct}%'] = positions.loc[positions['Type'] == 'STK', 'MV'] * (pct / 100)
        # else:
        positions.loc[positions['Sec Type'] == 'STK', f'{pct}%'] = positions.loc[positions['Sec Type'] == 'STK', 'Market Value'] * (pct / 100) #TODO avg cost mv for now. make this to actual mv

    new_columns=list(set(positions.columns.to_list()) - set(base_file_columns))

    for key, values in class_groups.items(): # this symmetrical logic only applies to stocks
        positions.loc[positions['Underlying'].str.contains(key),'Class Group']=list(values.keys())[0] # identify the class group
        positions.loc[positions['Underlying'].str.contains(key),'Factor']=list(values.values())[0]
        try:
            positions.loc[positions['Symbol']==key,new_columns]=positions.loc[np.logical_or(positions['Symbol']==key, positions['Class Group']==list(values.keys())[0]),new_columns]*list(values.values())[0] # Apply the underlying etfs
        except:
            pass

    #TODO add VaR
    risk_free_rate = fed_funds_rate/100 #TODO need to automate this
    covered_calls=positions.loc[positions['Underlying']==positions['Symbol'],'Underlying'].unique()
    positions.loc[np.logical_and(positions['Sec Type']=='OPT',positions['Underlying'].isin(covered_calls)),'Strategy']=np.nan
    positions['Theta']=0
    positions['Delta']=1
    positions['Dollar Delta']=positions['Quantity']*positions['Close Price'] # TODO build out covered call identifier
    
    for idx, row in positions.iterrows():
        if row['Sec Type']=="OPT": # Pull in the greeks
            positions.loc[idx, 'Theta']=black_scholes.theta(row['Underlying Price'], row['Strike'], row['TTM'], risk_free_rate, row['Implied Volatility'], row['Right']) * row['Quantity']  * 100
            positions.loc[idx, 'Delta']=black_scholes.delta(row['Underlying Price'], row['Strike'], row['TTM'], risk_free_rate, row['Implied Volatility'], row['Right']) * row['Quantity'] * row['Factor']
            positions.loc[idx,'Dollar Delta']=black_scholes.delta(row['Underlying Price'], row['Strike'], row['TTM'], risk_free_rate, row['Implied Volatility'], row['Right'])  * 100 * row['Quantity'] * row['Underlying Price'] * row['Factor']
            
    for pct in percentage_values: # Add beta shocks on top of this
        for idx, row in positions.iterrows():
            # if row['Factor']<0:
            adj_pct=pct * row['Factor'] if row['Factor'] < 0 else pct
            if row['Sec Type']!='STK': # if it is short we should flip #TODO fix this this is recalculated too many times
                if row['Strategy']=="CoveredCall":
                    if row['Underlying Price']*(1+adj_pct/100)>=row['Strike']:
                        bs_price=-row['Market Value']
                        positions.loc[positions['Symbol']==row['Underlying'], f'{pct}%']=(positions.loc[positions['Symbol']==row['Underlying'], 'Quantity']*row['Strike'] - positions.loc[positions['Symbol']==row['Underlying'], 'Market Value']).values[0]
                    else:
                        bs_price=black_scholes.black_scholes(row['Underlying Price']*(1+adj_pct/100), row['Strike'], row['TTM'], risk_free_rate * row['Factor'], row['Implied Volatility'], row['Right'])  * 100 * row['Quantity'] - row['Market Value']
                    positions.loc[idx, f'{pct}%']=bs_price
                else:
                    bs_price=black_scholes.black_scholes(row['Underlying Price']*(1+adj_pct/100), row['Strike'], row['TTM'], risk_free_rate * row['Factor'], row['Implied Volatility'], row['Right']) * 100  * row['Quantity'] 
                    positions.loc[idx, f'{adj_pct}%']=bs_price-row['Market Value'] # * row['Quantity']
                    
    underlying_distinct=positions['Underlying'].unique()
    master_file=pd.read_excel(r"master_file.xlsx")

    def proxy_beta_results(df1, df2):
        merge_data=df1[['Date','Returns']].merge(df2[['Date','Returns']], on='Date', how='left')
        beta_model=RollingOLS(endog=merge_data['Returns_y'].values, exog=sm.add_constant(merge_data['Returns_x']), window=21*3, missing="drop", min_nobs=5, expanding=True)
        beta_fit=beta_model.fit()
        beta=beta_fit.params['Returns_x'].iloc[-1]
        
        merge_data.loc[merge_data['Returns_y'].isna(),'Returns_y']=merge_data.loc[merge_data['Returns_y'].isna(),'Returns_x'] * beta #TODO store this beta.
        proxy_beta_fit=sm.OLS(merge_data['Returns_y'].iloc[-63:],exog=sm.add_constant(merge_data['Returns_x'].iloc[-63:])).fit()
        proxy_beta=proxy_beta_fit.params['Returns_x']
        return proxy_beta
    
    for i in underlying_distinct:
        stock=pd.read_csv(r"C:\RedXCapital\Dividends\Data\Symbol"+'\\'+i+'.csv')
        underlying_symbol=master_file.loc[master_file['Symbol']==i,'Underlying'].values[0]
        underlying_data=pd.read_csv(r"C:\RedXCapital\Dividends\Data\Symbol"+'\\'+underlying_symbol+'.csv')
        
        proxy_beta_underlying=proxy_beta_results(underlying_data, stock)
        
        market_hedge=master_file.loc[master_file['Symbol']==i,'Sector ETF'].values[0]
        market_data=pd.read_csv(r"C:\RedXCapital\Dividends\Data\Symbol"+'\\'+market_hedge+'.csv')
        
        proxy_beta_hedge=proxy_beta_results(market_data, stock)
        
        positions.loc[positions['Symbol']==i,'Underlying Delta']=proxy_beta_underlying * positions.loc[positions['Symbol']==i,'Market Value']
        positions.loc[positions['Symbol']==i,'Underlying Beta']=proxy_beta_underlying
        positions.loc[positions['Symbol']==i,'Market Hedge Delta']=proxy_beta_hedge * positions.loc[positions['Symbol']==i,'Market Value'] 
        positions.loc[positions['Symbol']==i,'Market Beta']=proxy_beta_hedge 
        
        returns_5day2yr=stock['Close'].pct_change(5).iloc[-252*2-5:].dropna()
        try:
            positions.loc[positions['Underlying']==i,'5Close']=stock['Close'].iloc[-6]
            
        except:
            positions.loc[positions['Underlying']==i,'5Close']=stock['Close'].iloc[-1]
            positions.loc[positions['Underlying']==i,'5Return']=0
        if not returns_5day2yr.empty:
            positions.loc[positions['Underlying']==i,'5Return']=returns_5day2yr.iloc[-1]
            positions.loc[positions['Underlying']==i,'5AvgRet2yr']=returns_5day2yr.mean()
            positions.loc[positions['Underlying']==i,'5Std2yr']=returns_5day2yr.std()
            positions.loc[positions['Underlying']==i,'5ProbStd2yr']=sum(returns_5day2yr.abs()<returns_5day2yr.std())/returns_5day2yr.dropna().shape[0]
            positions.loc[positions['Underlying']==i,'5VaR952yr']=returns_5day2yr.quantile(.05)
            positions.loc[positions['Underlying']==i,'5VaR052yr']=returns_5day2yr.quantile(.95) # Need to do max drawdown.distance from max drawdoown
            max_series=stock['Close'].rolling(252,min_periods=10).max()
            min_series=stock['Close'].rolling(252,min_periods=10).min()
            positions.loc[positions['Underlying']==i,'Max2yr']=max_series.iloc[-1]
            positions.loc[positions['Underlying']==i,'Min2yr']=min_series.iloc[-1]
            positions.loc[positions['Underlying']==i,'MaxDD2yr']=(stock['Close'].iloc[-1]/max_series.iloc[-1]-1)
            positions.loc[positions['Underlying']==i,'MaxDUp2yr']=(stock['Close'].iloc[-1]/min_series.iloc[-1]-1)
            positions.loc[positions['Underlying']==i,'MaxDD952yr']=(stock['Close'].iloc[-1]/max_series-1).quantile(.05)
            positions.loc[positions['Underlying']==i,'MaxDUp052yr']=(stock['Close'].iloc[-1]/min_series-1).quantile(.95)
            positions.loc[positions['Underlying']==i,'MinToClose']=(min_series.iloc[-1]/stock['Close'].iloc[-1]-1)
            positions.loc[positions['Underlying']==i,'MaxToClose']=(max_series.iloc[-1]/stock['Close'].iloc[-1]-1)
        else:
            positions.loc[positions['Underlying']==i,'5Return']=0
            positions.loc[positions['Underlying']==i,'5AvgRet2yr']=0
            positions.loc[positions['Underlying']==i,'5Std2yr']=0
            positions.loc[positions['Underlying']==i,'5ProbStd2yr']=0
            positions.loc[positions['Underlying']==i,'5VaR952yr']=0
            positions.loc[positions['Underlying']==i,'5VaR052yr']=0
            max_series=0
            min_series=0
            positions.loc[positions['Underlying']==i,'Max2yr']=0
            positions.loc[positions['Underlying']==i,'Min2yr']=0
            positions.loc[positions['Underlying']==i,'MaxDD2yr']=0
            positions.loc[positions['Underlying']==i,'MaxDUp2yr']=0
            positions.loc[positions['Underlying']==i,'MaxDD952yr']=0
            positions.loc[positions['Underlying']==i,'MaxDUp052yr']=0
            positions.loc[positions['Underlying']==i,'MinToClose']=0
            positions.loc[positions['Underlying']==i,'MaxToClose']=0
        
    positions.sort_values('Symbol', inplace=True, ascending=False)

    positions=positions.append(positions.sum(), ignore_index=True) 
    positions.loc[positions.shape[0]-1,['Symbol','Sec Type','Underlying','Underlying Price','Strike','Moneyness','Right','Expiry','Strategy','Class Group','Implied Volatility']]='Total'
    positions=positions[[ 'Class Group','Underlying', 'Sec Type', 'Symbol','Expiry','Underlying Price','Strike','Moneyness', 'Quantity','Average Cost','Close Price','Avg Cost MV','Market Value','Weight','Underlying Delta', 'Underlying Beta', 'Market Hedge Delta','Market Beta','PnL','Implied Volatility','Theta','Delta','Dollar Delta', '-50%', '-40%', '-30%', '-25%', '-20%', '-15%','-12.5%', '-10%', '-7.5%', '-5%', '-3%', '-2%', '-1%', '1%', '2%', '3%', '5%', '7.5%', '10%','12.5%', '15%', '20%', '25%', '30%','40%', '50%','5Close','5Return','5AvgRet2yr','5Std2yr','5ProbStd2yr','5VaR952yr','5VaR052yr','Max2yr','MaxDD2yr','MaxDD952yr','Min2yr','MaxDUp2yr','MaxDUp052yr','MinToClose','MaxToClose']]
    


    price_shock=positions.loc[positions['Symbol'].isin(positions['Class Group'].unique()),:] #TODO append over pnl percentage of equity.
    price_shock=price_shock.loc[~price_shock['Class Group'].isin(['Total']),:]

    for pct in percentage_values:
        price_shock.loc[price_shock['Sec Type'] == 'STK', f'{pct}%'] = price_shock.loc[price_shock['Sec Type'] == 'STK', 'Close Price'] * (1+pct / 100)
        
    positions=positions.append(price_shock)
    risk_shock_path=r"C:\RedXCapital\Dividends\Data\Risk Shock"
    start_time=utilities.last_business(utilities.next_business())
    prev_date=utilities.last_business()
    if start_time.hour>=16:
        date=start_time.strftime('%Y%m%d')
    else:
        date=prev_date.strftime('%Y%m%d')    

    positions=positions[[ 'Class Group','Underlying', 'Sec Type', 'Symbol','Expiry','Underlying Price','Strike','Moneyness', 'Quantity','Average Cost','Close Price','Avg Cost MV','Market Value','Weight','Underlying Delta', 'Underlying Beta', 'Market Hedge Delta','Market Beta','PnL','Implied Volatility','Theta','Delta','Dollar Delta', '-50%', '-40%', '-30%', '-25%', '-20%', '-15%','-12.5%', '-10%', '-7.5%', '-5%', '-3%', '-2%', '-1%', '1%', '2%', '3%', '5%', '7.5%', '10%','12.5%', '15%', '20%', '25%', '30%','40%', '50%','5Close','5Return','5AvgRet2yr','5Std2yr','5ProbStd2yr','5VaR952yr','5VaR052yr','Max2yr','MaxDD2yr','MaxDD952yr','Min2yr','MaxDUp2yr','MaxDUp052yr','Close Price','MinToClose','MaxToClose']]
    writer=pd.ExcelWriter(risk_shock_path+'\\'+'risk_shock_'+date+'.xlsx', engine='xlsxwriter')
    positions.to_excel(writer, sheet_name='Risk Shock', index=False)
    writer=excel.sheet_adj(writer,'Risk Shock')
    writer.save()
    writer.close()
    excel.auto_size_wrksht(risk_shock_path+'\\'+'risk_shock_'+date+'.xlsx', list(writer.sheets.keys()))
    return positions

# Build out to handle option pricing
# TODO build out deltas

# Market Beta Shock.

#Delta Shocks

#TODO Underlying price shock then sort by class  group and underlying.

# import yfinance as yf
# import numpy as np

# def calculate_5day_average_return(data):
#     return data.pct_change(5).rolling(window=21).mean().dropna()

# def calculate_5day_average_volatility(data): 
#     return data.pct_change(5).rolling(window=21).std().dropna()

# def main():
#     # Replace "ARKK" with the ticker symbol of ARKK or any other asset
#     ticker = "ARKK"
    
#     # Fetch historical price data
#     data = yf.download(ticker, period="1y")['Close']
    
#     # Calculate 5-day average return and average 5-day volatility
#     average_return = calculate_5day_average_return(data)
#     average_volatility = calculate_5day_average_volatility(data)
    
#     # Print the results 
#     print("5-day Average Return:")
#     print(average_return.tail(15))
#     print("\nAverage 5-day Volatility:")
#     print(average_volatility.tail(15))

# if __name__ == "__main__":
#     main()
