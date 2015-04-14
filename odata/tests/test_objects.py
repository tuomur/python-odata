# -*- coding: utf-8 -*-

import unittest
import json
from decimal import Decimal

import responses
import requests

from odata.tests import Service, Product


class TestSimpleObjectManipulation(unittest.TestCase):

    @responses.activate
    def test_create(self):
        # Post call ###########################################################
        def request_callback(request):
            payload = json.loads(request.body)

            assert 'OData-Version' in request.headers, 'OData-Version header not in request'

            assert 'ProductID' not in payload, 'Payload contains primary key'
            assert '@odata.type' in payload, 'Payload did not contain @odata.type'

            payload['ProductID'] = 1

            resp_body = payload
            headers = {}
            return requests.codes.created, headers, json.dumps(resp_body)

        responses.add_callback(
            responses.POST, Product.__odata_url__(),
            callback=request_callback,
            content_type='application/json',
        )
        #######################################################################

        new_product = Product()
        new_product.name = u'New Test Product'
        new_product.category = u'Category #1'
        new_product.price = 34.5

        Service.save(new_product)

        assert new_product.id is not None, 'Product.id is not set'

    @responses.activate
    def test_read(self):
        expected_id = 1024
        expected_name = 'Existing entity'
        expected_category = 'Existing category'
        expected_price = Decimal('85.2')

        # Initial data ########################################################
        def request_callback(request):
            payload = {
                'ProductID': expected_id,
                'ProductName': expected_name,
                'Category': expected_category,
                'Price': float(expected_price),
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        responses.add_callback(
            responses.GET, Product.__odata_url__(),
            callback=request_callback,
            content_type='application/json',
        )
        #######################################################################

        product = Service.query(Product).first()
        assert product.id == expected_id
        assert product.name == expected_name
        assert product.category == expected_category
        assert product.price == expected_price

    @responses.activate
    def test_update(self):
        expected_id = 1024
        expected_name = 'Existing entity'
        expected_category = 'Existing category'
        expected_price = Decimal('85.2')

        # Initial data ########################################################
        def request_callback(request):
            payload = {
                'ProductID': expected_id,
                'ProductName': expected_name,
                'Category': expected_category,
                'Price': float(expected_price),
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        responses.add_callback(
            responses.GET, Product.__odata_url__(),
            callback=request_callback,
            content_type='application/json',
        )
        #######################################################################

        product = Service.query(Product).first()
        new_name = 'Changed value'

        # Patch call ##########################################################
        def request_callback_patch(request):
            payload = json.loads(request.body)
            assert 'ProductName' in payload
            assert payload['ProductName'] == new_name
            headers = {}
            return requests.codes.no_content, headers, ''

        responses.add_callback(
            responses.PATCH, product.__odata__.instance_url,
            callback=request_callback_patch,
            content_type='application/json',
        )
        #######################################################################

        # Reload call #########################################################
        def request_callback_reload(request):
            payload = {
                'ProductID': expected_id,
                'ProductName': new_name,
                'Category': expected_category,
                'Price': float(expected_price),
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        responses.add_callback(
            responses.GET, product.__odata__.instance_url,
            callback=request_callback_reload,
            content_type='application/json',
        )
        #######################################################################

        product.name = new_name
        Service.save(product)

        assert product.name == new_name

    @responses.activate
    def test_delete(self):
        # Initial data ########################################################
        def request_callback(request):
            payload = {
                'ProductID': 2048,
                'ProductName': 'This product will be deleted',
                'Category': 'Something',
                'Price': 1234.5,
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        responses.add_callback(
            responses.GET, Product.__odata_url__(),
            callback=request_callback,
            content_type='application/json',
        )
        #######################################################################

        product = Service.query(Product).first()

        # Delete call #########################################################
        def request_callback_delete(request):
            headers = {}
            return requests.codes.ok, headers, ''

        responses.add_callback(
            responses.DELETE, product.__odata__.instance_url,
            callback=request_callback_delete,
            content_type='application/json',
        )
        #######################################################################

        Service.delete(product)
