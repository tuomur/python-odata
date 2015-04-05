# -*- coding: utf-8 -*-

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin

from .property import PropertyBase


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
    def __odata_pk_property__(cls):
        for prop_name in cls.__dict__:
            prop = cls.__dict__.get(prop_name)
            if isinstance(prop, PropertyBase) and prop.primary_key is True:
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

        if 'from_data' in kwargs:
            i.__odata__.update(kwargs.pop('from_data'))
        else:
            for prop_name in cls.__dict__:
                prop = cls.__dict__.get(prop_name)
                if isinstance(prop, PropertyBase):
                    i.__odata__[prop.name] = None

        return i

    def __repr__(self):
        return '<{0}(Entity)>'.format(self.__class__.__name__)


def declarative_base():
    class Entity(EntityBase):
        pass
    return Entity
