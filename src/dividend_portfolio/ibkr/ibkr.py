from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import TickerId
from threading import Thread
from ibapi.contract import Contract
from utilities import utilities
import pandas as pd
import time
import yfinance as yf
from excel import excel
from ibapi.common import *
from ibapi.contract import *
from ibapi.ticktype import *
from datetime import datetime
import polygon
import os
# from black_scholes import black_scholes
import scipy.optimize as opt
import numpy as np
from datetime import datetime
from datetime import timedelta
import fredapi
import requests
import implied_volatility as imply_volat
from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.implied_volatility import implied_volatility as implied_vols
from py_vollib.black_scholes.greeks.analytical import delta, gamma, vega, theta 
polygon_api_key=os.environ.get("polygon_api")
fred = fredapi.Fred(api_key=os.environ.get("fredapi_key"))
fed_funds_rate = fred.get_series('DFF').tail(1)[0]/100


client=polygon.RESTClient(os.environ.get('polygon_api'))
start_time=utilities.last_business(utilities.next_business())
prev_date=utilities.last_business()
# if start_time.hour>=16:
stock_date=start_time.strftime('%Y-%m-%d')
date=start_time.strftime('%Y%m%d')
# else:
#     stock_date=prev_date.strftime('%Y-%m-%d')    
#     date=prev_date.strftime('%Y%m%d')

