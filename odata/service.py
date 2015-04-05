# -*- coding: utf-8 -*-

from .connection import ODataConnection
from .query import Query
from .exceptions import ODataError

__all__ = (
    'ODataService',
    'ODataError',
)


class ODataService(object):

    def __init__(self, url, base, session=None, auth=None):
        self.url = url
        self.metadata_url = ''
        self.collections = {}
        self.connection = ODataConnection(session=session, auth=auth)

        self.base = base
        base.__odata_url_base__ = url
        base.__odata_connection__ = self.connection

    def __repr__(self):
        return '<ODataService at {0}>'.format(self.url)

    def query(self, entitycls):
        return Query(entitycls)

    def save(self, entity):
        instance_url = entity.__odata_instance_url__()

        if instance_url is None:
            self._insert_new(entity)
        else:
            self._update_existing(entity)

    def _insert_new(self, entity):
        """
        Creates a POST call to the service, sending the complete new entity
        """
        url = entity.__odata_url__()
        data = entity.__odata__.copy()
        pk_name, pk_prop = entity.__odata_pk_property__()
        data.pop(pk_prop.name)

        saved_data = self.connection.execute_post(url, data)
        entity.__odata_dirty__ = []

        if saved_data is not None:
            entity.__odata__.update(saved_data)

    def _update_existing(self, entity):
        """
        Creates a PATCH call to the service, sending only the modified values
        """
        dirty_keys = list(set([prop.name for prop in entity.__odata_dirty__]))

        patch_data = dict([(key, entity.__odata__[key]) for key in dirty_keys])

        if len(patch_data) == 0:
            return

        instance_url = entity.__odata_instance_url__()

        saved_data = self.connection.execute_patch(instance_url, patch_data)
        entity.__odata_dirty__ = []

        if saved_data is None:
            saved_data = self.connection.execute_get(instance_url)

        if saved_data is not None:
            entity.__odata__.update(saved_data)
