# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import inspect
import logging
import re
from collections import OrderedDict
try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin, urlparse
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin, urlparse

from odata.property import PropertyBase, NavigationProperty
import odata


class EntityState(object):

    def __init__(self, entity):
        self.log = logging.getLogger('odata.state')
        """:type entity: EntityBase """
        self.entity = entity
        self.dirty = []
        self.nav_cache = {}
        self.data = OrderedDict()
        self.connection = None
        # does this object exist serverside
        self.persisted = False
        self.persisted_id = None
        self.odata_scope = None

    # dictionary access
    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.data

    def get(self, key, default):
        return self.data.get(key, default)

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
        self.persisted_id = None

    @property
    def id(self):
        if self.persisted_id:
            return self.persisted_id
        ids = []
        entity_name = self.entity.__odata_collection__
        if entity_name is None:
            return

        for prop_name, prop in self.primary_key_properties:
            value = self.data.get(prop.name)
            if value is not None:
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
        odata_id = self.get('@odata.id', None)
        if self.id:
            if self.odata_scope:
                if self.odata_scope.endswith(self.entity.__odata_collection__):
                    url = re.sub(self.entity.__odata_collection__, '', self.odata_scope)
                    return urljoin(url, self.id)
                else:
                    return self.odata_scope
            elif odata_id and self.id in odata_id:
                url = re.sub(self.entity.__odata_collection__, '', self.entity.__odata_url__())
                odata_id = odata_id.split('/')[-1]
                return urljoin(url, odata_id)
            else:
                url = re.sub(self.entity.__odata_collection__, '', self.entity.__odata_url__())
                return urljoin(url, self.id)
        elif odata_id:
            url = re.sub(self.entity.__odata_collection__, '', self.entity.__odata_url__())
            odata_id = odata_id.split('/')[-1]
            return urljoin(url, odata_id)

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
        for prop_name, prop in self.navigation_properties:
            if prop.name in self.dirty:
                rv.append((prop_name, prop))
        return rv

    def set_property_dirty(self, prop):
        if prop.name not in self.dirty:
            self.dirty.append(prop.name)

    def data_for_insert(self):
        return self._new_entity(self.entity)

    def data_for_update(self):
        return self._updated_entity(self.entity)

    def set_scope(self, odata_scope):
        if odata_scope:
            self.odata_scope = odata_scope

    def _new_entity(self, entity):
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

            value = getattr(entity, prop_name, None)
            """:type : None | odata.entity.EntityBase | list[odata.entity.EntityBase]"""
            insert_data = self._add_or_update_associated(insert_data, prop, value)

        for _, prop in es.properties:
            if prop.name in insert_data:
                if not insert_data[prop.name]:
                    insert_data.pop(prop.name)

        return insert_data

    def _updated_entity(self, entity):
        update_data = OrderedDict()
        update_data['@odata.type'] = self.entity.__odata_type__

        es = entity.__odata__

        for _, pk_prop in es.primary_key_properties:
            update_data[pk_prop.name] = es[pk_prop.name]
        
        if '@odata.etag' in es:
            update_data['@odata.etag'] = es['@odata.etag']

        for _, prop in es.dirty_properties:
            if prop.is_computed_value:
                continue
            if prop.name in dict(es.navigation_properties).keys():
                continue

            update_data[prop.name] = es[prop.name]

        for prop_name, prop in es.navigation_properties:
            if prop.name in es.dirty:
                value = getattr(entity, prop_name, None)  # get the related object
                """:type : None | odata.entity.EntityBase | list[odata.entity.EntityBase]"""
                update_data = self._add_or_update_associated(update_data, prop, value)

        return update_data

    def _add_or_update_associated(self, data, prop, value):
        if value is None:
            return data
        if prop.is_collection:
            data = self._add_or_update_associated_collection(data, prop, value)
        else:
            data = self._add_or_update_associated_instance(data, prop, value)
        return data

    def _add_or_update_associated_collection(self, data, prop, value):

        def is_new(entity):
            if entity.__odata__.id is None:
                return True
            return False

        def is_dirty(entity):
            if is_new(entity):
                return False
            elif hasattr(entity.__odata__, 'dirty') and entity.__odata__.dirty:
                return True
            return False

        def is_persisted(entity):
            return (not is_new(entity) and not is_dirty(entity))

        ids = [i.__odata__.id for i in value if is_persisted(i)]
        if ids:
            data['{0}@odata.bind'.format(prop.name)] = ids

        upd_objs = [self._updated_entity(i) for i in value if is_dirty(i)]

        new_objs = [self._new_entity(i) for i in value if is_new(i)]

        if upd_objs or new_objs:
            data[prop.name] = upd_objs + new_objs

        return data

    def _add_or_update_associated_instance(self, data, prop, value):
        if isinstance(value, odata.entity.EntityBase):
            if value.persisted is False:
                data[prop.name] = self._new_entity(value)

            elif value.dirty:
                data[prop.name] = self._updated_entity(value)

            elif value.__odata__.id:
                data['{0}@odata.bind'.format(prop.name)] = value.__odata__.id

        elif value.__odata__.id:
            data['{0}@odata.bind'.format(prop.name)] = value.__odata__.id

        return data