class ib_class(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.all_positions = pd.DataFrame([], columns = ['Underlying','Symbol', 'Sec Type', 'Right',  'Strike', 'Expiry', 'Quantity', 'Average Cost'])
        self.account_data = pd.DataFrame([], columns = ['NetLiquidation','EquityWithLoanValue', 'InitMarginReq', 'MaintMarginReq', 'AvailableFunds', 'ExcessLiquidity',  'SMA', 'GrossPositionValue', 'TotalCashValue'])
  
    # def position(self, account: str, contract: Contract, position: float, avgCost: float):
    #     index = str(contract.localSymbol)
    #     if contract.right=='':
    #         contract.right='S'
    #     else:
    #         contract.exchange='SMART'
    #     self.all_positions.loc[index]= contract.symbol, contract.localSymbol, contract.secType, contract.right,  contract.strike, contract.lastTradeDateOrContractMonth, position, avgCost
    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        row = pd.DataFrame([{
            'Account': account,
            'Underlying': contract.symbol,
            'Symbol': contract.localSymbol,
            'Sec Type': contract.secType,
            'Right': contract.right if contract.right else 'S',
            'Strike': contract.strike,
            'Expiry': contract.lastTradeDateOrContractMonth,
            'Quantity': position,
            'Average Cost': avgCost
            }])
        self.all_positions = pd.concat([self.all_positions, row], ignore_index=True)        
 
    def positionEnd(self):
        self.done = True
        
    def accountSummary(self, reqId, account, tag, value, currency):
        index=account
        self.account_data.loc[index, tag]=float(value)

    def accountSummaryEnd(self, reqId):
        self.done=True

def get_close(df):
    # print(df)
    if df['Sec Type']=='STK':
        try:
            price=requests.get("https://api.polygon.io/v1/open-close/"+df['Symbol']+"/"+stock_date+"?adjusted=true&apiKey="+polygon_api_key).json()['close']
        except:
            print('failed to get stock price ', df['Symbol'])
            price=yf.download(df['Symbol'], start=(prev_date-timedelta(days=7)).strftime("%Y-%m-%d"),end=utilities.next_business().strftime("%Y-%m-%d"))
            price=price['Close'].iloc[-1][0]
    elif df['Sec Type']=='OPT':
        try:
            strike=str(int(df['Strike']*1000)).rjust(8,'0')
            try:
                option=requests.get("https://api.polygon.io/v3/snapshot/options/"+df['Underlying']+"/O:"+df['Underlying']+df['Expiry'][-6:]+df['Right']+strike+"?apiKey="+polygon_api_key).json()['results']
                price=option['day']['close']
            except:
                price=client.get_daily_open_close_agg("O:"+df['Symbol'].replace(' ',''), date=stock_date).close
        except:
            price=bs(df['Right'].lower(), df['Underlying Price'], df['Strike'], df['TTM'], fed_funds_rate, option['implied_volatility'])
            print('failed to get option price')                        
            
            # price=df['Average Cost']
    return round(price,2)

def get_underlying_close(df):
    try:
        price=client.get_daily_open_close_agg(df['Underlying'], date=stock_date).close
    except:
        price=yf.download(df['Underlying'], start=(datetime.now()-timedelta(days=7)).strftime("%Y-%m-%d"),end=utilities.last_business().strftime("%Y-%m-%d"))
        price=price['Close'].iloc[-1][0]
    return price

def apply_price(df):
    if start_time.hour>=16:
        if df['Sec Type']=='OPT':
            return df['Close Price']*100
        else:
            return df['Close Price']
    else:
        if df['Sec Type']=='OPT':
            strike=str(int(df['Strike']*1000)).rjust(8,'0')
            price=pd.json_normalize(requests.get("https://api.polygon.io/v3/quotes/O:"+df['Underlying']+df['Expiry'][-6:]+df['Right']+strike+"?apiKey="+polygon_api_key).json()['results'])
            price=((price['ask_price']+price['bid_price'])/2).mean()
            return price * 100
        else:
            price=pd.json_normalize(requests.get("https://api.polygon.io/v3/quotes/"+df['Underlying']+"?apiKey="+polygon_api_key).json()['results'])
            price=((price['ask_price']+price['bid_price'])/2).mean()
            return price
    return df['Close Price']

def implied_volatility(df):          
    print(df['Symbol'])
    # try:
    #     initial_guess = imply_volat.get_implied_volatility(df['Underlying']) # Initial guess for implied volatility
    # except:
    initial_guess = imply_volat.get_volatility(df['Underlying'])
    if df['Sec Type']=="OPT":
        strike=str(int(df['Strike']*1000)).rjust(8,'0')
        try:
            option=requests.get("https://api.polygon.io/v3/snapshot/options/"+df['Underlying']+"/O:"+df['Underlying']+df['Expiry'][-6:]+df['Right']+strike+"?apiKey="+polygon_api_key).json()['results']        
        
            implied_vol=option['implied_volatility']
            print("polygon", implied_vol)
        except:
            try:
                implied_vol=implied_vols(df['Close Price'], round(option['underlying_asset']['price'],2), df['Strike'], df['TTM'], fed_funds_rate, df['Right'].lower())
                print("reverse engineer", implied_vol)
            except:
                try:
                    implied_vol = imply_volat.get_implied_volatility(df['Underlying'])
                    print("yahoo finance", implied_vol)
                except:
                    implied_vol=initial_guess
    else:
        implied_vol=initial_guess
    implied_vol= initial_guess if implied_vol <= 0.05 else implied_vol
    return implied_vol

class_groups=utilities.read_config_file("ClassGroups.jsonc")

def adjust_avg_cost(df):
    if df['Sec Type']=='OPT':
        return df['Average Cost'] /100
    return df['Average Cost']

def download_positions():
    def run_loop():
        app.run()    

    app = ib_class()
    app.connect('127.0.0.1', 7496, 999)
    api_thread = Thread(target=run_loop, daemon=True)
    api_thread.start()
    time.sleep(3) #Sleep interval to allow time for connection to server

    app.reqAccountSummary(1, "All", "NetLiquidation,EquityWithLoanValue,InitMarginReq,MaintMarginReq,AvailableFunds,ExcessLiquidity,SMA,GrossPositionValue,TotalCashValue")    
    app.reqPositions()
    time.sleep(1)
    time.sleep(1)
    app.disconnect()
    
    current_positions = app.all_positions.copy()
    current_positions.set_index('Symbol',drop=False, inplace=True)
    current_positions.index.names=[None]
    current_positions=current_positions.loc[current_positions['Quantity']!=0,]
    for key, values in class_groups.items(): # this symmetrical logic only applies to stocks
        current_positions.loc[current_positions['Underlying'].str.contains(key),'Class Group']=list(values.keys())[0]
        current_positions.loc[current_positions['Underlying'].str.contains(key),'Factor']=list(values.values())[0]
        
    current_positions.sort_values(['Class Group','Underlying','Symbol'], inplace=True)
    current_positions['Avg Cost MV']=current_positions['Quantity']*current_positions['Average Cost']
    current_positions['Average Cost']=current_positions.apply(adjust_avg_cost, axis=1)
    current_time=datetime.now()
    time_adj=utilities.next_business().replace(hour=9, minute=30, second=0) if current_time.hour>=16 else current_time
    # hours_remain=((24 - current_time.hour) + (60 - current_time.minute)/60 + (60-current_time.second) / 3600) / 24 / 365
    current_positions['TTM']=current_positions['Expiry'].apply(lambda x: (datetime.strptime(str(x), '%Y%m%d').replace(hour=16, minute=0,second=0)-time_adj).total_seconds() / (60*60*24*365.25) if x!='' else np.nan)    
    current_positions=current_positions.loc[~(current_positions['TTM']<0)]
    current_positions['Underlying Price']=current_positions.apply(get_underlying_close, axis=1)
    current_positions['Close Price']=current_positions.apply(get_close, axis=1)    
    current_positions['Market Value']=current_positions['Quantity'] * current_positions.apply(apply_price, axis=1)
    current_positions['Strike']=current_positions['Strike'].replace(0, np.nan)    
    current_positions['Implied Volatility']=current_positions.apply(implied_volatility, axis=1) # get option implied else get stock 60 day volatility. 
    current_positions['Daily Volatility']=current_positions['Implied Volatility'] / (252**0.5)
    
    percentage_values=[-25, -15, -12, -10, -5, -3, -1, 1, 3, 5, 10, 15, 25]
    for pct in percentage_values: # Add beta shocks on top of this
        pct=int(pct)
        for idx, row in current_positions.iterrows():
            adj_pct=pct * row['Factor'] # if row['Factor'] < 0 else pct
            direction_adjustor = -1 if row['Factor'] < 0 else pct
            option_contract=np.logical_and(current_positions['Underlying']==row['Underlying'], current_positions['Sec Type']=='OPT')
            if row['Sec Type']!='STK': # if it is short we should flip #TODO fix this this is recalculated too many times
                # if np.logical_and(current_positions['Underlying']==row['Underlying'],current_positions['Sec Type']=='STK').any() and row['Underlying Price']*(1+adj_pct/100)>=row['Strike'] and row['Right']=='C' and row['Quantity']<0:
                #     bs_price=-row['Market Value']
                #     current_positions.loc[idx, str(pct)+'%']=bs_price
                # else:
                # bs_price=black_scholes.black_scholes(row['Underlying Price']*(1+adj_pct/100), row['Strike'], row['TTM'], fed_funds_rate * row['Factor'], row['Implied Volatility'], row['Right']) * 100  * row['Quantity'] 
                try:
                    bs_price=bs(row['Right'].lower(), row['Underlying Price']*(1+adj_pct/100), row['Strike'], row['TTM'], fed_funds_rate, row['Implied Volatility']) * 100  * row['Quantity'] 
                    if pct==1:
                        current_positions.loc[idx,'Delta']=delta(row['Right'].lower(), row['Underlying Price'], row['Strike'], row['TTM'], fed_funds_rate , row['Implied Volatility']) * 100 * row['Quantity'] * direction_adjustor
                        current_positions.loc[idx,'Gamma']=gamma(row['Right'].lower(),row['Underlying Price'], row['Strike'], row['TTM'], fed_funds_rate , row['Implied Volatility']) * 100 * row['Quantity'] * direction_adjustor
                        current_positions.loc[idx,'Dollar Delta']=current_positions.loc[idx,'Delta'] * row['Underlying Price'] * row['Factor'] * direction_adjustor
                        current_positions.loc[idx,'Net Exposure']=current_positions.loc[idx,'Dollar Delta'] + current_positions.loc[idx,'Gamma']  * row['Underlying Price'] * row['Factor'] * direction_adjustor#* row['Quantity'] #* 100 
                        current_positions.loc[idx,'Theta']=theta(row['Right'].lower(), row['Underlying Price'], row['Strike'], row['TTM'], fed_funds_rate , row['Implied Volatility']) * 100 * row['Quantity']
                        current_positions.loc[idx,'Vega']=vega(row['Right'].lower(), row['Underlying Price'], row['Strike'], row['TTM'], fed_funds_rate , row['Implied Volatility']) * 100 * row['Quantity']
                except ValueError:
                    bs_price=row['Close Price']
                    current_positions.loc[idx,'Delta']=0
                    current_positions.loc[idx,'Gamma']=0
                    current_positions.loc[idx,'Dollar Delta']=0
                    current_positions.loc[idx,'Net Exposure']=0
                    current_positions.loc[idx,'Theta']=0
                    current_positions.loc[idx,'Vega']=0
                current_positions.loc[idx, str(pct)+'%']=bs_price-row['Market Value'] # * row['Quantity']    
                # current_positions.loc[idx,'Delta']=black_scholes.delta(row['Underlying Price'], row['Strike'], row['TTM'], fed_funds_rate * row['Factor'], row['Implied Volatility'], row['Right'])
                # current_positions.loc[idx,'Gamma']=black_scholes.gamma(row['Underlying Price'], row['Strike'], row['TTM'], fed_funds_rate * row['Factor'], row['Implied Volatility'], row['Right'])
                # current_positions.loc[idx,'Dollar Delta']=black_scholes.delta(row['Underlying Price'], row['Strike'], row['TTM'], fed_funds_rate * row['Factor'], row['Implied Volatility'], row['Right'])  * 100 * row['Quantity'] * row['Underlying Price']
                # current_positions.loc[idx,'Net Exposure']=current_positions.loc[idx,'Dollar Delta'] + current_positions.loc[idx,'Gamma'] * 100 * row['Quantity'] * row['Underlying Price']
                # current_positions.loc[idx,'Theta']=black_scholes.theta(row['Underlying Price'], row['Strike'], row['TTM'], fed_funds_rate * row['Factor'], row['Implied Volatility'], row['Right']) * 100 * row['Quantity']
                # current_positions.loc[idx,'Vega']=black_scholes.vega(row['Underlying Price'], row['Strike'], row['TTM'], fed_funds_rate * row['Factor'], row['Implied Volatility'], row['Right']) * 100 * row['Quantity']
                

            # elif row['Sec Type']=='STK' and np.logical_and(current_positions['Underlying']==row['Underlying'],current_positions['Sec Type']=='OPT').any() and row['Underlying Price']*(1+direction_adjustor/100)>=current_positions.loc[option_contract,'Strike'].values[0] and row['Quantity']>0 and current_positions.loc[option_contract,'Quantity'].values[0]<0 and (current_positions.loc[option_contract,'Right']=='C').any():
            #     current_positions.loc[current_positions['Symbol']==row['Symbol'], str(pct)+'%']=(-current_positions.loc[option_contract,'Strike'] * current_positions.loc[option_contract,'Quantity'] * 100 - row['Market Value']).values[0]
            #         # row['Quantity']* row['Strike'] * 100 + current_positions.loc[current_positions['Symbol']==row['Underlying'], 'Market Value']).values[0]
            # elif row['Sec Type']=='STK' and np.logical_and(current_positions['Underlying']==row['Underlying'],current_positions['Sec Type']=='OPT').any() and row['Underlying Price']*(1+direction_adjustor/100)>=current_positions.loc[option_contract,'Strike'].values[0] and row['Quantity']<0 and current_positions.loc[option_contract,'Quantity'].values[0]<0 and (current_positions.loc[option_contract,'Right']=='P').any():
            #     current_positions.loc[current_positions['Symbol']==row['Symbol'], str(pct)+'%']=(-current_positions.loc[option_contract,'Strike'] * current_positions.loc[option_contract,'Quantity'] * 100 - row['Market Value']).values[0]
                current_positions.loc[idx,'Daily Dollar Volatility']=current_positions.loc[idx,'Daily Volatility'] * current_positions.loc[idx,'Dollar Delta']   
            else:
                current_positions.loc[idx, str(pct)+'%'] = current_positions.loc[idx, 'Market Value'] * (adj_pct / 100) #* row['Factor'] #TODO multiple this by factor
                current_positions.loc[idx,'Delta']=row['Quantity']
                current_positions.loc[idx,'Dollar Delta']=row['Market Value'] * row['Factor']
                current_positions.loc[idx,'Net Exposure']=current_positions.loc[idx,'Dollar Delta'] #* row['Factor']
                current_positions.loc[idx,'Daily Dollar Volatility']=current_positions.loc[idx,'Daily Volatility'] * current_positions.loc[idx,'Market Value']   
                
                current_positions.loc[idx,'Gamma']=0
                current_positions.loc[idx,'Theta']=0
                current_positions.loc[idx,'Vega']=0
    
    
    current_positions.sort_values(['Dollar Delta','Underlying','Symbol'], inplace=True)
    

    # positions['Theta']=0
    # positions['Delta']=1
    # positions['Dollar Delta']=positions['Quantity']*positions['Close Price'] # TODO build out covered call identifier
    
    # for idx, row in positions.iterrows():
    #     if row['Sec Type']=="OPT": # Pull in the greeks
    #         positions.loc[idx, 'Theta']=black_scholes.theta(row['Underlying Price'], row['Strike'], row['TTM'], risk_free_rate, row['Implied Volatility'], row['Right']) * row['Quantity']  * 100
    #         positions.loc[idx, 'Delta']=black_scholes.delta(row['Underlying Price'], row['Strike'], row['TTM'], risk_free_rate, row['Implied Volatility'], row['Right']) * row['Quantity'] * row['Factor']
    #         positions.loc[idx,'Dollar Delta']=black_scholes.delta(row['Underlying Price'], row['Strike'], row['TTM'], risk_free_rate, row['Implied Volatility'], row['Right'])  * 100 * row['Quantity'] * row['Underlying Price'] * row['Factor']        
        
    current_positions['PnL']=current_positions['Market Value']-current_positions['Avg Cost MV']   
    current_positions['Moneyness']=current_positions['Strike']/current_positions['Underlying Price']-1
    current_positions.loc[current_positions['Sec Type']=='STK','Moneyness']=0 #np.nan
    current_positions.sort_values(['Class Group','Market Value','Symbol'], ascending=[True, False, True], na_position='first', inplace=True)
    
    class_group_level=current_positions.groupby('Class Group',as_index=False).sum()
    class_group_level[['Moneyness','Daily Volatility','Implied Volatility','Close Price','Quantity','Average Cost']]=np.nan
    class_group_level['Max Loss']=class_group_level[['-15%','-12%','-10%','-5%','-3%','-1%','1%','3%','5%','10%','15%']].min(axis=1)
    total=class_group_level.sum()
    current_positions=class_group_level.append(current_positions) #current_positions.append(class_group_level)
    
    
    
    # current_positions.sort_values('Market Value', inplace=True, ascending=False)
    
    # current_positions['_________']=np.nan #TODO min loss
    
    relevant_columns=['Class Group','Symbol','Right','Quantity','Max Loss','Market Value','Dollar Delta','-25%','-15%','-10%','-5%','-3%','-1%','1%','3%','5%','10%','15%','25%','PnL','Net Exposure','Daily Dollar Volatility','Delta','Gamma','Theta','Vega','Daily Volatility','Moneyness','Average Cost','Close Price']
    current_positions=current_positions[relevant_columns] #TODO # ,'Avg Cost MV' ,'Average Cost'
    # current_positions.sort_values(['Class Group','Market Value','Symbol'], ascending=[True, False, True], na_position='first', inplace=True)
    
    sort_df=pd.DataFrame()
    for i in class_group_level.sort_values('Market Value', ascending=False)['Class Group']:
        class_group_subset=current_positions.loc[current_positions['Class Group']==i,:] #.sort_values('Underlying Exposure', ascending=False)
        sort_df=pd.concat([sort_df,class_group_subset])    
    current_positions=sort_df
    
    
    # total['_________']=np.nan
    total['Symbol']='Total'
    total['Right']='Total'
    total=total[relevant_columns]
    total.loc['Class Group']='Total'
    total.loc[['Moneyness','Daily Volatility','Close Price','Average Cost','Quantity']]=np.nan
    current_positions=current_positions.append(total, ignore_index=True)
    symbol_nans=current_positions['Symbol'].notna()
    current_positions.loc[symbol_nans,'Class Group']=current_positions.loc[symbol_nans,'Symbol']
    current_positions.loc[~symbol_nans,'Symbol']=current_positions.loc[~symbol_nans,'Class Group']
    current_positions.loc[symbol_nans,'Symbol']=np.nan
    current_positions.loc[current_positions['Class Group']=='Total','Symbol']='Total'
    

    #TODO build the aggregate row
    
    account_summary=app.account_data.copy()
    account_summary.reset_index(inplace=True, names='Account')
    # account_summary.rename(columns={'index':'Account'}, inplace=True)
    time.sleep(1)  # Adjust this sleep duration as needed
    
    

    # writer.save()
    # writer.close()
    # excel.auto_size_wrksht(pos_directory, list(writer.sheets.keys()))
    return current_positions, account_summary
