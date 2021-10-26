"""
********************************************************************************
     Module: gp.job
Description: Prevents multiple instances; measures duration;
      Usage: Call gp.job.success() or failure();  
             Note, failure() is called automatically for unhandled exceptions.
             Call gp.job.run_job() to run a child job, and wait for finish.
     Author: Justin Jones
    Created: 2017-09-18
********************************************************************************
"""

import os
import sys
import re
import traceback
import logging
import atexit
import psutil
from datetime import datetime
import subprocess
from types import SimpleNamespace
import glob
# import uuid

import gp.singleton
import gp.gp_email
import gp.runlog
import gp.settings
import gp.utils
import gp.s3
from botocore.exceptions import NoCredentialsError,ClientError
from boto3.exceptions import S3UploadFailedError
import gp.snowflake as snowflake

#################################

log = logging.getLogger(__name__)

path_parts      = os.getcwd().split(os.path.sep)
job_name        = path_parts[-1].replace('_',' ').replace('job ','')
job_group       = path_parts[-2]
job_name_full   = job_group + '.' + job_name
run_id          = gp.runlog.get_run_id()


#################################

start_time  = datetime.now() 
# run_id      = int(start_time.strftime('%Y%m%d%H%M%S%f'))
singleton   = gp.singleton.SingleInstance()
is_finished = False
process     = psutil.Process(os.getpid())
initial_mem = process.memory_info().rss/10000000

git_hash        = subprocess.check_output(['git', 'rev-parse', 'HEAD'           ], cwd='/dev/da.main').decode('ascii').strip()
git_status      = subprocess.check_output(['git', 'status',    '-s'             ], cwd='/dev/da.main').decode('ascii')
git_describe    = subprocess.check_output(['git', 'describe'                    ], cwd='/dev/da.main').decode('ascii').strip()
git_timestamp   = subprocess.check_output(['git', 'show', '-s','--format=%ci'   ], cwd='/dev/da.main').decode('ascii').strip()


################ USED BY send_job_output_to_s3 ##################
__PARENT_FOLDER = path_parts[-2].lower()
__JOB_FOLDER = path_parts[-1].lower()
__RUN_DATE = start_time.strftime('%Y%m%d')

__settings_name = 'none'
__SETTINGS_FILE = gp.settings.settings_file
__SETTINGS_FILE_BASE = os.path.basename(__SETTINGS_FILE)
if os.path.exists(__SETTINGS_FILE_BASE):
    __SETTINGS = __SETTINGS_FILE_BASE.split('.')
    if len(__SETTINGS)==3:
        __settings_name = __SETTINGS[1]
    elif len(__SETTINGS)==2:
        __settings_name = 'unnamed'

__SNOWFLAKE_INTERNAL = f'@rawdata.s3.internal/job/{__PARENT_FOLDER}/{__JOB_FOLDER}/{__RUN_DATE}.{run_id}.{__settings_name}.{git_hash}'
__S3_INTERNAL =  F's3://guidepoint.internal/job/{__PARENT_FOLDER}/{__JOB_FOLDER}/{__RUN_DATE}.{run_id}.{__settings_name}.{git_hash}'
__BUCKET = gp.s3.extract_bucket(__S3_INTERNAL)
__PATH = gp.s3.extract_path(__S3_INTERNAL)  

JOB_OUTPUT_URL = f'https://s3.amazonaws.com/{__BUCKET}/{__PATH}'

###########################################################

### API ##############################

def success(): 
    _finish(True)

def failure(error_msg=None):
    _finish(False, error_msg)

##################

### PRIVATE ##############################

