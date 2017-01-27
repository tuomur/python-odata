# -*- coding: utf-8 -*-

import unittest
import json

import requests
import responses

from odata.exceptions import ODataError
from odata.tests import Service, Product


class TestODataError(unittest.TestCase):

    def test_parse_error_json(self):
        expected_code = '0451'
        expected_message = 'Testing error message handling'
        expected_innererror_message = 'Detailed messages here'

        # Initial data ########################################################
        def request_callback(request):
            resp_body = {'error': {
                'code': expected_code,
                'message': expected_message,
                'innererror': {
                    'message': expected_innererror_message
                }
            }}
            headers = {
                'Content-Type': 'application/json;odata.metadata=minimal'
            }
            return requests.codes.bad_request, headers, json.dumps(resp_body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, Product.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            def action():
                try:
                    Service.query(Product).first()
                except ODataError as e:
                    errmsg = str(e)
                    assert expected_code in errmsg, 'Code not in text'
                    assert expected_message in errmsg, 'Upper level message not in text'
                    assert expected_innererror_message in errmsg, 'Detailed message not in text'
                    raise

            self.assertRaises(ODataError, action)
