# -*- coding: utf-8 -*-

from odata import ODataService
from odata.entity import declarative_base
from odata.property import StringProperty, IntegerProperty, DecimalProperty

Base = declarative_base()
url = 'http://unittest.server.local/odata/'
Service = ODataService(url, base=Base)


class Product(Base):
    id = IntegerProperty('ProductID', primary_key=True)
    name = StringProperty('ProductName')
    category = StringProperty('Category')
    price = DecimalProperty('Price')
