import pandas as pd
def add_to_df(series, name, df, interpolation=False):
    fred_df=pd.DataFrame({"Date":series.index,name:series.values})
    if interpolation:
        fred_df[name]=fred_df[name].interpolate()
    df=df.merge(fred_df, on='Date', how='left')
    return df