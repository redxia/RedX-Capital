import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import snowflake.connector
import os
import re



cnx = snowflake.connector.connect(
        user = os.environ.get("SNOWSQL_USER"),
        password = os.environ.get("SNOWSQL_PWD"),
        account = 'guidepoint')
cur = cnx.cursor()


df = pd.read_excel(r'C:\Users\AFontanella\Desktop\overlap_facilities_review_dedupe.xlsx', 
                   sheet_name='overlap_facilities_review_yeses')

df = df[['MOA_FACILITY', 'SARCO_FACILITY']]

def format_fac(x):
    if x[-1] == '_':
        y = x[:-1]
    else:
        y = x
    return y

df['MOA_FACILITY'] = df['MOA_FACILITY'].apply(lambda x: format_fac(x))
df['PETREL_FACILITY'] = df['PETREL_FACILITY'].apply(lambda x: format_fac(x))

df['MOA_DUPLICATE'] = df.duplicated(subset='MOA_FACILITY', keep=False)
df['PETREL_DUPLICATE'] = df.duplicated(subset='PETREL_FACILITY', keep=False)


def relationship(x):
    if x['MOA_DUPLICATE'] and x['PETREL_DUPLICATE']:
        y = 'MANY:MANY'
    elif x['MOA_DUPLICATE'] and ~x['PETREL_DUPLICATE']:
        y = 'ONE:MANY'
    elif ~x['MOA_DUPLICATE'] and x['PETREL_DUPLICATE']:
        y = 'MANY:ONE'
    else:
        y = 'ONE:ONE'
    return y

df['MOA_TO_PETREL_RELATIONSHIP'] = df.apply(lambda x: relationship(x), axis=1)

df = df[['MOA_FACILITY', 'PETREL_FACILITY', 'MOA_TO_PETREL_RELATIONSHIP']]

df.to_csv(r'C:\Users\AFontanella\Desktop\overlap_facilities_upload.csv', index=False, sep='|')

cur.execute("""
            create or replace table research.afontanella.overlap_facilities (
                    moa_facility varchar(1000) not NULL, 
                    petrel_facility varchar(1000) not NULL,
                    relationship varchar(1000) not NULL
                    );
""")

cur.execute("""
            put 'file://C://Users//AFontanella//Desktop//overlap_facilities_upload.csv' @~/temp/ source_compression=none auto_compress=true;
""")

cur.execute("""
            truncate research.afontanella.overlap_facilities;
""")

cur.execute("""
            copy into research.afontanella.overlap_facilities from  @~/temp/overlap_facilities_upload.csv.gz
            file_format = (type='CSV' compression=gzip field_delimiter='|' skip_header=1 field_optionally_enclosed_by='"')
            enforce_length = false 
            purge = true 
            force = true;
""")