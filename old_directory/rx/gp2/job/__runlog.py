"""
********************************************************************************
     Module: gp2.joblog
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

import gp2.utils
import gp2.settings
import gp2.snowflake

#################################

log = logging.getLogger(__name__)

#################################

run_id = None
def get_run_id():

    global run_id

    # Return cached copy if available
    if run_id: return run_id

    # Otherwise fetch new run_id
    run_id = gp2.snowflake.fetchone('select rawdata.metadata.job_run_id.nextval as run_id')[0]
    assert isinstance(run_id, int)
    log.info(f'RUN_ID: {run_id}')

    # Set QUERY_TAG and CURRENT_RUN_ID
    gp2.snowflake.execute(f"alter session set query_tag='RUN_ID={run_id}'")
    
    return run_id

#################################

def log_run_start(jobinfo, sysinfo, details=None):

    assert run_id

    settings_file = os.path.basename(gp2.settings.settings_file)

    insert = f'''
        insert into rawdata.metadata.job_run_v3 (run_id, job_group, job_name, settings_file, host_ip, host_name, windows_user, git_timestamp, git_hash, git_status, git_describe, warehouse_size, details)
        select $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, parse_json($13)
        from values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    '''

    # gp2.snowflake.connect().cursor().execute_async(insert, (
    gp2.snowflake.cursor().execute(insert, (
        run_id,                     # 1
        jobinfo.job_group,          # 2 
        jobinfo.job_name,           # 3
        settings_file,              # 4
        sysinfo.host_ip,            # 5
        sysinfo.hostname,           # 6
        sysinfo.username,           # 7
        jobinfo.git_timestamp,      # 8
        jobinfo.git_hash,           # 9
        jobinfo.git_status,         # 10
        jobinfo.git_describe,       # 11
        '',                         # 12 # warehouse["size"]
        json.dumps(details)         # 13
    ), _no_results=True)

#################################

def log_run_finish(success, finish_error=None, details=None):

    # Mark as finished
    insert = f'''
        update rawdata.metadata.job_run_v3
        set finish_success=%s, finish_error=%s, finish_time=current_timestamp(), finish_duration=timestampdiff(second, start_time, current_timestamp()), finish_details=parse_json(%s)
        where run_id=%s
    '''
    gp2.snowflake.cursor().execute(insert, 
        (success, finish_error, json.dumps(details), run_id),
        _no_results=True
    ) #.fetchall()


#################################

# # event_id        int             not null identity primary key,
# # event_time      timestamp_tz    not null default current_timestamp(),
# # event_name      text            not null,
# # run_id          int             not null,
# # details         variant         not null

# def log_run_event(details):

#     insert = f'''
#         update rawdata.metadata.job_run_v3
#         set success=%s, finish_time=current_timestamp() 
#         where run_id=%s
#     '''
#     gp2.snowflake.cursor().execute(insert, (run_id, success), _no_results=True)

# #################################