def _finish(success=False, error_msg=None):

    # Prevent re-entrence
    global is_finished
    if is_finished: return
    is_finished = True
   
    # Measure duration
    global start_time
    finish_time = datetime.now()
    duration_sec = (finish_time - start_time).total_seconds()
    log.info('duration seconds: {:.2f}'.format(duration_sec))
    log.info('duration minutes: {:.2f}'.format(duration_sec/60.0))

    mem_used = process.memory_info().rss/1000000
    log.debug(f'Memmory Used: {mem_used:.1f} MB, Delta: {mem_used - initial_mem:.1f} MB')

    result = 'SUCCESS' if success else ' FAIL'
    log.info(f'JOB RESULT: {result}')

    gp.runlog.log_run_finish(success, error_msg, details={
        "memory_used_mb": mem_used,
        "memory_delta_mb": mem_used - initial_mem
    })


    subject = f"JOB {job_group} - {job_name}: {result}".upper()
    
    # email body 
    try:
        body = send_job_output_to_s3()

        if not gp.settings.get('email_enabled', default=False):
            log.warning('EMAIL DISABLED - Message not sent')
        else:    
            # Send email
            gp.email.send(subject,body=body, body_filename=None, plain=False, attachments=[])
    except (NoCredentialsError,ClientError,S3UploadFailedError) as ex:
        log.debug(ex)
        log.warning('ARCHIVING AND EMAILING OF LOGS DISABLED')
    
    start_time = None

    if not success:
        exit("*** FAIL ***")

#################################

def _uncaught_exception_handler(exc_type, value, traceback):

    #Unhook this exception handler
    sys.excepthook = sys.__excepthook__

    msg = 'ERROR'

    if issubclass(exc_type, KeyboardInterrupt):
        log.critical('EXCEPTION: KeyboardInterrupt')
        msg = 'EXCEPTION: KeyboardInterrupt'
        
    elif exc_type == gp.singleton.SingleInstanceException:
        log.critical('EXCEPTION: SingletonException - Already running')
        msg = 'EXCEPTION: SingletonException - Already running'

    else:
        log.critical('UNCAUGHT EXCEPTION', exc_info=(exc_type, value, traceback))
        msg = str(value)

    #Log failure
    failure(msg)

    log.error('******* Never get here ************')

    # Call next handler in chain
    sys.__excepthook__(exc_type, value, traceback)

#################################

def _exit():

    # Handle case where neither success() or failure() was called
    if not is_finished: 
        log.error('gp.job.finish() was not called')
        failure('gp.job.finish() was not called')

    log.debug('******* EXIT *******')


#################################

def _initialize():

    import socket
    import platform as p
    import boto3

    # Python Version
    log.debug(f'Python Version: {sys.version}')

    # System Info
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)  

    #External IP
    external_ip = ''
    try:
        from requests import get
        external_ip = get('https://ipapi.co/ip/').text
    except:
        pass

    log.debug(f'Working Directory: {os.getcwd()}')
    log.debug(f'Username={os.getlogin()}, Hostname={hostname}, Host IP={host_ip}, External IP={external_ip}')
    log.debug(f'{p.system()} {p.version()}, {p.architecture()[0]}, {p.machine()}, {p.processor()} ')
    log.debug(f'Memmory Used: {initial_mem:.1f} MB')
    log.debug(f'Module Paths: {sys.path}')
    log.debug(f'Command Line: {sys.argv}')

    # AWS SDK
    log.debug(f'Boto3 Version: {boto3.__version__}')

    # # Snowsql Username
    # snowsql_user = os.environ['SNOWSQL_USER'] if 'SNOWSQL_USER' in os.environ.keys() else 'undefined'
    # log.debug(f'SNOWSQL_USER: {snowsql_user}')

    settings_file = os.path.basename(gp.settings.settings_file)

    gp.runlog.log_run_start(job_group, job_name, settings_file, host_ip, hostname, os.getlogin().upper(), git_timestamp, git_hash, git_status, git_describe, details={
        "python_version":           sys.version,
        "external_ip":              external_ip,
        "workding_dir":             os.getcwd(),
        "command_line":             ' '.join(sys.argv),
        "platform_system":          p.system(),
        "plaform_version":          p.version(),
        "platform_architecture":    p.architecture()[0], 
        "platform_machine":         p.machine(), 
        "platform_processor":       p.processor(),
        "memory_used_mb":           initial_mem,
        "module_paths":             ';'.join(sys.path),
        "settings_file":            gp.settings.settings["settings_map"] if "settings_map" in gp.settings.settings else None
    })

    # Sign up for notification of unhandled exceptions
    sys.excepthook = _uncaught_exception_handler

    # Sign up for notification of app termination
    atexit.register(_exit)

_initialize()

#################################

def run_cmd(cmd, folder, timeout_seconds=60*3*3):

    import shlex
    import subprocess

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

