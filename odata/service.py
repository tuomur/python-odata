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
from .metadata import MetaData
from .exceptions import ODataError
from .context import Context
from .action import Action, Function

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
        self.log = logging.getLogger('odata.service')
        self.default_context = Context(auth=auth, session=session)

        self.entities = {}
        """
        A dictionary containing all the automatically created Entity classes.
        Empty if the service is created with ``reflect_entities=False``

        :type entities: dict
        """
        self.actions = {}
        """
        A dictionary containing all the automatically created unbound Action
        callables. Empty if the service is created with
        ``reflect_entities=False``

        :type actions: dict
        """
        self.functions = {}
        """
        A dictionary containing all the automatically created unbound Function
        callables. Empty if the service is created with
        ``reflect_entities=False``

        :type functions: dict
        """
        self.types = {}
        """
        A dictionary containing all types (EntityType, EnumType) created
        during reflection. Empty if the service is created with
        ``reflect_entities=False``

        :type types: dict
        """

        self.metadata = MetaData(self)
        self.Base = base or declarative_base()
        """
        Entity base class. Either a custom one given in init or a generated one. Can be used to define entities

        :type Base: EntityBase
        """
        self.Entity = self.Base  # alias

        self.Action = type('Action', (Action,), dict(__odata_service__=self))
        """
        A baseclass for this service's Actions

        :type Action: Action
        """

        self.Function = type('Function', (Function,), dict(__odata_service__=self))
        """
        A baseclass for this service's Functions

        :type Function: Function
        """

        if reflect_entities:
            _, self.entities, self.types = self.metadata.get_entity_sets(base=self.Entity)

        self.Entity.__odata_url_base__ = url
        self.Entity.__odata_service__ = self

    def __repr__(self):
        return u'<ODataService at {0}>'.format(self.url)

    def create_context(self, auth=None, session=None):
        """
        Create new context to use for session-like usage

        :param auth: Custom Requests auth object to use for credentials
        :param session: Custom Requests session to use for communication with the endpoint
        :return: Context instance
        :rtype: Context
        """
        return Context(auth=auth, session=session)

    def describe(self, entity):
        """
        Print a debug screen of an entity instance

        :param entity: Entity instance to describe
        """
        entity.__odata__.describe()

    def is_entity_saved(self, entity):
        """Returns boolean indicating entity's status"""
        return self.default_context.is_entity_saved(entity)

    def query(self, entitycls):
        """
        Start a new query for given entity class

        :param entitycls: Entity to query
        :return: Query object
        """
        return self.default_context.query(entitycls)

    def delete(self, entity):
        """
        Creates a DELETE call to the service, deleting the entity

        :type entity: EntityBase
        :raises ODataConnectionError: Delete not allowed or a serverside error. Server returned an HTTP error code
        """
        return self.default_context.delete(entity)

    def save(self, entity, force_refresh=True):
        """
        Creates a POST or PATCH call to the service. If the entity already has
        a primary key, an update is called. Otherwise the entity is inserted
        as new. Updating an entity will only send the changed values

        :param entity: Model instance to insert or update
        :param force_refresh: Read full entity data again from service after PATCH call
        :raises ODataConnectionError: Invalid data or serverside error. Server returned an HTTP error code
        """
        return self.default_context.save(entity, force_refresh=force_refresh)
