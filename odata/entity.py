# -*- coding: utf-8 -*-

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin

from odata.state import EntityState


class EntityBase(object):
    __odata_connection__ = None
    __odata_url_base__ = ''
    __odata_collection__ = 'Entities'
    __odata_type__ = 'ODataSchema.Entity'

    @classmethod
    def __odata_url__(cls):
        # used by Query
        return urljoin(cls.__odata_url_base__, cls.__odata_collection__)

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
        else:
            for prop_name, prop in es.properties:
                i.__odata__[prop.name] = None

        return i

    def __repr__(self):
        clsname = self.__class__.__name__
        prop_name, prop = self.__odata__.primary_key_property
        if prop:
            value = self.__odata__[prop.name]
            if value:
                return '<Entity({0}:{1})>'.format(clsname, prop.escape_value(value))
        return '<Entity({0})>'.format(clsname)

    def __eq__(self, other):
        if isinstance(other, EntityBase):
            my_id = self.__odata__.id
            if my_id:
                return my_id == other.__odata__.id
        return False


def declarative_base():
    class Entity(EntityBase):
        pass
    return Entity
