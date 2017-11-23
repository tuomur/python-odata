# -*- coding: utf-8 -*-

import os
from unittest import TestCase
import json

import requests
import responses

from odata import ODataService
from odata.entity import EntityBase

path = os.path.join(os.path.dirname(__file__), 'demo_metadata.xml')
with open(path, mode='rb') as f:
    metadata_xml = f.read()


class TestMetadataImport(TestCase):

    def test_read(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, 'http://demo.local/odata/$metadata/',
                     body=metadata_xml, content_type='text/xml')
            Service = ODataService('http://demo.local/odata/', reflect_entities=True)

        self.assertIn('Products', Service.entities)

        # non-entityset things should not be listed in entities
        expected_keys = {'Products', 'ProductsWithNavigation', 'Manufacturers',
                         'Product_Manufacturer_Sales'}
        self.assertEqual(set(Service.entities.keys()), expected_keys)

        Product = Service.entities['Products']
        ProductWithNavigation = Service.entities['ProductsWithNavigation']

        assert issubclass(Product, EntityBase)
        assert hasattr(Product, 'DemoCollectionAction')

        test_product = Product()
        # shortcut for saving the entity
        test_product.__odata__.persisted = True
        assert hasattr(test_product, 'DemoActionWithParameters')
        assert hasattr(ProductWithNavigation, 'Manufacturer')
        self.assertIn('Manufacturers', Service.entities)

        self.assertIn('DemoUnboundAction', Service.actions)

    def test_computed_value_in_insert(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, 'http://demo.local/odata/$metadata/',
                     body=metadata_xml, content_type='text/xml')
            Service = ODataService('http://demo.local/odata/', reflect_entities=True)

        Product = Service.entities['Products']
        test_product = Product()

        def request_callback_part(request):
            payload = json.loads(request.body)
            self.assertNotIn('ExampleComputed', payload)
            headers = {}
            return requests.codes.created, headers, json.dumps(payload)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(
                rsps.POST, Product.__odata_url__(),
                callback=request_callback_part,
                content_type='application/json',
            )
            Service.save(test_product)
