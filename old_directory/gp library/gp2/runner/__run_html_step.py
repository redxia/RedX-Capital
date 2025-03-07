import logging
import sys
import os

import gp2.utils
import gp2.snowflake as snowflake
from gp2.settings import settings as settings_map, namespace as settings, settings_file

log = logging.getLogger(__name__)

def run_html_step(filename, output_filename, env):

    log.info(f'run_html_step: {filename}')
    gp2.utils.write_file(output_filename, '')

    try:
        html_template = gp2.utils.read_file(filename)
        t = env.from_string(html_template)
        # Warning: DO NOT REFERENCE t.module after t.render()
        html_rendered = t.render()
        gp2.utils.append_file(output_filename, html_rendered)

    except Exception as ex:
        # Log errors
        gp2.utils.append_file(output_filename, '\nFATAL ERROR: ' + str(ex) + '\n\n')
        raise ex

###########################################

