"""
********************************************************************************
     Module: gp.s3
Description: Wrappers for common S3 tasks
      Usage: 
     Author: Justin Jones
    Created: 2017-10-10
********************************************************************************
"""
# NOTE - Removing `Callback=progress` - errors out for Linux distributions
# Evaluate implementation of callback / TransferConfig details

import os
import re
import boto3
import json
from datetime import datetime
from datetime import date
from botocore.exceptions import ClientError
import logging
import gp.utils 

log = logging.getLogger(__name__)

##########################

session = None
resource = None
client = None

###########################

def extract_bucket(url):
    assert url.startswith('s3://')
    return url.split('/')[2]

def extract_path(url):
    assert url.startswith('s3://')
    return '/'.join(url.split('/')[3:])    

def extract_filename(path):
    # assert not path.endswith('/')
    return path.split('/')[-1]    

##########################

def connect(profile=None, region='us-east-1'):

    global session, resource, client

    session  = boto3.Session(profile_name=profile)
    resource = session.resource('s3')
    client   = session.client('s3')
    '''
    NOTE - Remove after testing
    priting buckets after connecting
    '''
    print('BUCKETS IN ACCT: ', str(client.list_buckets()))
    print('BUCKET OBJECTS: ', str())

##########################        

def get_resource_bucket(url):
    bucket_name = extract_bucket(url)
    return resource.Bucket(bucket_name)

##########################        

def delete_files(url, recursive=True):
        
    bucket = get_resource_bucket(url)
    prefix = extract_path(url)
    items = bucket.objects.filter(Prefix=prefix)

    assert items and len(prefix)>1

    log.debug(f'deleting {len(list(items))} items')

    result = items.delete()
    log.debug(f'delete result: \n {result}' )

##########################        

def get_file_names(url):

    bucket = get_resource_bucket(url)
    prefix = extract_path(url)

    #Full paths
    keys = [item.key for item in bucket.objects.filter(Prefix=prefix)]

    #Extract file name
    filenames = [extract_filename(s) for s in keys]

    #Filter out empty file names (caused by folder keys)
    filename = [f for f in filenames if f]

    #Screen out folder
    clean = [s for s in filenames if len(s)>0]

    log.debug('%s - file count: %s' % (url, len(clean)))
    log.debug('file names:\n %s' % gp.utils.to_json(clean))

    return clean

    # exit(0)

    # #initiali request    
    # response = self.client.list_objects_v2(Bucket=bucket, Prefix=path)

    # if response['KeyCount'] == 0:
    #     return {}

    # #results
    # files = {}
    
    # while True:

    #     contents = response['Contents']
    #     print('S3.list()', url, len(contents))

    #     #assumes filenames are unique!
    #     f = { extract_filename(item['Key']) : item for item in contents }
    #     files.update(f)

    #     is_truncated = response['IsTruncated']
    #     if not is_truncated: break

    #     #Follow up requests
    #     token = response['NextContinuationToken'] 
    #     response = self.client.list_objects_v2(Bucket=bucket, Prefix=path, ContinuationToken=token)

    # return files

def get_file_details(url):

    bucket = get_resource_bucket(url)
    prefix = extract_path(url)

    #Full paths
    items = [{
        'filename':extract_filename(i.key), 
        'url': 's3://' + i.bucket_name + '/' + i.key, 
        'key':i.key, 
        'etag':i.e_tag, 
        'size':i.size
    } for i in bucket.objects.filter(Prefix=prefix)]

    return items

##########################        

def make_presigned_url(url, expiration_minutes=60):

    signed_url = client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': extract_bucket(url),
            'Key': extract_path(url)
        },
        ExpiresIn=expiration_minutes*60
    )

    return signed_url

##########################        

