import logging
import sys
import os
import re
from datetime import date, datetime, timedelta
import time
from glob import glob
from types import SimpleNamespace
import shutil
import importlib
import threading
import gp.job
import gp.utils
from gp.settings import namespace as settings, settings_file
import gp.snowflake as snowflake
import jinja2
from snowflake.connector.errors import ProgrammingError
#from jinja2 import Template
#from jinja2 import Environment, FileSystemLoader
import concurrent.futures
from gp.settings import namespace as settings, settings as settings_map

### Init ##############################

# Get logger for this module
log = logging.getLogger(__name__)

# Minimize logging from our Snowflake library
# if not settings.debug: logging.getLogger('gp.snowflake').setLevel(logging.WARNING)

#### RUN #########################

log_duration = settings.log_duration if 'log_duration' in settings_map else True
log_query_id = settings.log_query_id if 'log_query_id' in settings_map else True


env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'), 
    trim_blocks=True, 
    # lstrip_blocks=True,
    line_statement_prefix = '::',
    line_comment_prefix = '#'
)

def fetch_all(result_name='last_fetch'):
    env.globals[result_name] = env.globals['last_fetch']
    return ''

def fetch_all_simple(sql="select * from table(result_scan(last_query_id()))", result_name='last_fetch'):
    cur = snowflake.execute(sql)
    result = cur.fetchall()
    keys = [ c[0].upper() for c in cur.description]
    simple_result = [ SimpleNamespace(**dict(zip(keys, values))) for values in result ]
    env.globals[result_name] = env.globals['last_fetch'] = simple_result
    #gp.utils.append_file(tmp_file, snowflake.format_rows(result))
    # log.info(simple_result)
    return simple_result

def fetch_one_simple(sql="select * from table(result_scan(last_query_id()))", result_name='last_fetch'):
    cur = snowflake.execute(sql)
    values = cur.fetchone()
    keys = [ c[0].upper() for c in cur.description]
    simple_result = SimpleNamespace(**dict(zip(keys, values))) 
    env.globals[result_name] = env.globals['last_fetch'] = simple_result
    #gp.utils.append_file(tmp_file, snowflake.format_rows(result))
    # log.info(simple_result)
    return simple_result

def fetch_value(sql="select * from table(result_scan(last_query_id()))", result_name='last_fetch'):
    value = snowflake.fetchone(sql)[0]
    env.globals['last_fetch'] = env.globals[result_name] = value
    return value

env.globals['fetch_all_simple'] = fetch_all_simple
env.globals['fetch_one_simple'] = fetch_one_simple
env.globals['fetch_value'] = fetch_value
# env.globals['fetch_all'] = fetchall
env.globals['SimpleNamespace'] = SimpleNamespace


env.globals['last_fetch'] = []
env.globals['settings'] = settings
env.globals['run_id'] = gp.job.run_id
env.globals['git_hash'] = gp.job.git_hash
env.globals['run_date'] = gp.job.start_time.date()
env.globals['job_output_url'] = gp.job.JOB_OUTPUT_URL
env.globals['cwd'] = os.getcwd()

### LOG HELPERS #################

def log_debug(msg:str):   log.debug(msg);   return f'-- DEBUG: {msg}'
def log_info(msg:str):    log.info(msg);    return f'-- INFO: {msg}'
def log_warning(msg:str): log.warning(msg); return f'-- WARNING: {msg}'
def log_error(msg:str):   log.error(msg);   return f'-- ERROR: {msg}'

env.globals['log_debug']   = log_debug
env.globals['log_info']    = log_info
env.globals['log_warning'] = log_warning
env.globals['log_error']   = log_error

### RAISE HELPERS #################

def assert_helper(test:bool, msg:str):
    if not test:
        s = f'ASSERT FAILED: {msg}'
        log.info(s)
        raise Exception(s)
    return f'-- ASSERT PASSED: {msg}'

def raise_helper(msg):
    log.info(f'EXCEPTION RAISED: {msg}')
    raise Exception(msg)

env.globals['raise'] = raise_helper
env.globals['assert'] = assert_helper

### QA HELPER(S) ################

