r'''

EXAMPLE:

    Currend working directory:  = C:\dev\da.main\Job\pika\job_pika_load\

    Command: run live_x

    SETTINGS FILE LOAD ORDER:

    First, Load Defaults
        1. GLOBAL  DEFAULT:   Job\shared\gp2\settings\          settings.default.json
        2. GROUP   DEFAULT:   Job\pika\shared\settings\         settings.default.json
        3. PROJECT DEFAULT:   Job\pika\job_pika_load\settings\  settings.default.json

    Then, Load "Kind" Settings" (live|stage|test|dev|other)
        4. GROUP   LIVE:      da.main\Job\pika\shared\settings\         settings.live.json
        5. PROJECT LIVE:      da.main\Job\pika\job_pika_load\settings\  settings.live.json

    Then, Load "Exact" Settings
        6. GROUP   LIVE_X:    da.main\Job\pika\shared\settings\         settings.live_x.json
        7. PROJECT LIVE_X:    da.main\Job\pika\job_pika_load\settings\  settings.live_x.json

'''

import os
import sys
import re
import logging
import json
from types import SimpleNamespace

#########################

if len(sys.argv) < 2:
    print('ERROR: Expecting settings file argument')
    sys.exit(1)

log = logging.getLogger(__name__)

#########################

def get_settings_from_file(filename:str) -> dict:

    if not os.path.isfile(filename):
        return {}

    # Get settings as text first
    with open(filename, 'r') as f:
        text = f.read()

    # Remove lines commented out with //
    text = re.sub(r'^\s*//.*?$', '', text, flags=re.MULTILINE)

    # Convert from json to dictionary
    try:
        d = json.loads(text)
    except json.decoder.JSONDecodeError as ex:
        log.fatal(f'ERROR IN SETTINGS FILE {filename}:\n' + str(ex))
        exit(1)
    assert isinstance(d, dict), 'Settings files must be dictionaries: ' + filename

    # Remove comment key
    for k in list(d.keys()):
        if k.startswith('//'):
            del d[k]

    # Return a dictionary
    return d

#########################

def fix_type(v):
    if v and v.lower() == 'true': return True
    elif v and v.lower() == 'false': return False
    elif v and re.match(r"[-+]?\d+(\.0*)?$", v) is not None: return int(v)
    elif v.startswith('[') or v.startswith('{'): return json.loads(v.replace("'",'"'))
    else: return v

def get_cli_settings():
    '''
    Return dictionary of CLI args
    Example: python main.py email_enabled=false debug=False x=123 y="a b c"
    TODO: Handle lists
    '''
    args = [ a.split('=') for a in sys.argv if '=' in a ]
    args = { a[0]:a[1] for a in args if a[0] }
    args = { k:fix_type(v) for k,v in args.items() }
    # print('args',args)
    return args


#########################

def get_merged_settings() -> ({}, [], str, str):

    global_folder  = os.path.dirname(__file__)
    group_folder   = os.path.join(os.getcwd(), '..', 'shared', 'settings')
    project_folder = os.path.join(os.getcwd(),                 'settings')

    # Load defaults first
    files = [
        os.path.join(global_folder,  'settings.default.json'),  # Global defaults
        os.path.join(group_folder,   'settings.default.json'),  # Group defaults
        os.path.join(project_folder, 'settings.default.json'),  # Project defaults
    ]

    # Override with specified settings
    settings_name = sys.argv[1].lower()

    # Kind
    if   'live'  in settings_name: kind = 'live'
    elif 'stage' in settings_name: kind = 'stage'
    elif 'test'  in settings_name: kind = 'test'
    elif 'dev'   in settings_name: kind = 'dev'
    else:                          kind = 'other'
    if kind!='other' and kind!=settings_name:
        f = f'settings.{kind}.json'
        files = files + [
            os.path.join(group_folder, f),  # Group kind settings
            os.path.join(group_folder, f),  # Project kind settings
        ]

    # Exact
    f = f'settings.{settings_name}.json'
    files = files + [
        os.path.join(group_folder,   f),  # Group settings
        os.path.join(project_folder, f),  # Project settings
    ]

    # Load
    settings = {}
    settings_files = []
    for f in files:
        d = get_settings_from_file(f)
        if d:
            settings.update(d)
            settings_files.append(f)

    # Apply CLI args
    cli_settings = get_cli_settings()
    settings.update(cli_settings)
    # print('settings',settings)

    # Prompt for data entry
    for k,v in settings.items():
        if v=='**ASK**':
            settings[k] = fix_type(input(f'ENTER A VALUE FOR SETTING [{k}]: '))

    return settings, settings_files, settings_name, kind, cli_settings




#########################
#########################

# Test: python -m gp2.settings.__settings
if __name__=='__main__':
    d,_,_,_,_ = get_merged_settings()
    for k,v in d.items():
        print(f'SETTING [{k}]: {v}')
    namespace = SimpleNamespace(**d)

