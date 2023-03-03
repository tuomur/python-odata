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


.. automodule:: odata.navproperty


Creating new property types
---------------------------

All properties must subclass :py:class:`PropertyBase`, and implement the
serialization methods. You can then use the created Property class in your
custom defined entities. Replacing the default types is not supported.

.. autoclass:: odata.property.PropertyBase
    :members:

----

Types
-----
"""

import datetime
from decimal import Decimal

import dateutil.parser

from .navproperty import NavigationProperty  # actually used by other imports, don't remove
from .exceptions import ODataQueryError


class SortOrder(object):
    def __init__(self, member, sort_order):
        self.member = member
        self.sort_order = sort_order

    def __str__(self):
        return f"{self.member} {self.sort_order}"

    def __repr__(self):
        return self.__str__()


class BaseQueryFilter(object):
    def __init__(self, member, op, value):
        self.member = member
        self.op = op
        self.value = value

    def __and__(self, other: "BaseQueryFilter"):
        if isinstance(other, BaseQueryFilter):
            return CompoundQueryFilter(self, "and", other)
        else:
            raise ODataQueryError("Can only use other PropertyBase classes for & (AND) operation")

    def __or__(self, other: "BaseQueryFilter"):
        if isinstance(other, BaseQueryFilter):
            return CompoundQueryFilter(self, "or", other)
        else:
            raise ODataQueryError("Can only use other PropertyBase classes for | (OR) operation")

    def __repr__(self):
        return self.__str__()


class UnaryQueryFilter(BaseQueryFilter):
    def __init__(self, op, value):
        super().__init__(None, op, value)

    def __str__(self):
        return f"{self.op}({self.value})"


class SimpleQueryFilter(BaseQueryFilter):
    def __str__(self):
        return f"{self.member} {self.op} {self.value}"


class ParameterizedQueryFilter(BaseQueryFilter):
    def __str__(self):
        return f"{self.op}({self.member}, {self.value})"


class CompoundQueryFilter(BaseQueryFilter):
    def __str__(self):
        return f"({self.member}) {self.op} ({self.value})"


class PropertyBase(object):
    """
    A base class for all properties.

    :param name: Name of the property in the endpoint
    :param primary_key: This property is a primary key
    :param is_collection: This property contains multiple values
    """
    def __init__(self, name, primary_key=False, is_collection=False, is_computed_value=False):
        """
        :type name: str
        :type primary_key: bool
        """
        self.name = name
        self.primary_key = primary_key
        self.is_collection = is_collection
        self.is_computed_value = is_computed_value

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
            if self.is_collection:
                if raw_data is None:
                    return

                data = []
                for i in raw_data:
                    data.append(self.deserialize(i))
                return data
            else:
                return self.deserialize(raw_data)
        else:
            raise AttributeError()

    def __set__(self, instance, value):
        """
        :type instance: odata.entity.EntityBase
        """

        es = instance.__odata__

        if self.name in es:
            if self.is_collection:
                data = []
                for i in (value or []):
                    data.append(self.serialize(i))
                new_value = data
            else:
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

        :param value: Value of this property
        :return: Escaped value that can be used in Query string
        """
        if value is None:
            return 'null'
        return value

    def asc(self):
        return SortOrder(self.name, "asc")

    def desc(self):
        return SortOrder(self.name, "desc")

    def __eq__(self, other):
        value = self.escape_value(other)
        return SimpleQueryFilter(self.name, "eq", value)

    def __ne__(self, other):
        value = self.escape_value(other)
        return SimpleQueryFilter(self.name, "ne", value)

    def __ge__(self, other):
        value = self.escape_value(other)
        return SimpleQueryFilter(self.name, "ge", value)

    def __gt__(self, other):
        value = self.escape_value(other)
        return SimpleQueryFilter(self.name, "gt", value)

    def __le__(self, other):
        value = self.escape_value(other)
        return SimpleQueryFilter(self.name, "le", value)

    def __lt__(self, other):
        value = self.escape_value(other)
        return SimpleQueryFilter(self.name, "lt", value)

    def startswith(self, value):
        value = self.escape_value(value)
        return ParameterizedQueryFilter(self.name, "startswith", value)

    def endswith(self, value):
        value = self.escape_value(value)
        return ParameterizedQueryFilter(self.name, "endswith", value)

    def contains(self, value):
        """Extend the StringProperty with contains method"""
        value = self.escape_value(value)
        return ParameterizedQueryFilter(self.name, "contains", value)

    def lacks(self, value):
        """Does not contain"""
        value = self.escape_value(value)
        return UnaryQueryFilter("not", ParameterizedQueryFilter(self.name, "contains", value))


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
        if value is None:
            return 'null'
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
    def escape_value(self, value):
        if value is None:
            return 'null'
        return str(value)

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
        if value is None:
            return 'null'
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


class UUIDProperty(StringProperty):
    """
    Property that stores a UUID (also known as GUID) value. JSON does not
    support this directly, so the value will be transmitted as a string.
    Unlike :py:class:`StringProperty`, it does not escape quotes as query
    filters do not use quotes for UUID
    """
    def serialize(self, value):
        return str(value)

    def deserialize(self, value):
        return str(value)

    def escape_value(self, value):
        if value is None:
            return 'null'
        return str(value)