def validate_keys(DBS,table_name,key_indicator,*keys):
    keys_formatted = "', '".join(keys)
    keys_res = ', '.join(keys)
    if key_indicator not in ('uk','pk'): 
        raise ValueError("key_indicator is not of form:'uk' nor 'pk'")
    key_str = 'PRIMARY KEY(S)' if key_indicator == 'pk' else 'UNIQUE KEY(S)' 
    query = f"""
        call shared.utils.p_validate_{key_indicator}(
        '{DBS}.{table_name}',
        array_construct('{keys_formatted}')
        );
        """
    results = fetch_value(query)
    log.debug(results)
    return assert_helper(results,
    f'{key_str}: {keys_res} VALID FOR {DBS}.{table_name}!')

def validate_primary_keys(DBS,table_name,*primary_keys):
    return validate_keys(DBS,table_name,'pk',*primary_keys)

def validate_unique_keys(DBS,table_name,*unique_keys):
    return validate_keys(DBS,table_name,'uk',*unique_keys)

env.globals['validate_pk'] = validate_primary_keys 
env.globals['validate_uk'] = validate_unique_keys

### FILTERS #####################

def comment_lines(s):
    return re.sub('^', '-- ', s, flags=re.MULTILINE)

def trim_lines(s):
    s = re.sub('^\s+', '', s, flags=re.MULTILINE)
    # s = re.sub('\s+$', '', s, flags=re.MULTILINE)
    return s

def condense_spaces(s):
    s = re.sub(' +', ' ', s)
    return s

def condense_whitespace(s):
    s = re.sub('\s+', ' ', s)
    return s

env.filters['comment_lines'] = comment_lines 
env.filters['trim_lines'] = trim_lines
env.filters['condense_spaces'] = condense_spaces
env.filters['condense_whitespace'] = condense_whitespace

##################################


#ctx = {}
modules = {}

TMP_DIR = '.\\tmp\\'
# Clear/Create tmp folder at startup
if os.path.exists(TMP_DIR):
    try: shutil.rmtree(TMP_DIR)
    except: pass
    time.sleep(1)
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR) 

# executor = concurrent.futures.ThreadPoolExecutor(max_workers=settings.max_threads, thread_name_prefix='SQL') 
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5, thread_name_prefix='SQL') 
tasks = []

###########################################

# def dump_result(rows, cols=None):

#     # Empty or Null
#     if not rows:
#         return f'-- RESULT {rows}'

#     # Single value
#     if len(rows)==1 and len(rows[0])==1:
#        return f'-- {rows[0][0]}'

#     # # Row of values
#     # if len(rows)==1 and len(rows[0])>1:
#     #     return '\n'.join([f'-- {value}' for value in rows[0]]) 

#     max_width = lambda i: max(len(cols[i][0]), len(str(max(rows, key=lambda r: len(str(r[i])))[i]))) # Sorry

#     padded = lambda i,c: c + (' ' * (max_width(i) - len(c or '')))

#     # Table 
#     s  = '-- ' + (' | '.join([padded(i,c[0]) for i,c in enumerate(cols)]) +'\n') if cols else ''
#     s += '-- ' + (' | '.join(['-'*len(padded(i,c[0])) for i,c in enumerate(cols)]) +'\n') if cols else ''
#     for row in rows:
#         s += '-- ' + (' | '.join([padded(i,str(c)) for i,c in enumerate(row)]) +'\n')

#     return (s)

###########################################

def get_table_value(rows, row_num, column_name):
    if not rows or not len(rows) or row_num>len(rows):
        raise ValueError(f'Row not found: row_count={len(rows)}, row_num={row_num}')
    for i in i,c in cols:
        if c[0] == column_name:
            return rows[row_num][i]
    raise ValueError(f'Column not found: {column_name}')

def to_dict_table(rows,cols,lower_case=True):
    lcase = lambda s: lower(s) if s else s 
    return [ { lcase(cols[i][0]):r[i] for i,c in enumerate(cols) } for r in rows ]

def assert_load_success(rows, cols):
    if rows and len(cols)>1 and cols[1][0]=='status': 
        for r in rows:
            assert r[1] != 'LOAD_FAILED'

###########################################

