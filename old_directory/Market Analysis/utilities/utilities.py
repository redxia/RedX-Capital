import pandas_market_calendars as mcal
from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np


def add_to_df(series, name, df, interpolation=False):
    fred_df=pd.DataFrame({"Date":series.index,name:series.values})
    if interpolation:
        fred_df[name]=fred_df[name].interpolate()
    df=df.merge(fred_df, on='Date', how='left')
    return df

nyse=mcal.get_calendar("NYSE")
def business_day():
    start_time=datetime.now()
    holidays=nyse.holidays().holidays[1500:2500]
    run=True
    if np.datetime64(start_time.strftime("%Y-%m-%d")) in holidays:
        run=False
    return run

def last_business(today=datetime.now()):
    two_weeks=nyse.schedule((today-timedelta(days=7)).strftime(r"%Y%m%d"), (today+timedelta(days=7)).strftime(r"%Y%m%d"))
    if nyse.open_at_time(two_weeks, pd.Timestamp((today-timedelta(days=1)).strftime(r"'%Y-%m-%d 9:30"), tz='America/New_York')):
        last_business_date=(today-timedelta(days=1))
    elif nyse.open_at_time(two_weeks, pd.Timestamp((today-timedelta(days=2)).strftime(r"'%Y-%m-%d 9:30"), tz='America/New_York')):
        last_business_date=(today-timedelta(days=2))        
    elif nyse.open_at_time(two_weeks, pd.Timestamp((today-timedelta(days=3)).strftime(r"'%Y-%m-%d 9:30"), tz='America/New_York')):
        last_business_date=(today-timedelta(days=3))        
    elif nyse.open_at_time(two_weeks, pd.Timestamp((today-timedelta(days=4)).strftime(r"'%Y-%m-%d 9:30"), tz='America/New_York')):
        last_business_date=(today-timedelta(days=4))    
    return last_business_date        

def next_business(today=datetime.now()):
    two_weeks=nyse.schedule((today-timedelta(days=7)).strftime(r"%Y%m%d"), (today+timedelta(days=7)).strftime(r"%Y%m%d"))
    if nyse.open_at_time(two_weeks, pd.Timestamp((today+timedelta(days=1)).strftime(r"'%Y-%m-%d 9:30"), tz='America/New_York')):
        next_business_date=(today+timedelta(days=1))
    elif nyse.open_at_time(two_weeks, pd.Timestamp((today+timedelta(days=2)).strftime(r"'%Y-%m-%d 9:30"), tz='America/New_York')):
        next_business_date=(today+timedelta(days=2))        
    elif nyse.open_at_time(two_weeks, pd.Timestamp((today+timedelta(days=3)).strftime(r"'%Y-%m-%d 9:30"), tz='America/New_York')):
        next_business_date=(today+timedelta(days=3))        
    elif nyse.open_at_time(two_weeks, pd.Timestamp((today+timedelta(days=4)).strftime(r"'%Y-%m-%d 9:30"), tz='America/New_York')):
        next_business_date=(today+timedelta(days=4))    
    return next_business_date

