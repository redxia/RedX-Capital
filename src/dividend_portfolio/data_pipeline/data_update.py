import pandas as pd
import yfinance as yf
import os
from datetime import datetime
import time
from datetime import timedelta
from data_pipeline import data_properties
stock_path=r"C:\RedXCapital\Dividends\Data\Symbol"
market_path=r"C:\RedXCapital\Dividends\Data\Market Data"

def download_data(symbol, directory): #downloads the whole data  for monthly - weekly
    # stock=yf.download(symbol,actions=True, auto_adjust=True,progress=False, period="max")
    # if directory==stock_path:
    #     stock=yf.download(symbol,actions=True,progress=False, period="max")
    # else:
    #     stock=yf.download(symbol,actions=True,progress=False, period="max", auto_adjust=True)
    stock=yf.download(symbol,actions=True,progress=False, period="max")
    stock=stock[['Close','Close',"Volume",'Dividends']]
    stock['Returns']=stock['Close'].pct_change()
    stock.reset_index(inplace=True)
    stock["Date"]=stock["Date"].dt.strftime("%Y-%m-%d")
    stock['ADV_20']=stock['Volume'].rolling(20, min_periods=5).mean()
    stock['Dollar_ADV_20']=stock['Close']*stock['ADV_20']
    stock.to_csv(directory+'\\'+symbol+".csv",index=False)
    return

def stock_data(ticker, path): # updates the data
    today=datetime.now().strftime("%Y-%m-%d")
    # stock=yf.download(ticker,actions=True, auto_adjust=True,progress=False, start=today)
    stock=yf.download(ticker,actions=True,progress=False, start=(datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d'))
    # if path==stock_path:
    #     stock=yf.download(ticker,actions=True,progress=False, start=(datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d'))
    # else:
    #     stock=yf.download(ticker,actions=True,progress=False, auto_adjust=True, start=(datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d'))
    historical=pd.read_csv(path+'\\'+ticker+'.csv')
    # historical=pd.read_csv(path+'\\'+ticker+'.csv').iloc[:-1]
    if path==stock_path:
        if (historical.columns[0:5]==['Date', 'Close','Close','Volume','Dividends']).all():
            stock=stock[['Close','Close',"Volume", "Dividends"]]
        elif (historical.columns[0:5]==['Date', 'Close','Close','Dividends','Volume']).all():
            stock=stock[['Close','Close', "Dividends", "Volume"]]
    elif path==market_path:
        stock=stock[['Close','Close',"Volume"]]
    stock.reset_index(inplace=True)
    stock["Date"]=stock["Date"].dt.strftime("%Y-%m-%d")
    #stock['Returns']=stock["Close"] / historical.loc[historical.shape[0]-1,"Close"] - 1
    stock['Returns']=stock['Close'].pct_change()
    new_row=pd.DataFrame(columns=historical.columns.to_list())
    
    if stock.shape[0]==1:
        new_row.loc[0,'Date']=stock.loc[0,"Date"]
        new_row.loc[0,'Close']=stock.loc[0,"Close"]
        new_row.loc[0,'Close']=stock.loc[0,"Close"]
        new_row.loc[0,'Volume']=stock.loc[0,"Volume"]
        new_row.loc[0,'Returns']=stock.loc[0,"Returns"]
        if path==stock_path:
            new_row.loc[0,'Dividends']=stock.loc[0,"Dividends"]
        if not new_row.loc[0,"Date"] in historical["Date"].to_list():
            historical=pd.concat([historical, new_row], ignore_index=True)
            if path==stock_path:
                historical=data_properties.stock_properties(ticker, path, historical)
            historical.to_csv(path+'\\'+ticker+'.csv',index=False)
    elif stock.shape[0]>1:
        for i in range(0,stock.shape[0]):
            if not stock.loc[i,"Date"] in historical["Date"].to_list():
                new_row.loc[i,'Date']=stock.loc[i,"Date"]
                new_row.loc[i,'Close']=stock.loc[i,"Close"]
                new_row.loc[i,'Close']=stock.loc[0,"Close"]
                new_row.loc[i,'Volume']=stock.loc[i,"Volume"]
                new_row.loc[i,'Returns']=stock.loc[i,"Returns"]
                if path==stock_path:
                    new_row.loc[i,'Dividends']=stock.loc[i,"Dividends"]
        historical=pd.concat([historical, new_row], ignore_index=True)
        if path==stock_path:
            historical=data_properties.stock_properties(ticker, path, historical)
        historical.to_csv(path+'\\'+ticker+'.csv',index=False)
            
def data_updater(path): 
    symbols=os.listdir(path)
    for i in symbols:
        print("Working with Stock: ", i.split('.')[0])
        stock_data(i.split('.')[0], path)
        time.sleep(1.5)
    return