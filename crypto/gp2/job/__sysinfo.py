import os
import sys
import logging
import psutil
import socket
from types import SimpleNamespace

import gp2.settings

#################################

log = logging.getLogger(__name__)

#################################

process     = psutil.Process(os.getpid())
initial_mem = process.memory_info().rss/10000000

def get_mem_used_delta():
    used_mem = process.memory_info().rss/1000000
    delta = used_mem - initial_mem
    log.debug(f'SYSINFO - MEMORY DELTA: {delta} MB')
    return delta

#################################

def get_external_ip():
    return ''
    # try:
    #     from requests import get
    #     return get('https://ipapi.co/ip/').text
    # except:
    #     return ''

#################################

sysinfo = SimpleNamespace()
def get_sysinfo() -> SimpleNamespace:

    # Done if not empty
    if sysinfo.__dict__:
        return sysinfo

    # Login
    import getpass
    sysinfo.username = getpass.getuser() #or os.getlogin().upper()

    # Network Info
    sysinfo.hostname = socket.gethostname()
    sysinfo.host_ip = socket.gethostbyname(sysinfo.hostname)  
    sysinfo.external_ip = get_external_ip()

    # Python
    sysinfo.python_version          = sys.version
    sysinfo.module_paths            = ';'.join(sys.path)

    # AWS
    import boto3
    sysinfo.boto3_version           = boto3.__version__
    sysinfo.aws_batch_job_id        = os.getenv('AWS_BATCH_JOB_ID', '')

    # Environment
    sysinfo.workding_dir            = os.getcwd()
    sysinfo.command_line            = ' '.join(sys.argv)

    # Platform
    import platform as p
    sysinfo.platform_system         = p.system()
    sysinfo.plaform_version         = p.version()
    sysinfo.platform_architecture   = p.architecture()[0]
    sysinfo.platform_machine        = p.machine()
    sysinfo.platform_processor      = p.processor()
    sysinfo.memory_used_mb          = initial_mem

    # Log it
    for k,v in sysinfo.__dict__.items(): 
        log.debug(f'SYSINFO - {k}: {v}')

    # Done
    return sysinfo

