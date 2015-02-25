# -*- coding: utf-8 -*-

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin


class Property(object):

    def __init__(self, name, primary_key=False):
        self.name = name
        self.primary_key = primary_key

    def __repr__(self):
        return '<Property {0}>'.format(self.name)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.name in instance.__odata__:
            return instance.__odata__[self.name]
        else:
            raise AttributeError()

    def __set__(self, instance, value):
        if self.name in instance.__odata__:
            instance.__odata__[self.name] = value

    def escape_value(self, value):
        return value

    # Ordering

    def asc(self):
        return '{0} asc'.format(self.name)

    def desc(self):
        return '{0} desc'.format(self.name)

    # Comparators supported by OData ###########################################

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

    def substringof(self, value):
        value = self.escape_value(value)
        return u'substringof({1}, {0})'.format(self.name, value)

    def startswith(self, value):
        value = self.escape_value(value)
        return u'startswith({0}, {1})'.format(self.name, value)

    def endswith(self, value):
        value = self.escape_value(value)
        return u'endswith({0}, {1})'.format(self.name, value)


class IntegerProperty(Property):
    pass


class StringProperty(Property):

    def escape_value(self, value):
        return u"'{0}'".format(value)


class Entity(object):
    __odata_connection__ = None
    __odata_url_base__ = ''
    __odata_collection__ = 'Entities'
    __odata_type__ = 'ODataSchema.Entity'

    @classmethod
    def __odata_url__(cls):
        return urljoin(cls.__odata_url_base__, cls.__odata_collection__)

    @classmethod
    def __odata_single_url__(cls):
        return cls.__odata_url__() + u'({pk})'

    @classmethod
    def __odata_pk_property__(cls):
        for prop_name in cls.__dict__:
            prop = cls.__dict__.get(prop_name)
            if isinstance(prop, Property) and prop.primary_key is True:
                return prop_name, prop

    def __odata_instance_url__(self):
        prop_name, prop = self.__odata_pk_property__()
        pk_value = getattr(self, prop_name, None)
        if pk_value is not None:
            pk_value = prop.escape_value(pk_value)
            return self.__odata_single_url__().format(pk=pk_value)

    def __new__(cls, *args, **kwargs):
        i = super(Entity, cls).__new__(cls)
        i.__odata__ = {
            'odata.type': cls.__odata_type__,
        }

        if 'from_data' in kwargs:
            i.__odata__.update(kwargs.pop('from_data'))
        else:
            for prop_name in cls.__dict__:
                prop = cls.__dict__.get(prop_name)
                if isinstance(prop, Property):
                    i.__odata__[prop.name] = None

        return i

    def __repr__(self):
        return '<{0}(Entity)>'.format(self.__class__.__name__)
