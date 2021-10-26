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

import gp.utils
from gp.utils import to_json

log = logging.getLogger(__name__)

# Default settings
settings = {'email.enabled': False, 'snowflake.debug': True}

# SimpleNamespace
namespace = None

# Default settings file name
settings_file = os.getcwd() + f'\\settings.json'

# Add first command line arg to setting file if present
if len(sys.argv)>=2:
    settings_file = os.getcwd() + f'\\settings.{sys.argv[1].lower()}.json'

# If settings file does not exists -- Change ext from js to json
# if not os.path.isfile(settings_file):
#     settings_file += 'on'

# In any case log which settings file
log.info(f'SETTINGS FILE: {os.path.basename(settings_file)}')

# Load the file if exists
if os.path.isfile(settings_file):

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
