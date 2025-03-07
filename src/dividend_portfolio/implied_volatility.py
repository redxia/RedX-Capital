import yfinance as yf
import numpy as np
import pandas as pd
import datetime
from slack_sdk.webhook import WebhookClient
red_bot_url="https://hooks.slack.com/services/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"
webhook=WebhookClient(red_bot_url)
from utilities import utilities

leverage_factor=utilities.read_config_file("leverage_factor.jsonc")
class_group=utilities.read_config_file("ClassGroups.jsonc")

def get_implied_volatility(ticker):
    stock = yf.Ticker(ticker)
    expiration_dates=stock.options
    expiration_dates = [datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in expiration_dates]
    today = datetime.date.today()
    target_expiry_date = today + datetime.timedelta(days=10)

    # Find the closest available expiration date to the target date
    closest_expiry_date = min(expiration_dates, key=lambda date: abs(date - target_expiry_date))    
    
    option_chain = stock.option_chain(closest_expiry_date.strftime("%Y-%m-%d"))
    
    spot_price = stock.history().iloc[-1]['Close']
    # Get the expiry dates from the DataFrame
    options = option_chain.calls[['strike','impliedVolatility']]
    options['Distance'] = abs(options['strike'] - spot_price)
    atm_option_iv = options.loc[options['Distance'].idxmin(),'impliedVolatility']
    return atm_option_iv

def get_volatility(ticker, period='60d'):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    returns = data['Close'].pct_change().dropna()  # Calculate daily returns and drop the first NaN value
    if ticker=='QQQY' or ticker=='IWMY' or ticker=='JEPY':
        returns=returns[returns < 0]
        volatility=(returns.abs().sum() / returns.shape)[0]
    volatility = np.sqrt(returns.var() * 252)  # Annualize volatility assuming 252 trading days in a year
    return volatility

def get_dividends(ticker, period='60d', historical=False):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    if historical:
        return (data.loc[data['Dividends']!=0,'Dividends'].mean()/data['Close'].iloc[-1])*12 #TODO make this trailing 6 months
    else:
        return (data.loc[data['Dividends']!=0,'Dividends'].iloc[-1]/data['Close'].iloc[-1])*12 #TODO make this trailing 6 months

start_time=utilities.last_business(utilities.next_business())
prev_date=utilities.last_business()
if start_time.hour>=16:
    stock_date=start_time.strftime('%Y-%m-%d')
    date=start_time.strftime('%Y%m%d')
else:
    stock_date=prev_date.strftime('%Y-%m-%d')    
    date=prev_date.strftime('%Y%m%d')
    
dividend_tickers=utilities.read_config_file("dividend_tickers.jsonc")

