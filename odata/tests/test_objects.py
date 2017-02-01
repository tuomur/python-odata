# -*- coding: utf-8 -*-

import unittest
import json
from decimal import Decimal

import responses
import requests

from odata.tests import Service, Product, ProductWithNavigation, ProductPart


class TestSimpleObjectManipulation(unittest.TestCase):

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

        new_product = Product()
        new_product.name = u'New Test Product'
        new_product.category = u'Category #1'
        new_product.price = 34.5

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.POST, Product.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            Service.save(new_product)

        assert new_product.id is not None, 'Product.id is not set'

    def test_create_with_primary_key(self):
        # Post call ###########################################################
        def request_callback(request):
            payload = json.loads(request.body)
            self.assertEqual(payload.get('ProductID'), 55,
                             msg='Did not receive ProductID')
            resp_body = payload
            headers = {}
            return requests.codes.created, headers, json.dumps(resp_body)

        new_product = Product()
        new_product.id = 55
        new_product.name = u'New Test Product'
        new_product.category = u'Category #1'
        new_product.price = 34.5

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.POST, Product.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            Service.save(new_product)

        assert new_product.id is not None, 'Product.id is not set'

    def test_create_deep_inserts(self):
        # Initial part data ###################################################
        def request_callback_part(request):

            payload = {
                'PartID': 35,
                'PartName': 'Testing',
                'Size': 55,
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.created, headers, json.dumps(resp_body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, ProductPart.__odata_url__(),
                callback=request_callback_part,
                content_type='application/json',
            )

            queried_part = Service.query(ProductPart).first()

        # Post call ###########################################################
        def request_callback(request):
            payload = json.loads(request.body)

            assert 'OData-Version' in request.headers, 'OData-Version header not in request'

            assert 'ProductID' not in payload, 'Payload contains primary key'
            assert '@odata.type' in payload, 'Payload did not contain @odata.type'

            assert 'Parts@odata.bind' in payload, 'Parts bind not in payload'
            assert payload['Parts@odata.bind'] == ['ProductParts(35)']

            assert 'Parts' in payload, 'Parts not in payload'
            parts = payload['Parts']
            assert isinstance(parts, list), 'Parts is not a list'
            part = parts[0]
            assert len(part) == 3, 'Extra keys in deep inserted part: {0}'.format(part)
            assert '@odata.type' in part
            assert part['PartName'] == 'Foo'
            assert part['Size'] == 12.5

            payload['ProductID'] = 1

            resp_body = payload
            headers = {}
            return requests.codes.created, headers, json.dumps(resp_body)

        part = ProductPart()
        part.name = 'Foo'
        part.size = 12.5

        new_product = ProductWithNavigation()
        new_product.name = u'New Test Product'
        new_product.category = u'Category #1'
        new_product.price = 34.5
        new_product.parts = [part, queried_part]

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.POST, ProductWithNavigation.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            Service.save(new_product)

        assert new_product.id is not None, 'Product.id is not set'

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

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, Product.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            product = Service.query(Product).first()

        assert product.id == expected_id
        assert product.name == expected_name
        assert product.category == expected_category
        assert product.price == expected_price

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

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, Product.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            product = Service.query(Product).first()

        new_name = 'Changed value'

        # Patch call ##########################################################
        def request_callback_patch(request):
            payload = json.loads(request.body)
            assert 'ProductName' in payload
            assert payload['ProductName'] == new_name
            headers = {}
            return requests.codes.no_content, headers, ''

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

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.PATCH, product.__odata__.instance_url,
                callback=request_callback_patch,
                content_type='application/json',
            )
            rsps.add_callback(
                rsps.GET, product.__odata__.instance_url,
                callback=request_callback_reload,
                content_type='application/json',
            )

            product.name = new_name
            Service.save(product)

        assert product.name == new_name

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

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, Product.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            product = Service.query(Product).first()

        # Delete call #########################################################
        def request_callback_delete(request):
            headers = {}
            return requests.codes.ok, headers, ''

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.DELETE, product.__odata__.instance_url,
                callback=request_callback_delete,
                content_type='application/json',
            )

            Service.delete(product)
