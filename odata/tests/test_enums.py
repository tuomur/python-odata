# -*- coding: utf-8 -*-

from unittest import TestCase
import json

import responses
import requests

from odata.tests import Service, Product, ColorSelection


class TestEnums(TestCase):

    def test_insert_value(self):

        def request_callback(request):
            content = json.loads(request.body)
            content['ProductID'] = 1
            self.assertIn('ColorSelection', content)
            self.assertEqual(content.get('ColorSelection'), 'Black')
            headers = {}
            return requests.codes.ok, headers, json.dumps(content)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(rsps.POST,
                              Product.__odata_url__(),
                              callback=request_callback,
                              content_type='application/json')

            new_product = Product()
            new_product.name = 'Test Product'
            new_product.color_selection = ColorSelection.Black
            Service.save(new_product)

    def test_read_value(self):
        test_product_values = dict(
            ProductID=1,
            ProductName='Test Product',
            Category='',
            ColorSelection='Red',
            Price=0.0,
        )
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, Product.__odata_url__(),
                     content_type='application/json',
                     json=dict(value=[test_product_values]))

            product = Service.query(Product).get(1)

        self.assertIsInstance(product.color_selection, ColorSelection)
        self.assertEqual(product.color_selection, ColorSelection.Red)
