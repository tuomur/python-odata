# -*- coding: utf-8 -*-

"""
Connecting to an endpoint
=========================

A service object represents a single endpoint which has at least one EntitySet.
It is the cornerstone of this library. If you have multiple endpoints to
connect to, create multiple instances of :py:class:`ODataService`. All Entity
objects are each bound to exactly one Service and cannot be used across
multiple services.

Optionally, the Service object can connect to the endpoint and request its
metadata document. This document will then be used to build Entity objects
corresponding to each EntitySet provided by the endpoint. This operation
requires a working network connection to the endpoint. Creating an instance with
``reflect_entities=False`` will not cause any network activity.


Authentication
--------------

``auth`` and ``session`` keyword arguments to :py:class:`ODataService` are
passed as-is to Requests calls, so most of the same `guides`_ can be used.

.. _guides: http://docs.python-requests.org/en/master/user/authentication/


HTTP Basic authentication:

.. code-block:: python

    >>> from requests.auth import HTTPBasicAuth
    >>> my_auth = HTTPBasicAuth('username', 'password')
    >>> Service = ODataService('url', auth=my_auth)


NTLM Auth (for services like Microsoft Dynamics 2016):

.. code-block:: python

    >>> import requests
    >>> from requests_ntlm import HttpNtlmAuth
    >>> my_session = requests.Session()
    >>> my_session.auth = HttpNtlmAuth('domain\\username', 'password')
    >>> my_session.get('basic url')  # should return 200 OK
    >>> Service = ODataService('url', session=my_session)


----

API
---
"""

import logging

from .entity import EntityBase, declarative_base
from .connection import ODataConnection
from .metadata import MetaData
from .query import Query
from .exceptions import ODataError

__all__ = (
    'ODataService',
    'ODataError',
)


class ODataService(object):
    """
    :param url: Endpoint address. Must be an address that can be appended with ``$metadata``
    :param base: Custom base class to use for entities
    :param reflect_entities: Create a request to the service for its metadata, and create entity classes automatically
    :param session: Custom Requests session to use for communication with the endpoint
    :param auth: Custom Requests auth object to use for credentials
    :raises ODataConnectionError: Fetching metadata failed. Server returned an HTTP error code
    """
    def __init__(self, url, base=None, reflect_entities=False, session=None, auth=None):
        self.url = url
        self.metadata_url = ''
        self.collections = {}
        self.connection = ODataConnection(session=session, auth=auth)
        self.log = logging.getLogger('odata.service')

        self.entities = {}
        """
        A dictionary containing all the automatically created Entity classes.
        Empty if the service is created with ``reflect_entities=False``

        :type entities: dict
        """
        self.metadata = MetaData(self)

        self.Base = base or declarative_base()
        """
        Entity base class. Either a custom one given in init or a generated one. Can be used to define entities

        :type Base: EntityBase
        """

        if reflect_entities:
            _, self.entities = self.metadata.get_entity_sets(base=self.Base)

        self.Base.__odata_url_base__ = url
        self.Base.__odata_connection__ = self.connection

    def __repr__(self):
        return u'<ODataService at {0}>'.format(self.url)

    def describe(self, entity):
        """
        Print a debug screen of an entity instance

        :param entity: Entity instance to describe
        """
        entity.__odata__.describe()

    def query(self, entitycls):
        """
        Start a new query for given entity class

        :param entitycls: Entity to query
        :return: Query object
        """
        return Query(entitycls)

    def delete(self, entity):
        """
        Creates a DELETE call to the service, deleting the entity

        :type entity: EntityBase
        :raises ODataConnectionError: Delete not allowed or a serverside error. Server returned an HTTP error code
        """
        self.log.info(u'Deleting entity: {0}'.format(entity))
        url = entity.__odata__.instance_url
        self.connection.execute_delete(url)
        self.log.info(u'Success')

    def save(self, entity, force_refresh=True):
        """
        Creates a POST or PATCH call to the service. If the entity already has
        a primary key, an update is called. Otherwise the entity is inserted
        as new. Updating an entity will only send the changed values

        :param entity: Model instance to insert or update
        :param force_refresh: Read full entity data again from service after PATCH call
        :raises ODataConnectionError: Invalid data or serverside error. Server returned an HTTP error code
        """
        instance_url = entity.__odata__.instance_url

        if instance_url is None:
            self._insert_new(entity)
        else:
            self._update_existing(entity, force_refresh=force_refresh)

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

    def _update_existing(self, entity, force_refresh=True):
        """
        Creates a PATCH call to the service, sending only the modified values

        :type entity: EntityBase
        """
        es = entity.__odata__
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
