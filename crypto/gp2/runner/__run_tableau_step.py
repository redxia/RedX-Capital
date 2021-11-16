import logging
import sys
import os

import gp2.snowflake as snowflake
import gp2.utils

log = logging.getLogger(__name__)

def run_tableau_step(filename, output_filename, env):

    log.info(f'run_tableau_step: {filename}')
    gp2.utils.write_file(output_filename, '')

    try:
        tableau_template = gp2.utils.read_file(filename)
        t = env.from_string(tableau_template)
        # Warning: DO NOT REFERENCE t.module after t.render()
        tableau_rendered = t.render()
        gp2.utils.append_file(output_filename, tableau_rendered)

    except Exception as ex:
        # Log errors
        gp2.utils.append_file(output_filename, '\nFATAL ERROR: ' + str(ex) + '\n\n')
        raise ex

