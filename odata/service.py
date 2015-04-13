# -*- coding: utf-8 -*-

import logging

from .connection import ODataConnection
from .metadata import MetaData
from .query import Query
from .exceptions import ODataError

__all__ = (
    'ODataService',
    'ODataError',
)


class ODataService(object):

    def __init__(self, url, base=None, metadata=None, reflect_entities=False, session=None, auth=None):
        self.url = url
        self.metadata_url = ''
        self.collections = {}
        self.connection = ODataConnection(session=session, auth=auth)
        self.log = logging.getLogger('odata.service')

        self.entities = {}
        self.metadata = metadata or MetaData(self)
        if reflect_entities:
            base, self.entities = self.metadata.get_entity_sets(base=base)

        self.base = base
        base.__odata_url_base__ = url
        base.__odata_connection__ = self.connection

    def __repr__(self):
        return '<ODataService at {0}>'.format(self.url)

    def query(self, entitycls):
        return Query(entitycls)

    def delete(self, entity):
        self.log.info(u'Deleting entity: {0}'.format(entity))
        instance_url = entity.__odata_instance_url__()
        self.connection.execute_delete(instance_url)
        self.log.info(u'Success')

    def save(self, entity):
        instance_url = entity.__odata_instance_url__()

        if instance_url is None:
            self._insert_new(entity)
        else:
            self._update_existing(entity)

    def _clean_new_entity(self, entity):
        insert_data = {
            '@odata.type': entity.__odata_type__,
        }
        for _, prop in entity.__odata_properties__():
            insert_data[prop.name] = entity.__odata__[prop.name]

        _, pk_prop = entity.__odata_pk_property__()
        insert_data.pop(pk_prop.name)

        # Deep insert from nav properties
        for prop_name, prop in entity.__odata_nav_properties__():
            if prop.foreign_key:
                insert_data.pop(prop.foreign_key, None)

            value = getattr(entity, prop_name, None)
            if value is not None:

                if prop.is_collection:
                    insert_data[prop.name] = [self._clean_new_entity(i) for i in value]
                else:
                    insert_data[prop.name] = self._clean_new_entity(value)

        return insert_data

    def _insert_new(self, entity):
        """
        Creates a POST call to the service, sending the complete new entity
        """
        self.log.info(u'Saving new entity')

        url = entity.__odata_url__()

        insert_data = self._clean_new_entity(entity)

        saved_data = self.connection.execute_post(url, insert_data)
        entity.__odata_dirty__ = []
        entity.__odata_nav_cache__ = {}

        if saved_data is not None:
            entity.__odata__.update(saved_data)

        self.log.info(u'Success')

    def _update_existing(self, entity):
        """
        Creates a PATCH call to the service, sending only the modified values
        """
        dirty_keys = list(set([pn for pn in entity.__odata_dirty__]))

        patch_data = {
            '@odata.type': entity.__odata_type__,
        }

        for _, prop in entity.__odata_properties__():
            if prop.name in dirty_keys:
                patch_data[prop.name] = entity.__odata__[prop.name]

        for prop_name, prop in entity.__odata_nav_properties__():
            if prop.name in entity.__odata_dirty__:
                value = getattr(entity, prop_name, None)
                if value is not None:
                    key = '{0}@odata.bind'.format(prop.name)
                    if prop.is_collection:
                        patch_data[key] = [i.__odata_id__() for i in value]
                    else:
                        patch_data[key] = value.__odata_id__()

        if len(patch_data) == 0:
            return

        self.log.info(u'Updating existing entity: {0}'.format(entity))

        instance_url = entity.__odata_instance_url__()

        saved_data = self.connection.execute_patch(instance_url, patch_data)
        entity.__odata_dirty__ = []
        entity.__odata_nav_cache__ = {}

        if saved_data is None:
            self.log.info(u'Reloading entity from service')
            saved_data = self.connection.execute_get(instance_url)

        if saved_data is not None:
            entity.__odata__.update(saved_data)

        self.log.info(u'Success')
