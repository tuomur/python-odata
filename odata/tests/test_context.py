# -*- coding: utf-8 -*-

import json
import base64
import decimal
from unittest import TestCase

import requests
import responses

from odata.tests import Service, Product, DemoUnboundAction


class TestContext(TestCase):

    def test_context_query_without_auth(self):
        def request_callback(request):
            self.assertIsNone(request.headers.get('Authorization'))
            headers = {}
            body = dict(value=[])
            return requests.codes.ok, headers, json.dumps(body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(rsps.GET, Product.__odata_url__(),
                              callback=request_callback,
                              content_type='application/json')

            context = Service.create_context()
            context.query(Product).first()

    def test_context_query_with_basic_auth(self):
        test_username = 'username'
        test_password = 'password'
        test_auth = (test_username, test_password)

        def request_callback(request):
            auth_text = request.headers.get('Authorization')
            _, auth_b64 = auth_text.split(' ', 1)
            decoded = base64.urlsafe_b64decode(auth_b64.encode()).decode()
            username, password = decoded.split(':', 1)

            self.assertEqual(test_username, username)
            self.assertEqual(test_password, password)

            headers = {}
            body = dict(value=[])
            return requests.codes.ok, headers, json.dumps(body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(rsps.GET, Product.__odata_url__(), request_callback,
                              content_type='application/json')

            context = Service.create_context(auth=test_auth)
            context.query(Product).first()

    def test_context_call_unbound_action(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, Service.url + 'ODataTest.DemoUnboundAction')

            context = Service.create_context()
            context.call(DemoUnboundAction)

    def test_context_call_bound_action(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, Product.__odata_url__() + '/ODataTest.DemoActionParameters')

            context = Service.create_context()
            context.call(Product.DemoActionWithParameters,
                         Name='TestName',
                         Price=decimal.Decimal('25.0'))
