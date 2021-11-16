import logging
import sys
import os
import re
import time
from glob import glob
import shutil

from gp2.settings import settings as settings_map, namespace as settings, settings_file
from gp2.job import TMP_DIR

from .__run_sql_step     import run_sql_step
from .__run_html_step    import run_html_step
from .__run_tableau_step import run_tableau_step
from .__run_jupyter_step import run_jupyter_step
from .__run_py_step      import run_py_step
from .__jinja            import env

### Init ##############################

# Get logger for this module
log = logging.getLogger(__name__)

#### RUN #########################

def run_step(filename, output_filename):

    # Skip disabled steps
    if 'disabled' in filename.lower():
        log.debug(f'skipping disabled step: {filename}')
        return

    # Check step filter
    if 'step_filter' in settings_map and settings.step_filter:

        run_it = False # True when there is a positive match
        positive = False # True when there is at least one positive rule; when True, there must be at least one positive match

        for sf in settings.step_filter:

            assert sf[0] in ['+','-']
            assert len(sf)>1

            prefix = sf[0] 
            p = ('%' + sf[1:] + '%').replace('%', '.*')
            match = re.search(p, filename, flags=re.IGNORECASE)

            # Negative Match
            if prefix == '-':
                if match:
                    log.warn(f'SKIPPING {filename}, RULE: {sf}')
                    return

            # Match Pattern
            elif prefix == '+':
                positive = True
                if match:
                    run_it = True
                    break

            # Bad rule if we get here
            else:
                log.error(f'BAD RULE {sf} IGNORED')
                continue

        if not run_it and positive:
            log.warn(f'SKIPPING {filename}, NO POSITIVE MATCH')
            return

    env.globals['step_filename'] = filename
    env.globals['step_basename'] = os.path.basename(filename)
    env.globals['step_name'] = os.path.splitext(os.path.basename(filename))[0]

    if   filename.endswith('.sql'):     run_sql_step    (filename, output_filename, env)
    elif filename.endswith('.py'):      run_py_step     (filename, output_filename, env)
    elif filename.endswith('.html'):    run_html_step   (filename, output_filename, env)
    elif filename.endswith('.twb'):     run_tableau_step(filename, output_filename, env)
    elif filename.endswith('.ipynb'):   run_jupyter_step(filename, output_filename, env)
    else: log.debug(f'UNSUPPORTED STEP TYPE: {filename}')

###########################################

def run_system_step(step):
    filename = os.path.join(os.path.split(__file__)[0], 'steps', step)
    output_filename = os.path.join(TMP_DIR, 'output.' + step)
    run_sql_step(filename, output_filename, env)

def run_steps():

    run_system_step('system_step_1_initialize.sql')
    run_system_step('system_step_2_initial_state.sql')

    steps = glob('steps/**/*.*', recursive=True)
    steps.sort()
    log.debug(f'steps: {steps}')
    for filename in steps:
        output_filename = re.sub('^steps','output',filename, re.IGNORECASE)
        output_filename = re.sub(r'[\\/]','.', output_filename)
        output_filename = os.path.join(TMP_DIR, output_filename)
        run_step(filename, output_filename)

    run_system_step('system_step_3_finish_state.sql')

###########################################


