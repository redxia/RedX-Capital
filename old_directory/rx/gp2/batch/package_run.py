assert __name__ == '__main__'

import boto3
import json
import time
import re
import sys
import os
import pathlib
import logging

###########################################

logging.basicConfig(level=logging.INFO, format='BATCH JOB RUN | %(levelname)s | %(message)s')
log = logging.getLogger(__name__)

# Guard
if 2 != len(sys.argv):
    print('ERROR: Expecting settings name argument')
    sys.exit(1)

###########################################

# API objects
batch = boto3.client('batch')
cloudwatch = boto3.client('logs')

###########################################
# Args
###########################################

relative_path   = re.sub(r'^\w:\\dev\\', '', os.getcwd(), re.IGNORECASE).replace('\\','/').lower()
cwd = pathlib.Path.cwd()

job_name        = cwd.parent.name + '-' + cwd.name # use parent + current folder name
job_queue       = 'QS-Queue-Priority'
# job_queue       = 'QS-Queue-Default'
job_def         = 'QS-JobDef-Fetchnrun-py37'

FETCHNRUN_PATH  = relative_path + '.zip'
FETCHNRUN_ARG   = sys.argv[1]

log.info('FETCHNRUN_ARG: %s', FETCHNRUN_ARG)
log.info('FETCHNRUN_PATH: %s', FETCHNRUN_PATH)
log.info('JOB NAME: %s', job_name)
log.info('JOB QUEUE: %s', job_queue)
log.info('JOB DEF: %s', job_def)

###########################################
# Submit Job
###########################################

# aws batch submit-job ^
#     --job-name jj_fetchnrun_test_etl ^
#     --job-queue QS-Batch-Job-Queue ^
#     --job-definition Job-Def-Fetchnrun ^
#     --timeout attemptDurationSeconds=60 ^
#     --parameters FETCHNRUN_PATH=da.main/infrastructure/cdk/apps/batch2/docker/fetchnrun/test_etl.zip,FETCHNRUN_ARG=test ^
#     --container-overrides environment=[{name=asdf1,value=asdf2}]
#     @REM --container-overrides environment=[{name=FETCHNRUN_PATH,value=da.main/infrastructure/cdk/apps/batch2/docker/fetchnrun/test_etl.zip},{name=FETCHNRUN_ARG,value=test}]

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/batch.html#Batch.Client.submit_job
start_time = time.time()
r = batch.submit_job(
    jobName=job_name,
    jobQueue=job_queue,
    jobDefinition=job_def,

    parameters = { 'FETCHNRUN_PATH': FETCHNRUN_PATH, 'FETCHNRUN_ARG': FETCHNRUN_ARG }
    )
# log.info(json.dumps(r,indent=2))
job_id = r['jobId']
log.info('JOB_ID: %s', job_id)
# log.info('*'*37)

###########################################
# Poll for completion
###########################################

job_desc = None
job_status = None
while True:
    r = batch.describe_jobs(jobs=[job_id])
    # log.info(json.dumps(r,indent=2))
    job_desc = r["jobs"][0]
    job_status = job_desc["status"]
    duration = time.time() - start_time
    log.info(f'{job_status}, {duration}')
    if job_status in ['SUCCEEDED','FAILED']: break
    time.sleep(1)
    # log.info('*'*37)
exit_code = job_desc["container"]["exitCode"]
log.info('EXIT_CODE: %s', exit_code)

###########################################
# Dump logs
###########################################

log_stream = job_desc["container"]["logStreamName"]
log.info('LOG STREAM: %s', log_stream)
for i in range(1,10):
    time.sleep(i*2)
    r = cloudwatch.get_log_events(
        logGroupName='/aws/batch/job',
        logStreamName=log_stream,
        # startTime=123,
        # endTime=123,
        # nextToken='string',
        # limit=123,
        # startFromHead=True|False
    )
    # log.info(json.dumps(r,indent=2))
    events=r["events"]
    if len(events)>0:
        # log.info(json.dumps(events,indent=2))
        for e in events:
            log.info('LOG STREAM >>> %s', e["message"])
        break