def run_sql_block(filename, sql_block):

    is_background = threading.current_thread() != threading.main_thread()

    tmp_file = filename
    gp.utils.write_file(tmp_file, '-- Background Thread\n\n')

    for j,sql in enumerate(sql_block.split(';'),1):

        # Record SQL
        #sql = sql.strip()
        if not sql or sql=='None' or not sql.strip(): continue
        ignore_sql_errors = '@try:' in sql
        sql = sql.replace('@try:', '--@try:\n')
        sql = unindent(sql.strip())
        # log.info(f'sql {j}: "{sql}"')
        gp.utils.append_file(tmp_file, sql + ';\n')


        try:

            # Execute & fetch
            start_time = datetime.now() 
            cursor = snowflake.execute(sql)
            if not cursor: continue
            result = cursor.fetchall() if cursor else None

            if not is_background:
                env.globals['last_fetch'] = result

            #workers.append(executor.submit(_run_sql_file_with_replacements, sql_file, r))

            # Log duration
            finish_time = datetime.now()
            duration = finish_time - start_time
            if log_duration: gp.utils.append_file(tmp_file, f'-- {duration}\n')
            if log_query_id: gp.utils.append_file(tmp_file, f'-- {cursor.sfqid}\n')
            # gp.utils.append_file(tmp_file, f'-- https://guidepoint.snowflakecomputing.com/console#/monitoring/queries/detail?queryId={cursor.sfqid}\n')
    
            # Log result
            log.debug(f'{result}')
            gp.utils.append_file(tmp_file, snowflake.format_rows(result, cursor.description) + '\n\n')

            # Check if load failed
            assert_load_success(result, cursor.description)

        except ProgrammingError as ex:        
            gp.utils.append_file(tmp_file, '\n'*5 + '-- ERROR IGNORED --\n\n' + str(ex))
            if not ignore_sql_errors: 
                raise ex

        except Exception as ex:
            # log errors
            gp.utils.append_file(tmp_file, '\n'*5 + '-- FATAL ERROR --\n\n' + str(ex))
            raise ex

###########################################

def unindent(stuff):
    return '\n'.join([ s.strip() for s in stuff.split('\n')]) 

###########################################

task_map = {}
background_count = 0

def parallelize_blocks(filename, sql):

    pattern = r"""
        ^ \s* @background \s+ begin \s+ (?P<group>\w*) \s* ;? \s+ 
        (?P<body>.*?) 
        ^ \s* @background \s+ end   \s* ;? \s* $
    """

    for (group,body) in re.findall(pattern, sql, flags=re.MULTILINE|re.DOTALL|re.VERBOSE|re.IGNORECASE):
        log.info(f'group name: {group}')

        g = group or 'default'

        global background_count
        background_count += 1
        filename_no_ext = os.path.splitext(filename)[0]
        background_filename = f'{filename_no_ext}.{g}-{background_count}.sql'

        # Save SQL block
        task_map[background_count] = SimpleNamespace(group=g, filename=background_filename, sql=body, id=background_count, task=None)

        # Replace SQL block
        sql = re.sub(pattern, f'\n@background {background_count}; \n', sql, count=1, flags=re.MULTILINE|re.DOTALL|re.VERBOSE|re.IGNORECASE)


    return sql


def start_background_sql_block(id):

    task_info = task_map[id]
    task_info.task = executor.submit(run_sql_block, task_info.filename, task_info.sql)
    tasks.append(task_info)

def wait_for_tasks(group_name=None):

    for ti in tasks:
        if group_name and group_name!=ti.group:
            continue
        result = ti.task.result()
        ex = ti.task.exception()
        log.debug(f'WORKER RESULT: result={result}, ex={ex}')
        if ex: raise Exception(str(ex)) 


###########################################

