"""
"""

import os
import re
from datetime import datetime
import time
from pprint import PrettyPrinter
from datetime import datetime
from datetime import date
import json
import logging
import sys

from gp2.settings.__settings import get_merged_settings

####################

settings, _, _, _, _ = get_merged_settings()
logfile              = settings.get('logfile',       'log.txt')
logfile_debug        = settings.get('logfile_debug', 'log.debug.txt')

####################

_initialized = False
def init_logger():

    #Prevent re-entry
    global _initialized
    if _initialized: return
    _initialized = True

    #Only want urgent messages from these libs
    logging.getLogger('s3transfer').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('paramiko').setLevel(logging.WARNING)
    logging.getLogger('paramiko.transport').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.ocsp_pyopenssl').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.ssl_wrap_socket').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.converter').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.connection').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.network').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.cursor').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.auth').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.chunk_downloader').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.ocsp_asn1crypto').setLevel(logging.WARNING)
    # logging.getLogger('snowflake.connector.json_result').setLevel(logging.WARNING) #snowflake-connector-python==2.2.0
    # logging.getLogger('snowflake.connector.arrow_result').setLevel(logging.WARNING) #snowflake-connector-python==2.2.0
    logging.getLogger('tendo.singleton').setLevel(logging.WARNING)
    logging.getLogger('requests.packages.urllib3').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    # Make top logfile folder if specified, and if not exists
    if '/' in logfile:
        try:
            # p, _ = os.path.split(logfile)
            p = logfile.split('/')[0]
            os.mkdir(p)
        except:
            pass

    #Debug File Logger
    logging.basicConfig(filename=logfile_debug,  filemode='w', level=logging.DEBUG, format='%(asctime)s | %(threadName)s | %(levelname)s | %(funcName)s | %(name)s | %(message)s\n')
    logger = logging.getLogger()

    #Info File Logger
    f_handler = logging.FileHandler(logfile, mode='w')
    f_handler.setLevel(logging.INFO)
    # f_formatter = logging.Formatter('%(levelname)s | %(name)s | %(funcName)s | %(message)s\n')
    f_formatter = logging.Formatter('%(levelname)s | %(message)s\n')
    f_handler.setFormatter(f_formatter)
    logger.addHandler(f_handler)

    #Console logger
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    # c_formatter = logging.Formatter('%(levelname)s | %(name)s | %(funcName)s | %(message)s\n')
    c_formatter = logging.Formatter('%(levelname)s | %(message)s\n')
    c_handler.setFormatter(c_formatter)
    logger.addHandler(c_handler)

    logger.debug('Logging configured')

init_logger()
log = logging.getLogger(__name__)

####################