######## Send output to s3 #########
def send_job_output_to_s3(snowflake_archive =__SNOWFLAKE_INTERNAL,s3_archive = __S3_INTERNAL,
    web_template=JOB_OUTPUT_URL,settings_file = __SETTINGS_FILE,
    settings_file_base=__SETTINGS_FILE_BASE,run_id=run_id):
    '''
        Step 1. Copy files from ./tmp/*.sql to S3 root/output/
        Step 2. Copy settings file to S3 root/
        Step 3. Copy queries from Snowflake to S3 root/
        Step 4. Copy log files to S3 root/logs/
    '''
    gp.s3.connect()
    
    # Store all s3 web paths created during copy  
    
    all_s3_web_paths = []

    # STEP 1: load output in tmp folder to s3
    file_types = ('./tmp/*.sql','./tmp/*.html','./tmp/*.png', './tmp/*.ipynb', './tmp/*.twb')
    tmp_files = []
    for file_type in file_types:
        tmp_files+=glob.glob(file_type)
    output_files = ['output/'+os.path.basename(filename) for filename in tmp_files]
    
    n = len(tmp_files)

    for i in range(n):
        tmp_file = tmp_files[i]
        full_s3_path = s3_archive+'/'+output_files[i]
        if output_files[i].endswith('.html'):
            gp.s3.upload_file(tmp_file,full_s3_path,content_type='text/html')
        elif output_files[i].endswith('.sql'):
            gp.s3.upload_file(tmp_file,full_s3_path,content_type='text/plain')
        elif output_files[i].endswith('.png'):
            gp.s3.upload_file(tmp_file,full_s3_path,content_type='image/png')
        elif output_files[i].endswith('.ipynb'):
            gp.s3.upload_file(tmp_file,full_s3_path,content_type='application/vnd.jupyter') #https://jupyter.readthedocs.io/en/latest/reference/mimetype.html
        elif output_files[i].endswith('.twb'):
            gp.s3.upload_file(tmp_file,full_s3_path,content_type='application/twb') #https://community.tableau.com/thread/111179
        web_path = web_template+'/'+output_files[i]
        all_s3_web_paths.append(web_path)
    
    # STEP 2: load settings file to s3

    if os.path.exists(settings_file_base):
        s3_settings_file_path = s3_archive+'/'+ settings_file_base
        gp.s3.upload_file(settings_file,s3_settings_file_path,content_type='text/plain')
        web_path = web_template+'/'+settings_file_base
        all_s3_web_paths.append(web_path)


    # STEP 3: Copy queries during run from snowflake to queries.csv in s3
        # Queries will always exist

    snowflake.execute(f'''
        copy into '{snowflake_archive+'/queries.csv'}'
        from (
            select *, 'https://guidepoint.snowflakecomputing.com/console#/monitoring/queries/detail?queryId=' || query_id as query_url 
            from rawdata.metadata.job_query_history
            where run_id = {run_id}
        )
        file_format = (field_delimiter = ',' null_if = ()  field_optionally_enclosed_by='"' empty_field_as_null = true compression = none) 
        overwrite = true 
        header = true 
        single = true
        max_file_size = 5368709120;
    ''')
    all_s3_web_paths.append(web_template +'/queries.csv')

    # STEP 4: load log files to s3
    local_log_files = [log_file for log_file in glob.glob('log*.txt')]
    s3_log_file_paths = ['logs/'+log_file for log_file in local_log_files]

    k = len(local_log_files)

    for i in range(k):
        local_log_file = local_log_files[i]
        s3_log_file_path = s3_archive + '/' + s3_log_file_paths[i]
        gp.s3.upload_file(local_log_file,s3_log_file_path,content_type='text/plain')
        web_path = web_template +'/'+ s3_log_file_paths[i]
        all_s3_web_paths.append(web_path)

    if all_s3_web_paths:
        body = '<ul>'
        for path in all_s3_web_paths:
            body+=f'\n<li><a href="{path}">{os.path.basename(path)}</a></li>'
        body+='\n</ul>'
    else:
        body = '' 
    body = gp.utils.read_file(gp.utils.logfile).replace('\n','<br>') +'\n\n'+body
    gp.s3.upload_str(body,s3_archive+'/index.html',content_type='text/html')

    return body
    
#################################

#################################
