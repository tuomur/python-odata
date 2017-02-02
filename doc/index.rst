.. python-odata documentation master file, created by
   sphinx-quickstart on Thu Feb 18 15:45:14 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-odata's documentation!
========================================

What is this?
-------------

A simple library to consume an OData 4.0 endpoint. For example, an endpoint
created with Microsoft's WebAPI 2.2. This library exposes the OData entities
in a manner that mimics some of the modern ORM libraries for easy usage.

Features:

- Supports OData version 4.0 with JSON format
- Supports creating, reading, updating and deleting data
- Supports simple queries on EntitySets
- Powered by the excellent Requests library


Not currently supported:

- ATOM format
- ComplexTypes
- Streams
- Most of the more intricate querying options

Project source code and issue tracker: `GitHub`_

.. _GitHub: https://github.com/tuomur/python-odata

Code example
------------

Connecting to a service and building entity classes from the service's metadata:

.. code-block:: python

   from odata import ODataService
   url = 'http://services.odata.org/V4/Northwind/Northwind.svc/'
   Service = ODataService(url, reflect_entities=True)

Fetch the Order entity from reflected classes:

.. code-block:: python

    Order = Service.entities['Order']

Query some orders:

.. code-block:: python

    query = Service.query(Order)
    query = query.filter(Order.Name.startswith('Demo'))
    query = query.order_by(Order.ShippedDate.desc())
    for order in query:
        print(order.Name)


Topics
------

.. toctree::
   :maxdepth: 1

   service
   query
   entity
   action
   property
   exceptions


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
