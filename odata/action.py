# -*- coding: utf-8 -*-

"""
Actions, Functions
==================

Actions and Functions are set up automatically when using reflection. Unbound
callables are collected in :py:attr:`~odata.service.ODataService.actions` and
:py:attr:`~odata.service.ODataService.functions`. Bound callables are assigned
to the Entity classes they are bound to.

.. code-block:: python

    >>> from odata import ODataService
    >>> Service = ODataService(url, reflect_entities=True)
    >>> Product = Service.entities['Product']

    >>> prod = Service.query(Product).get(1234)
    >>> prod.GetAvailabilityDate()
    datetime.datetime(2018, 6, 1, 12, 0, 0)

    >>> import datetime
    >>> GetExampleDecimal = Service.functions['GetExampleDecimal']
    >>> GetExampleDecimal(Date=datetime.datetime.now())
    Decimal('34.0')


Unbound action/functions
------------------------

Similar to Entities, Functions are subclassed from the Service baseclasses
:py:attr:`~odata.service.ODataService.Action` and
:py:attr:`~odata.service.ODataService.Function`:

.. code-block:: python

    Service = ODataService(url)

    class _GetExampleDecimal(Service.Function):
        name = 'GetExampleDecimal'
        parameters = dict(
            Date=DatetimeProperty,
        )
        return_type = DecimalProperty

    GetExampleDecimal = _GetExampleDecimal()

Usage:

.. code-block:: python

    >>> import datetime
    >>> # calls GET http://service/GetExampleDecimal(Date=2017-01-01T12:00:00Z)
    >>> GetExampleDecimal(Date=datetime.datetime.now())
    Decimal('34.0')


Bound action/function
---------------------

Bound functions are otherwise the same, but the instanced object should be set
under the Entity it belongs to:

.. code-block:: python

    class _GetAvailabilityDate(Service.Function):
        name = 'ODataService.GetAvailabilityDate'
        parameters = dict()
        return_type = DatetimeProperty

    class _RemoveAllReservations(Service.Action):
        name = 'ODataService.RemoveAllReservations'
        parameters = dict()
        return_type = BooleanProperty

    class _ReserveAmount(Service.Action):
        name = 'ODataService.ReserveAmount'
        parameters = dict(
            Amount=DecimalProperty,
        )
        return_type = BooleanProperty

    class Product(Service.Entity):
        Id = IntegerProperty('Id', primary_key=True)
        Name = StringProperty('Name')

        GetAvailabilityDate = GetAvailabilityDate()
        RemoveAllReservations = _RemoveAllReservations()
        ReserveAmount = _ReserveAmount()

Usage:

.. code-block:: python

    >>> # collection bound Action. calls POST http://service/Product/ODataService.RemoveAllReservations
    >>> Product.RemoveAllReservations()
    True

    >>> # if the Action is instance bound, call the Action from the Product instance instead
    >>> from decimal import Decimal
    >>> prod = Service.query(Product).get(1234)
    >>> # calls POST http://service/Product(1234)/ODataService.ReserveAmount
    >>> prod.ReserveAmount(Amount=Decimal('5.0'))
    True

    >>> # calls GET http://service/Product(1234)/ODataService.GetAvailabilityDate()
    >>> prod.GetAvailabilityDate()
    datetime.datetime(2018, 6, 1, 12, 0, 0)


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
from collections import OrderedDict


class ActionCallable(object):
    """
    A helper class for ActionBase, representing a callable
    """
    def __init__(self, actionbase_instance, url, errmsg=None):
        self.actionbase_instance = actionbase_instance
        self.url = url
        self.errmsg = errmsg
        self.query = None

    def __repr__(self):
        name = self.actionbase_instance.name
        url = self.url + '/' + name
        return '<Callable for {0}>'.format(url)

    def with_query(self, query):
        self.query = query
        return self

    def __call__(self, **kwargs):
        if self.errmsg is not None:
            raise AttributeError(self.errmsg)

        connection = self.actionbase_instance._get_context_or_default_connection(kwargs)
        return self.actionbase_instance._callable(connection, self.url, self.query, **kwargs)


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

    :type parameters: dict
    """

    return_type_collection = None
    """
    Reference to the returned value's type, when retuning multiple values.
    Entity or Property class
    """
    return_type = None
    """
    Reference to the returned value's type. Entity or Property class
    """

    bound_to_collection = False
    """
    Action is bound to Entity collection. If True, Action is not available in
    Entity class instances. If False, Action is not available in Entity class
    objects
    """

    def __get__(self, instance, owner):
        # return a callable that acts on EntitySet or the Entity itself

        errmsg = None
        if self.bound_to_collection and instance is not None:
            errmsg = '{0} is bound to collection {1}'.format(self.name, owner)
        if self.bound_to_collection is False:
            if instance is None:
                errmsg = '{0} is bound to instances of {1}'.format(self.name, owner)
            else:
                es = instance.__odata__
                if es.persisted is False:
                    errmsg = ('Trying to call instance bound Action or '
                              'Function \'{0}\', but instance {1} is not saved'
                              ''.format(self.name, instance))

        url = None
        if instance:
            # /MyEntity(1234)/SchemaName.ActionName
            url = instance.__odata__.instance_url

        # default to /MyEntity/SchemaName.ActionName
        url = url or owner.__odata_url__()

        ac = ActionCallable(self, url, errmsg=errmsg)
        return ac

    def __call__(self, **kwargs):
        url = self.__odata_service__.url
        ac = ActionCallable(self, url)
        # call immediately, otherwise user needs to double-call. this removes
        # the ability to query results
        return ac(**kwargs)

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

    def _callable(self, connection, url, query, **kwargs):
        self._check_call_arguments(kwargs)

        if not url.endswith('/'):
            url += '/'
        url += self.name

        query_options = None
        if query:
            query_options = query._get_options()

        response_data = self._execute_http(connection, url, query_options, kwargs)
        response_data = (response_data or {}).get('value')

        simple_types_values = self.__odata_service__.metadata.property_types.values()

        if self.return_type_collection:
            if self.return_type_collection in simple_types_values:
                values_collection = []
                prop = self.return_type_collection
                for value in response_data:
                    deserialized = prop('temp').deserialize(value)
                    values_collection.append(deserialized)
                return values_collection

            entity_collection = []
            for value in (response_data or []):
                entity_instance = self.return_type_collection.__new__(self.return_type_collection, from_data=value)
                entity_collection.append(entity_instance)
            return entity_collection

        if self.return_type:
            if self.return_type in simple_types_values:
                prop = self.return_type
                return prop('temp').deserialize(response_data)

            entity_instance = self.return_type.__new__(self.return_type, from_data=response_data)
            return entity_instance

        # no defined type, return whatever we got
        return response_data

    def _execute_http(self, connection, url, query_options, kwargs):
        raise NotImplementedError()


