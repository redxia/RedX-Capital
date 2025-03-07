import logging
import sys
import os
import importlib
from types import SimpleNamespace

import gp2.snowflake as snowflake
import gp2.utils
from gp2.settings import settings as settings_map, namespace as settings, settings_file

log = logging.getLogger(__name__)

def run_py_step(filename, output_filename, env):

    log.info(filename)

    module_name = filename.replace('\\','.').replace('/','.').replace('.py','')
    module = importlib.import_module(module_name)

    if 'run' in module.__dict__:
        log.debug('PY STEP: RUN()')
        result = module.run(SimpleNamespace(**env.globals))
        if (type(result) is dict): 
            for k,v in result.items():
                env.globals[k] = v
                # log.debug(f'PY STEP RETURN: {k} = {v}')

    else:
        log.debug('PY STEP: NO RUN()')

    if ('exports' in module.__dict__) and (type(module.exports) is dict):
        for k,v in module.exports.items():
            env.globals[k] = v
            # log.debug(f'PY STEP EXPORT: {k} = {v}')



