import logging
import os
import re
import shutil
import sys
import tempfile
import zipfile
import time
import subprocess

import boto3

import gp2.s3

##############################

log = logging.getLogger(__name__)

##############################

def create_package():
    '''
    Zip files in temporary directory 
    '''
    cwd = os.getcwd()
    temp_file = os.path.join(tempfile.gettempdir(),f'batch.package.{time.time()}.zip')

    # Zip file object
    z = zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED)
    z.comment = b'Job Package'
    
    # Add etl_group folders
    n_files = 0
    for root, dirs, files in os.walk(cwd):
        for file in files:
            if os.path.basename(root).lower() in ['tmp','temp','node_modules','__pycache__','.vscode']:
                log.debug(f'*** SKIP FOLDER: {root}')
                continue
            if file.lower() in ('.gitignore','log.txt','log.debug.txt','package_info.json'):
                log.debug(f'*** SKIP FILE: {file}')
                continue
            if (os.path.splitext(file)[1].lower() in ('.zip')):
                log.debug(f'*** SKIP FILE: {file}')
                continue
            repo_path = root.replace(cwd,'')
            src_path = os.path.join(root, file)
            zip_path = os.path.join('job','.'+repo_path,file)
            z.write(src_path, zip_path)
            n_files = n_files + 1
            log.info(f'ADDED PROJECT FILE: {src_path} --> {zip_path}')

    shared_dir = os.path.join(cwd,'..','shared')
    if os.path.exists(shared_dir):
        for root, dirs, files in os.walk(shared_dir):
            for file in files:
                if os.path.basename(root).lower() in ['tmp','temp','node_modules','__pycache__','.vscode']:
                    log.debug(f'*** SKIP FOLDER: {root}')
                    continue
                if file.lower() in ('.gitignore','log.txt','log.debug.txt','package_info.json'):
                    log.debug(f'*** SKIP FILE: {file}')
                    continue
                if (os.path.splitext(file)[1].lower() in ('.zip')):
                    log.debug(f'*** SKIP FILE: {file}')
                    continue
                repo_path = root.replace(shared_dir,'')
                src_path = os.path.join(root, file)
                zip_path = os.path.join('job','.'+ repo_path, file)
                z.write(src_path, zip_path)
                n_files = n_files + 1
                log.info(f'ADDED PROJECT FILE: {src_path} --> {zip_path}')

    # Add lib folders as subdir
    # shared_lib = os.path.normpath('\dev\da.main\job\shared\gp2')
    # for file in os.listdir(shared_lib):
    #     log.info(f'ADDED LIB FILE: gp2/{file}')
    #     z.write(os.path.join(shared_lib, file), f'gp2/{file}')
    #     n_files = n_files + 1

    # Git Hash
    git_hash        = subprocess.run(['git', 'rev-parse', 'HEAD'           ], capture_output=True, check=True).stdout.decode('ascii').strip()
    git_status      = subprocess.run(['git', 'status', '-s'                ], capture_output=True, check=True).stdout.decode('ascii').rstrip()
    git_describe    = subprocess.run(['git', 'describe'                    ], capture_output=True, check=True).stdout.decode('ascii').strip()
    git_timestamp   = subprocess.run(['git', 'show', '-s', '--format=%ci'  ], capture_output=True, check=True).stdout.decode('ascii').strip()

    # More Package Info
    repo_path   = re.sub(r'^\w+:\\dev\\', '', cwd, re.IGNORECASE)
    path_parts  = os.getcwd().split(os.path.sep)
    job_name    = path_parts[-1].replace('_',' ').replace('job ','')
    job_group   = path_parts[-2]

    # Zip up Package Info
    package_info = dict(git_hash=git_hash, git_status=git_status, git_describe=git_describe, git_timestamp=git_timestamp, repo_path=repo_path, job_name=job_name, job_group=job_group)
    package_info_json = gp2.utils.to_json(package_info)
    z.writestr('job/package_info.json', package_info_json)
    log.info(f'GIT HASH: {git_hash}')
    if git_status:
        log.warning(f'GIT STATUS:\n{git_status}')

    # assert git_status != 'M', 'ERROR: Commit before publishing package'

    # Done
    z.close()
    log.info(f'FILES IN PACKAGE: {n_files}')
    return temp_file

##############################

def upload_package():

    STACK_ENV = os.getenv('STACK_ENV', 'DEV')
    if STACK_ENV=='LIVE':
        # s3_prefix = 's3://gp.da.temp/jj/fetchnrun'
        s3_prefix = 's3://guidepoint.internal/fetchnrun'
    elif STACK_ENV=='STAGE':
        s3_prefix = 's3://gp.da.temp/jj/fetchnrun'
    else:
        s3_prefix = 's3://qsight.dev.temp/jj/fetchnrun'
    log.info(f'S3 PREFIX: {s3_prefix}')

    # Maksure we're in the root of an ETL folder
    cwd = os.getcwd()
    # assert(os.path.exists('run.sh'))
    assert os.path.exists('run.bat') or os.path.exists('run.sh')
    assert cwd.lower() != os.path.split(__file__)[0].lower()

    # Compute repo_path for use in URL
    dev = os.path.normpath('c:\\dev\\')
    assert os.path.normpath(cwd).lower().startswith(dev)
    repo_path = os.path.relpath(cwd, dev).replace(os.path.sep, '/')
    log.info(f'REPO PATH: {repo_path}')

    # Get ENV and incorporate into URL
    stack_env = os.getenv('STACK_ENV','DEV')
    assert stack_env in ['LIVE','STAGE','DEV']
    log.info(f'STACK ENV: {stack_env}')

    # Construct pacakge URL
    s3_url = f'{s3_prefix}/{stack_env}/{repo_path}.zip'.lower()

    # Create and publish the package
    package_zip = create_package()
    gp2.s3.connect()
    gp2.s3.upload_file(package_zip, s3_url)
    os.remove(package_zip)

    # Debug
    log.info(f'PACKAGE ZIP: {package_zip}')
    log.info(f'S3 URL: {s3_url}')

##############################

if __name__ == '__main__': 
    logging.basicConfig(level=logging.INFO, format='BATCH JOB UPLOAD | %(levelname)s | %(message)s')
    upload_package()
