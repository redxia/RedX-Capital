'''
Clear outputs from previous run
'''
import os
from shutil import rmtree
from glob import glob

import gp2.settings as settings

#################################

# Remove files from previous run
TMP_DIR = settings.get('tmp_dir', 'tmp')
assert TMP_DIR.startswith('tmp')

#################################

try:
    os.mkdir(TMP_DIR)
except FileExistsError:
    for f in glob(os.path.join(TMP_DIR, '*'), recursive=False):
        if os.path.isdir(f):
            rmtree(f)
        else:
            os.remove(f)

#################################
