# -*- coding: utf-8 -*-

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin

from .property import PropertyBase, Relationship


class EntityBase(object):
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
    def __odata_properties__(cls):
        props = []
        for prop_name in cls.__dict__:
            prop = cls.__dict__.get(prop_name)
            if isinstance(prop, PropertyBase):
                props.append((prop_name, prop))
        return props

    @classmethod
    def __odata_nav_properties__(cls):
        props = []
        for prop_name in cls.__dict__:
            prop = cls.__dict__.get(prop_name)
            if isinstance(prop, Relationship):
                props.append((prop_name, prop))
        return props

    @classmethod
    def __odata_pk_property__(cls):
        for prop_name, prop in cls.__odata_properties__():
            if prop.primary_key is True:
                return prop_name, prop

    def __odata_instance_url__(self):
        prop_name, prop = self.__odata_pk_property__()
        pk_value = getattr(self, prop_name, None)
        if pk_value is not None:
            pk_value = prop.escape_value(pk_value)
            return self.__odata_single_url__().format(pk=pk_value)

    def __new__(cls, *args, **kwargs):
        i = super(EntityBase, cls).__new__(cls)
        i.__odata__ = {
            '@odata.type': cls.__odata_type__,
        }
        i.__odata_dirty__ = []
        i.__odata_nav_cache__ = {}

        if 'from_data' in kwargs:
            raw_data = kwargs.pop('from_data')
            for prop_name, prop in cls.__odata_properties__():
                i.__odata__[prop.name] = raw_data.get(prop.name)
        else:
            for prop_name, prop in cls.__odata_properties__():
                i.__odata__[prop.name] = None

        return i

    def __repr__(self):
        v = self.__odata_pk_property__()
        if v is not None:
            pk_prop = v[1]
            pk = self.__odata__[pk_prop.name]
            return '<Entity({0}:{1})>'.format(self.__class__.__name__, pk)
        return '<Entity({0})>'.format(self.__class__.__name__)


def declarative_base():
    class Entity(EntityBase):
        pass
    return Entity
