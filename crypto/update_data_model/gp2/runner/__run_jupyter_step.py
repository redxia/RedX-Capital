import logging
import sys
import os

import gp2.snowflake as snowflake
import gp2.utils
import gp2.job
from gp2.settings import settings as settings_map, namespace as settings, settings_file

log = logging.getLogger(__name__)

def run_jupyter_step(filename, output_filename, env):

    import subprocess

    log.info(filename)
    html_filename = output_filename.replace('.ipynb', '.html')
    tmp_notebook_filename = output_filename 

    s = gp2.utils.read_file(filename)
    s = s.replace('$$JOB_RUN_ID$$', str(gp2.job.run_id))
    s = s.replace('$$JOB_OUTPUT_URL$$', gp2.job.jobinfo.output_url)
    s = s.replace('$$SETTINGS_FILE$$', settings_file.replace('\\', '\\\\\\\\'))
    gp2.utils.write_file(tmp_notebook_filename, s)

    args = ["jupyter", "nbconvert", "--execute", tmp_notebook_filename, "--to", "html", "--output", html_filename]
    log.debug(args)
    subprocess.check_output(args)
