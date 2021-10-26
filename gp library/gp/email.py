"""
********************************************************************************
     Module: gp.mail
Description: Sends email alerts
      Usage: Call send() to 
     Author: Justin Jones
    Created: 2017-09-28
********************************************************************************
"""

import os
import boto3
import os.path
import logging
import gp.utils
import gp.settings

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger(__name__)

################

default_src     = 'noreply@guidepointdata.com' #'jjones@guidepoint.com' #'no-reply@amazonses.com'
# default_dest    = gp.settings.get('email.dest', default=['jjones@guidepoint.com', 'spodder@guidepoint.com', 'lto@guidepoint.com', 'kdolgin@guidepoint.com'])
default_dest    = gp.settings.get('email.dest', default=['data-insights-alerts@guidepoint.com'])

################

def send(subject, body="empty", body_filename=None, src=default_src, dest=default_dest, plain=False, attachments=[]):

    log.debug('send_text() %s, %s' % (subject, dest[0]))

    if body_filename != None and os.path.exists(body_filename):
        body = gp.utils.read_file(body_filename)

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = src
    msg['To'] = ','.join(dest)

    msg.attach(MIMEText(body, 'plain' if plain else 'html'))
    
    for a in attachments:
        
        contents = None
        name = None
        t = type(a).__name__

        if t=='str': 
            name = os.path.basename(a)
            contents = open(a, 'rb').read(5000000) #5MB
            
        elif t=='tuple' and type(a[1]).__name__=='str':
            name = a[0]
            contents = open(a[1], 'rb').read(5000000) #5MB
        
        elif t=='tuple' and type(a[1]).__name__=='bytes':
            name = a[0]
            contents = a[1]

        else:
            raise ValueError("Bad attachment: %s" % a)

        part = MIMEApplication(contents)
        part.add_header('Content-Disposition', 'attachment', filename=name)
        msg.attach(part)
    
    session = boto3.Session()
    client = session.client('ses','us-east-1')
    result = client.send_raw_email(RawMessage={'Data': msg.as_string()}, Source=src, Destinations=dest) 

################