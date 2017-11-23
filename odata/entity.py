# -*- coding: utf-8 -*-

"""
Entity classes
==============

The data model can be created manually if you wish to use separate property
names from the data keys, or define custom methods for your objects.

Custom Entity class
-------------------

Each Service instance has their separate base classes for Entities,
Actions and Functions. Use them to define your model:

.. code-block:: python

    class Product(Service.Entity):
        __odata_type__ = 'ProductDataService.Objects.Product'
        __odata_collection__ = 'Products'

        name = StringProperty('ProductName')
        quantity_in_storage = IntegerProperty('QuantityInStorage')

Note that the type (EntityType) and collection (EntitySet) must be defined.
These are used in querying and saving data.


Custom base class
-----------------

Define a base. These properties and methods are shared by all objects in the endpoint.

.. code-block:: python

    from odata.entity import declarative_base
    from odata.property import IntegerProperty, StringProperty, DatetimeProperty

    class MyBase(declaractive_base()):
        id = IntegerProperty('Id', primary_key=True)
        created_date = DatetimeProperty('Created')
        modified_date = DatetimeProperty('Modified')

        def did_somebody_touch_this(self):
            return self.created_date != self.modified_date

Define a model:

.. code-block:: python

    class Product(MyBase):
        __odata_type__ = 'ProductDataService.Objects.Product'
        __odata_collection__ = 'Products'

        name = StringProperty('ProductName')
        quantity_in_storage = IntegerProperty('QuantityInStorage')

        def is_product_available(self):
            return self.quantity_in_storage > 0


Use the base to init :py:class:`~odata.service.ODataService`:

.. code-block:: python

    Service = ODataService(url, base=MyBase)

Unlike reflection, this does not require any network connections. Now you can
use the Product class to create new objects or query existing ones:

.. code-block:: python

    query = Service.query(Product)
    query = query.filter(Product.name.startswith('Kettle'))
    for product in query:
        print(product.name, product.is_product_available())
"""

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin

from odata.state import EntityState


class EntityBase(object):
    __odata_service__ = None
    __odata_collection__ = None
    __odata_type__ = 'ODataSchema.Entity'
    __odata_singleton__ = False
    __odata_schema__ = None

    @classmethod
    def __odata_url__(cls):
        # used by Query
        if cls.__odata_collection__:
            return urljoin(cls.__odata_service__.url, cls.__odata_collection__)

    def __new__(cls, *args, **kwargs):
        i = super(EntityBase, cls).__new__(cls)
        i.__odata__ = es = EntityState(i)

        if 'from_data' in kwargs:
            raw_data = kwargs.pop('from_data')

            # check for values from $expand
            for prop_name, prop in es.navigation_properties:
                if prop.name in raw_data:
                    expanded_data = raw_data.pop(prop.name)
                    if prop.is_collection:
                        es.nav_cache[prop.name] = dict(collection=prop.instances_from_data(expanded_data))
                    else:
                        es.nav_cache[prop.name] = dict(single=prop.instances_from_data(expanded_data))

            for prop_name, prop in es.properties:
                i.__odata__[prop.name] = raw_data.get(prop.name)

            i.__odata__.persisted = True
        else:
            for prop_name, prop in es.properties:
                i.__odata__[prop.name] = None

        return i

    def __repr__(self):
        clsname = self.__class__.__name__
        display_string = self.__odata__.id or clsname
        return '<Entity({0})>'.format(display_string)

    def __eq__(self, other):
        if isinstance(other, EntityBase):
            my_id = self.__odata__.id
            if my_id:
                return my_id == other.__odata__.id
        return False


def declarative_base():
    return type('Entity', (EntityBase,), dict())
