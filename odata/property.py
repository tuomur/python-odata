# -*- coding: utf-8 -*-

from decimal import Decimal
import datetime

import dateutil.parser

from .navproperty import NavigationProperty


class PropertyBase(object):

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
            return self._return_data(raw_data)
        else:
            raise AttributeError()

    def __set__(self, instance, value):
        """
        :type instance: odata.entity.EntityBase
        """

        es = instance.__odata__

        if self.name in es:
            new_value = self._set_data(value)
            old_value = es[self.name]
            if new_value != old_value:
                es[self.name] = new_value
                es.set_property_dirty(self)

    def _set_data(self, value):
        """ Called when serializing the value to JSON """
        return value

    def _return_data(self, value):
        """ Called when deserializing the value from JSON to Python """
        return value

    def escape_value(self, value):
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
    pass


class StringProperty(PropertyBase):

    def escape_value(self, value):
        return u"'{0}'".format(value.replace("'", "''"))


class BooleanProperty(PropertyBase):

    def escape_value(self, value):
        if value:
            return 'true'
        return 'false'

    def _set_data(self, value):
        return bool(value)

    def _return_data(self, value):
        return bool(value)


class FloatProperty(PropertyBase):
    pass


class DecimalProperty(PropertyBase):

    def _set_data(self, value):
        if value is not None:
            return float(value)

    def _return_data(self, value):
        if value is not None:
            return Decimal(str(value))


class DatetimeProperty(PropertyBase):

    def _set_data(self, value):
        if isinstance(value, datetime.datetime):
            r = value.isoformat()
            if value.tzinfo is None:
                r += 'Z'
            return r

    def _return_data(self, value):
        if value:
            return dateutil.parser.parse(value)
