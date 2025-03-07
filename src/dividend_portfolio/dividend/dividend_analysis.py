from ibkr import ibkr
import yfinance as yf
import numpy as np
from utilities import utilities
from excel import excel
import pandas as pd
import pandas.io.formats.excel
pandas.io.formats.excel.ExcelFormatter.header_style=None
import polygon
import requests
import os
polygon_api_key=os.environ.get("polygon_api")
client=polygon.RESTClient(os.environ.get('polygon_api'))
from datetime import datetime
from datetime import timedelta
import requests
start_time=datetime.now()
prev_date=utilities.last_business()
api_key=os.environ.get('polygon_api')

if start_time.hour>=16:
    stock_date=start_time.strftime('%Y-%m-%d')
    date=start_time.strftime('%Y%m%d')
else:
    stock_date=prev_date.strftime('%Y-%m-%d')    
    date=prev_date.strftime('%Y%m%d')

def get_dividends(ticker, period='60d'):
    try:
        dividend=requests.get("https://api.polygon.io/v3/reference/dividends?ticker="+ticker+"&limit=1&apiKey="+api_key+'&sort=pay_date&order=desc').json()['results'][0]['cash_amount']
        return dividend
    except:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, end=utilities.next_business().timestamp()) #.strftime('%Y-%m-%d')
            return (data.loc[data['Dividends']!=0,'Dividends'].iloc[-1])
        except:
            return 0

target_weight=utilities.read_config_file('target_weight.jsonc')
class_group=utilities.read_config_file('ClassGroups.jsonc')

def dividend_summary(positions, portfolio_value, alpha): # amount of years to look back
    positionals_bool=(positions['Symbol'].isna()) & (positions['Right']=='S')
    positions['Symbol']=positions['Symbol'].bfill()
    dividend=positions.loc[positionals_bool,['Class Group','Symbol','Quantity','Market Value','Average Cost','Close Price']]
    dividend['Weights']=dividend['Market Value'] / dividend['Market Value'].sum()
    dividend.index=dividend['Class Group']

    missing_symbols=pd.Series(target_weight.keys())
    for i in missing_symbols[~missing_symbols.isin(dividend['Class Group'])]: # add to data frame missing tickers
        dividend.loc[i,'Class Group']=i
    for key, values in class_group.items(): # this symmetrical logic only applies to stocks
        dividend.loc[dividend['Class Group'].str.contains(key),'Symbol']=list(values.keys())[0] # gets the class group
        
    for i in dividend.loc[dividend['Close Price'].isna(),'Class Group']:
        try:
            dividend.loc[dividend['Class Group']==i,'Close Price']=client.get_daily_open_close_agg(i, date=stock_date).close
        except:
            try:
                dividend.loc[dividend['Class Group']==i,'Close Price']=requests.get("https://api.polygon.io/v1/open-close/"+i+"/"+stock_date+"?adjusted=true&apiKey="+polygon_api_key).json()['close']
            except:
                try:
                    data=yf.download(i, start=(datetime.now()-timedelta(days=7)).strftime("%Y-%m-%d"),end=utilities.next_business().strftime("%Y-%m-%d"))
                    dividend.loc[dividend['Class Group']==i,'Close Price']=data['Close'].iloc[-1]
                except:
                    dividend.loc[dividend['Class Group']==i,'Close Price']=np.nan
            
            
    for idx, row in dividend.iterrows():
        if row['Class Group']=='XDTE' or row['Class Group']=='QDTE' or row['Class Group']=='RDTE' or row['Class Group']=='SDTY' or row['Class Group']=='QDTY':
            dividend.loc[idx, 'Dividend']=get_dividends(row['Class Group'])*52/12
        elif row['Class Group']=='TMF' or row['Class Group']=='TQQQ':
            dividend.loc[idx, 'Dividend']=get_dividends(row['Class Group'])*4/12
        # elif row['Class Group']=='TSPY':
        #     dividend.loc[idx, 'Dividend']=row['Close Price'] * .07 / 12
        # elif row['Class Group']=='QQQT':
        #     dividend.loc[idx, 'Dividend']=row['Close Price'] * .2 / 12 
        else:
            dividend.loc[idx, 'Dividend']=get_dividends(row['Class Group'])

        
    dividend['Annual Dividend']=dividend['Dividend'] * 12
    dividend['Monthly Income']=dividend['Dividend'] * dividend['Quantity']
    dividend['Annual Income']=dividend['Annual Dividend'] * dividend['Quantity']
    dividend['Dividend Yield']=dividend['Annual Dividend'] / dividend['Close Price']
    dividend['Yield on Cost']=dividend['Annual Income'] / (dividend['Average Cost'] * dividend['Quantity'])    
    
    for i in dividend['Class Group'].dropna():
        try:
            dividend.loc[dividend['Class Group']==i,'Target Weight']=target_weight[i]
        except:
            dividend.loc[dividend['Class Group']==i,'Target Weight']=np.nan

    dividend['Target Market Value']=dividend['Target Weight'] * portfolio_value
    dividend['Target Diff MV'] = dividend['Target Market Value'] - dividend['Market Value']
    dividend.loc[dividend['Target Diff MV'].isna(),'Target Diff MV']=dividend.loc[dividend['Target Diff MV'].isna(),'Target Market Value']
    dividend['Target Diff Qty']=(dividend['Target Diff MV'] / dividend['Close Price']).round(0)
    dividend['Target Monthly Income'] = (dividend['Target Market Value'] / (dividend['Close Price'])) * dividend['Dividend']
    dividend['Target Annual Income'] = dividend['Target Market Value'] / (dividend['Close Price'] ) * dividend['Annual Dividend']
    
    dividend.sort_values('Target Diff MV', ascending=False, inplace=True)
    
    dividend['Average Cost MV'] = dividend['Average Cost'] * dividend['Quantity']
    del dividend['Symbol']
    
    dividend.reset_index(inplace=True, drop=True)
    dividend=dividend.merge(alpha[['Symbol','Positive_Returns', 'Win_Rate','Negative_Returns', 'Lose_Rate']], left_on='Class Group', right_on='Symbol', how='left')
    del dividend['Symbol']
    
    dividend['%K Criterion']=dividend['Win_Rate'] - dividend['Lose_Rate'] / (dividend['Positive_Returns'] / dividend['Negative_Returns'].abs())
    dividend['Target % KCriterion']=dividend['%K Criterion'] * dividend['Target Weight']
    # dividend['Target % KC MV']=dividend['%K Criterion'] * dividend['Target Diff MV']
    dividend['DCA'] = dividend['Target Diff MV'] *  0.2#dividend['%K Criterion']
    dividend['DCA Qty']=(dividend['DCA'] / dividend['Close Price'])
    del dividend['Positive_Returns']
    del dividend['Win_Rate']
    del dividend['Negative_Returns']
    del dividend['Lose_Rate']
    
    dividend.loc['Total']=dividend.sum(numeric_only=True)
    dividend.loc['Total','Average Cost'] = np.nan
    dividend.loc['Total','Dividend Yield'] = dividend.loc['Total','Annual Income'] / dividend.loc['Total','Market Value']
    dividend.loc['Total','Yield on Cost'] = dividend.loc['Total','Annual Income'] / dividend.loc['Total','Average Cost MV']
    #TODO make this risk adjusted dividend. dividend yield times the beta.
    del dividend['Average Cost MV']
    

    return dividend