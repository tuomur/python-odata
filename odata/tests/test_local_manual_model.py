# -*- coding: utf-8 -*-

import os
from decimal import Decimal
import unittest

from odata.service import ODataService
from odata.entity import declarative_base
from odata.property import StringProperty, IntegerProperty, DecimalProperty

service_url = os.environ.get('ODATA_LOCALHOST_SERVICE')

if service_url:
    LocalBase = declarative_base()
    ReadWriteService = ODataService(service_url, LocalBase)

    class LocalProduct(LocalBase):
        __odata_collection__ = 'Products'
        __odata_type__ = 'WebApplication2.Models.Product'

        id = IntegerProperty('Id', primary_key=True)
        name = StringProperty('Name')
        price = DecimalProperty('Price')
        category = StringProperty('Category')


@unittest.skipIf(service_url is None, 'Local OData endpoint not configured')
class ReadWriteManualModelTest(unittest.TestCase):

    def test_1_insert_new(self):
        n = LocalProduct()
        n.name = 'testing'
        n.price = Decimal('12.3')
        n.category = 'testing category'

        ReadWriteService.save(n)

        assert n.id is not None, 'creating new object did not receive updated data from server'

    def test_2_update_existing(self):
        q = ReadWriteService.query(LocalProduct)
        n = q.first()

        value = 'something else'
        n.name = value
        ReadWriteService.save(n)

        assert n.name == 'something else', 'name was not changed'

    def test_3_delete(self):
        q = ReadWriteService.query(LocalProduct)
        q.order_by(LocalProduct.id.desc())
        last = q.first()
        last_id = last.id

        ReadWriteService.delete(last)

        q = ReadWriteService.query(LocalProduct)
        q.filter(LocalProduct.id == last_id)
        notexisting = q.first()
        assert notexisting is None, 'object was not properly deleted'
