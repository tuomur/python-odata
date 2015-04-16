# -*- coding: utf-8 -*-

import unittest
import json

import responses
import requests

from odata.tests import Service, ProductWithNavigation, ProductPart


class TestNavigationObjects(unittest.TestCase):

    @responses.activate
    def test_read_navigation_property(self):
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

        responses.add_callback(
            responses.GET, ProductWithNavigation.__odata_url__(),
            callback=request_callback,
            content_type='application/json',
        )
        #######################################################################

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

        responses.add_callback(
            responses.GET, parts_url,
            callback=request_callback_parts,
            content_type='application/json',
        )
        #######################################################################

        for part in product.parts:
            assert isinstance(part, ProductPart)

    @responses.activate
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

        responses.add_callback(
            responses.GET, ProductWithNavigation.__odata_url__(),
            callback=request_callback,
            content_type='application/json',
        )
        #######################################################################

        query = Service.query(ProductWithNavigation)
        query.expand(ProductWithNavigation.parts)
        product = query.first()

        # Get parts ###########################################################
        parts_url = product.__odata__.instance_url + '/Parts'

        def request_callback_parts(request):
            assert False, 'Expanded NavigationProperty should not cause GET'

        responses.add_callback(
            responses.GET, parts_url,
            callback=request_callback_parts,
            content_type='application/json',
        )
        #######################################################################

        for part in product.parts:
            assert isinstance(part, ProductPart)

    @responses.activate
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

        responses.add_callback(
            responses.GET, ProductWithNavigation.__odata_url__(),
            callback=request_callback,
            content_type='application/json',
        )
        #######################################################################

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

        responses.add_callback(
            responses.GET, ProductPart.__odata_url__(),
            callback=request_callback_parts,
            content_type='application/json',
        )
        #######################################################################

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

        responses.add_callback(
            responses.PATCH, product.__odata__.instance_url,
            callback=request_callback_set_parts,
            content_type='application/json',
        )
        #######################################################################

        # Reload data #########################################################
        responses.add_callback(
            responses.GET, product.__odata__.instance_url,
            callback=request_callback,
            content_type='application/json',
        )
        #######################################################################

        Service.save(product)
