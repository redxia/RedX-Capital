"""
********************************************************************************
     Module: gp.secrets
Description: Retrieves secrets from AWS Secrets Manager
      Usage: call get_secret with secret name to retrieve a dictionary of secrets
      then use get_secret_value to in key into those secrets and return values
    Created: 2019-07-09
********************************************************************************
"""

import boto3
import base64
from botocore.exceptions import ClientError,NoCredentialsError
import time
import logging
import json

log = logging.getLogger(__name__)

def get_secret(secret_name):
    """
    Gets secret from AWS Secrets Manager
    """
    try:
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager') #, region_name=os.environ['REGION'])
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            secret = json.loads(response['SecretString']) # Return type dictionary (normal case)
        else:
            secret = base64.b64decode(response['SecretBinary']) # Return type ? (not in use)
        return secret
    except Exception:
        log.error(f"ERROR: Unable to get secret: {secret_name}")
        raise
