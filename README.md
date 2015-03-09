# python-odata

A simple library for read/write access to OData services I hacked together.

- Supports OData version 3.0 (Not tested on anything else, really)
- Requires JSON format support from the service
- Pure Python
- Should work on both Python 2.x and 3.x


## Examples

### Reading data from service

Create a new instance of the _Service_ class with the OData endpoint URL:

    from odata import ODataService
    
    NorthwindService = ODataService('http://services.odata.org/V3/Northwind/Northwind.svc/')

The generated _ODataService_ object has a property called _Entity_ which you 
can subclass to create model classes of the data (a Collection) you are 
accessing:

    from odata.entity import StringProperty

    class Customer(NorthwindService.Entity):
        __odata_collection__ = 'Customers'
        __odata_type__ = 'NorthwindModel.Customer'
    
        id = StringProperty('CustomerID', primary_key=True)
        name = StringProperty('CompanyName')
        contact_name = StringProperty('ContactName')
        contact_title = StringProperty('ContactTitle')
        address = StringProperty('Address')
        city = StringProperty('City')
        region = StringProperty('Region')
        postal_code = StringProperty('PostalCode')
        country = StringProperty('Country')
        phone = StringProperty('Phone')
        fax = StringProperty('Fax')

Read a single entry from the collection:

    query = NorthwindService.query(Customer)
    customer1 = query.first()

Filter the entries:

    query.filter(Customer.city == 'Berlin')

    query.filter(Customer.contact_title.startswith('Sales'))

Order the entries:

    query.order_by(Customer.name.desc())

Iterate over the results:

    for customer in query:
        print customer.id, customer.name


### Inserting new data to service

Create a new instance of the model with some data:

    new_customer = Customer()
    new_customer.name = 'Offworld Trading Company'
    new_customer.country = 'Mars'

Save the instance:

    NorthwindService.save(new_customer)

Any values that are generated server-side are updated to the object:

    >>> new_customer.id
    8364


### Authentication

The _auth_ parameter is passed as-is to requests:


    from requests.auth import HTTPBasicAuth
    my_auth = HTTPBasicAuth('user', 'pass')
    NorthwindService = ODataService('http://services.odata.org/V3/Northwind/Northwind.svc/', auth=my_auth)


Any requests-like session can be used as well:

    from requests_oauthlib import OAuth2Session
    my_session = OAuth2Session(client_id, token=token)
    NorthwindService = ODataService('http://services.odata.org/V3/Northwind/Northwind.svc/', session=my_session)
