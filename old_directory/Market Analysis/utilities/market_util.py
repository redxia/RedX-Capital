import pandas as pd

def get_returns(df, periods='monthly', ewma=False): 
    if ewma:
        column='Close_ewma'
    else:
        column='Close'
    
    
    if periods=='monthly':
        df['returns']=df[column].pct_change()
        df['returns_3mo']=df[column].pct_change(3)
        df['returns_6mo']=df[column].pct_change(6)
        df['returns_9mo']=df[column].pct_change(9)
        df['returns_12mo']=df[column].pct_change(12)
        df['returns_18mo']=df[column].pct_change(18)
        df['returns_24mo']=df[column].pct_change(24)
    elif periods=='daily':
        df['returns']=df[column].pct_change()
        df['returns_3mo']=df[column].pct_change(3*21)
        df['returns_6mo']=df[column].pct_change(6*21)
        df['returns_9mo']=df[column].pct_change(9*21)
        df['returns_12mo']=df[column].pct_change(12*21)
        df['returns_18mo']=df[column].pct_change(18*21)
        df['returns_24mo']=df[column].pct_change(24*21)
    return df