# python-odata

A simple library for read/write access to OData services.

- Supports OData version 4.0
- Requires JSON format support from the service
- Should work on both Python 2.x and 3.x

## Documentation

Available on [readthedocs.org](http://tuomur-python-odata.readthedocs.org/en/latest/)

## Dependencies

- requests >= 2.0
- python-dateutil

## Demo

Reading data from the Northwind service.

```python
from odata import ODataService
url = 'http://services.odata.org/V4/Northwind/Northwind.svc/'
Service = ODataService(url, reflect_entities=True)
Supplier = Service.entities['Supplier']

query = Service.query(Supplier)
query = query.limit(2)
query = query.order_by(Supplier.CompanyName.asc())

for supplier in query:
    print('Company:', supplier.CompanyName)

    for product in supplier.Products:
        print('- Product:', product.ProductName)
```

Writing changes. Note that the real Northwind service is _read-only_
and the data modifications do not work against it.

```python
import datetime

Order = Service.entities['Order']
Employee = Service.entities['Employee']

empl = Service.query(Employee).first()

query = Service.query(Order)
query = query.filter(Order.ShipCity == 'Berlin')

for order in query:
    order.ShippedDate = datetime.datetime.utcnow() 
    order.Employee = empl
    Service.save(order)
```

## Running tests

To run the tests, you can use pytest or unittest:

- python -m pytest
- python -m unittest discover

To include tests that call the Northwind service, set the envionment variable:

```
export ODATA_DO_REMOTE_TESTS=1
```

The Northwind tests are automatically skipped if it cannot connect to the service.

Test dependency:
- responses
