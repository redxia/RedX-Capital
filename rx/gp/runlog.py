"""
********************************************************************************
     Module: gp.joblog
Description: 
      Usage: 
     Author: Justin Jones
    Created: 2018-04-24
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

import gp.utils
import gp.settings
import gp.snowflake

#################################

log = logging.getLogger(__name__)

#################################

run_id = None
def get_run_id():

    global run_id

    # Return cached copy if available
    if run_id: return run_id

    # Otherwise fetch new run_id
    run_id = gp.snowflake.fetchone('select rawdata.metadata.job_run_id.nextval as run_id')[0]
    assert isinstance(run_id, int)
    log.info(f'RUN_ID: {run_id}')

    # Set QUERY_TAG and CURRENT_RUN_ID
    gp.snowflake.execute(f"alter session set query_tag='RUN_ID={run_id}'")
    gp.snowflake.execute(f"set current_run_id={run_id}::number")
    
    return run_id

#################################

def log_run_start(job_group, job_name, settings_file, host_ip, host_name, windows_user, git_timestamp, git_hash, git_status, git_describe, details=None):

    assert run_id

    warehouse = gp.snowflake.get_warehouse_details()

    insert = f'''
        insert into rawdata.metadata.job_run_v3 (run_id, job_group, job_name, settings_file, host_ip, host_name, windows_user, git_timestamp, git_hash, git_status, git_describe, warehouse_size, details)
        select $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, parse_json($13)
        from values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    '''

    gp.snowflake.execute(insert, args=(run_id, job_group, job_name, settings_file, host_ip, host_name, windows_user, git_timestamp, git_hash, git_status, git_describe, warehouse["size"], json.dumps(details))).fetchall()

    gp.snowflake.execute('set current_git_hash=%s::text', git_hash).fetchall()

#################################

def log_run_finish(success, finish_error=None, details=None):

    # Mark as finished
    insert = f'''
        update rawdata.metadata.job_run_v3
        set finish_success=%s, finish_error=%s, finish_time=current_timestamp(), finish_duration=timestampdiff(second, start_time, current_timestamp()), finish_details=parse_json(%s)
        where run_id=%s
    '''
    gp.snowflake.execute(insert, args=(success, finish_error, json.dumps(details), run_id)).fetchall()

    # Delete old query history
    gp.snowflake.execute('delete from rawdata.metadata.job_query_history where datediff(days, start_time, current_timestamp())>30').fetchall()

    # Insert new query history
    gp.snowflake.execute("""
        insert into rawdata.metadata.job_query_history 
        select %s as run_id, QUERY_ID,QUERY_TEXT,DATABASE_NAME,SCHEMA_NAME,QUERY_TYPE,SESSION_ID,USER_NAME,ROLE_NAME,WAREHOUSE_NAME,WAREHOUSE_SIZE,WAREHOUSE_TYPE,QUERY_TAG,EXECUTION_STATUS,ERROR_CODE,ERROR_MESSAGE,START_TIME,END_TIME,TOTAL_ELAPSED_TIME,COMPILATION_TIME,EXECUTION_TIME,QUEUED_PROVISIONING_TIME,QUEUED_REPAIR_TIME,QUEUED_OVERLOAD_TIME,TRANSACTION_BLOCKED_TIME,OUTBOUND_DATA_TRANSFER_CLOUD,OUTBOUND_DATA_TRANSFER_REGION,OUTBOUND_DATA_TRANSFER_BYTES
        from table(rawdata.information_schema.query_history_by_session(session_id => current_session()::number, result_limit => 10000))
        order by start_time
    """, (run_id,)).fetchall()

#################################

# event_id        int             not null identity primary key,
# event_time      timestamp_tz    not null default current_timestamp(),
# event_name      text            not null,
# run_id          int             not null,
# details         variant         not null

def log_run_event(details):

    insert = f'''
        update rawdata.metadata.job_run_v3
        set success=%s, finish_time=current_timestamp() 
        where run_id=%s
    '''
    gp.snowflake.execute(insert, args=(run_id, success))

#################################
