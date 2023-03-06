# -*- coding: utf-8 -*-

"""
Navigation properties
---------------------

The entity can define properties that link to other entities. These are known
as navigation properties and are supported in this library.

.. code-block:: python

    >>> order = Service.query(Order).first()
    >>> order.Shipper
    <Entity(Shipper:3)>
    >>> order.Shipper.CompanyName
    'Federal Shipping'

When creating new instances, relationships can be assigned via navigation
properties:

.. code-block:: python

    # query a shipper instance, just for this example
    Shipper = Service.entities['Shipper']
    my_shipper = Service.query(Shipper).first()

    # assign for the new Order
    order.Shipper = my_shipper
    Service.save(order)
"""
import copy
import importlib
from typing import Union

from odata.exceptions import ODataReflectionError

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin


class NavigationProperty(object):
    """
    A Property-like object for marking relationships between entities, but does
    not inherit from PropertyBase.
    """
    def __init__(self, name, entitycls: Union[type, str], entity_package: str = None, collection=False, foreign_key=None):
        from odata.property import PropertyBase
        self.name = name
        self.class_package = entity_package
        self.entityclass = entitycls
        self.is_collection = collection
        if isinstance(foreign_key, PropertyBase):
            self.foreign_key = foreign_key.name
        else:
            self.foreign_key = foreign_key

    def __repr__(self):
        return u'<NavigationProperty to {0}>'.format(self.entitycls)

    def __populate_entity(self, data, connection, parent_navigation_url):
        result = self.entitycls.__new__(self.entitycls, from_data=data, connection=connection)
        es = result.__odata__
        es.parent_navigation_url = parent_navigation_url

        return result

    @property
    def entitycls(self):
        # if we've been given the type as a string
        # we need to look for the actual type now, at runtime
        if isinstance(self.entityclass, str):
            if not self.class_package:
                raise ODataReflectionError("Entitycls is a string, if you specify the entity class as a string you also need to specify "
                                           "the class_package where that class can be imported from at runtime")

            module = importlib.import_module(self.class_package)
            self.entityclass = getattr(module, self.entityclass)

        return self.entityclass

    def instances_from_data(self, raw_data, connection, parent_navigation_url):
        if self.is_collection:
            return [self.__populate_entity(d, connection, parent_navigation_url) for d in raw_data]
        else:
            return self.__populate_entity(raw_data, connection, parent_navigation_url)

    def _get_parent_cache(self, instance):
        es = instance.__odata__
        ic = es.nav_cache
        if self.name not in ic:
            cache = {}
            ic[self.name] = cache
        else:
            cache = ic[self.name]
        return cache

    def __set__(self, instance, value):
        """
        :type instance: odata.entity.EntityBase
        """
        cache = self._get_parent_cache(instance)
        if self.is_collection:
            cache['collection'] = value
        else:
            cache['single'] = value
        instance.__odata__.set_property_dirty(self)

    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(f"Skipping recursive check for {item}")
        if self.entitycls:
            # we're doing a recursive query here
            cpy = copy.copy(getattr(self.entitycls, item))
            cpy.name = f"{self.name}/{item}"
            return cpy
        else:
            raise Exception(f"Couldn't find {item} in {self.name}")

    def navigation_url(self, instance):
        es = instance.__odata__
        parent_url = es.instance_url

        if not parent_url:
            parent_url = es.parent_navigation_url

        if parent_url:
            url = parent_url
            if not url.endswith("/"):
                url += "/"
            url = urljoin(url, self.name)
            return url

        return None

    def __get__(self, instance, owner):
        """
        :type instance: odata.entity.EntityBase
        """
        if instance is None:
            return self

        es = instance.__odata__
        connection = es.connection
        nav_url = self.navigation_url(instance)
        new_object = nav_url is None
        cache = self._get_parent_cache(instance)

        if new_object:
            if self.is_collection:
                return cache.get('collection', [])
            return cache.get('single', None)

        if self.is_collection:
            if 'collection' not in cache:
                raw_data = connection.execute_get(nav_url)
                if raw_data:
                    cache['collection'] = self.instances_from_data(raw_data['value'], connection, nav_url)
                else:
                    cache['collection'] = []
            return cache['collection']
        else:
            if 'single' not in cache:
                raw_data = connection.execute_get(nav_url)
                if raw_data:
                     value = self.instances_from_data(raw_data, connection, nav_url)
                     cache['single'] = value
                else:
                    cache['single'] = None
            return cache['single']
