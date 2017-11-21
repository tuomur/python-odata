# -*- coding: utf-8 -*-

"""
Querying
========

Entities can be queried from a service's singletons with a QuerySingle object:

.. code-block:: python

    query = Service.querySingle(Order)

Adding selects and other options always creates a new Query object with the
given directives:

.. code-block:: python

    >>> query.filter(Order.Name == 'Foo')
    <Query for <Order>>

This makes object chaining possible:

.. code-block:: python

    >>> first_order = query.filter(...).filter(...).order_by(...).first()

The resulting objects can be fetched with :py:func:`~QuerySingle.get`. 
Network is not accessed until this method is triggered.

Navigation properties can be loaded in the same request with 
:py:func:`~QuerySingle.expand`:

.. code-block:: python

    >>> querySingle.expand(Order.Shipper, Order.Customer)
    >>> order = querySingle.get()

----

API
---
"""

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin

import odata.exceptions as exc


class QuerySingle(object):
    """
    This class should not be instantiated directly, but from a
    :py:class:`~odata.service.ODataService` object.
    """
    def __init__(self, entitycls, connection=None, options=None):
        self.entity = entitycls
        self.options = options or dict()
        self.connection = connection

    def get(self):
        url = self._get_url()
        options = self._get_options()
        data = self.connection.execute_get(url, options)
        return self._create_model(data)
        

    def __repr__(self):
        return '<QuerySingle for {0}>'.format(self.entity)

    def __str__(self):
        return self.as_string()

    def _get_url(self):
        return self.entity.__odata_single_url__()

    def _get_options(self):
        """
        Format current query options to a dict that can be passed to requests
        :return: Dictionary
        """
        options = dict()

        _top = self.options.get('$top')
        if _top is not None:
            options['$top'] = _top

        _offset = self.options.get('$skip')
        if _offset is not None:
            options['$skip'] = _offset

        _select = self.options.get('$select')
        if _select:
            options['$select'] = ','.join(_select)

        _filters = self.options.get('$filter')
        if _filters:
            options['$filter'] = ' and '.join(_filters)

        _expand = self.options.get('$expand')
        if _expand:
            options['$expand'] = ','.join(_expand)

        _order_by = self.options.get('$orderby')
        if _order_by:
            options['$orderby'] = ','.join(_order_by)
        return options

    def _create_model(self, row):
        if len(self.options.get('$select', [])):
            return row
        else:
            e = self.entity.__new__(self.entity, from_data=row)
            es = e.__odata__
            es.connection = self.connection
            return e

    def _get_or_create_option(self, name):
        if name not in self.options:
            self.options[name] = []
        return self.options[name]

    def _format_params(self, options):
        return '&'.join(['='.join((key, str(value))) for key, value in options.items() if value is not None])

    def _new_query(self):
        """
        Create copy of this query without mutable values. All query builders
        should use this first.

        :return: Query instance
        """
        o = dict()
        o['$top'] = self.options.get('$top', None)
        o['$skip'] = self.options.get('$skip', None)
        o['$select'] = self.options.get('$select', [])[:]
        o['$filter'] = self.options.get('$filter', [])[:]
        o['$expand'] = self.options.get('$expand', [])[:]
        o['$orderby'] = self.options.get('$orderby', [])[:]
        return QuerySingle(self.entity, options=o, connection=self.connection)

    def as_string(self):
        query = self._format_params(self._get_options())
        return urljoin(self._get_url(), '?{0}'.format(query))

    # Query builders ###########################################################

    def select(self, *values):
        """
        Set properties to fetch instead of full Entity objects

        :return: Raw JSON values for given properties
        """
        q = self._new_query()
        option = q._get_or_create_option('$select')
        for prop in values:
            option.append(prop.name)
        return q

    def expand(self, *values):
        """
        Set ``$expand`` query parameter

        :param values: ``Entity.Property`` instance
        :return: Query instance
        """
        q = self._new_query()
        option = q._get_or_create_option('$expand')
        for prop in values:
            option.append(prop.name)
        return q
