import os
import os.path
import re
import io
import logging
from types import SimpleNamespace

import snowflake.connector
from snowflake.connector import DictCursor
from snowflake.connector.errors import ProgrammingError

from gp2.secrets import get_secret
from gp2.settings import namespace as settings, settings as settings_map

#################################

log = logging.getLogger(__name__)
conn = None

#################################

def get_credentials() -> SimpleNamespace:
    '''
    Returns credentials from environment environment variables or from AWS secret manager
    '''
    if 'SNOWSQL_PWD' in os.environ and 'SNOWSQL_USER' in os.environ:
        return SimpleNamespace(
            user            = os.environ['SNOWSQL_USER'],
            password        = os.environ['SNOWSQL_PWD'],
            insecure_mode   = os.getenv('SNOWSQL_INSECUREMODE','true').lower().strip()=='true',
            warehouse       = settings_map.get('warehouse', os.getenv('SNOWSQL_WAREHOUSE', 'skywalker')), # try settings, then env, then default
            role            = settings_map.get('role',      os.getenv('SNOWSQL_ROLE', 'analyst')),        # try settings, then env, then default
            account         = 'guidepoint'
        )
    else:
        secret = get_secret('ETL.SNOWFLAKE')
        return SimpleNamespace(
            user            = secret['USERNAME'],
            password        = secret['PASSWORD'],
            insecure_mode   = secret.get('SNOWSQL_INSECUREMODE','true').lower().strip()=='true',
            warehouse       = 'solo',
            role            = 'etl',
            account         = 'guidepoint'
        )

def get_sqlalchemy_connection_string(database='research', schema='scratch') -> str:
    '''Returns a SqlAlchemy Connection String - https://docs.snowflake.net/manuals/user-guide/sqlalchemy.html'''
    c = get_credentials()
    connection_string = f'snowflake://{c.user}:{c.password}@{c.account}/{database}/{schema}?insecure_mode={c.insecure_mode}&warehouse={c.warehouse}'
    return connection_string

#################################

def connect(reconnect=False):
    '''Returns: Existing connection or initialized new connection'''
    global conn
    if reconnect:
        disconnect()
    elif conn:
        return conn
    else:
        c = get_credentials()
        conn = snowflake.connector.connect(account=c.account, warehouse=c.warehouse, user=c.user, password=c.password, role=c.role, insecure_mode=c.insecure_mode)
        log.debug(f'SNOWFLAKE CONNECTED: USER={c.user}, VERSION={snowflake.connector.__version__}')
        del c
        log.info(f'SNOWFLAKE SESSION_ID: {conn.session_id}')
        return conn

def disconnect():
    '''Closes the existing connetion, if established'''
    global conn
    if conn:
        conn.close()
        conn = None
        log.debug('SNOWFLAKE DISCONNECTED')

#################################

def remove_comment_lines(sql):
    return re.sub(r'^\s*--.*$', '', sql, flags=re.MULTILINE)

def execute(sql, args=None, ignore_empty=True, clean=False):
    # Remove comments and leading white space
    if clean:
        sql = remove_comment_lines(sql).strip(u' \t\n\r')
    if not sql:
        return
    try:
        return connect().cursor().execute(sql, args)
    except ProgrammingError as ex:        
        if ex.errno==900 and ignore_empty: return None #Ignore empty statements
        raise

def fetchone(sql, args=None, ignore_empty=False):
    cur = execute(sql,args)
    return cur.fetchone() if cur else None

def fetchall(sql, args=None, ignore_empty=False):
    cur = execute(sql,args)
    return cur.fetchall() if cur else None

def fetchall_simple(sql):
    cur = execute(sql)
    if not cur: 
        return None
    else:
        result = cur.fetchall()
        keys = [ c[0] for c in cur.description]
        simple_result = [ SimpleNamespace(**dict(zip(keys, values))) for values in result ]
        return simple_result

#################################