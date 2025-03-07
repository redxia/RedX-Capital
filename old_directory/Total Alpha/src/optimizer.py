from pypfopt import EfficientFrontier
from pypfopt import EfficientSemivariance
import numpy as np
import matplotlib.pyplot as plt

def run_optimizer(total_index, returns):
    # target_tickers=total_index['Tickers'].to_list()
    print(total_index.loc[total_index['mu'].isna()])
    total_index=total_index.loc[total_index['mu'].notna(),:]
    
    cov=returns.iloc[(-21*4):,:].cov() * 252
    cov.drop(index='SPY',columns='SPY', errors='ignore', inplace=True) 
    missing_tickers=total_index['Tickers'].isin(cov.columns)
    cov_missing=cov.columns[~cov.columns.isin(total_index['Tickers'])]
    cov.drop(index=cov_missing,columns=cov_missing, errors='ignore', inplace=True) 
    print('Missing Tickers: ',total_index['Tickers'][~missing_tickers])
    total_index=total_index.loc[missing_tickers]
    total_index['Volatility']=np.diag(cov)**0.5 
        
    # total_index['Upper Bound']=total_index['Weight']+.03
    # total_index['Upper Bound']=.03
    total_index.loc[(total_index['Market Cap']>150000000000) ,'Upper Bound']=total_index['Weight']+.025 # 150bil
    total_index.loc[(total_index['Market Cap']<=150000000000) & (total_index['Market Cap']>50000000000) ,'Upper Bound']=total_index['Weight']+.02
    total_index.loc[(total_index['Market Cap']<=50000000000) ,'Upper Bound']=total_index['Weight']+.01 # 50 bil
    
    total_index['Lower Bound']=(total_index['Weight']-.01).clip(0)
    # total_index['Lower Bound']=(total_index['Weight']-.02)
    # total_index['Lower Bound']=-.02
    # total_index.loc[(total_index['Market Cap']>200000000000) ,'Lower Bound']=-.02
    # total_index.loc[(total_index['Market Cap']<=200000000000) & (total_index['Market Cap']>50000000000) ,'Lower Bound']=-.01
    # total_index.loc[(total_index['Market Cap']<=50000000000) ,'Lower Bound']=-.005

    #TODO add beta and alpha into the df.
    
    wgt_bounds=list(zip(total_index['Lower Bound'], total_index['Upper Bound']))
    spy_ret=returns['SPY']
    del returns['SPY']
    # ef=EfficientFrontier(total_index['mu'], cov, weight_bounds=wgt_bounds) #
    ef=EfficientSemivariance(expected_returns=total_index['mu'], returns=returns, weight_bounds=wgt_bounds)
    ef.max_quadratic_utility(risk_aversion=0.01) 
    
    # dirty_weight=ef.max_sharpe(risk_free_rate=0.02)
    # dirty_weight=ef.max_quadratic_utility(risk_aversion=5)
    clean_weights=ef.clean_weights()
    total_index['MVO Weight']=list(clean_weights.values())
    total_index['MVO Weight']=total_index['MVO Weight'].round(4)
    total_index['Active Weights']=total_index['MVO Weight'] - total_index['Weight']
    # total_index['Active Weights']=total_index['MVO Weight'] + total_index['Weight']
    optimal_weights=total_index.loc[total_index['MVO Weight']!=0,:]
    optimal_weights.sort_values('MVO Weight', ascending=False, inplace=True)
    # optimal_weights.sort_values('Active Weights', ascending=False, inplace=True)
    print(ef.portfolio_performance())
    print('Portfolio Beta',(optimal_weights['beta'] * optimal_weights['MVO Weight']).sum())
    
    # alpha.loc[:,optimal_weights['Tickers']].plot(figsize=(16,14))
    # beta.loc[:,optimal_weights['Tickers']].plot(figsize=(16,14))
    # exp_ret.loc[:,optimal_weights['Tickers']].plot(figsize=(16,14))
    correlation=returns.iloc[(-21*4):,:].corr()
    
    optimal_returns=returns.loc[:, optimal_weights['Tickers']]

    mvo_weights = optimal_weights.set_index('Tickers')['MVO Weight']  # Set Tickers as index for alignment
    mvo_weights_aligned = mvo_weights.reindex(optimal_returns.columns)  # Align weights to the columns of optimal_returns

    # Perform the dot product
    result = optimal_returns.dot(mvo_weights_aligned)

    # Display the result
    print(result)

    # Calculate cumulative results
    cumulative_results = (result+1).cumprod()

    spy_cum=(spy_ret.iloc[-cumulative_results.dropna().shape[0]:]+1).cumprod()
    spy_cum.plot()
    
    (cumulative_results-spy_cum ).plot()
    print((cumulative_results-spy_cum ).dropna().head(40))
    
    # # Plot cumulative results
    # plt.figure(figsize=(10, 6))
    # plt.plot(cumulative_results, label="Cumulative Results")
    # plt.title("Cumulative Results Over Time")
    # plt.xlabel("Date")
    # plt.ylabel("Cumulative Returns")
    # plt.legend()
    # plt.grid(True)
    # plt.show()
    
    
    return total_index, optimal_weights, cov, correlation