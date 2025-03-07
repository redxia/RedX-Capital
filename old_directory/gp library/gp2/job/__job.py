import os
import sys
import traceback
import logging
from datetime import datetime

import gp2.settings as settings

from .__tmp_dir import TMP_DIR
from .__upload import upload_job_outputs, email_job_report, get_job_output_locations
from .__runlog import get_run_id, log_run_start, log_run_finish
from .__sysinfo import get_sysinfo, get_mem_used_delta
from .__jobinfo import get_jobinfo

#################################
### PRIVATE
#################################

log = logging.getLogger(__name__)
is_finished = False
is_initialized = False
start_time = datetime.now() 

#################################
### API 
#################################

def success(): 
    __finish(True)

def failure(error_msg=None):
    __finish(False, error_msg)
    exit(1)

#################################
### PRIVATE 
#################################

def __log_job_finish(success, error_msg):

    # Measure duration
    global start_time
    finish_time = datetime.now()
    duration = finish_time - start_time
    log.info(f'JOB DURATION: {duration}')

    # Log result to logfiles
    if success:
        log.info('JOB RESULT: SUCCESS')
    else:
        log.error('JOB RESULT: FAIL')

    # Log result to Snowflake
    mem_used_delta = get_mem_used_delta()
    try:
        log_run_finish(success, error_msg, details=dict(memory_delta_mb=mem_used_delta))
    except Exception as ex:
        log.error('ERROR LOGGING JOB RESULT TO SNOWFLAKE')
        log.debug(ex)


def __finish(success=False, error_msg=None):

    # Prevent re-entrence
    global is_finished
    if is_finished: return
    is_finished = True
   
    # Log outcome to Snowflake
    __log_job_finish(success, error_msg)

    # Upload Outputs
    body = upload_job_outputs(job_output_locations, run_id)

    # Send email
    email_job_report(success, jobinfo, body)

    # Done    
    log.info('JOB DONE')

#################################
### UNHANDLED EXCEPTION HOOK
#################################

from snowflake.connector.errors import DatabaseError

def __unhandled_exception_handler(exc_type, value, traceback):

    # Unhook this exception handler
    sys.excepthook = sys.__excepthook__

    # Keyboard Interrupt    
    if issubclass(exc_type, KeyboardInterrupt):
        log.critical('EXCEPTION: KeyboardInterrupt')
        exit(2)
        
    # SingleInstance error
    # elif exc_type == gp2.singleton.SingleInstanceException:
    #     log.critical('EXCEPTION: SingletonException - Already running')

    # Snowflake login error
    elif issubclass(exc_type, DatabaseError) and value.errno==250001 and not is_initialized:
        # before_init = '' if is_initialized else ' (BEFORE INITIALIZATION)'
        # log.critical(f'UNHANDLED EXCEPTION{before_init} [{exc_type.__name__}]: {str(value)}')
        log.critical(f'SNOWFLAKE ERROR [{exc_type.__name__}]: {str(value)}')
        exit(3)

    # Detailed message
    else:
        log.critical('UNANDLED_EXCEPTION', exc_info=(exc_type, value, traceback))

    # Log failure
    if is_initialized:
        __finish(False, str(value))
        sys.exit(4)
    else:
        # TODO: Send email
        sys.exit(5)

    # SHOULD NOT GET HERE!
    log.error('*** UNEXPECTED ERROR ***')

    # Call next handler in chain
    sys.__excepthook__(exc_type, value, traceback)

#################################

# Sign up for notification of unhandled exceptions
sys.excepthook = __unhandled_exception_handler

#################################
### EXIT HOOK
#################################

def __exit():
    '''
    Called on application exits.  Marks job as failed and uploads results and optionally send email alert.
    '''
    log.debug('*** EXIT ***')
    if not is_finished: 
        log.critical('UNEXPECTED EXIT')
        if is_initialized:
            failure('UNEXPECTED EXIT')
        else:
            # TODO: Send email
            pass

#################################

import atexit
atexit.register(__exit)

#################################
### INITIALIZE
#################################

sysinfo                 = get_sysinfo()
jobinfo                 = get_jobinfo()
run_id                  = get_run_id()
job_output_locations    = get_job_output_locations(jobinfo.repo_path, run_id, start_time)
is_initialized  = True

log.info(f'AWS_BATCH_JOB_ID: {sysinfo.aws_batch_job_id}') if sysinfo.aws_batch_job_id else None
log.info(f'GIT HASH: {jobinfo.git_hash}')
log.warning(f'GIT STATUS:\n{jobinfo.git_status}') if jobinfo.git_status and jobinfo.git_status!='NOT AVAILABLE' else None
log.info(f'REPO PATH: {jobinfo.repo_path}')

# Run
log_run_start(jobinfo, sysinfo)

#################################
#################################


