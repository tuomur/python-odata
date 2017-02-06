# -*- coding: utf-8 -*-

from odata import ODataService
from odata.property import StringProperty, IntegerProperty, DecimalProperty, \
    NavigationProperty, DatetimeProperty
from odata.enumtype import EnumType, EnumTypeProperty

url = 'http://unittest.server.local/odata/'
Service = ODataService(url)


class DemoActionWithParameters(Service.Action):
    name = 'ODataTest.DemoActionParameters'
    parameters = dict(
        Name=StringProperty,
        Price=DecimalProperty,
    )
    bound_to_collection = True


class DemoAction(Service.Action):
    name = 'ODataTest.DemoAction'
    parameters = {}


class DemoCollectionAction(Service.Action):
    name = 'ODataTest.DemoCollectionAction'
    parameters = {}
    bound_to_collection = True


class _DemoUnboundAction(Service.Action):
    name = 'ODataTest.DemoUnboundAction'
    parameters = {}

DemoUnboundAction = _DemoUnboundAction()


class DemoFunction(Service.Function):
    name = 'ODataTest.DemoFunction'
    parameters = {}
    bound_to_collection = True


class ColorSelection(EnumType):
    Black = 0
    Red = 1
    Blue = 2
    Green = 3


class Product(Service.Entity):
    __odata_type__ = 'ODataTest.Objects.Product'
    __odata_collection__ = 'ProductParts'

    id = IntegerProperty('ProductID', primary_key=True)
    name = StringProperty('ProductName')
    category = StringProperty('Category')
    price = DecimalProperty('Price')
    color_selection = EnumTypeProperty('ColorSelection',
                                       enum_class=ColorSelection)

    DemoAction = DemoAction()
    DemoCollectionAction = DemoCollectionAction()
    DemoActionWithParameters = DemoActionWithParameters()
    DemoFunction = DemoFunction()


class ProductPart(Service.Entity):
    __odata_type__ = 'ODataTest.Objects.ProductPart'
    __odata_collection__ = 'ProductParts'
    id = IntegerProperty('PartID', primary_key=True)
    name = StringProperty('PartName')
    size = DecimalProperty('Size')
    product_id = IntegerProperty('ProductID')


class Manufacturer(Service.Entity):
    __odata_type__ = 'ODataTest.Objects.Manufacturer'
    __odata_collection__ = 'Manufacturers'

    id = IntegerProperty('ManufacturerID', primary_key=True)
    name = StringProperty('Name')
    established_date = DatetimeProperty('DateEstablished')


class ProductWithNavigation(Product):
    __odata_type__ = 'ODataTest.Objects.ProductWithNavigation'
    __odata_collection__ = 'ProductsWithNavigation'

    manufacturer_id = IntegerProperty('ManufacturerID')

    manufacturer = NavigationProperty('Manufacturer', Manufacturer, foreign_key=manufacturer_id)
    parts = NavigationProperty('Parts', ProductPart, collection=True)

ProductPart.product = NavigationProperty('Product', ProductWithNavigation, foreign_key=ProductPart.product_id)


class ProductManufacturerSales(Service.Entity):
    __odata_type__ = 'ODataTest.Objects.ProductManufacturerSales'
    __odata_collection__ = 'Product_Manufacturer_Sales'

    product_id = IntegerProperty('ProductID', primary_key=True)
    manufacturer_id = IntegerProperty('ManufacturerID', primary_key=True)
    sales_amount = DecimalProperty('SalesAmount')
