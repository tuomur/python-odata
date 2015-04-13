
# Examples

## Reading data from service

This library mimics the SQLAlchemy API to some degree. Defining models is done
in a similar fashion:

    from odata import ODataService
    from odata.entity import declarative_base, StringProperty

    Base = declarative_base()

    class Customer(Base):
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

Creating the service object:

    url = 'http://services.odata.org/V4/Northwind/Northwind.svc/'
    NorthwindService = ODataService(url, base=Base)

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


## Reflection

The models can be read from the service metadata as well, without defining any 
classes yourself. The metadata document is fetched once at `ODataService` init.

    NorthwindService = ODataService(url, reflect_entities=True)
    Customer = NorthwindService.entities.get('Customer')
    
    c = NorthwindService.query(Customer).first()
    c.Address = 'Somewhere else'
    NorthwindService.save(c)


## Inserting new data to service

Create a new instance of the model with some data:

    new_customer = Customer()
    new_customer.name = 'Offworld Trading Company'
    new_customer.country = 'Mars'

Save the instance:

    NorthwindService.save(new_customer)

Any values that are generated server-side are updated to the object:

    >>> new_customer.id
    8364


## Updating data

Any modifications done to the entity can be saved by calling `ODataService.save()` again.
This sends only the changed values to the service with a HTTP PATCH call.

    new_customer.address = 'Street 123'
    NorthwindService.save(new_customer)


## Deleting data

Call the service method:

    NorthwindService.delete(new_customer)


## Authentication

The _auth_ parameter is passed as-is to requests:

    from requests.auth import HTTPBasicAuth
    my_auth = HTTPBasicAuth('user', 'pass')
    MyService = ODataService(url, Base, auth=my_auth)


Any requests-like session can be used as well:

    from requests_oauthlib import OAuth2Session
    my_session = OAuth2Session(client_id, token=token)
    MyService = ODataService(url, Base, session=my_session)


## Exceptions

All exceptions are derived from `odata.exceptions.ODataError`. The exception's 
`message` property contains the error message received from the service.
