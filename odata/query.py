# -*- coding: utf-8 -*-

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin

import odata.exceptions as exc


class Query(object):

    def __init__(self, entitycls):
        self.entity = entitycls
        """:type : odata.entity.EntityBase"""
        self.connection = entitycls.__odata_connection__
        self.url = entitycls.__odata_url__()
        self.model = None

        self._select = []
        self._filters = []
        self._expand = []
        self._order_by = []
        self.limit = None
        self.offset = None

    def __iter__(self):
        while True:
            data = self.connection.execute_get(self.url, self._get_options())
            if 'value' in data:
                value = data.get('value', [])
                value_length = len(value)
                for row in value:
                    yield self._create_model(row)

                if '@odata.nextLink' in data:
                    self.offset += value_length
                else:
                    break
        self.offset = 0

    def __repr__(self):
        return '<Query for {0}>'.format(self.entity)

    def __str__(self):
        return self.as_string()

    def _create_model(self, row):
        if len(self._select):
            return row
        else:
            return self.entity.__new__(self.entity, from_data=row)

    def _format_params(self, options):
        return '&'.join(['='.join((key, str(value))) for key, value in options.items() if value is not None])

    def _get_options(self):
        options = dict()

        if self.limit is not None:
            options['$top'] = self.limit

        if self.offset is not None:
            options['$skip'] = self.offset

        if self._select:
            options['$select'] = ','.join(self._select)

        if self._filters:
            options['$filter'] = ' and '.join(self._filters)

        if self._expand:
            options['$expand'] = ','.join(self._expand)

        if self._order_by:
            options['$orderby'] = ','.join(self._order_by)
        return options

    def as_string(self):
        query = self._format_params(self._get_options())
        return urljoin(self.url, '?{0}'.format(query))

    def select(self, *values):
        for prop in values:
            self._select.append(prop.name)

    def filter(self, value):
        self._filters.append(value)

    def expand(self, *values):
        for prop in values:
            self._expand.append(prop.name)

    def order_by(self, *values):
        self._order_by.extend(values)

    def all(self):
        return list(iter(self))

    def first(self):
        oldvalue = self.limit
        self.limit = 1
        data = list(iter(self))
        self.limit = oldvalue
        if data:
            return data[0]

    def one(self):
        oldlimit = self.limit

        self.limit = 2
        data = self.all()

        self.limit = oldlimit
        if len(data) == 0:
            raise exc.NoResultsFound()
        if len(data) > 1:
            raise exc.MultipleResultsFound()
        return data[0]

    def get(self, pk):
        i = self.entity.__new__(self.entity)
        es = i.__odata__
        _, prop = es.primary_key_property
        oldfilters = self._filters

        self._filters = [prop == pk]
        data = list(iter(self))

        self._filters = oldfilters
        if len(data) > 0:
            return data[0]

    @staticmethod
    def and_(value1, value2):
        return '{0} and {1}'.format(value1, value2)

    @staticmethod
    def or_(value1, value2):
        return '{0} or {1}'.format(value1, value2)

    @staticmethod
    def grouped(value):
        return '({0})'.format(value)
