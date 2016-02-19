# -*- coding: utf-8 -*-

"""
Entity properties
=================

Entities are a collection of Properties of different types. These classes
implement the default set of types used in endpoints.

At entity class level, these properties are used in querying entities:

.. code-block:: python

    >>> import datetime
    >>> Order.ShippedDate > datetime.datetime.now()
    'ShippedDate gt 2016-02-19T12:02:04.956226'
    >>> Service.query(Order).filter(Order.OrderID == 1234)

Once the entity is instanced, the properties act as data getters and setters:

.. code-block:: python

    >>> order = Order()
    >>> order.ShippedDate = datetime.datetime.now()
    >>> Service.save(order)

Setting a new value to a property marks the property as `dirty`, and will be
sent to the endpoint when :py:func:`~odata.service.ODataService.save` is
called.

This behavior is similar to SQLAlchemy's ORM.


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


Creating new property types
---------------------------

All properties must subclass :py:class:`PropertyBase`, and implement the
serialization methods. You can then use the created Property class in your
custom defined entities. Replacing the default types is not supported.

.. autoclass:: PropertyBase
    :members:

----

Types
-----
"""

from decimal import Decimal
import datetime

import dateutil.parser

from .navproperty import NavigationProperty


class PropertyBase(object):
    """
    A base class for all properties.

    :param name: Name of the property in the endpoint
    :param primary_key: This property is a primary key
    """
    def __init__(self, name, primary_key=False):
        """
        :type name: str
        :type primary_key: bool
        """
        self.name = name
        self.primary_key = primary_key

    def __repr__(self):
        return '<Property({0})>'.format(self.name)

    def __get__(self, instance, owner):
        """
        :type instance: odata.entity.EntityBase
        :type owner: odata.entity.EntityBase
        """
        if instance is None:
            return self

        es = instance.__odata__

        if self.name in es:
            raw_data = es[self.name]
            return self.deserialize(raw_data)
        else:
            raise AttributeError()

    def __set__(self, instance, value):
        """
        :type instance: odata.entity.EntityBase
        """

        es = instance.__odata__

        if self.name in es:
            new_value = self.serialize(value)
            old_value = es[self.name]
            if new_value != old_value:
                es[self.name] = new_value
                es.set_property_dirty(self)

    def serialize(self, value):
        """
        Called when serializing the value to JSON. Implement this method when
        creating a new Property class

        :param value: Value given in Python code
        :returns: Value that will be used in JSON
        """
        raise NotImplementedError()

    def deserialize(self, value):
        """
        Called when deserializing the value from JSON to Python. Implement this
        method when creating a new Property class

        :param value: Value received in JSON
        :returns: Value that will be passed to Python
        """
        raise NotImplementedError()

    def escape_value(self, value):
        """
        Called when escaping the property value for usage in Query string.
        Implement this method when creating a new Property class

        :param value: Value of this propery
        :return: Escaped value that can be used in Query string
        """
        return value

    def asc(self):
        return '{0} asc'.format(self.name)

    def desc(self):
        return '{0} desc'.format(self.name)

    def __eq__(self, other):
        value = self.escape_value(other)
        return u'{0} eq {1}'.format(self.name, value)

    def __ne__(self, other):
        value = self.escape_value(other)
        return u'{0} ne {1}'.format(self.name, value)

    def __ge__(self, other):
        value = self.escape_value(other)
        return u'{0} ge {1}'.format(self.name, value)

    def __gt__(self, other):
        value = self.escape_value(other)
        return u'{0} gt {1}'.format(self.name, value)

    def __le__(self, other):
        value = self.escape_value(other)
        return u'{0} le {1}'.format(self.name, value)

    def __lt__(self, other):
        value = self.escape_value(other)
        return u'{0} lt {1}'.format(self.name, value)

    def startswith(self, value):
        value = self.escape_value(value)
        return u'startswith({0}, {1})'.format(self.name, value)

    def endswith(self, value):
        value = self.escape_value(value)
        return u'endswith({0}, {1})'.format(self.name, value)


class IntegerProperty(PropertyBase):
    """
    Property that stores a plain old integer
    """
    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class StringProperty(PropertyBase):
    """
    Property that stores a unicode string
    """
    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value

    def escape_value(self, value):
        return u"'{0}'".format(value.replace("'", "''"))


class BooleanProperty(PropertyBase):
    """
    Property that stores a boolean value
    """
    def escape_value(self, value):
        if value:
            return 'true'
        return 'false'

    def serialize(self, value):
        return bool(value)

    def deserialize(self, value):
        return bool(value)


class FloatProperty(PropertyBase):
    """
    Property that stores a float value
    """
    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class DecimalProperty(PropertyBase):
    """
    Property that stores a decimal value. JSON does not support this directly,
    so the value will be transmitted as a float
    """
    def serialize(self, value):
        if value is not None:
            return float(value)

    def deserialize(self, value):
        if value is not None:
            return Decimal(str(value))


class DatetimeProperty(PropertyBase):
    """
    Property that stores a datetime object. JSON does not support date objects
    natively so dates are transmitted as ISO-8601 formatted strings
    """
    def escape_value(self, value):
        return value.isoformat()

    def serialize(self, value):
        if isinstance(value, datetime.datetime):
            r = value.isoformat()
            if value.tzinfo is None:
                r += 'Z'
            return r

    def deserialize(self, value):
        if value:
            return dateutil.parser.parse(value)
