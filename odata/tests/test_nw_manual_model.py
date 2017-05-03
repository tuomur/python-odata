# -*- coding: utf-8 -*-

import unittest

from odata.service import ODataService
from odata.entity import declarative_base
from odata.property import StringProperty, IntegerProperty


Base = declarative_base()

NorthwindService = ODataService('http://services.odata.org/V4/Northwind/Northwind.svc/', Base)
service = NorthwindService


class Customer(Base):
    __odata_collection__ = 'Customers'
    __odata_type__ = 'NorthwindModel.Customer'

    id = StringProperty('CustomerID', primary_key=True)
    name = StringProperty('CompanyName')
    contact_name = StringProperty('ContactName')
    contact_title = StringProperty('ContactTitle')
    address = StringProperty('Address')
    city = StringProperty('City')
    region = StringProperty('Region')
    postal_code = StringProperty('PostalCode')
    country = StringProperty('Country')
    phone = StringProperty('Phone')
    fax = StringProperty('Fax')


class Product(Base):
    __odata_collection__ = 'Products'
    __odata_type__ = 'NorthwindModel.Product'

    id = IntegerProperty('ProductID', primary_key=True)
    name = StringProperty('ProductName')
    supplier_id = IntegerProperty('SupplierID')
    category_id = IntegerProperty('CategoryID')
    quantity_per_unit = StringProperty('QuantityPerUnit')


@unittest.skip('unavailable')
class NorthwindManualModelReadTest(unittest.TestCase):

    def test_query_one(self):
        q = service.query(Customer)
        q = q.filter(Customer.contact_title.startswith('Sales'))
        q = q.filter(Customer.postal_code == '68306')
        data = q.first()
        assert data is not None, 'data is None'
        assert isinstance(data, Customer), 'Did not return Customer instance'
        assert data.postal_code == '68306'

    def test_query_all(self):
        q = service.query(Customer)
        q = q.filter(Customer.city != 'Berlin')
        q = q.limit(30)
        q = q.order_by(Customer.city.asc())
        data = q.all()
        assert data is not None, 'data is None'
        assert len(data) > 20, 'data length wrong'

    def test_iterating_query_result(self):
        q = service.query(Customer)
        q = q.limit(20)
        for result in q:
            assert isinstance(result, Customer), 'Did not return Customer instance'

    def test_query_raw_data(self):
        q = service.query(Customer)
        q = q.select(Customer.name)
        data = q.first()
        assert isinstance(data, dict), 'Did not return dict'
        assert Customer.name.name in data

    def test_query_filters(self):
        q = service.query(Product)

        q = q.filter(
            q.or_(
                q.grouped(
                    q.or_(
                        Product.name.startswith('Chai'),
                        Product.name.startswith('Chang'),
                    )
                ),
                Product.quantity_per_unit == '12 - 550 ml bottles',
            )
        )

        data = q.all()
        assert len(data) == 3, 'data length wrong'
