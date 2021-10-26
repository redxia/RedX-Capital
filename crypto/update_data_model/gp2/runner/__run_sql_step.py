import logging
import sys
import os
import re
import importlib
from datetime import date, datetime, timedelta

from snowflake.connector.errors import ProgrammingError

import gp2.snowflake as snowflake
import gp2.snowflake.utils as snowflake_utils
import gp2.utils
from gp2.settings import settings as settings_map, namespace as settings, settings_file

log = logging.getLogger(__name__)

###########################################

log_duration = settings_map.get('log_duration', False)
log_query_id = settings_map.get('log_query_id', False)

###########################################

# def unindent(sql):
#     return '\n'.join([ s.strip() for s in sql.split('\n')])

def unindent(sql):
    '''Unindent SQL statements'''
    if not sql: return sql
    lines = sql.splitlines()
    # Find minimum leading whitespace, excluding comments and empty lines
    m = 1000000
    for l in lines:
        if not l.strip() or l.startswith('--'): continue
        spaces = len(l) - len(l.lstrip())
        if not spaces: return sql
        m = min(m,spaces)
    # Remove minimum leading whitespace, excluding comments and empty lines
    result = '\n'.join([ l[m:] if l.strip() and not l.startswith('--') else l for l in lines ])
    return result

def assert_load_success(rows, cols):
    if rows and len(cols)>1 and cols[1][0]=='status':
        for r in rows:
            assert r[1] != 'LOAD_FAILED'

def remove_comment_lines(sql):
    return re.sub(r'^\s*--.*$', '', sql, flags=re.MULTILINE)

###########################################

def run_sql_step(filename, output_filename, env):

    log.info(f'run_sql_step: {filename}')

    tmp_file = output_filename
    gp2.utils.write_file(tmp_file, '\n\n')

    # Load raw Jinja-SQL
    sql_template = gp2.utils.read_file(filename)

    # Loop over Jinja blocks
    sql_blocks = sql_template.split('@go')
    for sql_block in sql_blocks:

        # Execute Jinja
        t = env.from_string(sql_block)
        # Osa/JJ Bugfix 5/24/2019 -- Solve issue of duplicate execution of python-step methods in sql steps
        # sql_rendered = t.render()
        sql_rendered = str(t.module)

        # Capture Jinja vars -- add to globals for use in next jinja block
        module_vars = [x for x in dir(t.module) if not str(x).startswith('_')]
        for key in module_vars:
            value = getattr(t.module, key)
            log.debug(f'var {key}: {value}')
            env.globals[key] = value

        # Iterate of SQL statements
        for sql in sql_rendered.split(';'):

            # Record SQL
            if not sql or sql=='None' or not sql.strip(): continue
            ignore_sql_errors = '@try:' in sql
            sql = sql.replace('@try:', '--@try:\n')
            # sql = unindent(sql.strip(' \r\n'))
            sql = unindent(sql)

            # Skip blank queries
            clean_sql = remove_comment_lines(sql).strip(' \r\n')
            if not clean_sql:
                gp2.utils.append_file(tmp_file, sql + '\n')
                continue

            gp2.utils.append_file(tmp_file, sql + ';\n')

            try:

                # Execute & fetch
                env.globals["last_error"] = None
                start_time = datetime.now()
                cursor = snowflake.execute(sql)
                if not cursor: continue # Emtpy query
                result = cursor.fetchall() if cursor else None
                env.globals['last_fetch'] = result
                env.globals['last_fetch_columns'] = cursor.description

                # Log duration
                finish_time = datetime.now()
                duration = finish_time - start_time
                if log_duration: gp2.utils.append_file(tmp_file, f'-- {duration}\n')
                if log_query_id: gp2.utils.append_file(tmp_file, f'-- {cursor.sfqid}\n')

                # Log result
                gp2.utils.append_file(tmp_file, snowflake_utils.format_rows(result, cursor.description) + '\n\n')

                # Check if load failed
                assert_load_success(result, cursor.description)

            except ProgrammingError as ex:
                # Log errors
                gp2.utils.append_file(tmp_file, '\nERROR: ' + str(ex) + '\n\n')
                if ignore_sql_errors:
                    env.globals["last_error"] = str(ex)
                else:
                    raise ex

            except Exception as ex:
                # Log errors
                gp2.utils.append_file(tmp_file, '\nFATAL ERROR: ' + str(ex) + '\n\n')
                raise ex

