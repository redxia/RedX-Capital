import logging

import pandas as pd

#################################

log = logging.getLogger(__name__)

#################################

def get_excel_dataframe(filename, sheet_name='sheet1', column_count=0, **kwargs) -> pd.DataFrame:
    '''
    NOTES: 
    * Convert to list of lists: df.values
    * Convert to list of dicts: df.dict('records')
    '''

    #Load Excel file
    df = pd.read_excel(filename, sheet_name=sheet_name, header=0, **kwargs) #, names=None, index_col=None, usecols=None, squeeze=False, dtype=None, engine=None, converters=None, true_values=None, false_values=None, skiprows=None, nrows=None, na_values=None, parse_dates=False, date_parser=None, thousands=None, comment=None, skipfooter=0, convert_float=True, **kwds
    
    if column_count:

        #Remove Extra Columns
        while len(df.columns)>column_count:
            log.warn('DROPPING COLUMN')
            df = df = df.iloc[:, :-1] #df.drop(index=len(df.columns)-1)

        # Add Missing Columns
        while len(df.columns)<column_count:
            log.warn('ADDING COLUMN')
            df[f'COLUMN_{len(df.columns)}'] = None

    return df

#################################

def get_csv_dataframe(filename, sep=',', **kwargs):
    df = pd.read_csv(filename,sep=sep, **kwargs)
    return df


