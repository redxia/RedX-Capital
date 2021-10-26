print('module looker')

import os
import requests
import logging
import gp.utils

# https://looker.com/docs/reference/api-and-integration/api-reference

######################

log = logging.getLogger(__name__)

######################

class Looker:


    def __init__(self, client_id=None, client_secret=None):
        self.client_id     = client_id     or os.environ['default_looker_client_id']
        self.client_secret = client_secret or os.environ['default_looker_client_secret']
        self.token = None
        self.base_url = 'https://guidepoint.looker.com:19999/api/3.0/'

    def login(self):
        log.debug('login')
        url = self.base_url + 'login?client_id={}&client_secret={}'.format(self.client_id, self.client_secret)
        r = requests.post(url)
        js = r.json()
        self.token = js['access_token']
        #log.debug ('token %s' % token)
        #return token

    def all_looks(self):

        log.debug("all_looks")

        url = self.base_url + "looks?fields=id,title"
        headers = {"Authorization": "Bearer " + self.token}

        r = requests.get(url, headers=headers)

        js = r.json()

        #log.debug('result js: %s' % js)

        return js

    #https://looker.com/docs/reference/api-and-integration/api-reference/look#run_look
    def run_look(self,look_id, result_format='html', filename=None):

        log.debug("run_look %s %s" % (look_id, result_format))

        #api/3.0/looks/{look_id}/run/{result_format}
        url = self.base_url + "/looks/%s/run/%s" % (look_id, result_format)
        headers = {"Authorization": "Bearer " + self.token}

        # #print requests.post(endpoint,data=data,headers=headers).json()
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            raise Exception("Looker HTTP Response Code %d" % r.status_code)

        #log.debug("RESPONSE REPR: %s" % repr(r))
        log.debug("RESPONSE TEXT: %s" % r.content)
        #js = r.json()

        if filename:
            ga.utils.write_file(filename, r.content)
            return 

        return r

######################