def upload_file(filename, url,content_type=None):

    log.debug('filename=%s, url=%s' % (filename, url))

    bucket = get_resource_bucket(url)
    '''
    NOTE - REMOVE after dev
    - Displaying bucket contents
    '''
    print('BUCKET RESOURCES: ', str(bucket.get_available_subresources()))
    key = extract_path(url)

    # def progress(count):
    #     if gp.utils.enter_pressed():
    #         raise Exception('Key Pressed')
    
    # md5 = gp.utils.get_md5_digest(filename)
    # ExtraArgs={"Metadata": {"MD5": md5}}
    print('FILE BEING UPLOADED: ', filename)
    print('FILE KEY: ', key)
    print('CONTENT TYPE: ', content_type)
    
    if content_type:
        # bucket.upload_file(Filename=filename, Key=key, ExtraArgs = {'ContentType':content_type},Callback=progress)
        bucket.upload_file(Filename=filename, Key=key, ExtraArgs = {'ContentType':content_type})
    else:
        bucket.upload_file(Filename=filename, Key=key)
        # bucket.upload_file(Filename=filename, Key=key, Callback=progress)


def upload_bytes(s, url, content_type=None):
    # log.debug('url=%s, s=%s' % (url, s))
    log.debug(f'url={url}')
    bucket = get_resource_bucket(url)
    path = extract_path(url)
    if content_type == None:
        bucket.put_object(Key=path, Body=s)
    else:
        bucket.put_object(Key=path, Body=s, ContentType=content_type)


def upload_str(s, url, content_type=None):
    upload_bytes(s.encode('utf-8'), url, content_type)


def download_str(url):

    bucket = get_resource_bucket(url)
    key = extract_path(url)

    o = bucket.Object(key)
    result = o.get()['Body'].read().decode('utf-8')         

    return result

def download_file(url, filename):

    gp.utils.delete_file(filename)

    log.debug('filename=%s, url=%s' % (filename, url))

    bucket = get_resource_bucket(url)
    key = extract_path(url)

    # NOTE - commenting out the progress count
    # def progress(count):
    #     if gp.utils.enter_pressed():
    #         raise Exception('Key Pressed')

    #
    # bucket.download_file(Filename=filename, Key=key, Callback=progress)
    bucket.download_file(Filename=filename, Key=key)

    log.debug('Complete')

def copy(src_url, dest_url, src_session=None):

    log.debug('src_url=%s, dest_url=%s' % (src_url, dest_url))

    src = { 
        'Bucket': extract_bucket(src_url), 
        'Key': extract_path(src_url) 
    }

    dest_bucket = get_resource_bucket(dest_url)
    dest_path = extract_path(dest_url)

    # def progress(count):
    #     if gp.utils.enter_pressed():
    #         raise Exception('Key Pressed')

    # dest_bucket.copy(src, dest_path, ExtraArgs=None, Callback=progress, SourceClient=src_session.client, Config=None)
    dest_bucket.copy(src, dest_path, ExtraArgs=None, SourceClient=src_session.client, Config=None)

    log.debug('Complete')

def key_exists(url):
    
    bucket = extract_bucket(url)
    path = extract_path(url)

    try:        
        # response = self.client.list_objects_v2(Bucket=bucket, Prefix=path, MaxKeys=1)
        # exists = response['KeyCount'] > 0
        # print('S3.key_exists()', url, bucket, path, exists)            
        # return exists
        client.head_object(Bucket=bucket, Key=path)
        return True

    except ClientError as ex:
        # log.debug('key_exists()', url, bucket, path, 'Exception:', ex)            
        return False

# def bucket_info(self, url):

#     bucket = extract_bucket(url)
    
#     response = self.head_bucket(Bucket=bucket)
#     print('S3.bucket_info()', url, bucket, response)

# def key_info(self, url):

#     bucket = extract_bucket(url)
#     path   = extract_path(url)

#     response = self.head_bucket(Bucket=bucket, Key=path)
#     print('S3.key_info()', url, bucket, response)

#     return response


# def s3_upload(self, filename, url):

#     bucket = extract_bucket(url)
#     path   = extract_path(url)

#     self.client.upload_file(filename, bucket, path) #, Callback=progress)

######################