class Action(ActionBase):
    """
    Baseclass for all Actions. Should not be used directly, use the
    subclass :py:class:`~odata.service.ODataService.Action` instead.

    .. py:attribute:: name

        Action's fully qualified name. Bound Actions are prefixed with their
        schema's name (``SchemaName.ActionName``).
        **Required when subclassing**

    .. py:attribute:: parameters

        Dictionary. Defines all the keyword arguments and their types the
        Action can accept. Key names must match with ones accepted by the
        server.
        **Required when subclassing**

    .. py:attribute:: return_type

        Reference to either Entity class or Property class. Defines the return
        value's type for this Action.
        **Required when subclassing**

    .. py:attribute:: return_type_collection

        Reference to either Entity class or Property class. Defines the return
        value's type for this Action when retuning multiple values.
        **Required when subclassing**

    .. py:attribute:: bound_to_collection

        Action is bound to Entity collection. If True, Action is not available
        in Entity class instances. If False, Action is not available in Entity
        class objects. Defaults to *false*
    """

    name = 'ODataSchema.Action'

    def _execute_http(self, connection, url, query_options, kwargs):
        # Execute http POST, encoding kwargs to json body
        data = OrderedDict()
        for key, value in kwargs.items():
            prop_type = self.parameters.get(key)
            escaped_value = prop_type('temp').serialize(value)
            data[key] = escaped_value

        return connection.execute_post(url, data, params=query_options)


class Function(ActionBase):
    """
    Baseclass for all Functions. Should not be used directly, use the
    subclass :py:class:`~odata.service.ODataService.Function` instead.

    .. py:attribute:: name

        Function's fully qualified name. Function Actions are prefixed with
        their schema's name (``SchemaName.FunctionName``).
        **Required when subclassing**

    .. py:attribute:: parameters

        Dictionary. Defines all the keyword arguments and their types the
        Function can accept. Key names must match with ones accepted by the
        server.
        **Required when subclassing**

    .. py:attribute:: return_type

        Reference to either Entity class or Property class. Defines the return
        value's type for this Function.
        **Required when subclassing**

    .. py:attribute:: return_type_collection

        Reference to either Entity class or Property class. Defines the return
        value's type for this Function when retuning multiple values.
        **Required when subclassing**

    .. py:attribute:: bound_to_collection

        Function is bound to Entity collection. If True, Function is not
        available in Entity class instances. If False, Function is not
        available in Entity class objects. Defaults to *false*
    """

    name = 'ODataSchema.Function'

    def _execute_http(self, connection, url, query_options, kwargs):
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

        return connection.execute_get(url, params=query_options)
