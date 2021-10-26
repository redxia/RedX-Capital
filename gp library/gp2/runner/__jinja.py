import logging
import sys
import os
import re
from datetime import date, datetime, timedelta
import time
from types import SimpleNamespace
import jinja2
#from jinja2 import Template
#from jinja2 import Environment, FileSystemLoader

import pandas

import gp2.job
import gp2.utils
import gp2.utils.dataframe
import gp2.snowflake as snowflake
from gp2.settings import settings as settings_map, namespace as settings, settings_file

log = logging.getLogger(__name__)

#############################
# Create Jinja environment
#############################

LoggingUndefined = jinja2.make_logging_undefined(logger=log, base=jinja2.Undefined)

template_folders = [
    '.',
    os.path.join(os.path.dirname(__file__), 'templates'),
    os.path.join(os.getcwd(), '..', 'shared', 'templates')
]

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_folders),
    trim_blocks=True,
    # lstrip_blocks=True,
    line_statement_prefix = '::',
    line_comment_prefix = '#',
    autoescape =False,
    # undefined=jinja2.StrictUndefined
    undefined=jinja2.StrictUndefined if settings_map.get('jinja_strict_undefined', True) else LoggingUndefined, #jinja2.Undefined,
    extensions = ['jinja2.ext.do', 'jinja2.ext.loopcontrols'] #, 'jinja2.ext.with_']
)

#############################
# Initialize useful globals
#############################

env.globals['SimpleNamespace'] = SimpleNamespace
env.globals['last_fetch'] = []
env.globals['settings'] = settings
env.globals['start_time'] = gp2.job.start_time
env.globals['run_id'] = gp2.job.run_id
env.globals['git_hash'] = gp2.job.git_hash
env.globals['run_date'] = gp2.job.start_time.date()
env.globals['job_output_url'] = gp2.job.job_output_locations.output_url
env.globals['cwd'] = os.getcwd()
env.globals['pandas'] = pandas
env.globals['get_excel_dataframe'] = gp2.utils.dataframe.get_excel_dataframe
env.globals['get_csv_dataframe'] = gp2.utils.dataframe.get_csv_dataframe

#############################
# SQL help functions
#############################

def fetch_all(result_name='last_fetch'):
    env.globals[result_name] = env.globals['last_fetch']
    return ''

def fetch_all_simple(sql="select * from table(result_scan(last_query_id()))", result_name='last_fetch') -> [SimpleNamespace]:
    cur = snowflake.execute(sql)
    result = cur.fetchall()
    keys = [ c[0].upper() for c in cur.description]
    simple_result = [ SimpleNamespace(**dict(zip(keys, values))) for values in result ]
    env.globals[result_name] = env.globals['last_fetch'] = simple_result
    #gp2.utils.append_file(tmp_file, snowflake.format_rows(result))
    # log.info(simple_result)
    return simple_result

def fetch_all_simple2(sql=None) -> [SimpleNamespace]:
    '''
    1. Execute specified query, or use previous results
    2. Convert to list of SimpleNamespaces
    '''
    last_fetch = env.globals.get('last_fetch', None)
    last_fetch_columns = env.globals.get('last_fetch_columns', None)
    assert sql or (last_fetch and last_fetch_columns)
    if sql:
        cur = snowflake.execute(sql)
        rows = cur.fetchall()
        cols = cur.description
    else:
        rows = last_fetch
        cols = last_fetch_columns
    col_names = [ c[0].upper() for c in cols]
    simple_result = [ SimpleNamespace(**dict(zip(col_names, row))) for row in rows ]
    return simple_result


def fetch_many_simple(n, sql="select * from table(result_scan(last_query_id()))", result_name='last_fetch') -> [SimpleNamespace]:
    cur = snowflake.execute(sql)
    result = cur.fetchmany(n)
    keys = [ c[0].upper() for c in cur.description]
    simple_result = [ SimpleNamespace(**dict(zip(keys, values))) for values in result ]
    env.globals[result_name] = env.globals['last_fetch'] = simple_result
    #gp2.utils.append_file(tmp_file, snowflake.format_rows(result))
    # log.info(simple_result)
    return simple_result

def fetch_one_simple(sql="select * from table(result_scan(last_query_id()))", result_name='last_fetch') -> SimpleNamespace:
    cur = snowflake.execute(sql)
    values = cur.fetchone()
    keys = [ c[0].upper() for c in cur.description]
    simple_result = SimpleNamespace(**dict(zip(keys, values)))
    env.globals[result_name] = env.globals['last_fetch'] = simple_result
    #gp2.utils.append_file(tmp_file, snowflake.format_rows(result))
    # log.info(simple_result)
    return simple_result

def fetch_value(sql="select * from table(result_scan(last_query_id()))", result_name='last_fetch') -> any:
    value = snowflake.fetchone(sql)[0]
    env.globals['last_fetch'] = env.globals[result_name] = value
    return value

env.globals['fetch_all_simple'] = fetch_all_simple
env.globals['fetch_all_simple2'] = fetch_all_simple
env.globals['fetch_many_simple'] = fetch_all_simple
env.globals['fetch_one_simple'] = fetch_one_simple
env.globals['fetch_value'] = fetch_value
# env.globals['fetch_all'] = fetchall

#############################
# LOG HELPERS
#############################

def log_debug(msg:str):   log.debug(msg);   return f'DEBUG: {msg}'
def log_info(msg:str):    log.info(msg);    return f'INFO: {msg}'
def log_warning(msg:str): log.warning(msg); return f'WARNING: {msg}'
def log_error(msg:str):   log.error(msg);   return f'ERROR: {msg}'

env.globals['log_debug']   = log_debug
env.globals['log_info']    = log_info
env.globals['log_warning'] = log_warning
env.globals['log_error']   = log_error

#############################
# ASSERT HELPERS
#############################

def assert_helper(test:bool, msg:str):
    if not test:
        s = f'ASSERT FAILED: {msg}'
        log.error(s)
        raise Exception(s)
    return f'ASSERT PASSED: {msg}'

def raise_helper(msg):
    log.error(f'EXCEPTION RAISED: {msg}')
    raise Exception(msg)

env.globals['raise'] = raise_helper
env.globals['assert'] = assert_helper

#############################
# FILTER HELPERS
#############################

def comment_lines(s):
    return re.sub('^', '-- ', s, flags=re.MULTILINE) if s else ''

def trim_lines(s):
    return re.sub(r'^\s+', '', s, flags=re.MULTILINE)  if s else ''

def condense_spaces(s):
    return re.sub(' +', ' ', s) if s else ''

def condense_whitespace(s):
    return re.sub(r'\s+', ' ', s) if s else ''

def format_date(d, format=r'%Y-%m-%d'):
    return d.strftime(format) if d else ''

def format_datetime(d, format=r'%Y-%m-%d %H:%M'):
    return d.strftime(format)  if d else ''

env.filters['comment_lines'] = comment_lines
env.filters['trim_lines'] = trim_lines
env.filters['condense_spaces'] = condense_spaces
env.filters['condense_whitespace'] = condense_whitespace
env.filters['format_date'] = format_date
env.filters['formate_datetime'] = format_datetime
env.filters['strip'] = lambda s,chars=' ': s.strip(chars) if s else ''

#############################
#############################


