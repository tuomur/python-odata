# -*- coding: utf-8 -*-

import json

from odata import version
from .exceptions import ODataError


class OData3Connection(object):

    base_headers = {
        'Accept': 'application/json',
        'OData-Version': '4.0',
        'User-Agent': 'python-odata {0}'.format(version),
    }

    def __init__(self, session=None, auth=None):
        if session is None:
            import requests
            self.session = requests.Session()
        else:
            self.session = session
        self.auth = auth

    def _apply_auth(self, kwargs):
        if self.auth is not None:
            kwargs['auth'] = self.auth

    def _do_get(self, *args, **kwargs):
        self._apply_auth(kwargs)
        return self.session.get(*args, **kwargs)

    def _do_post(self, *args, **kwargs):
        self._apply_auth(kwargs)
        return self.session.post(*args, **kwargs)

    def _do_put(self, *args, **kwargs):
        self._apply_auth(kwargs)
        return self.session.put(*args, **kwargs)

    def _do_patch(self, *args, **kwargs):
        self._apply_auth(kwargs)
        return self.session.patch(*args, **kwargs)

    def _handle_odata_error(self, response):
        try:
            response.raise_for_status()
        except:
            code = 'None'
            message = 'Unknown error'
            detailed_message = 'None'
            response_ct = response.headers.get('content-type')

            if 'application/json' in response_ct:
                errordata = response.json()
                if 'odata.error' in errordata:
                    odata_error = errordata.get('odata.error')

                    if 'code' in odata_error:
                        code = odata_error.get('code', code)
                    if 'message' in odata_error:
                        message = odata_error['message'].get('value', message)
                    if 'innererror' in odata_error:
                        ie = odata_error['innererror']
                        detailed_message = ie.get('message', detailed_message)

            msg = ' | '.join([code, message, detailed_message])
            raise ODataError(msg)

    def execute_get(self, url, params=None):
        headers = {}
        headers.update(self.base_headers)

        response = self._do_get(url, params=params, headers=headers)
        self._handle_odata_error(response)
        response_ct = response.headers.get('content-type')
        if 'application/json' in response_ct:
            data = response.json()
            return data
        else:
            msg = u'Unsupported response Content-Type: {0}'.format(response_ct)
            raise ODataError(msg)

    def execute_post(self, url, data):
        headers = {
            'Content-Type': 'application/json',
        }
        headers.update(self.base_headers)

        response = self._do_post(url, data=json.dumps(data), headers=headers)
        self._handle_odata_error(response)
        if response.status_code == 201:
            data = response.json()
            return data

    def execute_put(self, url, data):
        headers = {
            'Content-Type': 'application/json',
        }
        headers.update(self.base_headers)

        response = self._do_put(url, data=json.dumps(data), headers=headers)
        self._handle_odata_error(response)
        if response.status_code == 201:
            data = response.json()
            return data

    def execute_patch(self, url, data):
        headers = {
            'Content-Type': 'application/json',
        }
        headers.update(self.base_headers)

        response = self._do_patch(url, data=json.dumps(data), headers=headers)
        self._handle_odata_error(response)
        if response.status_code == 201:
            data = response.json()
            return data
