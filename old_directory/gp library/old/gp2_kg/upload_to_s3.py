# https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
# https://stackoverflow.com/questions/3223604/how-to-create-a-temporary-directory-and-get-the-path-file-name-in-python

import logging
import os
import shutil
import sys
import tempfile
import zipfile

import boto3

import gp.s3

### Init ##############################

# Get logger for this module
log = logging.getLogger(__name__)

## TO RUN -- From folder root:
# PRODUCTION -- upload gp.da.temp pika job_pika6_load
# DEV -- upload kg.da.archive pika job_pika6_load

### Funcs ##############################

def create_working_dir(JOB, PROJECT):

    # Get full directory name of the script, no matter where it is called from
    dir_path = os.path.join("C:\dev\da.main\Job", PROJECT, JOB)
    log.info(f'DIRECTORY PATH: {dir_path}')

    # Create temporary directory
    WORK_DIR = os.path.join(dir_path, 'ZIP_DIR')
    STEPS_DIR = os.path.join(WORK_DIR, 'steps')
    log.info(f'TEMPORARY DIR: {WORK_DIR}')
    os.mkdir(WORK_DIR)
    os.mkdir(STEPS_DIR)

    # Check if tmp dir was created
    if not os.path.isdir(WORK_DIR) or not os.path.exists(WORK_DIR):
        log.info(f'PATH DOES NOT EXIST: {WORK_DIR}')
        sys.exit()

    # Check if steps dir was created
    if not os.path.isdir(os.path.join(WORK_DIR, 'steps')) or not os.path.exists(os.path.join(WORK_DIR, 'steps')):
        log.info(f'PATH DOES NOT EXIST: {WORK_DIR}/steps')
        sys.exit()

    return dir_path, WORK_DIR


def copy_files(dir_path, WORK_DIR):
    '''
    # Copy all files to be zipped to temporary folder
    '''
    file_names = os.listdir(dir_path)
    
    for file_name in file_names:
        if file_name == 'steps':
            log.info(f'DIRECTORY: {os.listdir(file_name)}')
            for step in os.listdir(file_name):
                log.info(f'STEP: {step}')
                if step != '__pycache__':
                    log.info(f'COPYING: {step}')
                    shutil.copy(os.path.join(file_name, step), os.path.join(WORK_DIR, 'steps'))

            log.info(f'MOVED STEPS folder to {WORK_DIR}')
        elif file_name.endswith('.json'):
            shutil.copy(file_name, WORK_DIR)
            log.info(f'MOVED JSON files to {WORK_DIR}')
        elif file_name == 'main.py':
            shutil.copy(file_name, WORK_DIR)
            log.info(f'MOVED main.py to {WORK_DIR}')

def zip_directory(JOB, WORK_DIR):
    '''
    Zip files in temporary directory 
    '''
    zip_file = zipfile.ZipFile(f'{JOB}.zip', 'w', zipfile.ZIP_DEFLATED)
    for file in os.listdir(WORK_DIR):
        if file == 'steps':
            for step in os.listdir(file):
                if step != '__pycache__':
                    zip_file.write(os.path.join(WORK_DIR, file, step))
        zip_file.write(os.path.join(WORK_DIR, file))
    zip_file.close()
    return zip_file

def upload_to_s3(BUCKET, JOB, PROJECT):
    '''
    Upload zip file in working directory to S3
    '''
    # NOTE -- REMOVE PROFILE_NAME ARGUMENT FOR PROD
    session = boto3.session.Session(profile_name='dev')
    s3 = session.resource('s3')

    dir_path, WORK_DIR = create_working_dir(JOB, PROJECT)
    copy_files(dir_path, WORK_DIR)
    zip_file = zip_directory(JOB, WORK_DIR)

    try:
        log.info('CONNECTING TO S3...')
        # gp.s3.connect(profile='dev')
    except Exception as ex:
        log.info(f'EXCEPTION RAISED: COULD NOT CONNECT TO S3 {str(ex)}')
    
    log.info(f'ZIPPED FILE: {zip_file}')
    url = f'{BUCKET}/kg/batch/job/{PROJECT}/{JOB}.zip'
    KEY = f'kg/batch/job/{PROJECT}/{JOB}.zip'
    log.info(f'S3 KEY: {KEY}')

    log.info(f'CURRENT DIRECTORY: %s' % os.getcwd())

    if os.path.exists(zip_file.filename):
        try:
            log.info(f'UPLOADING {zip_file} TO {url}...')
            s3.meta.client.upload_file(zip_file.filename, BUCKET, KEY)
            # gp.s3.upload_file(zip_file, url, content_type='application/zip')
            log.info(f'SUCCESSFULLY UPLOADED {zip_file} TO {url}')
        except Exception as ex:
            log.info(f'EXCEPTION RAISED: UNABLE TO UPLOAD FILE {zip_file} TO {url}: {str(ex)}')
    else: 
        log.info('FILE PATH DOES NOT EXIST')

    # delete the temp directory
    try:
        log.info(f'REMOVING TEMPORARY DIRECTORY: {WORK_DIR}')
        shutil.rmtree(WORK_DIR)
    except Exception as ex:
        log.info(f'EXCEPTION RAISED: UNABLE TO REMOVE TEMP DIRECTORY {str(ex)}')

### MAIN ##############################

if __name__ == '__main__': 
    BUCKET = sys.argv[1]
    PROJECT = sys.argv[2]
    JOB = sys.argv[3]

    print("BUCKET: ", BUCKET)
    print("PROJECT: ", PROJECT)
    print("JOB: ", JOB)

    upload_to_s3(BUCKET, JOB, PROJECT)