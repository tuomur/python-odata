# -*- coding: utf-8 -*-

import json
from decimal import Decimal
from unittest import TestCase

import requests
import responses

from odata.tests import Service, Product, Dimensions


class TestComplextype(TestCase):

    def test_insert_value(self):
        def request_callback(request):
            content = json.loads(request.body)
            content['ProductID'] = 1
            self.assertIn('Dimensions', content)
            self.assertEqual(content.get('Dimensions'), {'Height': 10.1})
            headers = {}
            return requests.codes.ok, headers, json.dumps(content)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(rsps.POST,
                              Product.__odata_url__(),
                              callback=request_callback,
                              content_type='application/json')

            new_product = Product()
            new_product.name = 'Test Product'
            new_product.dimensions = Dimensions({'Height': 10.1})
            Service.save(new_product)

    def test_read_value(self):
        expected_height = Decimal('11')
        expected_weight = u'110 kg.'
        expected_length = Decimal('8')
        test_product_values = dict(
            ProductID=1,
            ProductName='Test Product',
            Category='',
            ColorSelection='Red',
            Dimensions={'Height': float(expected_height),
                        'Weight': expected_weight,
                        'Length': float(expected_length)},
            Price=0.0,
        )
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, Product.__odata_url__(),
                     content_type='application/json',
                     json=dict(value=[test_product_values]))

            product = Service.query(Product).get(1)
        self.assertIsInstance(product.dimensions, Dimensions)
        assert product.dimensions['Height'] == expected_height
        assert product.dimensions['Weight'] == expected_weight
        assert product.dimensions['Length'] == expected_length