if __name__ == "__main__":
    # if 
    # date=utilities.last_business(utilities.next_business()).strftime("%Y%m%d")
    position_path=r"C:\RedXCapital\Dividends\Data\Position" #TODO add vix in the account level
    
    #current_positions.to_csv(position_path+'\\'+'ibkr_pos_'+date+'.csv', index=False) # TODO make this into excel
    print("Grab Positions and Summary!")
    pos_directory=position_path+'\\'+'ibkr_pos_'+date+'.xlsx'    
    try:
        account_summary=pd.read_excel(pos_directory, sheet_name='Dividend')
        portfolio_value=account_summary.iloc[-1]['Target Market Value']
    except:
        portfolio_value=110000
    
    stock_symbols = ['TSLA', 'NVDA','COIN', 'ARKK', 'META','AMD','PYPL','SQ','NFLX', 'AMZN', 'GOOGL','XOM', 'AAPL','MSFT','JPM','DIS','CLM','CRF','SVOL','QQQY','JEPY','IWMY','FEPI',"BITO","ISPY","AI",'SVIX']
    stocks_iv_actual=pd.DataFrame({'Stocks':stock_symbols,'Implied Volatility':np.nan})
    stocks_iv=pd.DataFrame({'Stocks':stock_symbols,'Implied Volatility':np.nan, 'Leverage Factor':np.nan})
    stocks_div=pd.DataFrame({'Stocks':list(dividend_tickers.keys()),'Dividend Yield':np.nan, 'Leverage Factor':np.nan})
    
    for symbol in list(dividend_tickers.keys()):
        dividend_yield=get_dividends(symbol, period='90d', historical=True)
        stocks_div.loc[stocks_div['Stocks']==symbol,'Dividend Yield']=(dividend_yield*100).round(2)
        stocks_div.loc[stocks_div['Stocks']==symbol,'Leverage Factor']=leverage_factor[symbol]
    stocks_div['Adj Yield']=stocks_div['Dividend Yield'] * stocks_div['Leverage Factor']
    # stocks_div=stocks_div.loc[stocks_div['Dividend Yield']>=25,:]
    stocks_div['Weights']=(stocks_div['Adj Yield'] / stocks_div['Adj Yield'].sum() * 100).round(2)
    stocks_div['Market Value']=(stocks_div['Weights'] / 100 * portfolio_value).round(2)
    stocks_div.sort_values('Market Value', ascending=False, inplace=True) 
    for symbol in stocks_div['Stocks']:
        div_yield=stocks_div.loc[stocks_div['Stocks']==symbol,'Dividend Yield'].values[0]
        if div_yield>=60:
            div_yield=1.5*div_yield
        elif div_yield>=50 and div_yield<60:
            div_yield=1.25*div_yield
        elif div_yield>=40 and div_yield<50:
            div_yield=.3*div_yield #implied_vols/10
        else:
            div_yield=0.0*div_yield #implied_vols/10
        stocks_div.loc[stocks_div['Stocks']==symbol,'Scaled Yield']=div_yield
    stocks_div['Scaled Adj Yield']=stocks_div['Scaled Yield'] * stocks_div['Leverage Factor']
    stocks_div['Scaled Weights']=(stocks_div['Scaled Yield'] / stocks_div['Scaled Yield'].sum() * 100).round(2)
    stocks_div['Scaled Market Value']=(stocks_div['Scaled Weights'] / 100 * portfolio_value).round(2)
    stocks_div.sort_values('Scaled Market Value', ascending=False, inplace=True) 
    #TODO remove this filter
    for symbol in stock_symbols:
        try:
            
            implied_vols = get_implied_volatility(symbol)
        except:
            implied_vols=get_volatility(symbol)
        if implied_vols<.01:
            implied_vols=get_volatility(symbol)
        if symbol=='CLM' or symbol=='CRF':
            # implied_vols=.19*3#implied_vols/2.5
            implied_vols=(get_dividends(symbol, historical=True))
        if symbol=='SVOL':
            implied_vols=.17*2 # 3
        if symbol=='QQQY':
            implied_vols=(get_dividends(symbol, historical=True))*4
        if symbol=='JEPY' : # stocks_div
            implied_vols=(get_dividends(symbol, historical=True))*3
        if symbol=="IWM" or symbol=='IWMY':
            implied_vols=get_dividends(symbol, historical=True)*1.5
        if symbol=='ISPY':
            implied_vols=.15*6 #(get_dividends(symbol, historical=True))*4            
        # if symbol=='ISPY':
        #     implied_vols=.4
            # implied_vols=.7*6
        # if symbol=='QQQ':
        #     implied_vols=0.51
        # if symbol=='SPY':
        #     implied_vols=0.51
        # implied_vols=implied_vols-.1a
        stocks_iv_actual.loc[stocks_iv_actual['Stocks']==symbol,'Implied Volatility']=implied_vols
        
        if implied_vols>=.6:
            implied_vols=1.5*implied_vols
        elif implied_vols>=.5 and implied_vols<.6:  
            implied_vols=1.25*implied_vols
        elif implied_vols>=.4 and implied_vols<.5:
            implied_vols=.3*implied_vols #implied_vols/10
        # elif implied_vols<.4:
        #     implied_vols=0
        elif implied_vols>=.3 and implied_vols<.4:
            implied_vols=0 # implied_vols/100
        elif implied_vols>.2 and implied_vols<.3:
            implied_vols=0 #implied_vols/100
        elif implied_vols<=.2:
            implied_vols=0# implied_vols/100
        implied_vols=implied_vols*leverage_factor[symbol]

        stocks_iv.loc[stocks_iv['Stocks']==symbol,'Implied Volatility']=implied_vols
        stocks_iv.loc[stocks_iv['Stocks']==symbol,'Leverage Factor']=leverage_factor[symbol]
        
    stocks_iv.sort_values('Implied Volatility', inplace=True, ascending=False)
    stocks_iv['Implied Volatility']=(stocks_iv['Implied Volatility']*100).round(2)
    stocks_iv['weights']=(stocks_iv['Implied Volatility']/stocks_iv['Implied Volatility'].sum()*100).round(2)
    stocks_iv['MV']=(stocks_iv['weights']/100)* portfolio_value
    stocks_iv['Leverage Factor']=stocks_iv['Leverage Factor'].map('{:.1f}'.format)
    
    stocks_iv_actual.sort_values('Implied Volatility', inplace=True, ascending=False)
    stocks_iv_actual['Implied Volatility']=(stocks_iv_actual['Implied Volatility']*100).round(2)
    stocks_iv_actual['weights']=(stocks_iv_actual['Implied Volatility']/stocks_iv_actual['Implied Volatility'].sum()*100).round(2)
    stocks_iv_actual['MV']=(stocks_iv_actual['weights']/100)* portfolio_value
    
    stocks_iv=stocks_iv[['Stocks','Implied Volatility','weights','MV','Leverage Factor']]
    stocks_iv=stocks_iv.loc[stocks_iv['MV']!=0,:]
    
    # webhook.send(text='Date: '+datetime.datetime.today().strftime('%m/%d/%Y')+'\n Recent 90 trading days yield. \n'+stocks_div.to_markdown())
    # webhook.send(text='Date: '+datetime.datetime.today().strftime('%m/%d/%Y')+'\n 10 days out IV. \n'+stocks_iv_actual.to_markdown())
       
    
    portfolio_tickers=list(dividend_tickers.keys())   
    # portfolio_tickers.extend(['SPY','QQQ',"IWM"])
    stock=yf.download(portfolio_tickers,progress=False, period="5y") # actions=None,
    # stock['Adj Close']
    portfolio_adv=stock['Volume'].rolling(20, min_periods=5).mean().iloc[-1].round(0)
    adv=pd.DataFrame((portfolio_adv * stock['Close'].iloc[-1]).round(2))
    # adv.apply(lambda x: '{:,.0f}'.format(x))
    adv.sort_values(by=adv.columns[0],ascending=False, inplace=True)
    adv=adv[adv.columns[0]].map('{:,.0f}'.format)
    

    
    current_levels=stock['Close'].iloc[-1].round(2)
    minimum_levels=stock['Low'].rolling(252*2, min_periods=5).min().iloc[-1].round(2)
    portfolio_maxdrawup=((current_levels/minimum_levels - 1)*100).round(2) #TODO add underlying class group as part of this
    portfolio_analytics=pd.concat([current_levels,minimum_levels,portfolio_maxdrawup],axis=1) # ,portfolio_dolar_adv,portfolio_adv
    portfolio_analytics.columns=['Current PX','Min PX 2yr','Max drawup'] # , 'Dollar ADV20','ADV20'
    portfolio_analytics.reset_index(inplace=True)
    portfolio_analytics.rename(columns={'index':'Ticker'}, inplace=True)
    # portfolio_analytics['Dollar ADV20']=portfolio_analytics['Dollar ADV20'].map('{:,.0f}'.format)
    # portfolio_analytics['ADV20']=portfolio_analytics['ADV20'].map('{:,.0f}'.format)
    portfolio_analytics.sort_values('Max drawup', inplace=True)
    portfolio_analytics.rename(columns={'Ticker':'Stocks'}, inplace=True)
    
    
    portfolio_analytics['Underlying Stocks']=portfolio_analytics['Stocks'].apply(lambda x: list(class_group[x].keys())[0])
    
    underlying_data=yf.download(portfolio_analytics['Underlying Stocks'].to_list(),progress=False, period="5y") # actions=None,
    current_levels=underlying_data['Close'].iloc[-1].round(2)
    minimum_levels=underlying_data['Low'].rolling(252*2, min_periods=5).min().iloc[-1].round(2)
    portfolio_maxdrawup=((current_levels/minimum_levels - 1)*100).round(2) #TODO add underlying class group as part of this
    underlying_data=pd.concat([current_levels,minimum_levels,portfolio_maxdrawup],axis=1) # ,portfolio_dolar_adv,portfolio_adv
    underlying_data.columns=['Current PX','Min PX 2yr','Max drawup 2yr'] # , 'Dollar ADV20','ADV20'
    underlying_data.reset_index(inplace=True)
    underlying_data.sort_values('Max drawup 2yr', inplace=True)
    underlying_data.rename(columns={'index':'Ticker'}, inplace=True)
    
    portfolio_analytics=portfolio_analytics.merge(underlying_data, left_on="Underlying Stocks",right_on="Ticker",how='left')
    # stocks_iv=stocks_iv.merge(portfolio_analytics, left_on="Stocks",right_on="Underlying Stocks",how='left')
    # portfolio_analytics=portfolio_analytics.merge(stocks_iv, how='left', right_on='Stocks',left_on="Underlying Stocks")
    # del underlying_data['Stocks_y']
    # del underlying_data['Underlying Stocks']
    del portfolio_analytics['Ticker']
    
    # underlying_data=underlying_data.loc[underlying_data['MV'].notna(),:]
    
    # webhook.send(text='Date: '+datetime.datetime.today().strftime('%m/%d/%Y')+'\n 10 days out IV. \n'+stocks_iv.to_markdown())
    webhook.send(text='Date: '+datetime.datetime.today().strftime('%m/%d/%Y')+'\n Max Drawup. \n'+portfolio_analytics.to_markdown())
    webhook.send(text='Date: '+datetime.datetime.today().strftime('%m/%d/%Y')+'\n Max Drawup Underlying. \n'+underlying_data.to_markdown())
    # webhook.send(text='Date: '+datetime.datetime.today().strftime('%m/%d/%Y')+'\n Daily Dollar ADV. \n'+adv.to_markdown())
 
