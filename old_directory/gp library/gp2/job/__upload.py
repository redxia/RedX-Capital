import os
import sys
import re
import traceback
import logging
from datetime import datetime
import subprocess
from types import SimpleNamespace
import glob
import uuid

from botocore.exceptions import NoCredentialsError,ClientError
from boto3.exceptions import S3UploadFailedError

import gp2.settings
import gp2.utils
import gp2.s3
import gp2.snowflake as snowflake
import gp2.email

from .__tmp_dir import TMP_DIR

#################################

log = logging.getLogger(__name__)

#################################
### PRIVATE
#################################

def __upload_job_files(locations):

    # File extensions to upload + content type
    content_types = { '.txt':'text/plain', '.html':'text/html', '.sql':'text/plain', '.png':'image/png', '.ipynb':'applicaiton/vnd.jupyter', 'twb':'application/twb', '.csv':'application/vnd.ms-excel' }
    
    # Log files to upload
    files = [ gp2.settings.logfile, gp2.settings.logfile_debug ]
    
    # Selected files from tmp folder -- Not recursive for now
    for ext in list(content_types.keys()):
        files += glob.glob(f'{TMP_DIR}/*{ext}')
    
    # Upload to S3
    gp2.s3.connect()
    for f in files:
        ext = os.path.splitext(f)[1] #if '.' in output_files[i] else None
        ct = content_types[ext]
        s3_url = locations.output_s3 + '/' + f.replace('\\','/')
        # log.info(f'UPLOADING: {f} --> {s3_url} ({ct})')
        gp2.s3.upload_file(f, s3_url, content_type=ct)
    
    # return list of files
    return files

def __upload_job_queries(locations):
    sql = f'''    
        select *
        from table(rawdata.information_schema.query_history_by_session(session_id => {snowflake.conn.session_id}::number, result_limit => 10000))
        order by start_time;
    '''
    gp2.s3.connect()
    gp2.s3.upload_str(sql, locations.output_s3+'/queries.sql', content_type='text/plain')
    # Too slow and causes locks
    # snowflake.conn.cursor().execute_async( # Not supported in current version yet
    # snowflake.cursor().execute(f'''
    #     copy into '{locations.output_stage}/queries.csv'
    #     from (
    #         select *
    #         from table(rawdata.information_schema.query_history_by_session(session_id => current_session()::number, result_limit => 10000))
    #         order by start_time
    #     )
    #     file_format = (field_delimiter=',' null_if = ()  field_optionally_enclosed_by='"' empty_field_as_null=true compression=none) 
    #     overwrite = true 
    #     header = true 
    #     single = true
    #     max_file_size = 5368709120;
    # ''', _no_results=True)

def __upload_job_index(locations, files):

    # TODO: Refactor to use Jinja
    
    # Links
    links = '<ul>\n'
    for f in sorted(files) + ['queries.sql', 'index.html']:
        url = locations.output_url + '/' + f.replace('\\','/')
        links +=f'<li><a href="{url}">{f}</a></li>\n'
    links += '</ul>\n'
    
    # Styling
    style = '''<style>
        body { font-family: Helvetica, Arial, Sans-Serif; } 
        a { text-decoration:none; }
    @media (prefers-color-scheme: dark) {
        body { background-color: #111; color: #e4e4e4; }
        a { color: #0089c7; }
    }
    </style>\n'''
    
    # log.txt
    logfile = gp2.utils.read_file(gp2.settings.logfile).replace('\n','<br>') +'\n\n'
    
    # HTML body
    body = f'{style}\n{logfile}\n{links}'
    
    # Upload body as index.html
    gp2.s3.upload_str(body, locations.output_s3+'/index.html',content_type='text/html')

    # Return body for use in email
    return body

#################################
### INTERNAL
#################################

def get_job_output_locations(repo_path, run_id, start_time):
    
    # C:\dev\...\settings.live.json --> 'live'
    # setting_name = re.search(r'\bsettings.(\w+).json$', gp2.settings.settings_file)
    # setting_name = setting_name.group(1) if setting_name else 'none'
    settings_name = gp2.settings.settings_name or 'none'

    # Make URLs unguessable
    random_id = uuid.uuid4()

    # Include time
    run_date = start_time.strftime('%Y%m%d')

    # Put it together
    path = f'job/gp2/{repo_path}/{run_date}.{run_id}.{settings_name}.{random_id}'.lower().replace('\\','/').replace('//','/')

    # Pack it up
    return SimpleNamespace(
        bucket       = 'rawdata.s3.internal',
        path         = path,
        output_stage =                         '@rawdata.s3.internal/' + path,
        output_s3    =                     's3://guidepoint.internal/' + path,
        output_url   = 'https://s3.amazonaws.com/guidepoint.internal/' + path
    )

#################################

def upload_job_outputs(locations, run_id): 

    try:
        log.info('UPLOADING JOB OUTPUTS')
        __upload_job_queries(locations)
        files = __upload_job_files(locations)
        body = __upload_job_index(locations, files)
        log.info(f'JOB OUTPUT: {locations.output_url}/index.html')

    except (NoCredentialsError, ClientError, S3UploadFailedError) as ex:
        log.warning('ERROR UPLOADING JOB OUTPUTS TO S3')
        log.debug(ex)
        body = gp2.utils.read_file(gp2.settings.logfile).replace('\n','<br>') +'\n\n'

    return body

#################################

def email_job_report(success, jobinfo, body):

    # Enabled?
    if not gp2.settings.get('email_enabled', default=False):
        log.warning('EMAIL DISABLED - JOB REPORT NOT SENT')
        return

    # Send
    try:
        log.info('EMAILING JOB REPORT')
        result = 'SUCCESS' if success else 'FAIL'
        subject = f"JOB {jobinfo.job_group} - {jobinfo.job_name}: {result}".upper()
        gp2.email.send(subject,body=body, body_filename=None, plain=False, attachments=[])

    except (NoCredentialsError, ClientError, S3UploadFailedError) as ex:
        log.warning('ERROR SENDING JOB REPORT')
        log.debug(ex)

#################################
#################################