def run_sql_step(filename):

    global last_cursor
    log.info(f'run_sql_step: {filename}')
    env.globals["modules"] = modules

    basename = os.path.basename(filename)
    basename_no_ext = os.path.splitext(basename)[0]
    tmp_file = f'{TMP_DIR}\\output.{basename_no_ext}.sql'
    gp.utils.write_file(tmp_file, '\n\n')

    sql_template = gp.utils.read_file(filename).replace(';;','$SEMICOLON$')
    sql_blocks = sql_template.split('@go')
    for i,sql_block in enumerate(sql_blocks,1):

        log.debug(f'env.globals: {env.globals}')
        t = env.from_string(sql_block)

        # Osa/JJ Bugfix 5/24/2019 -- Solve issue of duplicate execution of python-step methods in sql steps
        # sql_rendered = t.render().replace('$SEMICOLON$',';')
        sql_rendered = str(t.module).replace('$SEMICOLON$',';')

        log.debug(f'env.globals: {env.globals}')

        sql_rendered = parallelize_blocks(tmp_file,sql_rendered)

        module_vars = [x for x in dir(t.module) if not str(x).startswith('_')]
        for key in module_vars:
            value = getattr(t.module, key)
            # log.info(f'var {key}: {value}')
            #ctx[key] = value
            env.globals[key] = value
        log.debug(f'env.globals: {env.globals}')

        for j,sql in enumerate(sql_rendered.split(';'),1):

            # Record SQL
            #sql = sql.strip()
            if not sql or sql=='None' or not sql.strip(): continue
            ignore_sql_errors = '@try:' in sql
            sql = sql.replace('@try:', '--@try:\n')
            sql = unindent(sql.strip())
            # log.info(f'sql {i}.{j}: "{sql}"')

            try:

                background_match = re.search(r'@background \s+ \w* \s* (\d+)', sql, flags=re.MULTILINE|re.DOTALL|re.VERBOSE|re.IGNORECASE)
                if background_match:
                    gp.utils.append_file(tmp_file, '-- ' + sql + ';\n\n')
                    start_background_sql_block(int(background_match.group(1)))
                    continue

                background_wait_match = re.search(r'@background \s+ wait(\w*)', sql, flags=re.MULTILINE|re.DOTALL|re.VERBOSE|re.IGNORECASE)
                if background_wait_match:
                    gp.utils.append_file(tmp_file, '-- ' + sql + ';\n\n')
                    g = background_match.group(1) or 'default'
                    wait_for_tasks(None if g=='all' else g)
                    continue

                gp.utils.append_file(tmp_file, sql + ';\n')

                # Execute & fetch
                start_time = datetime.now() 
                cursor = snowflake.execute(sql)
                if not cursor: continue
                result = cursor.fetchall() if cursor else None
                env.globals['last_fetch'] = result

                #workers.append(executor.submit(_run_sql_file_with_replacements, sql_file, r))

                # Log duration
                finish_time = datetime.now()
                duration = finish_time - start_time
                if log_duration: gp.utils.append_file(tmp_file, f'-- {duration}\n')
                if log_query_id: gp.utils.append_file(tmp_file, f'-- {cursor.sfqid}\n')
                # gp.utils.append_file(tmp_file, f'-- https://guidepoint.snowflakecomputing.com/console#/monitoring/queries/detail?queryId={cursor.sfqid}\n')
                
                # Log result
                log.debug(f'{result}')
                gp.utils.append_file(tmp_file, snowflake.format_rows(result, cursor.description) + '\n\n')

                # Check if load failed
                assert_load_success(result, cursor.description)

            except ProgrammingError as ex:        
                gp.utils.append_file(tmp_file, '\n'*5 + '-- ERROR IGNORED --\n\n' + str(ex))
                if not ignore_sql_errors: 
                    raise ex

            except Exception as ex:
                # log errors
                gp.utils.append_file(tmp_file, '\n'*5 + '-- FATAL ERROR --\n\n' + str(ex))
                raise ex


        # log.info(t.module.__dict__)
        # modules[filename.replace('.sql','').replace('\\','_').replace('steps_','')] = t.module
        # log.debug(f'modules: {modules.keys()}')

        wait_for_tasks()

###########################################

def run_html_step(filename):

    log.info(f'run_html_step: {filename}')

    def execute(sql): return snowflake.fetchall(sql)
    env.globals["execute"] = execute
    env.globals["modules"] = modules
    
    basename = os.path.basename(filename)
    basename_no_ext = os.path.splitext(basename)[0]
    tmp_file = f'{TMP_DIR}\\output.{basename_no_ext}.html'
    gp.utils.write_file(tmp_file, '')

    try:

        html_template = gp.utils.read_file(filename)
        t = env.from_string(html_template)
        # Warning: DO NOT REFERENCE t.module after t.render()
        html_rendered = t.render().replace('$SEMICOLON$',';')
        gp.utils.append_file(tmp_file, html_rendered)

    except Exception as ex:
        # log errors
        gp.utils.append_file(tmp_file, '\n'*5 + '-- FATAL ERROR --\n\n' + str(ex))
        raise ex

###########################################

