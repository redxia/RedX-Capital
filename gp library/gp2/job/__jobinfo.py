import os
import re
import subprocess
import logging
from datetime import datetime
from types import SimpleNamespace

import gp2.utils

######################################

log = logging.getLogger(__name__)

######################################

def __get_jobinfo_from_file(package_info_file ='package_info.json'):

    if not os.path.exists(package_info_file):
        return None
        
    package_info = gp2.utils.read_json(package_info_file)

    ji = SimpleNamespace()

    ji.git_hash        = package_info["git_hash"]
    ji.git_status      = package_info["git_status"]
    ji.git_describe    = package_info["git_describe"]
    ji.git_timestamp   = package_info["git_timestamp"]
    ji.repo_path       = package_info["repo_path"]
    ji.job_name        = package_info["job_name"]
    ji.job_group       = package_info["job_group"]
    ji.job_name_full   = ji.job_group + '.' + ji.job_name

    return ji

######################################

def __get_jobinfo_from_context():

    ji = SimpleNamespace()

    try:
        ji.git_hash        = subprocess.run(['git', 'rev-parse', 'HEAD'           ], capture_output=True, check=True).stdout.decode('ascii').strip()
        ji.git_status      = subprocess.run(['git', 'status', '-s'                ], capture_output=True, check=True).stdout.decode('ascii').rstrip()
        ji.git_describe    = subprocess.run(['git', 'describe', '--always'        ], capture_output=True, check=True).stdout.decode('ascii').strip()
        ji.git_timestamp   = subprocess.run(['git', 'show', '-s', '--format=%ci'  ], capture_output=True, check=True).stdout.decode('ascii').strip()

    except FileNotFoundError:
        ji.git_hash        = 'NOT AVAILABLE'
        ji.git_status      = 'NOT AVAILABLE'
        ji.git_describe    = 'NOT AVAILABLE'
        ji.git_timestamp   = datetime.now() # Has to be valid datetime
    
    ji.repo_path = re.sub(r'^\w+:\\dev\\', '', os.getcwd(), re.IGNORECASE)

    path_parts = os.getcwd().split(os.path.sep)
    
    ji.job_name        = path_parts[-1].replace('_',' ').replace('job ','')
    ji.job_group       = path_parts[-2]
    ji.job_name_full   = ji.job_group + '.' + ji.job_name

    return ji

######################################

__jobinfo = SimpleNamespace()

def get_jobinfo():

    global __jobinfo

    # Check Cache
    if __jobinfo.__dict__:
        return __jobinfo

    # Get it from file, if running in container
    ji = __get_jobinfo_from_file() 

    # Otherwise get it from context
    if not ji:
        ji = __get_jobinfo_from_context()

    #Validate
    assert ji.__dict__

    # Log it
    for k,v in ji.__dict__.items(): 
        log.debug(f'JOBINFO - {k}: {v}')

    # Warning
    # log.warning(f'GIT STATUS:\n{ji.git_status}') if ji.git_status else None

    # Return it
    __jobinfo = ji
    return ji

######################################

