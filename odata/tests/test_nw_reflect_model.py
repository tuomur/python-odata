# -*- coding: utf-8 -*-

import unittest

from odata.service import ODataService


url = 'http://services.odata.org/V4/Northwind/Northwind.svc/'
Service = ODataService(url, reflect_entities=True)
Customer = Service.entities.get('Customers')
Product = Service.entities.get('Products')


@unittest.skip('unavailable')
class NorthwindReflectModelReadTest(unittest.TestCase):

    def test_query_one(self):
        q = Service.query(Customer)
        q = q.filter(Customer.ContactTitle.startswith('Sales'))
        q = q.filter(Customer.PostalCode == '68306')
        data = q.first()
        assert data is not None, 'data is None'
        assert isinstance(data, Customer), 'Did not return Customer instance'
        assert data.PostalCode == '68306'

    def test_query_all(self):
        q = Service.query(Customer)
        q = q.filter(Customer.City != 'Berlin')
        q = q.limit(30)
        q = q.order_by(Customer.City.asc())
        data = q.all()
        assert data is not None, 'data is None'
        assert len(data) > 20, 'data length wrong'

    def test_iterating_query_result(self):
        q = Service.query(Customer)
        q = q.limit(20)
        for result in q:
            assert isinstance(result, Customer), 'Did not return Customer instance'

    def test_query_raw_data(self):
        q = Service.query(Customer)
        q = q.select(Customer.CompanyName)
        data = q.first()
        assert isinstance(data, dict), 'Did not return dict'
        assert Customer.CompanyName.name in data

    def test_query_filters(self):
        q = Service.query(Product)

        q = q.filter(
            q.or_(
                q.grouped(
                    q.or_(
                        Product.ProductName.startswith('Chai'),
                        Product.ProductName.startswith('Chang'),
                    )
                ),
                Product.QuantityPerUnit == '12 - 550 ml bottles',
            )
        )

        data = q.all()
        assert len(data) == 3, 'data length wrong'