def run_tableau_step(filename):

    log.info(f'run_tableau_step: {filename}')

    def execute(sql): return snowflake.fetchall(sql)
    env.globals["execute"] = execute
    env.globals["modules"] = modules
    
    basename = os.path.basename(filename)
    basename_no_ext = os.path.splitext(basename)[0]
    tmp_file = f'{TMP_DIR}\\output.{basename_no_ext}.twb'
    gp.utils.write_file(tmp_file, '')

    try:

        html_template = gp.utils.read_file(filename)
        t = env.from_string(html_template)
        # Warning: DO NOT REFERENCE t.module after t.render()
        # html_rendered = t.render().replace('$SEMICOLON$',';')
        gp.utils.append_file(tmp_file, html_rendered)

    except Exception as ex:
        # log errors
        gp.utils.append_file(tmp_file, '\n'*5 + '-- FATAL ERROR --\n\n' + str(ex))
        raise ex

###########################################

def run_jupyter_step(filename):

    import subprocess

    log.info(filename)
    # log.info(os.getcwd())

    basename = os.path.basename(filename)
    basename_no_ext = os.path.splitext(basename)[0]
    html_filename = f'../tmp/output.{basename_no_ext}.html'
    tmp_notebook_filename = f'{TMP_DIR}\\output.{basename_no_ext}.ipynb'

    s = gp.utils.read_file(filename)
    s = s.replace('$$JOB_RUN_ID$$', str(gp.job.run_id))
    s = s.replace('$$JOB_OUTPUT_URL$$', gp.job.JOB_OUTPUT_URL)
    s = s.replace('$$SETTINGS_FILE$$', settings_file.replace('\\', '\\\\\\\\'))
    gp.utils.write_file(tmp_notebook_filename, s)

    args = ["jupyter", "nbconvert", "--execute", tmp_notebook_filename, "--to", "html", "--output", html_filename]
    log.debug(args)
    subprocess.check_output(args)

###########################################

def run_py_step(filename):

    log.info(filename)

    module_name = filename.replace('\\','.').replace('.py','')
    module = importlib.import_module(module_name)
    # log.info(module.__dict__)
    modules[module_name.replace('.','_').replace('steps_','')] = module

    if 'run' in module.__dict__:
        log.debug('RUN')
        module.run(SimpleNamespace(**modules), settings)
        module.run(modules, settings)

    else:
        log.debug('NO RUN')

    module_vars = [x for x in dir(module) if not str(x).startswith('_')]
    for key in module_vars:
        value = getattr(module, key)
        # log.info(f'var {key}: {value}')
        #ctx[key] = value
        env.globals[key] = value
    log.debug(f'env.globals: {env.globals}')

###########################################

def run_step(filename):

    # Skip disabled steps
    if 'disabled' in filename.lower():
        log.debug(f'skipping disabled step: {filename}')
        return

    # Check step filter
    if 'step_filter' in settings_map and settings.step_filter:

        run_it = False # True when there is a positive match
        positive = False # True when there is at least one positive rule; when True, there must be at least one positive match

        for sf in settings.step_filter:

            assert sf[0] in ['+','-']
            assert len(sf)>1

            prefix = sf[0] 
            pattern = p = ('%' + sf[1:] + '%').replace('%', '.*')
            match = re.search(p, filename, flags=re.IGNORECASE)

            # Negative Match
            if prefix == '-':
                if match:
                    log.warn(f'SKIPPING {filename}, RULE: {sf}')
                    return

            # Match Pattern
            elif prefix == '+':
                positive = True
                if match:
                    run_it = True
                    break

            # Bad rule if we get here
            else:
                log.error(f'BAD RULE {sf} IGNORED')
                continue

        if not run_it and positive:
            log.warn(f'SKIPPING {filename}, NO POSITIVE MATCH')
            return

    if filename.endswith('.sql'):  run_sql_step(filename)
    elif filename.endswith('.py'): run_py_step(filename)
    elif filename.endswith('.html'): run_html_step(filename)
    elif filename.endswith('.twb'): run_tableau_step(filename)
    elif filename.endswith('.ipynb'): run_jupyter_step(filename)

###########################################

def run_steps():

    steps = glob('steps/**/*.*', recursive=True)
    steps.sort()
    log.debug(f'steps: {steps}')

    for filename in steps:
        run_step(filename)

###########################################


