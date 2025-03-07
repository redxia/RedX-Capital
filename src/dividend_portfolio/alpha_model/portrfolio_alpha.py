from utilities import utilities
import yfinance as yf
import pandas as pd

def alpha_model(universe_returns, vix_cut):
    
    tickers=utilities.read_config_file("alpha_input.jsonc")
    tickers_ls=list(tickers.keys())
    tickers_ls.append('^VIX')
    universe=yf.download(tickers_ls, progress=False)['Close']
    universe_returns=universe.pct_change()
    del universe_returns['^VIX']
    vix_bucket=pd.qcut(universe['^VIX'],5,[1,2,3,4,5])
    universe_returns=pd.concat([universe_returns, vix_bucket], axis=1)
    win_rate=pd.DataFrame(index=universe_returns.columns, columns=['Positive_Returns','Win_Rate','Negative_Returns']).iloc[:-1]
    

    vix_returns=universe_returns.loc[universe_returns['^VIX']==vix_cut]

    for column in vix_returns.columns[:-1]:
        win_rate.loc[column,'Win_Rate']=(vix_returns[column].dropna()>0).mean()
        win_rate.loc[column,'Positive_Returns']=(vix_returns.loc[vix_returns[column].gt(0), column]).mean()
        win_rate.loc[column,'Negative_Returns']=(vix_returns.loc[vix_returns[column].lt(0), column]).mean()

    win_rate['Lose_Rate']=(1-win_rate['Win_Rate'])

    win_rate['Adj Sharpe']=(win_rate['Win_Rate'] * win_rate['Positive_Returns']) / (win_rate['Lose_Rate'] * win_rate['Negative_Returns'].abs()) - 1
        
    win_rate.sort_values('Adj Sharpe',ascending=False, inplace=True)