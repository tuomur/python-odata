# -*- coding: utf-8 -*-

import unittest

from odata.service import ODataService


url = 'http://services.odata.org/TripPinRESTierService/'
Service = ODataService(url, reflect_entities=True)
Person = Service.entities.get('Person')
Product = Service.entities.get('Product')


class TripPinReflectModelReadTest(unittest.TestCase):

    def test_query_single(self):
        s = Service.querySingle(Person)
        data = s.get()
        assert data is not None, 'data is None'
        assert isinstance(data, Person), 'Did not return Person instance'
        assert data.UserName == 'aprilcline'

    def test_query_raw_data(self):
        q = Service.querySingle(Person)
        q = q.select(Person.UserName)
        data = q.get()
        assert isinstance(data, dict), 'Did not return dict'
        assert Person.UserName.name in data
    