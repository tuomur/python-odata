# -*- coding: utf-8 -*-

from odata import ODataService
from odata.entity import declarative_base
from odata.property import StringProperty, IntegerProperty, DecimalProperty, NavigationProperty

Base = declarative_base()
url = 'http://unittest.server.local/odata/'
Service = ODataService(url, base=Base)


class Product(Base):
    id = IntegerProperty('ProductID', primary_key=True)
    name = StringProperty('ProductName')
    category = StringProperty('Category')
    price = DecimalProperty('Price')


class ProductPart(Base):
    __odata_type__ = 'ODataTest.Objects.ProductPart'
    __odata_collection__ = 'ProductParts'
    id = IntegerProperty('PartID', primary_key=True)
    name = StringProperty('PartName')
    size = DecimalProperty('Size')
    product_id = IntegerProperty('ProductID')


class ProductWithNavigation(Base):
    __odata_type__ = 'ODataTest.Objects.ProductWithNavigation'
    __odata_collection__ = 'ProductsWithNavigation'
    id = IntegerProperty('ProductID', primary_key=True)
    name = StringProperty('ProductName')
    category = StringProperty('Category')
    price = DecimalProperty('Price')


ProductPart.product = NavigationProperty('Product', ProductWithNavigation, foreign_key='ProductID')
ProductWithNavigation.parts = NavigationProperty('Parts', ProductPart, collection=True)
