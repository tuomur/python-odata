# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import inspect

from odata.property import PropertyBase, NavigationProperty


class EntityState(object):

    def __init__(self, entity):
        """:type entity: EntityBase """
        self.entity = entity
        self.dirty = []
        self.nav_cache = {}
        self.data = {}

    # dictionary access
    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.data

    def get(self, key, default):
        return self.data.get(key, default=default)

    def update(self, other):
        self.data.update(other)
    # /dictionary access

    def __repr__(self):
        return self.data.__repr__()

    def describe(self):
        rows = [
            (u'Entity', ''),
            (u' - ' + self.entity.__odata_collection__, ''),
            (u'URL', ''),
        ]

        if self.instance_url:
            rows.append((u' - ' + self.instance_url, ''))
        else:
            rows.append((u' - ' + self.entity.__odata_url__(), '')),

        rows.append(('', ''))
        rows.append(('Properties', ''))
        rows.append(('-' * 40, ''))

        _, prop = self.primary_key_property
        rows.append((u'{0}*'.format(prop.name), ''))

        for _, prop in self.properties:
            rows.append((prop.name, ''))

        rows.append(('', ''))
        rows.append(('Navigation Properties', ''))
        rows.append(('-' * 40, ''))

        for _, prop in self.navigation_properties:
            rows.append((prop.name, ''))

        rows = os.linesep.join([first.ljust(40) + second.ljust(30) for first, second in rows])
        print(rows)

    def reset(self):
        self.dirty = []
        self.nav_cache = {}

    @property
    def id(self):
        prop_name, prop = self.primary_key_property
        value = self.data.get(prop.name)
        if value:
            return u'{0}({1})'.format(self.entity.__odata_collection__, prop.escape_value(value))

    @property
    def instance_url(self):
        if self.id:
            return self.entity.__odata_url_base__ + self.id

    @property
    def properties(self):
        props = []
        cls = self.entity.__class__
        for key, value in inspect.getmembers(cls):
            if isinstance(value, PropertyBase):
                props.append((key, value))
        return props

    @property
    def primary_key_property(self):
        for prop_name, prop in self.properties:
            if prop.primary_key is True:
                return prop_name, prop

    @property
    def navigation_properties(self):
        props = []
        cls = self.entity.__class__
        for key, value in inspect.getmembers(cls):
            if isinstance(value, NavigationProperty):
                props.append((key, value))
        return props

    @property
    def dirty_properties(self):
        rv = []
        for prop_name, prop in self.properties:
            if prop.name in self.dirty:
                rv.append((prop_name, prop))
        return rv

    def set_property_dirty(self, prop):
        if prop.name not in self.dirty:
            self.dirty.append(prop.name)

    def data_for_insert(self):
        return self._clean_new_entity(self.entity)

    def data_for_update(self):
        update_data = {
            '@odata.type': self.entity.__odata_type__
        }

        for _, prop in self.dirty_properties:
            update_data[prop.name] = self.data[prop.name]

        for prop_name, prop in self.navigation_properties:
            if prop.name in self.dirty:
                value = getattr(self.entity, prop_name, None)  # get the related object
                if value is not None:
                    key = '{0}@odata.bind'.format(prop.name)
                    if prop.is_collection:
                        update_data[key] = [i.__odata__.id for i in value]
                    else:
                        update_data[key] = value.__odata__.id
        return update_data

    def _clean_new_entity(self, entity):
        """:type entity: odata.entity.EntityBase """
        insert_data = {
            '@odata.type': entity.__odata_type__,
        }
        es = entity.__odata__
        for _, prop in es.properties:
            insert_data[prop.name] = es[prop.name]

        _, pk_prop = es.primary_key_property
        insert_data.pop(pk_prop.name)

        # Deep insert from nav properties
        for prop_name, prop in es.navigation_properties:
            if prop.foreign_key:
                insert_data.pop(prop.foreign_key, None)

            value = getattr(entity, prop_name, None)
            if value is not None:

                if prop.is_collection:
                    insert_data[prop.name] = [self._clean_new_entity(i) for i in value]
                else:
                    insert_data[prop.name] = self._clean_new_entity(value)

        return insert_data
