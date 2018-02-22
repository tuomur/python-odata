# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import inspect
from collections import OrderedDict

from odata.property import PropertyBase, NavigationProperty


class EntityState(object):

    def __init__(self, entity):
        """:type entity: EntityBase """
        self.entity = entity
        self.dirty = []
        self.nav_cache = {}
        self.data = {}
        self.connection = None
        # does this object exist serverside
        self.persisted = False

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
            u'EntitySet: {0}'.format(self.entity.__odata_collection__),
            u'Type: {0}'.format(self.entity.__odata_type__),
            u'URL: {0}'.format(self.instance_url or self.entity.__odata_url__()),
            u'',
            u'Properties',
            u'-' * 40,
        ]

        for _, prop in self.properties:
            name = prop.name
            if prop.primary_key:
                name += '*'
            if prop.name in self.dirty:
                name += ' (dirty)'
            rows.append(name)

        rows.append(u'')
        rows.append(u'Navigation Properties')
        rows.append(u'-' * 40)

        for _, prop in self.navigation_properties:
            rows.append(prop.name)

        rows = os.linesep.join(rows)
        print(rows)

    def reset(self):
        self.dirty = []
        self.nav_cache = {}

    @property
    def id(self):
        ids = []
        entity_name = self.entity.__odata_collection__
        if entity_name is None:
            return

        for prop_name, prop in self.primary_key_properties:
            value = self.data.get(prop.name)
            if value:
                ids.append((prop, str(prop.escape_value(value))))
        if len(ids) == 1:
            key_value = ids[0][1]
            return u'{0}({1})'.format(entity_name,
                                      key_value)
        if len(ids) > 1:
            key_ids = []
            for prop, key_value in ids:
                key_ids.append('{0}={1}'.format(prop.name, key_value))
            return u'{0}({1})'.format(entity_name, ','.join(key_ids))

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
    def primary_key_properties(self):
        pks = []
        for prop_name, prop in self.properties:
            if prop.primary_key is True:
                pks.append((prop_name, prop))
        return pks

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
        update_data = OrderedDict()
        update_data['@odata.type'] = self.entity.__odata_type__

        for _, prop in self.dirty_properties:
            if prop.is_computed_value:
                continue

            update_data[prop.name] = self.data[prop.name]

        for prop_name, prop in self.navigation_properties:
            if prop.name in self.dirty:
                value = getattr(self.entity, prop_name, None)  # get the related object
                """:type : None | odata.entity.EntityBase | list[odata.entity.EntityBase]"""
                if value is not None:
                    key = '{0}@odata.bind'.format(prop.name)
                    if prop.is_collection:
                        update_data[key] = [i.__odata__.id for i in value]
                    else:
                        update_data[key] = value.__odata__.id
        return update_data

    def _clean_new_entity(self, entity):
        """:type entity: odata.entity.EntityBase """
        insert_data = OrderedDict()
        insert_data['@odata.type'] = entity.__odata_type__

        es = entity.__odata__
        for _, prop in es.properties:
            if prop.is_computed_value:
                continue

            insert_data[prop.name] = es[prop.name]

        # Allow pk properties only if they have values
        for _, pk_prop in es.primary_key_properties:
            if insert_data[pk_prop.name] is None:
                insert_data.pop(pk_prop.name)

        # Deep insert from nav properties
        for prop_name, prop in es.navigation_properties:
            if prop.foreign_key:
                insert_data.pop(prop.foreign_key, None)

            value = getattr(entity, prop_name, None)
            """:type : None | odata.entity.EntityBase | list[odata.entity.EntityBase]"""
            if value is not None:

                if prop.is_collection:
                    binds = []

                    # binds must be added first
                    for i in [i for i in value if i.__odata__.id]:
                        binds.append(i.__odata__.id)

                    if len(binds):
                        insert_data['{0}@odata.bind'.format(prop.name)] = binds

                    new_entities = []
                    for i in [i for i in value if i.__odata__.id is None]:
                        new_entities.append(self._clean_new_entity(i))

                    if len(new_entities):
                        insert_data[prop.name] = new_entities

                else:
                    if value.__odata__.id:
                        insert_data['{0}@odata.bind'.format(prop.name)] = value.__odata__.id
                    else:
                        insert_data[prop.name] = self._clean_new_entity(value)

        return insert_data
