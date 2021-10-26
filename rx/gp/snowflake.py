"""
********************************************************************************
     Module: gp.snowflake
Description: Simple wrapper for common Snowflake operations
      Usage: Set environment varaibles SNOWSQL_PWD, SNOWSQL_USER,
             before calling connect().
     Author: Justin Jones
    Created: 2017-09-18
********************************************************************************
"""

import os
import os.path
import re
import io
import sys
import json
import traceback
import logging
from datetime import datetime
from types import SimpleNamespace

import snowflake.connector
from snowflake.connector import DictCursor
from snowflake.connector.errors import ProgrammingError

import gp.utils
from gp.settings import namespace as settings, settings as settings_map
from .secrets import get_secret,get_secret_value

#################################

log = logging.getLogger(__name__)
conn = None

#################################

def get_credentials():
    '''Returns: Namespace containing credentials and other connection details'''
        
    if 'SNOWSQL_PWD' in os.environ and 'SNOWSQL_USER' in os.environ:

        return SimpleNamespace(
            user            = os.environ['SNOWSQL_USER'],
            password        = os.environ['SNOWSQL_PWD'],
            insecure_mode   = 'SNOWSQL_INSECUREMODE' in os.environ and os.environ['SNOWSQL_INSECUREMODE'].lower().strip()=='true',
            warehouse       = (settings.warehouse if 'warehouse' in settings_map
                                else os.environ['SNOWSQL_WAREHOUSE'] if 'SNOWSQL_WAREHOUSE' in os.environ 
                                else None),
            role            = (settings.role if 'role' in settings_map
                                else os.environ['SNOWSQL_ROLE'] if 'SNOWSQL_ROLE' in os.environ 
                                else 'analyst'),
            account         = 'guidepoint'
        )

    else:

        try:
            SNOWFLAKE_SECRETS = get_secret('ETL.SNOWFLAKE')
            return SimpleNamespace(
                user            = get_secret_value(SNOWFLAKE_SECRETS,'USERNAME'),
                password        = get_secret_value(SNOWFLAKE_SECRETS,'PASSWORD'),
                insecure_mode   = get_secret_value(SNOWFLAKE_SECRETS,'SNOWSQL_INSECUREMODE'),
                warehouse       = 'solo',
                role            = 'etl',
                account         ='guidepoint'
            )
        finally:
            del SNOWFLAKE_SECRETS

#################################

def get_sa_connection_string(database='research', schema='scratch'):
    '''Returns a SqlAlchemy Connection String - https://docs.snowflake.net/manuals/user-guide/sqlalchemy.html'''
    c = get_credentials()
    connection_string = f'snowflake://{c.user}:{c.password}@{c.account}/{database}/{schema}?insecure_mode={c.insecure_mode}&warehouse={c.warehouse}'
    return connection_string

#################################

def connect(reconnect=False):
    '''Returns: Exist connection singleton, initializing it if not already initialized. '''

    global conn

    # Stop here if already connected
    if (conn!=None and not reconnect):
        return conn

    else:
        c = get_credentials()
        conn = snowflake.connector.connect(account=c.account, warehouse=c.warehouse, user=c.user, password=c.password, role=c.role, insecure_mode=c.insecure_mode)
        log.debug(f'Snowflake Connector Version: {snowflake.connector.__version__}')
        log.debug(f'Snowflake Connected: user={c.user}')
        del c
        return conn

def disconnect():
    '''Closes the existing connetion, if established'''

    global conn
    if conn == None: return
    conn.close()
    conn = None

#################################

def autocommit(enabled=True):
    conn.autocommmit = enabled
    log.debug(f'autocommit: {enabled}')

def commit():
    conn.commit()

def rollback():
    conn.rollback()

#################################

def current_database():
    connect()
    return fetchone(f'select current_database()')[0]

def current_schema():
    connect()
    return fetchone(f'select current_schema()')[0]

def current_role():
    connect()
    return fetchone(f'select current_role()')[0]

#################################

def use_database(database):
    connect()
    execute(f'use database {database}')
    assert database.lower() == current_database().lower()

def use_schema(schema):
    connect()
    execute(f'use schema {schema}')
    assert schema.lower() == current_schema().lower()

def use_role(role):
    connect()
    execute(f'use role {role}')
    assert role.lower() == current_role().lower()

#################################

def set_variable(name, value):
    connect()
    #if type(value==str): value = f"'{value}'"
    execute(f'set {name}=%s', value)
    
def get_variable(name):
    connect()
    value = fetchone(f'select ${name}')[0]
    log.debug(f'value: {value}')

#################################

def remove_comment_lines(sql):
    return re.sub(r'^\s*--.*$', '', sql, flags=re.MULTILINE)
    

def execute(sql, args=None, ignore_empty=False):

    connect()

    # Remove comments and leading white space
    sql_clean = remove_comment_lines(sql).strip(u' \t\n\r')

    # Skip if nothing to do
    if not sql_clean:
        log.debug('SKIPPING EMPTY QUERY:')
        log.debug(f'SQL:\n{gp.utils.indent(sql,4)}')
        log.debug(f'SQL CLEAN:\n{gp.utils.indent(sql_clean,4)}')
        return None

    try:
        # log.debug(f'SQL:\n{gp.utils.indent(sql,4)}')
        log.debug(f'SQL CLEAN:\n{gp.utils.indent(sql_clean,4)}')
        if args: log.debug(f'Args:\n{gp.utils.indent(gp.utils.to_json(args))}')
        return conn.cursor().execute(sql_clean, args)
    
    except ProgrammingError as ex:        
        if ex.errno==900 and ignore_empty: return None #Ignore empty statements
        raise ex

