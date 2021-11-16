from types import SimpleNamespace

from .__logs import logfile, logfile_debug
from .__settings import get_merged_settings

settings, settings_files, settings_name, settings_kind, cli_settings = get_merged_settings()
settings_file = settings_files[-1]
namespace = SimpleNamespace(**settings)

def get(name, default=None):
    return settings.get(name, default)

# def __getattr__(name):
#     return settings.get(name, None)

###############################
# Debug
###############################

import os
import logging

log = logging.getLogger(__name__)

for f in settings_files:
    p = os.path.relpath(f, os.getcwd())
    log.info(f'SETTINGS FILE: {p}')

for k,v in settings.items():
    log.debug(f'SETTING [{k}]: {v}')

for k,v in cli_settings.items():
    log.info(f'CLI SETTING: {k}={v}')
