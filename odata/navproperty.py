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
    def __init__(self, name, entitycls, collection=False, foreign_key=None):
        from odata.property import PropertyBase
        self.name = name
        self.entitycls = entitycls
        self.is_collection = collection
        if isinstance(foreign_key, PropertyBase):
            self.foreign_key = foreign_key.name
        else:
            self.foreign_key = foreign_key

    def __repr__(self):
        return u'<NavigationProperty to {0}>'.format(self.entitycls)

    def instances_from_data(self, raw_data, connection):
        if self.is_collection:
            return [self.instance_from_data(d, connection) for d in raw_data['value']] if raw_data['value'] else []
        else:
            return self.instance_from_data(raw_data, connection) if raw_data else None

    def instance_from_data(self, raw_data, connection): # mwa: this needs to be seperated form navproperty
        entitycls = self._getClass_by_response_type(self.entitycls, raw_data.get('@odata.type'))
        e = entitycls.__new__(entitycls, from_data=raw_data)
        es = e.__odata__
        es.connection = connection
        return e
            
    def _getClass_by_response_type(self, matched_class, odata_type):
        if not odata_type: return matched_class
        for subclass in matched_class.__subclasses__():
            if subclass.__odata_type__ == odata_type[1:]: return self._getClass_by_response_type(subclass, odata_type)
        return matched_class
        
    def _get_parent_cache(self, instance):
        es = instance.__odata__
        ic = es.nav_cache
        if self.name not in ic:
            cache = {}
            ic[self.name] = cache
        else:
            cache = ic[self.name]
        return cache

    def _get_instances_from_server(self, instance):
        es = instance.__odata__
        connection = es.connection
        parent_url = es.instance_url
        parent_url += '/'
        url = urljoin(parent_url, self.name)
        instances = []
        while True:
            raw_data = connection.execute_get(url)
            instances.extend(self.instances_from_data(raw_data, connection))
            if not '@odata.nextLink' in raw_data:
                break
            url = raw_data.get('@odata.nextLink')
        return instances

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

    def __get__(self, instance, owner):
        """
        :type instance: odata.entity.EntityBase
        """
        if instance is None:
            return self

        es = instance.__odata__
        cache = self._get_parent_cache(instance)

        if es.instance_url is None:
            if self.is_collection:
                return cache.get('collection', [])
            return cache.get('single', None)

        cache_type  = 'collection' if self.is_collection else 'single'

        try:
            return cache[cache_type]
        except KeyError:
            cache[cache_type] = self._get_instances_from_server(instance)
        return cache[cache_type]
