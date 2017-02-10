# -*- coding: utf-8 -*-

import unittest
import json
import decimal

import responses
import requests

from odata.tests import Product, Service, DemoUnboundAction


class TestActions(unittest.TestCase):

    def test_call_bound_action_empty_result(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.POST, Product.__odata_url__() + '/ODataTest.DemoCollectionAction',
            )
            result = Product.DemoCollectionAction()
        self.assertIsNone(result)

    def test_call_bound_action_on_instance(self):
        test_product = Product()
        test_product.name = 'TestProduct'
        test_product.id = 1234
        test_product.price = decimal.Decimal('20.0')

        # shortcut for saving the entity
        test_product.__odata__.persisted = True

        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.POST, test_product.__odata__.instance_url + '/ODataTest.DemoAction',
            )
            result = test_product.DemoAction()
        self.assertIsNone(result)

    def test_call_instance_bound_action_on_collection(self):
        def _call():
            Product.DemoAction()
        self.assertRaises(AttributeError, _call)

    def test_call_bound_action_with_result(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.POST, Product.__odata_url__() + '/ODataTest.DemoCollectionAction',
                content_type='application/json',
                json=dict(value='test'),
            )
            result = Product.DemoCollectionAction()
        self.assertEqual(result, 'test')

    def test_call_unbound_action_with_result(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.POST, Service.url + 'ODataTest.DemoUnboundAction',
                content_type='application/json',
                json=dict(value='test'),
            )
            result = DemoUnboundAction()
        self.assertEqual(result, 'test')


class TestActionsWithParameters(unittest.TestCase):

    def test_call_action_with_result(self):
        def request_callback(request):
            payload = json.loads(request.body)
            expected = dict(Name='TestName', Price=decimal.Decimal('10.0'))

            self.assertDictEqual(payload, expected)

            headers = {}
            body = dict(value='ok')
            return requests.codes.ok, headers, json.dumps(body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.POST, Product.__odata_url__() + '/ODataTest.DemoActionParameters',
                callback=request_callback, content_type='application/json',
            )
            result = Product.DemoActionWithParameters(Name='TestName', Price=decimal.Decimal('10.0'))
        self.assertEqual(result, 'ok')


class TestFunctions(unittest.TestCase):

    def test_call_function_empty_result(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.GET, Product.__odata_url__() + '/ODataTest.DemoFunction()',
                content_type='application/json', status=requests.codes.no_content
            )
            result = Product.DemoFunction()
        self.assertIsNone(result)

    def test_collection_bound_function_on_instance(self):
        test_product = Product()

        def _call():
            test_product.DemoFunction()

        self.assertRaises(AttributeError, _call)

    def test_call_function_with_result_query(self):
        def request_callback(request):
            self.assertTrue('filter=ProductName+eq+%27testtest%27' in request.url)

            headers = {}
            body = dict(value='ok')
            return requests.codes.ok, headers, json.dumps(body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, Product.__odata_url__() + '/ODataTest.DemoFunction()',
                request_callback, content_type='application/json')

            query = Service.query(Product)
            query = query.filter(Product.name == 'testtest')
            Product.DemoFunction.with_query(query)()
