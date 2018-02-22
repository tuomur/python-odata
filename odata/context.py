# -*- coding: utf-8 -*-

import logging

from odata.query import Query
from odata.connection import ODataConnection
from odata.exceptions import ODataError


class Context:

    def __init__(self, session=None, auth=None):
        self.log = logging.getLogger('odata.context')
        self.connection = ODataConnection(session=session, auth=auth)

    def query(self, entitycls):
        q = Query(entitycls, connection=self.connection)
        return q

    def call(self, action_or_function, **parameters):
        """
        Call a defined Action or Function using this Context's connection

        :param action_or_function: Action/Function instance on a Entity class
        :param parameters: Keyword parameters to pass to Action/Function
        """
        parameters['__connection__'] = self.connection
        return action_or_function(**parameters)

    def call_with_query(self, action_or_function, query, **parameters):
        """
        Call a defined Action or Function using this Context's connection.

        :param action_or_function: Action/Function instance on a Entity class
        :param parameters: Keyword parameters to pass to Action/Function
        """
        parameters['__connection__'] = self.connection
        return action_or_function.with_query(query)(**parameters)

    def delete(self, entity):
        """
        Creates a DELETE call to the service, deleting the entity

        :type entity: EntityBase
        :raises ODataConnectionError: Delete not allowed or a serverside error. Server returned an HTTP error code
        """
        self.log.info(u'Deleting entity: {0}'.format(entity))
        url = entity.__odata__.instance_url
        self.connection.execute_delete(url)
        entity.__odata__.persisted = False
        self.log.info(u'Success')

    def save(self, entity, force_refresh=True):
        """
        Creates a POST or PATCH call to the service. If the entity already has
        a primary key, an update is called. Otherwise the entity is inserted
        as new. Updating an entity will only send the changed values

        :param entity: Model instance to insert or update
        :type entity: EntityBase
        :param force_refresh: Read full entity data again from service after PATCH call
        :raises ODataConnectionError: Invalid data or serverside error. Server returned an HTTP error code
        """

        if self.is_entity_saved(entity):
            self._update_existing(entity, force_refresh=force_refresh)
        else:
            self._insert_new(entity)

    def is_entity_saved(self, entity):
        return entity.__odata__.persisted

    def _insert_new(self, entity):
        """
        Creates a POST call to the service, sending the complete new entity

        :type entity: EntityBase
        """
        url = entity.__odata_url__()
        if url is None:
            msg = 'Cannot insert Entity that does not belong to EntitySet: {0}'.format(entity)
            raise ODataError(msg)

        self.log.info(u'Saving new entity')

        es = entity.__odata__
        insert_data = es.data_for_insert()
        saved_data = self.connection.execute_post(url, insert_data)
        es.reset()
        es.connection = self.connection
        es.persisted = True

        if saved_data is not None:
            es.update(saved_data)

        self.log.info(u'Success')

    def _update_existing(self, entity, force_refresh=True):
        """
        Creates a PATCH call to the service, sending only the modified values

        :type entity: EntityBase
        """
        es = entity.__odata__
        if es.instance_url is None:
            msg = 'Cannot update Entity that does not belong to EntitySet: {0}'.format(entity)
            raise ODataError(msg)

        patch_data = es.data_for_update()

        if len([i for i in patch_data if not i.startswith('@')]) == 0:
            self.log.debug(u'Nothing to update: {0}'.format(entity))
            return

        self.log.info(u'Updating existing entity: {0}'.format(entity))

        url = es.instance_url

        saved_data = self.connection.execute_patch(url, patch_data)
        es.reset()

        if saved_data is None and force_refresh:
            self.log.info(u'Reloading entity from service')
            saved_data = self.connection.execute_get(url)

        if saved_data is not None:
            entity.__odata__.update(saved_data)

        self.log.info(u'Success')
