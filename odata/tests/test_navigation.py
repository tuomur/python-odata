# -*- coding: utf-8 -*-

import unittest
import json

import responses
import requests

from odata.tests import Service, ProductWithNavigation, ProductPart, Manufacturer


class TestNavigationObjects(unittest.TestCase):

    def test_read_single_navigation_property(self):
        # Initial data ########################################################
        def request_callback(request):
            payload = {
                'ProductID': 51,
                'ProductName': 'Foo',
                'Category': 'Bar',
                'Price': 12.3,
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, ProductWithNavigation.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            product = Service.query(ProductWithNavigation).first()

        # Get parts ###########################################################
        parts_url = product.__odata__.instance_url + '/Manufacturer'

        def request_callback_manufacturer(request):
            payload = {
                'ManufacturerID': 33,
                'Name': 'Best Parts Ltd.',
                'DateEstablished': '2007-06-05T12:00:00Z',
            }

            resp_body = payload
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, parts_url,
                callback=request_callback_manufacturer,
                content_type='application/json',
            )
            mf = product.manufacturer

        assert isinstance(mf, Manufacturer)

    def test_read_collection_navigation_property(self):
        # Initial data ########################################################
        def request_callback(request):
            payload = {
                'ProductID': 51,
                'ProductName': 'Foo',
                'Category': 'Bar',
                'Price': 12.3,
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, ProductWithNavigation.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )
            product = Service.query(ProductWithNavigation).first()

        # Get parts ###########################################################
        parts_url = product.__odata__.instance_url + '/Parts'

        def request_callback_parts(request):
            payload = {
                'PartID': 512,
                'PartName': 'Bits and bobs',
                'Size': 5.333,
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, parts_url,
                callback=request_callback_parts,
                content_type='application/json',
            )

            for part in product.parts:
                assert isinstance(part, ProductPart)

    def test_read_expanded_navigation_property(self):
        # Initial data ########################################################
        def request_callback(request):
            payload = {
                'ProductID': 51,
                'ProductName': 'Foo',
                'Category': 'Bar',
                'Price': 12.3,
                'Parts': [
                    {
                        'PartID': 512,
                        'PartName': 'Bits and bobs',
                        'Size': 5.333,
                    }
                ]
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, ProductWithNavigation.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            query = Service.query(ProductWithNavigation)
            query.expand(ProductWithNavigation.parts)
            product = query.first()

        # Get parts ###########################################################
        for part in product.parts:
            assert isinstance(part, ProductPart)

    def test_set_navigation_property(self):
        # Initial data ########################################################
        def request_callback(request):
            payload = {
                'ProductID': 51,
                'ProductName': 'Foo',
                'Category': 'Bar',
                'Price': 12.3,
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, ProductWithNavigation.__odata_url__(),
                callback=request_callback,
                content_type='application/json',
            )

            product = Service.query(ProductWithNavigation).first()

        # Get part ############################################################
        def request_callback_parts(request):
            payload = {
                'PartID': 512,
                'PartName': 'Bits and bobs',
                'Size': 5.333,
            }

            resp_body = {'value': [payload]}
            headers = {}
            return requests.codes.ok, headers, json.dumps(resp_body)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.GET, ProductPart.__odata_url__(),
                callback=request_callback_parts,
                content_type='application/json',
            )
            part = Service.query(ProductPart).first()

        product.parts = [part]

        # Patch call ##########################################################
        def request_callback_set_parts(request):
            payload = json.loads(request.body)

            key = 'Parts@odata.bind'
            assert key in payload
            assert payload.get(key) == ['ProductParts(512)']

            headers = {}
            return requests.codes.no_content, headers, ''

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.PATCH, product.__odata__.instance_url,
                callback=request_callback_set_parts,
                content_type='application/json',
            )

            # Reload data #####################################################
            rsps.add_callback(
                rsps.GET, product.__odata__.instance_url,
                callback=request_callback,
                content_type='application/json',
            )

            Service.save(product)
