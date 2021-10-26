"""
********************************************************************************
     Module: gp.settings
Description: load "settings.json" into Python object
      Usage: use gp.settings.get() to access sessings in json file
     Author: Justin Jones
    Created: 2017-09-28
********************************************************************************
"""

import os
import sys
import re
import logging
import json
from types import SimpleNamespace
from glob import glob 

import gp.utils
from gp.utils import to_json

log = logging.getLogger(__name__)

# Default settings
settings = {'email.enabled': False, 'snowflake.debug': True}

# SimpleNamespace
namespace = None

# Default settings file name
## NOTE -- Adjusting for Linux
# settings_file = os.getcwd() + f'\\settings.json'
settings_file = os.getcwd() + f'/settings.json'

'''
NEW -- Adding function to import into runner.py for testing
'''


# Add first command line arg to setting file if present
if len(sys.argv)>=1:
    ## NOTE -- Adjusting for Linux
    '''
    In containers, the current output of settings_file is /app/settings.test.json
    - This is because the file paths are different in a docker container
    - Locally:
        - We execute each ETL by calling the .bat file located in the project directory
        - For `job_pika6_load`, this would be the .bat file in the root directory
        - Therefore, os.getcwd() produces the current directory - of that .bat file
    - Containers:
        - The script is executed from within the WORKDIR set in the Docker container, /app
        - It is from here that we call python3 pika/main.py test 
        - Therefore, os.getcwd() produces /app
    - RESOLUTION:
        - Update the below to add the project folder name to the directory listing
    
    - NOTE:
        - The function used at the moment, job_name(), should be reviewed. 
        - Works for projects with one subfolder, which is the assumption. Would test this
        with other jobs before moving them into production.
    '''
    # job_name = gp.utils.get_job_name()
    # project_name = job_name.split("_")[1]
    print('CLI ARGS >= 1: ', sys.argv[:])
    # ALL CLI CONTENTS:  ['./pika/job_pika6_load/main.py', 'test']
    project_name = sys.argv[0].split('/')[1]
    job_name = sys.argv[0].split('/')[2]
    # settings_file = os.getcwd() + f'\\settings.{sys.argv[1].lower()}.json'
    # settings_file = os.getcwd() + f'{project_name}/{job_name}/settings.{sys.argv[1].lower()}.json'
    settings_file = f'{project_name}/{job_name}/settings.{sys.argv[1].lower()}.json'

# If settings file does not exists -- Change ext from js to json
# if not os.path.isfile(settings_file):
#     settings_file += 'on'

# In any case log which settings file
log.info(f'SETTINGS FILE: {settings_file}')

# Load the file if exists
if os.path.isfile(settings_file):
    log.info('SETTINGS FILE EXISTS --- LOADING')
    # Get settings
    text = open(settings_file, 'r').read()

    # Fix old keys that are incompatible with SimpleNamespace
    text = text.replace('"email.enabled"', '"email_enabled"')
    text = text.replace('"snowflake.debug"', '"snowflake_debug"')

    # Remove lines commented out with //
    text = re.sub(r'^\s*//.*?$', '', text, flags=re.MULTILINE)
    
    # Debug
    log.debug(f'settings: {to_json(settings)}')

    # Convert from json
    settings = json.loads(text)

    # Remove comment key
    for k in list(settings.keys()):
        if k.startswith('//'): 
            del settings[k]

    settings['settings_file'] = settings_file
    settings['settings_json'] = text
    settings['settings_subfile'] = sys.argv[1] if len(sys.argv)>1 else ''
    settings['settings_map'] = json.loads(text)
    settings['max_threads'] = settings['max_threads'] if 'max_threads' in settings else 4

    # Convert to object
    namespace = json.loads(json.dumps(settings), object_hook=lambda d: SimpleNamespace(**d))



# API


def get(name, default=None):

    # Exists
    if name in settings.keys():
        return settings[name]

    # Doesn't exists -- Use default
    elif default != None:
        return default

    # Doesn't exist and no default -- Raise exception
    raise ValueError(f'Setting not found: {name}')