# import yfinance as yf
# import numpy as np
# def get_min_to_recent_close_price_ratio(tickers):
#     # Initialize a dictionary to store the min unadjusted close price and most recent close price for each ticker
#     min_to_recent_ratio = {}
#     for ticker in tickers:
#         # Fetch historical data for the ticker using yfinance
#         stock_data = yf.Ticker(ticker).history(period='2y')
#         print(stock_data.tail(5))
#         # Calculate the minimum unadjusted close price over the entire available history
#         min_unadjusted_close_price = stock_data['Close'].min()
#         # Get the most recent unadjusted close price
#         recent_close_price = stock_data['Close'].iloc[-1]
#         # Calculate the ratio of min to recent close price
#         ratio = min_unadjusted_close_price / recent_close_price - 1
#         # Store the ratio in the dictionary
#         min_to_recent_ratio[ticker] = ratio
#     return min_to_recent_ratio
# if __name__ == "__main__":
#     tickers = ['TSLA', 'META', 'ARKK', 'NVDA', 'AMZN', 'GOOGL', 'AAPL', 'CLM', 'CRF']
#     ratio_dict = get_min_to_recent_close_price_ratio(tickers)
#     stock_symbols = ['TSLA', 'META', 'ARKK', 'NVDA', 'AMZN', 'GOOGL', 'AAPL','CLM','CRF']
#     stocks_iv=pd.DataFrame({'Stocks':stock_symbols,'Loss Min':np.nan})
#     for ticker, ratio in ratio_dict.items():
#         stocks_iv.loc[stocks_iv['Stocks']==ticker,'Loss Min']=ratio
#     stocks_iv.sort_values('Loss Min', inplace=True)
# import yfinance as yf
# import pandas as pd
# import numpy as np
# def calculate_rolling_volatility(ticker, window=20):
#     stock_data = yf.download(ticker, period="1y")  # Download historical data for the last 1 year
#     stock_data['Ret'] = stock_data['Adj Close'].pct_change()
#     stock_data['Volatility'] = stock_data['Ret'].rolling(window=window).std()  # Calculate rolling volatility
#     return stock_data[['Adj Close', 'Volatility']].dropna()
# if __name__ == "__main__":
#     tickers = ["BITI", "BITO"]
#     for ticker in tickers:
#         volatility_data = calculate_rolling_volatility(ticker)
#         print(f"Rolling 20-day volatility for {ticker}:")
#         print(volatility_data.tail())  # Print the last few rows of volatility data
#         print("\n")
# volatility_data.tail(50)
# # conintegrgation BITO BITI
# import yfinance as yf
# import numpy as np
# import statsmodels.api as sm
# import matplotlib.pyplot as plt
# def get_historical_prices(ticker_list, start_date, end_date):
#     data = yf.download(ticker_list, start=start_date, end=end_date)['Adj Close']
#     return data
# def cointegration_analysis(data, ticker1, ticker2):
#     # Step 1: Calculate the spread between the two assets
#     spread = data[ticker1] - data[ticker2]
#     # Step 2: Perform cointegration test
#     results = sm.OLS(spread, sm.add_constant(data[ticker2])).fit()
#     # Get the hedge ratio (slope) from the regression result
#     hedge_ratio = results.params[ticker2]
#     # Calculate the spread mean and standard deviation for z-score calculation
#     spread_mean = np.mean(spread)
#     spread_std = np.std(spread)
#     return hedge_ratio, spread_mean, spread_std, spread
# def pair_cointegration_trade(ticker1, ticker2, hedge_ratio, spread_mean, spread_std, data):
#     # Step 1: Calculate the spread between the two assets
#     spread = data[ticker1] - hedge_ratio * data[ticker2]
#     # Step 2: Calculate z-score for the spread
#     z_score = (spread - spread_mean) / spread_std
#     # Step 3: Define trading signals based on z-score thresholds
#     entry_threshold = 2.0
#     exit_threshold = 0.5
#     # Step 4: Implement trading strategy
#     positions = np.zeros(len(data))
#     for i in range(1, len(data)):
#         if z_score[i - 1] > entry_threshold and z_score[i] <= entry_threshold:
#             # Buy signal (long ticker1, short hedge_ratio * ticker2)
#             positions[i] = 1
#         elif z_score[i - 1] < -entry_threshold and z_score[i] >= -entry_threshold:
#             # Sell signal (short ticker1, long hedge_ratio * ticker2)
#             positions[i] = -1
#         elif abs(z_score[i]) < exit_threshold:
#             # Exit signal (close positions)
#             positions[i] = 0
#         else:
#             positions[i] = positions[i - 1]
#     return positions, spread
# if __name__ == "__main__":
#     tickers = ["BITO", "BITI"]
#     start_date = "2023-01-01"
#     end_date = "2023-08-02"
#     # Step 1: Get historical prices
#     data = get_historical_prices(tickers, start_date, end_date)
#     # Step 2: Perform cointegration analysis
#     hedge_ratio, spread_mean, spread_std, spread = cointegration_analysis(data, tickers[0], tickers[1])
#     print(f"Hedge Ratio: {hedge_ratio}")
#     # Step 3: Implement pair trading strategy
#     positions, spread = pair_cointegration_trade(tickers[0], tickers[1], hedge_ratio, spread_mean, spread_std, data)
#     print(positions)
#     # Step 4: Plot the spread
#     plt.figure(figsize=(12, 6))
#     plt.plot(spread, label="Spread")
#     plt.axhline(spread_mean, color='r', linestyle='--', label='Spread Mean')
#     plt.axhline(spread_mean + 2 * spread_std, color='g', linestyle='--', label='Upper Threshold')
#     plt.axhline(spread_mean - 2 * spread_std, color='g', linestyle='--', label='Lower Threshold')
#     plt.legend()
#     plt




