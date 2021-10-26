"""
********************************************************************************
     Module: gp.secrets
Description: Retrieves secrets from AWS Secrets Manager
      Usage: call get_secret with secret name to retrieve a dictionary of secrets
      then use get_secret_value to in key into those secrets and return values
     Author: Osarodion Irabor
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
    '''
    Returns a dictionary of secrets from AWS Secrets Manager 
    associated with the given secret_name 
    '''

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.
    retry = 0
    secret = __get_secret(secret_name,client,retry,3) 
    if secret!=None:
        secret = json.loads(secret)
    return secret

def get_secret_value(secrets_map,key,default_value=None):
    '''
    Returns the value associated with a given key from the secrets 
    dictionary else None

    optional Arg
    -----------------
    default_value
    '''
    if type(secrets_map) ==dict:
        if key in secrets_map:
            return secrets_map[key].strip()
        else:
            return default_value
    return None

##################### PRIVATE FUNCTIONS ###############################
def __get_secret(secret_name,client,retry,max_retry):
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            if retry == max_retry:
                log.error(f'RETRYS FAILED AFTER {retry} ATTEMPTS: {e}')
                raise e
            log.warning('RETRY BECAUSE ERROR OCCURRED ON THE SERVER SIDE')
            time.sleep(3)
            return __get_secret(secret_name,client,retry+1,max_retry)

        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            raise e
        else:
            raise e
    except NoCredentialsError as e:
        raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return secret