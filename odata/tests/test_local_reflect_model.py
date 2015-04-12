# -*- coding: utf-8 -*-

import os
from decimal import Decimal
import unittest

from odata.service import ODataService
from odata.entity import declarative_base
from odata.property import StringProperty, IntegerProperty, DecimalProperty

service_url = os.environ.get('ODATA_LOCALHOST_SERVICE')

if service_url:
    ReadWriteService = ODataService(service_url, reflect_entities=True)
    LocalProduct = ReadWriteService.entities.get('Product')


@unittest.skipIf(service_url is None, 'Local OData endpoint not configured')
class ReadWriteReflectModelTest(unittest.TestCase):

    def test_1_insert_new(self):
        n = LocalProduct()
        n.Name = 'testing'
        n.Price = Decimal('12.3')
        n.Category = 'testing category'

        ReadWriteService.save(n)

        assert n.Id is not None, 'creating new object did not receive updated data from server'

    def test_2_update_existing(self):
        q = ReadWriteService.query(LocalProduct)
        n = q.first()

        value = 'something else'
        n.Name = value
        ReadWriteService.save(n)

        assert n.Name == 'something else', 'name was not changed'

    def test_3_delete(self):
        q = ReadWriteService.query(LocalProduct)
        q.order_by(LocalProduct.Id.desc())
        last = q.first()
        last_id = last.Id

        ReadWriteService.delete(last)

        q = ReadWriteService.query(LocalProduct)
        q.filter(LocalProduct.Id == last_id)
        notexisting = q.first()
        assert notexisting is None, 'object was not properly deleted'
