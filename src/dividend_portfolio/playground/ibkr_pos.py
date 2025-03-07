from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import TickerId
from threading import Thread
from ibapi.contract import Contract
import pandas as pd
import time
from ibapi.common import *
from ibapi.contract import *
from ibapi.ticktype import *
import yfinance as yf
import numpy as np
from datetime import datetime
from datetime import timedelta

class ib_class(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.all_positions = pd.DataFrame([], columns = ['Account', 'Symbol', 'Quantity', 'Average Cost', 'Sec Type', 'Right',  'Strike', 'Expiry'])
          
    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        index = str(contract.localSymbol)
        if contract.right=='':
            contract.right='S'
        else:
            contract.exchange='SMART'
        self.all_positions.loc[index]= account, contract.symbol, position, avgCost, contract.secType, contract.right,  contract.strike, contract.lastTradeDateOrContractMonth        
 
    def positionEnd(self):
        print("Positions ")
        self.done = True

def run_loop():
    app.run()

def get_positions():
    app = ib_class()
    app.connect('127.0.0.1', 7496, 999)
    #Start the socket in a thread
    api_thread = Thread(target=run_loop, daemon=True)
    api_thread.start()
    time.sleep(3) #Sleep interval to allow time for connection to server
    app.reqPositions()
    print("Waiting for IB's API response for accounts positions requests...\n")
    time.sleep(3)
    current_positions = app.all_positions
    current_positions=current_positions.loc[current_positions['Quantity']!=0,]  
    app.disconnect()

    current_positions['Close']=np.nan
    current_positions['STD_42']=np.nan
    current_positions['B_Mkt_Delta']=np.nan
    stock_dir=r"C:\RedXCapital\Dividends\Data\Symbol"
    for idx, row in current_positions.iterrows():
        stock=pd.read_csv(stock_dir+'\\'+row['Symbol']+'.csv')
        current_positions.loc[idx, 'Close']=stock['Close'].iloc[-1]
        current_positions.loc[idx, 'STD_42']=stock['STD_42'].iloc[-1]
        current_positions.loc[idx, 'B_Mkt_Delta']=stock['B_Mkt_Delta'].iloc[-1]        
    now=datetime.now()
    def convert_to_dt(df):
        if df['Expiry']=='':
            return ''
        else:
            return datetime.strptime(df['Expiry'], '%Y%m%d')
        
    current_positions['Expiry']=current_positions.apply(convert_to_dt, axis=1)

    current_positions['T']=(current_positions['Expiry'].apply(lambda x: '' if x=='' else x-now))
    current_positions['T']=current_positions['T'].apply(lambda x: x.timedelta.total_seconds if x!='' else 0)/(365.25*24*60*60)
    current_positions['T']= np.where(current_positions['T']<0, 0, current_positions['T'])
    return current_positions

get_positions()


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import TickerId
from threading import Thread
from ibapi.contract import Contract
import pandas as pd
import time
from ibapi.common import *
from ibapi.contract import *
from ibapi.ticktype import *
from datetime import datetime

class ib_class(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        # returns the data i want
        self.all_positions = pd.DataFrame([], columns = ['Account', 'Symbol', 'Quantity', 'Average Cost', 'Sec Type', 'Right',  'Strike', 'Expiry'])
        
    # def positionMulti(self,  reqId: int, account: str, modelCode: str, contract: Contract, pos: float, avgCost: float):
    #     index = str(contract.localSymbol)
    #     if contract.right=='':
    #         contract.right='S'
    #     else:
    #         contract.exchange='SMART'
    #     self.all_positions.loc[index]= account, contract.symbol, pos, avgCost, contract.secType, contract.right,  contract.strike, contract.lastTradeDateOrContractMonth
    #     # self.all_positions.loc[index]= account, contract.symbol, pos, avgCost
 
    # def positionMultiEnd(self, reqId: int):
    #     print("Position Multi End. ReqId:", reqId)
    #     self.done = True
  
    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        index = str(contract.localSymbol)
        if contract.right=='':
            contract.right='S'
        else:
            contract.exchange='SMART'
        self.all_positions.loc[index]= account, contract.symbol, position, avgCost, contract.secType, contract.right,  contract.strike, contract.lastTradeDateOrContractMonth        
 
    def positionEnd(self):
        print("Positions ")
        self.done = True
  
    # def securityDefinitionOptionParameter(self, reqId:int, exchange:str, underlyingConId:int, tradingClass:str, multiplier:str, expirations:SetOfString, strikes:SetOfFloat):
    #     print("Exchange:", exchange, "Underlying ConId:", underlyingConId, "Trading Class:", tradingClass, "Multiplier:", multiplier, "Expirations:", expirations, "Strikes:", strikes)
        
    # def securityDefinitionOptionParameterEnd(self, reqId:int):
    #     print("Security Definition Option Parameter End. ReqId:", reqId)
    #     self.done = True

    # def tickOptionComputation(self, reqId: TickerId, tickType: TickType, impliedVol: float, delta: float,
    #                         optPrice: float, pvDividend: float,
    #                         gamma: float, vega: float, theta: float, undPrice: float):
    #     super().tickOptionComputation(reqId, tickType, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta,
    #                                 undPrice)
    #     print("TickOptionComputation. TickerId:", reqId, "tickType:", tickType, "ImpliedVolatility:", impliedVol,
    #         "Delta:", delta, "OptionPrice:", optPrice, "pvDividend:", pvDividend, "Gamma: ", gamma, "Vega:", vega,
    #         "Theta:", theta, "UnderlyingPrice:", undPrice)
    #     self.all_risk.loc[str(TickerId)] = reqId, tickType, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice

def download_positions():

    def run_loop():
        app.run()

    app = ib_class()
    app.connect('127.0.0.1', 7496, 999)
    #Start the socket in a thread
    api_thread = Thread(target=run_loop, daemon=True)
    api_thread.start()
    time.sleep(3) #Sleep interval to allow time for connection to server

    # app.reqPositionsMulti(1, "Dividend Fund", "")
    app.reqPositions()


    # app.reqPositions() # associated callback: position
    print("Waiting for IB's API response for accounts positions requests...\n")
    time.sleep(3)
    current_positions = app.all_positions
    current_positions=current_positions.loc[current_positions['Quantity']!=0,]
    current_positions['Avg Cost MV']=current_positions['Quantity']*current_positions['Average Cost']

    #1. Live streaming (the default)
    #2. Frozen (typically used for bid/ask prices after market close)
    #3. Delayed (if the username does not have live market data subscriptions)
    #4. Delayed-Frozen (combination of types 2 & 3)
    # app.reqMarketDataType(3) #TODO instead run your own pricing engine
    # i=1
    # for idx, row in current_positions.loc[current_positions['Sec Type']=='OPT',:].iterrows():
    #     i=i+1
    #     app.reqMktData(i, row['contract'], "", False, False, [])
    app.disconnect()
    position_path=r"C:\RedXCapital\Dividends\Data\Position"
    date=datetime.now().strftime(r'%Y%m%d')
    current_positions.to_csv(position_path+'\\'+'ibkr_pos_'+date+'.csv', index=False)
    return current_positions


# import yfinance as yf
# import numpy as np
# from datetime import datetime
# from datetime import timedelta
# current_positions['Close']=np.nan
# current_positions['STD_42']=np.nan
# current_positions['B_Mkt_Delta']=np.nan
# stock_dir=r"C:\RedXCapital\Dividends\Data\Symbol"
# for idx, row in current_positions.iterrows():
#     stock=pd.read_csv(stock_dir+'\\'+row['Symbol']+'.csv')
#     current_positions.loc[idx, 'Close']=stock['Close'].iloc[-1]
#     current_positions.loc[idx, 'STD_42']=stock['STD_42'].iloc[-1]
#     current_positions.loc[idx, 'B_Mkt_Delta']=stock['B_Mkt_Delta'].iloc[-1]
    
    
# def convert_to_dt(df):
#     if df['Expiry']=='':
#         return datetime.now()
#     else:
#         return datetime.strptime(df['Expiry'], '%Y%m%d')
    
# current_positions['Expiry']=current_positions.apply(convert_to_dt, axis=1)

# current_positions['T']=(current_positions['Expiry']-datetime.now())
# current_positions['T']=current_positions['T'].apply(timedelta.total_seconds)/(365.25*24*60*60)
# current_positions['T']= np.where(current_positions['T']<0, 0, current_positions['T'])

    
# import py_vollib.black_scholes.greeks.analytical as greeks
# import os
# import fredapi
# fredapi_key=os.environ.get("fredapi_key")
# fred=fredapi.Fred(api_key=fredapi_key)
# fed_funds=fred.get_series_latest_release('FEDFUNDS')
# rf=fed_funds.iloc[-1]

# def delta(df):
#     if df['Sec Type']=='OPT':
#         return greeks.delta(df['Right'].lower(), df['Close'], df['Strike'], df['T'], rf, df['STD_42']*(252)**0.5) * 100 * abs(df['Quantity'])
#     elif df['Sec Type']=='STK':
#         return df['B_Mkt_Delta'] * df['Quantity'] #This is right. The amount of market delta i need to hedge.

# def dollar_delta(df):
#     if df['Sec Type']=='OPT':
#         return greeks.delta(df['Right'].lower(), df['Close'], df['Strike'], df['T'], rf, df['STD_42']*(252)**0.5) * 100 * abs(df['Quantity'])
#     elif df['Sec Type']=='STK':
#         return df['Quantity'] #This is right. The amount of market delta i need to hedge.
# # Define the option parameters

# current_positions['Mkt Delta']=current_positions.apply(delta, axis=1) #TODO run the hedging values for this.
# current_positions['Dollar Delta']=current_positions.apply(dollar_delta, axis=1)

# # gamma = greeks.gamma(option_type, underlying_price, strike_price, time_to_maturity, risk_free_rate, implied_volatility)
# # theta = greeks.theta(option_type, underlying_price, strike_price, time_to_maturity, risk_free_rate, implied_volatility)
# # vega = greeks.vega(option_type, underlying_price, strike_price, time_to_maturity, risk_free_rate, implied_volatility)
# # rho = greeks.rho(option_type, underlying_price, strike_price, time_to_maturity, risk_free_rate, implied_volatility)

# print("Delta: {:.4f}".format(delta))
# print("Gamma: {:.4f}".format(gamma))
# print("Theta: {:.4f}".format(theta))
# print("Vega: {:.4f}".format(vega))
# print("Rho: {:.4f}".format(rho))
