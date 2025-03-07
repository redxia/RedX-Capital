import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime
from sklearn.decomposition import PCA
stock_path=r"C:\RedXCapital\Dividends\Data\Symbol"
market_path=r"C:\RedXCapital\Dividends\Data\Market Data"


def risk_model_updater(date=datetime.now().strftime("%Y%m%d")):
    symbols=os.listdir(stock_path)
    
    returns_matrix=pd.read_csv(stock_path+'\\'+symbols[0])[['Date','Returns']]
    returns_matrix.rename(columns={'Returns':symbols[0].split('.')[0]}, inplace=True)

    for i in symbols[1:]:
        ticker=pd.read_csv(stock_path+'\\'+i)[['Date','Returns']]
        ticker.rename(columns={'Returns':i.split('.')[0]}, inplace=True)
        returns_matrix=returns_matrix.merge(ticker, on='Date', how='left')

    returns_matrix.dropna(inplace=True)
    returns_matrix.set_index('Date', inplace=True)
    returns_matrix=returns_matrix.iloc[-63:]

    # cov=(returns_matrix @ returns_matrix.T) / returns_matrix.shape[1]
    cov=returns_matrix.T.cov()
    pca=PCA(.99)
    pca=pca.fit(cov)
    print("PCA variance ratio explained: ", pca.explained_variance_ratio_.cumsum())
    U=pca.components_.T

    gamma=pd.DataFrame(index=returns_matrix.index, columns=returns_matrix.columns)
    for i in returns_matrix.columns.to_list():
        X=sm.add_constant(U)
        Y=np.array(returns_matrix[i])
        Y.shape=(Y.shape[0],1) # reshapes
        mod = sm.OLS(Y,X)
        model=mod.fit()
        gamma[i]=returns_matrix[i].to_numpy().reshape((returns_matrix[i].shape[0],1)) - U @ model.params[1:] - model.params[0]

    gamma=gamma.T #
    delta_sq=np.diag(gamma @ gamma.T) / gamma.shape[1] #
    returns_star= pd.DataFrame(index=returns_matrix.index, columns=returns_matrix.columns) #
    for i in returns_matrix.columns.to_list():
        returns_star[i]=returns_matrix[i] / delta_sq[returns_matrix.columns.get_loc(i)] / 100

    cov_star=returns_star.cov()
    #cov_star=returns_star.T @ returns_star / returns_star.shape[0]
    cov_star.to_csv(r"C:\RedXCapital\Dividends\Data\Risk Model\risk_model_"+date+".csv")
    return