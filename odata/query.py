# -*- coding: utf-8 -*-

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin

import odata.exceptions as exc


class Query(object):

    def __init__(self, entitycls, options=None):
        self.entity = entitycls
        """:type : odata.entity.EntityBase"""
        self.options = options or dict()

    def __iter__(self):
        connection = self._get_connection()
        url = self._get_url()
        options = self._get_options()
        while True:
            data = connection.execute_get(url, options)
            if 'value' in data:
                value = data.get('value', [])
                for row in value:
                    yield self._create_model(row)

                if '@odata.nextLink' in data:
                    url = urljoin(self.entity.__odata_url_base__, data['@odata.nextLink'])
                    options = {}  # we get all options in the nextLink url
                else:
                    break

    def __repr__(self):
        return '<Query for {0}>'.format(self.entity)

    def __str__(self):
        return self.as_string()

    def _get_connection(self):
        return self.entity.__odata_connection__

    def _get_url(self):
        return self.entity.__odata_url__()

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
            return self.entity.__new__(self.entity, from_data=row)

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
        return Query(self.entity, options=o)

    def as_string(self):
        query = self._format_params(self._get_options())
        return urljoin(self._get_url(), '?{0}'.format(query))

    # Query builders ###########################################################

    def select(self, *values):
        q = self._new_query()
        option = q._get_or_create_option('$select')
        for prop in values:
            option.append(prop.name)
        return q

    def filter(self, value):
        """
        Set $filter query parameter. Can be called multiple times. Multiple
        filter() calls are concatenated with 'and'
        :param value: Property comparison (Entity.Property == 2)
        :return: Query instance
        """
        q = self._new_query()
        option = q._get_or_create_option('$filter')
        option.append(value)
        return q

    def expand(self, *values):
        """
        Set $expand query parameter
        :param values: Entity.Property instance
        :return: Query instance
        """
        q = self._new_query()
        option = q._get_or_create_option('$expand')
        for prop in values:
            option.append(prop.name)
        return q

    def order_by(self, *values):
        """
        Set $orderby query parameter
        :param values: One of more of Property.asc() or Property.desc()
        :return: Query instance
        """
        q = self._new_query()
        option = q._get_or_create_option('$orderby')
        option.extend(values)
        return q

    def limit(self, value):
        """
        Set $top query parameter
        :param value: Number of records to return
        :return: Query instance
        """
        q = self._new_query()
        q.options['$top'] = value
        return q

    def offset(self, value):
        """
        Set $skip query parameter
        :param value: Number of records to skip
        :return: Query instance
        """
        q = self._new_query()
        q.options['$skip'] = value
        return q

    @staticmethod
    def and_(value1, value2):
        return '{0} and {1}'.format(value1, value2)

    @staticmethod
    def or_(value1, value2):
        return '{0} or {1}'.format(value1, value2)

    @staticmethod
    def grouped(value):
        return '({0})'.format(value)

    # Actions ##################################################################

    def all(self):
        """
        Returns a list of all Entity instances that match the current query
        :return: A list of Entity instances
        """
        return list(iter(self))

    def first(self):
        """
        Return the first Entity instance that matches current query
        :return: Entity instance or None
        """
        oldvalue = self.options.get('$top', None)
        self.options['$top'] = 1
        data = list(iter(self))
        self.options['$top'] = oldvalue
        if data:
            return data[0]

    def one(self):
        """
        Return only one resulting Entity. If no results are found, raises
        NoResultsFound. If multiple are found, raises MultipleResultsFound
        :return: Entity instance
        """
        oldlimit = self.options.get('$top', None)

        self.options['$top'] = 2
        data = self.all()

        self.options['$top'] = oldlimit
        if len(data) == 0:
            raise exc.NoResultsFound()
        if len(data) > 1:
            raise exc.MultipleResultsFound()
        return data[0]

    def get(self, pk):
        """
        Return a Entity with the given primary key.
        :param pk: Primary key value
        :return: Entity instance or None when not found.
        """
        i = self.entity.__new__(self.entity)
        es = i.__odata__
        _, prop = es.primary_key_property
        oldfilters = self._get_or_create_option('$filter')

        self.options['$filter'] = [prop == pk]
        data = list(iter(self))

        self.options['$filter'] = oldfilters
        if len(data) > 0:
            return data[0]
        raise exc.NoResultsFound()
