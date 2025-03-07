"""
********************************************************************************
     Module: gp.utils
Description: Common operations
      Usage:
     Author: Justin Jones
    Created: 2017-09-18
********************************************************************************
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
import select
import hashlib
import hmac
import base64

####################

logfile         = 'log.txt'
debug_logfile   = 'log.debug.txt' 

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
    logging.getLogger('snowflake.connector.ocsp_pyopenssl').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.ssl_wrap_socket').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.converter').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.connection').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.network').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.cursor').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.auth').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.chunk_downloader').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.ocsp_asn1crypto').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.json_result').setLevel(logging.WARNING) #snowflake-connector-python==2.2.0
    logging.getLogger('snowflake.connector.arrow_result').setLevel(logging.WARNING) #snowflake-connector-python==2.2.0
    logging.getLogger('tendo.singleton').setLevel(logging.WARNING)
    logging.getLogger('requests.packages.urllib3').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)


    #Debug File Logger
    logging.basicConfig(filename=debug_logfile,  filemode='w', level=logging.DEBUG, format='%(asctime)s | %(threadName)s | %(levelname)s | %(funcName)s | %(name)s | %(message)s\n')
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

###########################

def dump(obj, indent=4):
    #pp.pprint(obj)
    return PrettyPrinter(indent=indent).pformat(obj)


def indent(s, n=4):
    if not type(s) is str: s = str(s)
    return re.sub(r'^',' '*n, s, flags=re.MULTILINE)

###########################

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    elif isinstance(obj, date):
        serial = obj.isoformat()
        return serial
    else:
        return repr(obj)

def to_json(obj):
    return json.dumps(obj, default=json_serial, indent=4)         

###########################

def first_match(regex, text, default=None):
    search = re.search(regex, text)
    if search==None:
        return default
    result = search.group(1)
    return result


def symbol_to_snake_case_str(string):
    new_str = re.sub(r"\(|\)|\{|\}|\.|\[|\]|\?|\,|\*|\%|\$|\#|\@|\!|\^|\&|\~|\:|\-|\s+|\/",'_',string)
    new_str = re.sub(r"\’|\'|\_+$",'',new_str)
    new_str = re.sub(r"\<",'less',new_str)
    new_str = re.sub(r"\+",'plus',new_str)
    new_str = re.sub(r"^100",'one_hundred',new_str)
    new_str = re.sub(r"\_+",'_',new_str)
    return new_str

###########################

# Returns True if key was pressed
def enter_pressed():

    import platform

    #Windows
    if platform.system()=='Windows':
        import msvcrt
        return msvcrt.kbhit()
    
    
    ## NOTE - This is throwing the latest error. 
    # raise Exception('Key Pressed')
    # ==> Not necessary when running in containers
    # Commenting out Linux component for now.
    
    #Linux
    # i,o,e = select.select([sys.stdin],[],[],0.0001)
    # for s in i:
    #     if s == sys.stdin:
    #         input = sys.stdin.readline()
    #         return True
    # return False

###########################

def write_file(filename, content):
    
    mode = 'w'
    if type(content).__name__ == 'bytes': mode += 'b'

    with open(filename, mode) as out:
        out.write(content)

def append_file(filename, text):
    with open(filename, 'a') as out:
        try:
            out.write(text)
        except Exception as e:
            # out.write(text.encode('utf8'))
            log.error(e)
            log.error(text)

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def delete_file(filename):
    log.debug('deleting file: %s' % filename)
    if os.path.exists(filename):
        os.remove(filename)

def get_tmp_file(prefix):
    return r'd:\temp\%s_%d.tmp' % (prefix, time.time())

##################

def get_md5_digest(filename, block_size=65536):
    
    with open(filename, 'rb') as f:
        m = hashlib.md5()
        while True:
            data = f.read(block_size)
            if len(data) == 0:
                break
            m.update(data)
            return m.hexdigest()

def get_sha256_file(filename, block_size=65536):
    h = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            h.update(block)
    return h.hexdigest()

# def get_sha256_file_base64(filename, block_size=65536):
#     hexdigest = get_sha256_file(filename, block_size=65536)
#     signature = base64.b64encode(bytes(hexdigest))    
#     return signature

def get_sha256_hex(text):
    h = hashlib.sha256()
    h.update(text)
    return h.hexdigest()

def get_sha256_base64(text):
    message = bytes(text)
    #secret = bytes("985jkskjgkasd").encode('utf-8')
    signature = base64.b64encode(hmac.new(b'asdfasdf', message, digestmod=hashlib.sha256).digest())    

    return signature

#########
                  
def write_json(filename, obj):
    js = json.dumps(to_json(obj))
    write_file(filename,js)

def read_json(filename):
    js = read_file(filename)
    return json.loads(js)

##################

import gzip
import shutil

def gzip_file(src, dest):
    with open(src, 'rb') as f_in:
        with gzip.open(dest, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


# Gzip with progress callback
def gzip_file2(src, dest=None, level=9, callback=None, remove=False):

    if dest==None:
        dest = src + '.gz'

    log.info('src=%s, dest=%s, level=%s, remove%s' % (src, dest, level, remove))

    blocksize = 1<<20 # 1MB 
    count = 0
    amount = 0
    cb = lambda _=None: callback(src, dest, count, amount) if callback and count % 100 == 0 else None

    with open(src, 'rb') as f_in:
        
        with gzip.open(dest, 'wb', level) as f_out:

            while True:
                block = f_in.read(blocksize)
                amount += len(block)
                if not block:
                    break

                f_out.write(block)

                count += 1
                cb ()
            
    if remove:
        delete_file(src)
    return dest

##################

# NEW - Function to extract project name for run_steps()
def get_job_name():
    '''
    Return the name of the job
    glob needs to reference <job>/steps, not steps
    '''
    dirs = [x[0] for x in os.walk('.') if 'steps' in x[0]]
    print('DIRS FOUND: ', dirs)
    job = dirs[0].split('/')[-2]
    print('JOB FOUND: ', job)
    return job