def fetchall(sql, args=None, ignore_empty=False):

    connect()

    try:
        result = execute(sql,args)
        if result: return result.fetchall()
        return None

    except ProgrammingError as ex:        
        if ex.errno==900 and ignore_empty: return None #Ignore empty statements
        raise ex

def fetchall_simple(sql):
    cur = execute(sql)
    if not cur: return None
    result = cur.fetchall()
    keys = [ c[0] for c in cur.description]
    simple_result = [ SimpleNamespace(**dict(zip(keys, values))) for values in result ]
    return simple_result

def fetchone(sql, args=None, ignore_empty=False):

    connect()

    try:
        return execute(sql,args).fetchone()

    except ProgrammingError as ex:        
        if ex.errno==900 and ignore_empty: return None #Ignore empty statements
        raise ex

#################################

def get_table_details(database, schema):
    connect()
    return fetchall(f"select * from {database}.information_schema.tables\nwhere table_type='BASE TABLE' and lower(table_schema)=lower('{schema}')")

def get_tables(database, schema):
    connect()
    rows = fetchall(f"select table_name from {database}.information_schema.tables\nwhere table_type='BASE TABLE' and lower(table_schema)=lower('{schema}')")
    return [ r[0] for r in rows]

def get_view_details( database, schema):
    connect()
    return fetchall(f"select * from {database}.information_schema.tables\nwhere table_type='VIEW' and lower(table_schema)=lower('{schema}')")

def get_views(database, schema):
    connect()
    rows = fetchall(f"select table_name from {database}.information_schema.tables\nwhere table_type='VIEW' and lower(table_schema)=lower('{schema}')")
    return [ r[0] for r in rows]


#################################

def dump_cursor(cur, n=10):

    connect()

    # Print results, if any
    if cur == None: return

    import pandas as pd

    # Configure pandas
    pd.set_option('display.width', None)

    # Get column names
    columns = [col[0] for col in cur.description]

    # Get first 10 rows
    data = cur.fetchmany(n)

    # Print
    if len(data)>0:
        df = pd.DataFrame(data=data, columns=columns)
        if len(data)==1: df = df.transpose()
        log.debug(f'Results\n{gp.utils.indent(df)}\n')

###########################################

def format_rows(rows, cols=None):

    # Empty or Null
    if not rows:
        return f'-- RESULT {rows}'

    # Single value
    if len(rows)==1 and len(rows[0])==1:
       return f'-- {rows[0][0]}'
    
    n = len(rows)
    if n > 5000: 
        log.warning(f'TRUNCATING OUTPUT FROM {n} to 5000 ROWS')
        rows = rows[:5000]
    # # Row of values
    # if len(rows)==1 and len(rows[0])>1:
    #     return '\n'.join([f'-- {value}' for value in rows[0]]) 

    max_width = lambda i: max(len(cols[i][0]), len(str(max(rows, key=lambda r: len(str(r[i])))[i]))) # Sorry

    one_line = lambda x: 'NULL' if x==None else str(x).replace('\r','').replace('\n',' ').replace('\t',' ')[:200]

    padded = lambda i,c: c + (' ' * (max_width(i) - len(c or '')))

    # Table 
    s  = '-- ' + (' | '.join([padded(i,c[0]) for i,c in enumerate(cols)]) +'\n') if cols else ''
    s += '-- ' + (' | '.join(['-'*len(padded(i,c[0])) for i,c in enumerate(cols)]) +'\n') if cols else ''
    for row in rows:
        # s += '-- ' + (' | '.join([padded(i,str(c)) for i,c in enumerate(row)]) +'\n')
        s += '-- ' + (' | '.join([padded(i,one_line(c)) for i,c in enumerate(row)]) +'\n')
    if n > 5000:
        s+=f'\n-- WARNING: Output Truncated from size {n} to size 5000\n'
    return (s)

#################################

def execute_script(sql, ignoreDoesNotExistError=False):

    connect()

    queries = [ s.strip() for s in sql.split(';') ]

    for q in queries:
        if len(q)==0:
            continue

        try:
            result = execute(q, ignore_empty=True)
            log.debug(gp.utils.to_json(result))

        except ProgrammingError as ex:        
            if ex.errno==2003 and ignoreDoesNotExistError: 
                log.error(ex)
            else:
                raise ex

def execute_steam(sql):

    # https://docs.snowflake.net/manuals/user-guide/python-connector-example.html#using-execute-stream-to-execute-sql-scripts

    connect()
    stream = io.StringIO(sql)
    results = conn.execute_stream(stream) 
    log.debug(gp.utils.to_json(results))
    return results

def write_csv(filename, sql, header=True, field_sep='|', row_sep='\n'):

    log.debug(f'filename: {filename}')
    log.debug(f'sql:\r\n{sql}')

    connect()

    cur = conn.cursor()

    data = cur.execute(sql).fetchall()

    h = field_sep.join([col[0] for col in cur.description]) + row_sep if header else ''

    clean = lambda f: '' if f==None else str(f)

    lines = [field_sep.join( [clean(field) for field in line]) for line in data]
    
    csv = h + row_sep.join(lines) + row_sep

    gp.utils.write_file(filename, csv)

#################################

def get_warehouse_details(name='SKYWALKER'):
    result = conn.cursor(DictCursor).execute("show warehouses like %s", name).fetchone()
    log.debug(result)    
    return result

#################################



#################################
