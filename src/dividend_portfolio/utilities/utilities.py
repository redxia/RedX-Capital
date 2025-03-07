import pandas_market_calendars as mcal
from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import jstyleson
import win32com.client

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


def read_config_file(jsonc_config):
    config=open(jsonc_config, 'r')
    adj_acc=jstyleson.load(config)
    config.close()
    return adj_acc

def read_position_file():
    start_time=datetime.now()
    date=last_business(next_business()).strftime("%Y%m%d") if start_time.hour>16 else last_business().strftime("%Y%m%d")
    positions=pd.read_excel(r"C:\RedXCapital\Dividends\Data\Position\ibkr_pos_"+date+".xlsx", sheet_name="Current Portfolio")
    return positions

def read_summary_file():
    start_time=datetime.now()
    date=last_business(next_business()).strftime("%Y%m%d") if start_time.hour>16 else last_business().strftime("%Y%m%d")
    summary=pd.read_excel(r"C:\RedXCapital\Dividends\Data\Position\ibkr_pos_"+date+".xlsx", sheet_name="Account Summary")
    return summary

def read_hedge_file():
    start_time=datetime.now()
    date=last_business(next_business()).strftime("%Y%m%d") if start_time.hour>16 else last_business().strftime("%Y%m%d")
    risk_exposure=pd.read_excel(r"C:\RedXCapital\Dividends\Data\Position\ibkr_pos_"+date+".xlsx", sheet_name="Risk Exposures")
    return risk_exposure

def send_outlook_email(to, subject, cc, html_msg, attachment_dir=''):
    outlook=win32com.client.Dispatch("outlook.application")
    mail=outlook.CreateItem(0)
    From=[emails for emails in outlook.Session.Accounts if 'redmond.xia' in str(emails)][0]
    mail._oleobj_.Invoke(*(64209, 0 , 8, 0, From))
    mail.To=to
    mail.Subject=subject
    mail.CC=cc
    mail.HTMLBody=html_msg
    if attachment_dir!='':
        mail.Attachments.Add(attachment_dir)
    mail.Send()
    print('Email Sent!')
    return