# -*- coding: utf-8 -*-

from decimal import Decimal
from unittest import TestCase
import json

import requests
import responses

from odata.tests import Service, ProductManufacturerSales


class TestCompositeKeys(TestCase):

    def test_insert_entity(self):
        def request_callback(request):
            content = json.loads(request.body)
            self.assertIn('ProductID', content)
            self.assertIn('ManufacturerID', content)
            self.assertIsNotNone(content.get('ProductID'),
                                 msg='ProductID received as None')
            self.assertIsNotNone(content.get('ManufacturerID'),
                                 msg='ManufacturerID received as None')

            headers = {}
            return requests.codes.ok, headers, json.dumps(content)

        with responses.RequestsMock() as rsps:
            rsps.add_callback(rsps.POST,
                              ProductManufacturerSales.__odata_url__(),
                              callback=request_callback,
                              content_type='application/json')

            pm_sales = ProductManufacturerSales()
            pm_sales.product_id = 1
            pm_sales.manufacturer_id = 2
            pm_sales.sales_amount = Decimal('3.0')
            Service.save(pm_sales)

    def test_update_entity(self):
        test_pm_sales_value = dict(
            ProductID=1,
            ManufacturerID=2,
            SalesAmount=23.0
        )

        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, ProductManufacturerSales.__odata_url__(),
                     content_type='application/json',
                     json=dict(value=[test_pm_sales_value]))

            query = Service.query(ProductManufacturerSales)
            query = query.filter(ProductManufacturerSales.product_id == 1)
            query = query.filter(ProductManufacturerSales.manufacturer_id == 2)
            pm_sales = query.first()  # type: ProductManufacturerSales

            sales_id = pm_sales.__odata__.id
            self.assertIn('ProductID=1', sales_id)
            self.assertIn('ManufacturerID=2', sales_id)

            rsps.add(rsps.PATCH, pm_sales.__odata__.instance_url,
                     content_type='application/json')
            rsps.add(rsps.GET, pm_sales.__odata__.instance_url,
                     content_type='application/json',
                     json=dict(value=[test_pm_sales_value]))

            pm_sales.sales_amount = Decimal('50.0')
            Service.save(pm_sales)
