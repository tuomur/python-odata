# -*- coding: utf-8 -*-

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin


class Query(object):

    def __init__(self, entitycls):
        self.entity = entitycls
        self.connection = entitycls.__odata_connection__
        self.url = entitycls.__odata_url__()
        self.model = None

        self._select = []
        self._filters = []
        self._expand = []
        self._order_by = []
        self.limit = 1000
        self.offset = 0

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
        options = {
            '$top': self.limit,
            '$skip': self.offset,
        }

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
        return [row for row in self.__iter__()]

    def first(self):
        oldvalue = self.limit
        self.limit = 1
        data = [row for row in self.__iter__()]
        self.limit = oldvalue
        if data:
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
