# -*- coding: utf-8 -*-

from decimal import Decimal
try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin

import dateutil.parser


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
        return float(value)

    def _return_data(self, value):
        return Decimal(str(value))


class DatetimeProperty(PropertyBase):

    def _set_data(self, value):
        r = value.isoformat()
        if value.tzinfo is None:
            r += 'Z'
        return r

    def _return_data(self, value):
        return dateutil.parser.parse(value)


class Relationship(object):

    def __init__(self, name, entitycls, collection=False, foreign_key=None):
        self.name = name
        self.entitycls = entitycls
        self.is_collection = collection
        self.foreign_key = foreign_key

    def __repr__(self):
        return '<Relationship to {0}>'.format(self.entitycls)

    def instances_from_data(self, raw_data):
        if self.is_collection:
            return [self.entitycls.__new__(self.entitycls, from_data=d) for d in raw_data]
        else:
            return self.entitycls.__new__(self.entitycls, from_data=raw_data)

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

    def __get__(self, instance, owner):
        """
        :type instance: odata.entity.EntityBase
        """
        if instance is None:
            return self

        es = instance.__odata__
        parent_url = es.instance_url
        new_object = parent_url is None
        cache = self._get_parent_cache(instance)

        if new_object:
            if self.is_collection:
                return cache.get('collection', [])
            return cache.get('single', None)

        parent_url += '/'
        url = urljoin(parent_url, self.name)
        cnx = self.entitycls.__odata_connection__

        if self.is_collection:
            if 'collection' not in cache:
                raw_data = cnx.execute_get(url)
                if raw_data:
                    cache['collection'] = self.instances_from_data(raw_data['value'])
                else:
                    cache['collection'] = []
            return cache['collection']
        else:
            if 'single' not in cache:
                raw_data = cnx.execute_get(url)
                if raw_data:
                    cache['single'] = self.instances_from_data(raw_data)
                else:
                    cache['single'] = None
            return cache['single']
