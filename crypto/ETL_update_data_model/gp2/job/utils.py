import os
import sys
import re
import traceback
import logging
import shlex
import subprocess
from types import SimpleNamespace

#################################

log = logging.getLogger(__name__)

#################################

def run_cmd(cmd, folder, timeout_seconds=60*3*3):

    log.info(f'RUNNING CHILD PROCESS: {cmd}')

    # Parse Args
    args = shlex.split(cmd)

    # Excecute CMD
    proc = subprocess.Popen(args, cwd=folder, shell=True)

    # Capture output
    output, error = proc.communicate(timeout=timeout_seconds) #timeout in seconds

    # Debug
    log.debug(f'OUTPUT:\n{output}')

    # Search output for ERROR or FAIL
    error_search = re.search('^.*(error|fail).*$', output, re.MULTILINE|re.IGNORECASE) if output else None
    error_line = error_search.group(0) if error_search else None

    # Log errors
    if proc.returncode: log.warn(f'CHILD PROCESS RETURN CODE:\n{proc.return_code}')
    if error: log.warn(f'CHILD PROCESS ERROR:\n{error}')
    if error_line: log.warn(f'CHILD PROCESS OUTPUT ERROR:\n{output}')

    # Return results
    return SimpleNamespace(returncode=proc.returncode, output=output, error=error, error_line=error_line)

#################################

def run_job(job_name, timeout_seconds=60*60*3, args=''):

    # Debug
    # log.debug(f'Starting child job: {job_name}, with {timeout_seconds} second timeout.')

    # Path
    folder = os.path.join(os.getcwd(), '..', job_name)
    folder = os.path.normpath(folder)

    # Run Job
    result = run_cmd('run.bat ' + args, folder)

    # Grab log file if it exists
    log_txt_filename = folder + '/log.txt'
    log_txt = ''
    if os.path.exists(log_txt_filename):
        with open(log_txt_filename, 'r') as f:
            log_txt = f.read()
    log.debug(f'CHILD JOB OUTPUT:\n\n{log_txt}\n\n\n')

    # Fail the parent if child job not successful
    job_success = 'JOB RESULT: SUCCESS' in log_txt 
    if job_success:
        log.info('CHILD JOB RESULT: SUCCESS')
    else:
        log.error(f'CHILD JOB FAILED')
        log.debug(f'CHILD JOB OUTPUT:\n\n{log_txt}\n\n\n')
        raise Exception(f'CHILD JOB FAILED')
    
    return result

#################################
#################################
