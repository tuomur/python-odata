# -*- coding: utf-8 -*-

try:
    # noinspection PyUnresolvedReferences
    from urllib.parse import urljoin
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin
from collections import OrderedDict


class ActionBase(object):

    __odata_service__ = None

    name = None
    """
    Action's fully qualified name (usually SchemaName.ActionName)

    :type name: str
    """

    parameters = None
    """
    A dictionary that defines what keyword arguments and what types this Action
    accepts. For example, ``dict(productId=IntegerProperty)``

    :type name: dict
    """

    return_parameters = None

    def __get__(self, instance, owner):
        # return a callable that acts on EntitySet or the Entity itself
        url = None
        if instance:
            # /MyEntity(1234)/SchemaName.ActionName
            url = instance.__odata__.instance_url

        # default to /MyEntity/SchemaName.ActionName
        url = url or owner.__odata_url__()

        def call(**kwargs):
            connection = self._get_context_or_default_connection(kwargs)
            return self._callable(connection, url, **kwargs)

        return call

    def __call__(self, *args, **kwargs):
        connection = self._get_context_or_default_connection(kwargs)
        url = self.__odata_service__.url
        return self._callable(connection, url, **kwargs)

    def _get_context_or_default_connection(self, kwargs):
        connection = kwargs.pop('__connection__', None)
        connection = connection or self.__odata_service__.default_context.connection
        return connection

    def _check_call_arguments(self, kwargs):
        incorrect_keys = set(kwargs.keys()) != set(self.parameters.keys())
        if incorrect_keys:
            received_keys = ','.join(kwargs.keys())
            expected_keys = ','.join(self.parameters.keys())
            errmsg = 'Received keyword arguments: \'{}\', required: \'{}\''
            errmsg = errmsg.format(received_keys, expected_keys)
            raise TypeError(errmsg)

    def _callable(self, connection, url, **kwargs):
        self._check_call_arguments(kwargs)

        if not url.endswith('/'):
            url += '/'
        url += self.name

        response_data = self._execute_http(connection, url, kwargs)
        response_data = (response_data or {}).get('value')

        if self.return_parameters and response_data:
            # TODO: add support for collections
            return_data = OrderedDict()
            for key, value in response_data.items():
                prop_type = self.return_parameters.get(key)
                return_data[key] = prop_type('temp').deserialize(value)
            return return_data
        return response_data

    def _execute_http(self, connection, url, kwargs):
        raise NotImplementedError()


class Action(ActionBase):

    name = 'ODataSchema.Action'

    def _execute_http(self, connection, url, kwargs):
        # Execute http POST, encoding kwargs to json body
        data = OrderedDict()
        for key, value in kwargs.items():
            prop_type = self.parameters.get(key)
            escaped_value = prop_type('temp').serialize(value)
            data[key] = escaped_value

        return connection.execute_post(url, data)


class Function(ActionBase):

    name = 'ODataSchema.Function'

    def _execute_http(self, connection, url, kwargs):
        # Execute http GET, passing kwargs as parameters in url
        kwargs_escaped = []
        for key, value in kwargs.items():
            prop_type = self.parameters.get(key)
            escaped_value = prop_type('temp').escape_value(value)
            kwargs_escaped.append((key, escaped_value))

        kwargs_escaped = sorted(kwargs_escaped, key=lambda x: x[0])
        params = ['='.join([key, str(value)]) for key, value in kwargs_escaped]
        params = ','.join(params)
        url += '({0})'.format(params)

        return connection.execute_get(url)
