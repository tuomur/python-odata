# -*- coding: utf-8 -*-

import logging

from .entity import EntityBase
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
        """
        Creates a DELETE call to the service, deleting the entity
        :type entity: EntityBase
        """
        self.log.info(u'Deleting entity: {0}'.format(entity))
        url = entity.__odata__.instance_url
        self.connection.execute_delete(url)
        self.log.info(u'Success')

    def save(self, entity):
        instance_url = entity.__odata__.instance_url

        if instance_url is None:
            self._insert_new(entity)
        else:
            self._update_existing(entity)

    def _insert_new(self, entity):
        """
        Creates a POST call to the service, sending the complete new entity
        :type entity: EntityBase
        """
        self.log.info(u'Saving new entity')

        url = entity.__odata_url__()

        es = entity.__odata__
        insert_data = es.data_for_insert()
        saved_data = self.connection.execute_post(url, insert_data)
        es.reset()

        if saved_data is not None:
            es.update(saved_data)

        self.log.info(u'Success')

    def _update_existing(self, entity):
        """
        Creates a PATCH call to the service, sending only the modified values
        :type entity: EntityBase
        """
        es = entity.__odata__
        patch_data = es.data_for_update()

        if len(patch_data) == 0:
            return

        self.log.info(u'Updating existing entity: {0}'.format(entity))

        url = es.instance_url

        saved_data = self.connection.execute_patch(url, patch_data)
        es.reset()

        if saved_data is None:
            self.log.info(u'Reloading entity from service')
            saved_data = self.connection.execute_get(url)

        if saved_data is not None:
            entity.__odata__.update(saved_data)

        self.log.info(u'Success')
