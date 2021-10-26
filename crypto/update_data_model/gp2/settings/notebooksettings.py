"""
USAGE - ADD THIS CODE TO JUPYTER NOTEBOOK STEP - TO LOAD ACTIVE SETTINGS FILE

    from gp.notebooksettings import get_settings
    settings = get_settings('$$SETTINGS_FILE$$')
    print(settings)

"""

from types import SimpleNamespace
import re
import json

def get_settings(settings_file):
    ''' Returns SimpleNamespace for specified JSON settings file '''
    settings_text = open(settings_file, 'r').read()
    settings_text = re.sub(r'^\s*//.*?$', '', settings_text, flags=re.MULTILINE)
    settings_dict = json.loads(settings_text)
    settings = json.loads(json.dumps(settings_dict), object_hook=lambda d: SimpleNamespace(**d))
    return settings