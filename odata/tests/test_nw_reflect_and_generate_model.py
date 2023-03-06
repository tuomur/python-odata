# -*- coding: utf-8 -*-

import unittest

import requests

from odata.service import ODataService
from odata.tests.generated.northwind import ReflectionBase, Customers, Products

proxy = {'http': '', 'https': ''}

session = requests.Session()

session.trust_env = False
session.verify = False
session.proxies.update(proxy)

NorthwindService = ODataService('http://services.odata.org/V4/Northwind/Northwind.svc/', base=ReflectionBase, reflect_entities=True, reflect_output_package="generated.northwind", session=session, quiet_progress=True)
service = NorthwindService


class NorthwindAutomaticModelModelWithGenerationReadTest(unittest.TestCase):
    def test_query_one(self):
        q = service.query(Customers)
        q = q.filter(Customers.ContactTitle.startswith('Sales'))
        q = q.filter(Customers.PostalCode == '68306')
        data = q.first()
        assert data is not None, 'data is None'
        assert isinstance(data, Customers), 'Did not return Customer instance'
        assert data.PostalCode == '68306'

    def test_query_all(self):
        q = service.query(Customers)
        q = q.filter(Customers.City != 'Berlin')
        q = q.limit(30)
        q = q.order_by(Customers.City.asc())
        data = q.all()
        assert data is not None, 'data is None'
        assert len(data) > 20, 'data length wrong'

    def test_iterating_query_result(self):
        q = service.query(Customers)
        limit = 20
        q = q.limit(limit)
        count = 0
        for result in q:
            count += 1
            assert isinstance(result, Customers), 'Did not return Customer instance'
        assert count == limit, f"Did not return {limit} elements"

    def test_query_raw_data(self):
        q = service.query(Customers)
        q = q.select(Customers.CompanyName)
        data = q.first()
        assert Customers.CompanyName.name in data

    def test_query_filters(self):
        q = service.query(Products)

        q = q.filter(
            q.or_(
                q.grouped(
                    q.or_(
                        Products.ProductName.startswith('Chai'),
                        Products.ProductName.startswith('Chang'),
                    )
                ),
                Products.QuantityPerUnit == '12 - 550 ml bottles',
            )
        )

        data = q.all()
        assert len(data) == 3, 'data length wrong'
