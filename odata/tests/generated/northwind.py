import datetime
import uuid
import decimal

from odata.entity import EntityBase
from odata.property import StringProperty, IntegerProperty, NavigationProperty, DatetimeProperty, DecimalProperty, FloatProperty, BooleanProperty, UUIDProperty

class ReflectionBase(EntityBase):
    pass


# ************ Start type definitions ************
class Category(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Category"
  
    # Simple properties
    CategoryID: int = IntegerProperty("CategoryID", primary_key=True)
    CategoryName: str = StringProperty("CategoryName")
    Description: str = StringProperty("Description")
    Picture: str = StringProperty("Picture")

    # Navigation properties
    Products: list["Product"] = NavigationProperty(name="Products", entity_package="generated.northwind", entitycls="Product", collection=True)


class CustomerDemographic(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.CustomerDemographic"
  
    # Simple properties
    CustomerTypeID: str = StringProperty("CustomerTypeID", primary_key=True)
    CustomerDesc: str = StringProperty("CustomerDesc")

    # Navigation properties
    Customers: list["Customer"] = NavigationProperty(name="Customers", entity_package="generated.northwind", entitycls="Customer", collection=True)


class Customer(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Customer"
  
    # Simple properties
    CustomerID: str = StringProperty("CustomerID", primary_key=True)
    CompanyName: str = StringProperty("CompanyName")
    ContactName: str = StringProperty("ContactName")
    ContactTitle: str = StringProperty("ContactTitle")
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")
    Phone: str = StringProperty("Phone")
    Fax: str = StringProperty("Fax")

    # Navigation properties
    Orders: list["Order"] = NavigationProperty(name="Orders", entity_package="generated.northwind", entitycls="Order", collection=True)
    CustomerDemographics: list["CustomerDemographic"] = NavigationProperty(name="CustomerDemographics", entity_package="generated.northwind", entitycls="CustomerDemographic", collection=True)


class Employee(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Employee"
  
    # Simple properties
    EmployeeID: int = IntegerProperty("EmployeeID", primary_key=True)
    LastName: str = StringProperty("LastName")
    FirstName: str = StringProperty("FirstName")
    Title: str = StringProperty("Title")
    TitleOfCourtesy: str = StringProperty("TitleOfCourtesy")
    BirthDate: datetime.datetime = DatetimeProperty("BirthDate")
    HireDate: datetime.datetime = DatetimeProperty("HireDate")
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")
    HomePhone: str = StringProperty("HomePhone")
    Extension: str = StringProperty("Extension")
    Photo: str = StringProperty("Photo")
    Notes: str = StringProperty("Notes")
    ReportsTo: int = IntegerProperty("ReportsTo")
    PhotoPath: str = StringProperty("PhotoPath")

    # Navigation properties
    Employees1: list["Employee"] = NavigationProperty(name="Employees1", entity_package="generated.northwind", entitycls="Employee", collection=True)
    Employee1: "Employee" = NavigationProperty(name="Employee1", entity_package="generated.northwind", entitycls="Employee", foreign_key=ReportsTo)
    Orders: list["Order"] = NavigationProperty(name="Orders", entity_package="generated.northwind", entitycls="Order", collection=True)
    Territories: list["Territory"] = NavigationProperty(name="Territories", entity_package="generated.northwind", entitycls="Territory", collection=True)


class Order_Detail(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Order_Detail"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice")
    Quantity: int = IntegerProperty("Quantity")
    Discount: decimal.Decimal = DecimalProperty("Discount")

    # Navigation properties
    Order: "Order" = NavigationProperty(name="Order", entity_package="generated.northwind", entitycls="Order", foreign_key=OrderID)
    Product: "Product" = NavigationProperty(name="Product", entity_package="generated.northwind", entitycls="Product", foreign_key=ProductID)


class Order(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Order"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    CustomerID: str = StringProperty("CustomerID")
    EmployeeID: int = IntegerProperty("EmployeeID")
    OrderDate: datetime.datetime = DatetimeProperty("OrderDate")
    RequiredDate: datetime.datetime = DatetimeProperty("RequiredDate")
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    ShipVia: int = IntegerProperty("ShipVia")
    Freight: decimal.Decimal = DecimalProperty("Freight")
    ShipName: str = StringProperty("ShipName")
    ShipAddress: str = StringProperty("ShipAddress")
    ShipCity: str = StringProperty("ShipCity")
    ShipRegion: str = StringProperty("ShipRegion")
    ShipPostalCode: str = StringProperty("ShipPostalCode")
    ShipCountry: str = StringProperty("ShipCountry")

    # Navigation properties
    Customer: "Customer" = NavigationProperty(name="Customer", entity_package="generated.northwind", entitycls="Customer", foreign_key=CustomerID)
    Employee: "Employee" = NavigationProperty(name="Employee", entity_package="generated.northwind", entitycls="Employee", foreign_key=EmployeeID)
    Order_Details: list["Order_Detail"] = NavigationProperty(name="Order_Details", entity_package="generated.northwind", entitycls="Order_Detail", collection=True)
    Shipper: "Shipper" = NavigationProperty(name="Shipper", entity_package="generated.northwind", entitycls="Shipper", foreign_key=ShipVia)


class Product(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Product"
  
    # Simple properties
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName")
    SupplierID: int = IntegerProperty("SupplierID")
    CategoryID: int = IntegerProperty("CategoryID")
    QuantityPerUnit: str = StringProperty("QuantityPerUnit")
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice")
    UnitsInStock: int = IntegerProperty("UnitsInStock")
    UnitsOnOrder: int = IntegerProperty("UnitsOnOrder")
    ReorderLevel: int = IntegerProperty("ReorderLevel")
    Discontinued: bool = BooleanProperty("Discontinued")

    # Navigation properties
    Category: "Category" = NavigationProperty(name="Category", entity_package="generated.northwind", entitycls="Category", foreign_key=CategoryID)
    Order_Details: list["Order_Detail"] = NavigationProperty(name="Order_Details", entity_package="generated.northwind", entitycls="Order_Detail", collection=True)
    Supplier: "Supplier" = NavigationProperty(name="Supplier", entity_package="generated.northwind", entitycls="Supplier", foreign_key=SupplierID)


class Region(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Region"
  
    # Simple properties
    RegionID: int = IntegerProperty("RegionID", primary_key=True)
    RegionDescription: str = StringProperty("RegionDescription")

    # Navigation properties
    Territories: list["Territory"] = NavigationProperty(name="Territories", entity_package="generated.northwind", entitycls="Territory", collection=True)


class Shipper(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Shipper"
  
    # Simple properties
    ShipperID: int = IntegerProperty("ShipperID", primary_key=True)
    CompanyName: str = StringProperty("CompanyName")
    Phone: str = StringProperty("Phone")

    # Navigation properties
    Orders: list["Order"] = NavigationProperty(name="Orders", entity_package="generated.northwind", entitycls="Order", collection=True)


class Supplier(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Supplier"
  
    # Simple properties
    SupplierID: int = IntegerProperty("SupplierID", primary_key=True)
    CompanyName: str = StringProperty("CompanyName")
    ContactName: str = StringProperty("ContactName")
    ContactTitle: str = StringProperty("ContactTitle")
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")
    Phone: str = StringProperty("Phone")
    Fax: str = StringProperty("Fax")
    HomePage: str = StringProperty("HomePage")

    # Navigation properties
    Products: list["Product"] = NavigationProperty(name="Products", entity_package="generated.northwind", entitycls="Product", collection=True)


class Territory(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Territory"
  
    # Simple properties
    TerritoryID: str = StringProperty("TerritoryID", primary_key=True)
    TerritoryDescription: str = StringProperty("TerritoryDescription")
    RegionID: int = IntegerProperty("RegionID")

    # Navigation properties
    Region: "Region" = NavigationProperty(name="Region", entity_package="generated.northwind", entitycls="Region", foreign_key=RegionID)
    Employees: list["Employee"] = NavigationProperty(name="Employees", entity_package="generated.northwind", entitycls="Employee", collection=True)


class Alphabetical_list_of_product(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Alphabetical_list_of_product"
  
    # Simple properties
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    SupplierID: int = IntegerProperty("SupplierID")
    CategoryID: int = IntegerProperty("CategoryID")
    QuantityPerUnit: str = StringProperty("QuantityPerUnit")
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice")
    UnitsInStock: int = IntegerProperty("UnitsInStock")
    UnitsOnOrder: int = IntegerProperty("UnitsOnOrder")
    ReorderLevel: int = IntegerProperty("ReorderLevel")
    Discontinued: bool = BooleanProperty("Discontinued", primary_key=True)
    CategoryName: str = StringProperty("CategoryName", primary_key=True)

    # Navigation properties


class Category_Sales_for_1997(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Category_Sales_for_1997"
  
    # Simple properties
    CategoryName: str = StringProperty("CategoryName", primary_key=True)
    CategorySales: decimal.Decimal = DecimalProperty("CategorySales")

    # Navigation properties


class Current_Product_List(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Current_Product_List"
  
    # Simple properties
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)

    # Navigation properties


class Customer_and_Suppliers_by_City(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Customer_and_Suppliers_by_City"
  
    # Simple properties
    City: str = StringProperty("City")
    CompanyName: str = StringProperty("CompanyName", primary_key=True)
    ContactName: str = StringProperty("ContactName")
    Relationship: str = StringProperty("Relationship", primary_key=True)

    # Navigation properties


class Invoice(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Invoice"
  
    # Simple properties
    ShipName: str = StringProperty("ShipName")
    ShipAddress: str = StringProperty("ShipAddress")
    ShipCity: str = StringProperty("ShipCity")
    ShipRegion: str = StringProperty("ShipRegion")
    ShipPostalCode: str = StringProperty("ShipPostalCode")
    ShipCountry: str = StringProperty("ShipCountry")
    CustomerID: str = StringProperty("CustomerID")
    CustomerName: str = StringProperty("CustomerName", primary_key=True)
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")
    Salesperson: str = StringProperty("Salesperson", primary_key=True)
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    OrderDate: datetime.datetime = DatetimeProperty("OrderDate")
    RequiredDate: datetime.datetime = DatetimeProperty("RequiredDate")
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    ShipperName: str = StringProperty("ShipperName", primary_key=True)
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice", primary_key=True)
    Quantity: int = IntegerProperty("Quantity", primary_key=True)
    Discount: decimal.Decimal = DecimalProperty("Discount", primary_key=True)
    ExtendedPrice: decimal.Decimal = DecimalProperty("ExtendedPrice")
    Freight: decimal.Decimal = DecimalProperty("Freight")

    # Navigation properties


class Order_Details_Extended(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Order_Details_Extended"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice", primary_key=True)
    Quantity: int = IntegerProperty("Quantity", primary_key=True)
    Discount: decimal.Decimal = DecimalProperty("Discount", primary_key=True)
    ExtendedPrice: decimal.Decimal = DecimalProperty("ExtendedPrice")

    # Navigation properties


class Order_Subtotal(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Order_Subtotal"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    Subtotal: decimal.Decimal = DecimalProperty("Subtotal")

    # Navigation properties


class Orders_Qry(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Orders_Qry"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    CustomerID: str = StringProperty("CustomerID")
    EmployeeID: int = IntegerProperty("EmployeeID")
    OrderDate: datetime.datetime = DatetimeProperty("OrderDate")
    RequiredDate: datetime.datetime = DatetimeProperty("RequiredDate")
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    ShipVia: int = IntegerProperty("ShipVia")
    Freight: decimal.Decimal = DecimalProperty("Freight")
    ShipName: str = StringProperty("ShipName")
    ShipAddress: str = StringProperty("ShipAddress")
    ShipCity: str = StringProperty("ShipCity")
    ShipRegion: str = StringProperty("ShipRegion")
    ShipPostalCode: str = StringProperty("ShipPostalCode")
    ShipCountry: str = StringProperty("ShipCountry")
    CompanyName: str = StringProperty("CompanyName", primary_key=True)
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")

    # Navigation properties


class Product_Sales_for_1997(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Product_Sales_for_1997"
  
    # Simple properties
    CategoryName: str = StringProperty("CategoryName", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    ProductSales: decimal.Decimal = DecimalProperty("ProductSales")

    # Navigation properties


class Products_Above_Average_Price(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Products_Above_Average_Price"
  
    # Simple properties
    ProductName: str = StringProperty("ProductName", primary_key=True)
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice")

    # Navigation properties


class Products_by_Category(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Products_by_Category"
  
    # Simple properties
    CategoryName: str = StringProperty("CategoryName", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    QuantityPerUnit: str = StringProperty("QuantityPerUnit")
    UnitsInStock: int = IntegerProperty("UnitsInStock")
    Discontinued: bool = BooleanProperty("Discontinued", primary_key=True)

    # Navigation properties


class Sales_by_Category(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Sales_by_Category"
  
    # Simple properties
    CategoryID: int = IntegerProperty("CategoryID", primary_key=True)
    CategoryName: str = StringProperty("CategoryName", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    ProductSales: decimal.Decimal = DecimalProperty("ProductSales")

    # Navigation properties


class Sales_Totals_by_Amount(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Sales_Totals_by_Amount"
  
    # Simple properties
    SaleAmount: decimal.Decimal = DecimalProperty("SaleAmount")
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    CompanyName: str = StringProperty("CompanyName", primary_key=True)
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")

    # Navigation properties


class Summary_of_Sales_by_Quarter(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Summary_of_Sales_by_Quarter"
  
    # Simple properties
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    Subtotal: decimal.Decimal = DecimalProperty("Subtotal")

    # Navigation properties


class Summary_of_Sales_by_Year(ReflectionBase):
    __odata_collection__ = None
    __odata_type__ = "NorthwindModel.Summary_of_Sales_by_Year"
  
    # Simple properties
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    Subtotal: decimal.Decimal = DecimalProperty("Subtotal")

    # Navigation properties


# ************ End type definitions ************


# ************ Start entity definitions ************
class Categories(ReflectionBase):
    __odata_collection__ = "Categories"
    __odata_type__ = "NorthwindModel.Category"
  
    # Simple properties
    CategoryID: int = IntegerProperty("CategoryID", primary_key=True)
    CategoryName: str = StringProperty("CategoryName")
    Description: str = StringProperty("Description")
    Picture: str = StringProperty("Picture")

    # Navigation properties
    Products: list["Product"] = NavigationProperty(name="Products", entity_package="generated.northwind", entitycls="Product", collection=True)


class CustomerDemographics(ReflectionBase):
    __odata_collection__ = "CustomerDemographics"
    __odata_type__ = "NorthwindModel.CustomerDemographic"
  
    # Simple properties
    CustomerTypeID: str = StringProperty("CustomerTypeID", primary_key=True)
    CustomerDesc: str = StringProperty("CustomerDesc")

    # Navigation properties
    Customers: list["Customer"] = NavigationProperty(name="Customers", entity_package="generated.northwind", entitycls="Customer", collection=True)


class Customers(ReflectionBase):
    __odata_collection__ = "Customers"
    __odata_type__ = "NorthwindModel.Customer"
  
    # Simple properties
    CustomerID: str = StringProperty("CustomerID", primary_key=True)
    CompanyName: str = StringProperty("CompanyName")
    ContactName: str = StringProperty("ContactName")
    ContactTitle: str = StringProperty("ContactTitle")
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")
    Phone: str = StringProperty("Phone")
    Fax: str = StringProperty("Fax")

    # Navigation properties
    Orders: list["Order"] = NavigationProperty(name="Orders", entity_package="generated.northwind", entitycls="Order", collection=True)
    CustomerDemographics: list["CustomerDemographic"] = NavigationProperty(name="CustomerDemographics", entity_package="generated.northwind", entitycls="CustomerDemographic", collection=True)


class Employees(ReflectionBase):
    __odata_collection__ = "Employees"
    __odata_type__ = "NorthwindModel.Employee"
  
    # Simple properties
    EmployeeID: int = IntegerProperty("EmployeeID", primary_key=True)
    LastName: str = StringProperty("LastName")
    FirstName: str = StringProperty("FirstName")
    Title: str = StringProperty("Title")
    TitleOfCourtesy: str = StringProperty("TitleOfCourtesy")
    BirthDate: datetime.datetime = DatetimeProperty("BirthDate")
    HireDate: datetime.datetime = DatetimeProperty("HireDate")
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")
    HomePhone: str = StringProperty("HomePhone")
    Extension: str = StringProperty("Extension")
    Photo: str = StringProperty("Photo")
    Notes: str = StringProperty("Notes")
    ReportsTo: int = IntegerProperty("ReportsTo")
    PhotoPath: str = StringProperty("PhotoPath")

    # Navigation properties
    Employees1: list["Employee"] = NavigationProperty(name="Employees1", entity_package="generated.northwind", entitycls="Employee", collection=True)
    Employee1: "Employee" = NavigationProperty(name="Employee1", entity_package="generated.northwind", entitycls="Employee", foreign_key=ReportsTo)
    Orders: list["Order"] = NavigationProperty(name="Orders", entity_package="generated.northwind", entitycls="Order", collection=True)
    Territories: list["Territory"] = NavigationProperty(name="Territories", entity_package="generated.northwind", entitycls="Territory", collection=True)


class Order_Details(ReflectionBase):
    __odata_collection__ = "Order_Details"
    __odata_type__ = "NorthwindModel.Order_Detail"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice")
    Quantity: int = IntegerProperty("Quantity")
    Discount: decimal.Decimal = DecimalProperty("Discount")

    # Navigation properties
    Order: "Order" = NavigationProperty(name="Order", entity_package="generated.northwind", entitycls="Order", foreign_key=OrderID)
    Product: "Product" = NavigationProperty(name="Product", entity_package="generated.northwind", entitycls="Product", foreign_key=ProductID)


class Orders(ReflectionBase):
    __odata_collection__ = "Orders"
    __odata_type__ = "NorthwindModel.Order"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    CustomerID: str = StringProperty("CustomerID")
    EmployeeID: int = IntegerProperty("EmployeeID")
    OrderDate: datetime.datetime = DatetimeProperty("OrderDate")
    RequiredDate: datetime.datetime = DatetimeProperty("RequiredDate")
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    ShipVia: int = IntegerProperty("ShipVia")
    Freight: decimal.Decimal = DecimalProperty("Freight")
    ShipName: str = StringProperty("ShipName")
    ShipAddress: str = StringProperty("ShipAddress")
    ShipCity: str = StringProperty("ShipCity")
    ShipRegion: str = StringProperty("ShipRegion")
    ShipPostalCode: str = StringProperty("ShipPostalCode")
    ShipCountry: str = StringProperty("ShipCountry")

    # Navigation properties
    Customer: "Customer" = NavigationProperty(name="Customer", entity_package="generated.northwind", entitycls="Customer", foreign_key=CustomerID)
    Employee: "Employee" = NavigationProperty(name="Employee", entity_package="generated.northwind", entitycls="Employee", foreign_key=EmployeeID)
    Order_Details: list["Order_Detail"] = NavigationProperty(name="Order_Details", entity_package="generated.northwind", entitycls="Order_Detail", collection=True)
    Shipper: "Shipper" = NavigationProperty(name="Shipper", entity_package="generated.northwind", entitycls="Shipper", foreign_key=ShipVia)


class Products(ReflectionBase):
    __odata_collection__ = "Products"
    __odata_type__ = "NorthwindModel.Product"
  
    # Simple properties
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName")
    SupplierID: int = IntegerProperty("SupplierID")
    CategoryID: int = IntegerProperty("CategoryID")
    QuantityPerUnit: str = StringProperty("QuantityPerUnit")
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice")
    UnitsInStock: int = IntegerProperty("UnitsInStock")
    UnitsOnOrder: int = IntegerProperty("UnitsOnOrder")
    ReorderLevel: int = IntegerProperty("ReorderLevel")
    Discontinued: bool = BooleanProperty("Discontinued")

    # Navigation properties
    Category: "Category" = NavigationProperty(name="Category", entity_package="generated.northwind", entitycls="Category", foreign_key=CategoryID)
    Order_Details: list["Order_Detail"] = NavigationProperty(name="Order_Details", entity_package="generated.northwind", entitycls="Order_Detail", collection=True)
    Supplier: "Supplier" = NavigationProperty(name="Supplier", entity_package="generated.northwind", entitycls="Supplier", foreign_key=SupplierID)


class Regions(ReflectionBase):
    __odata_collection__ = "Regions"
    __odata_type__ = "NorthwindModel.Region"
  
    # Simple properties
    RegionID: int = IntegerProperty("RegionID", primary_key=True)
    RegionDescription: str = StringProperty("RegionDescription")

    # Navigation properties
    Territories: list["Territory"] = NavigationProperty(name="Territories", entity_package="generated.northwind", entitycls="Territory", collection=True)


class Shippers(ReflectionBase):
    __odata_collection__ = "Shippers"
    __odata_type__ = "NorthwindModel.Shipper"
  
    # Simple properties
    ShipperID: int = IntegerProperty("ShipperID", primary_key=True)
    CompanyName: str = StringProperty("CompanyName")
    Phone: str = StringProperty("Phone")

    # Navigation properties
    Orders: list["Order"] = NavigationProperty(name="Orders", entity_package="generated.northwind", entitycls="Order", collection=True)


class Suppliers(ReflectionBase):
    __odata_collection__ = "Suppliers"
    __odata_type__ = "NorthwindModel.Supplier"
  
    # Simple properties
    SupplierID: int = IntegerProperty("SupplierID", primary_key=True)
    CompanyName: str = StringProperty("CompanyName")
    ContactName: str = StringProperty("ContactName")
    ContactTitle: str = StringProperty("ContactTitle")
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")
    Phone: str = StringProperty("Phone")
    Fax: str = StringProperty("Fax")
    HomePage: str = StringProperty("HomePage")

    # Navigation properties
    Products: list["Product"] = NavigationProperty(name="Products", entity_package="generated.northwind", entitycls="Product", collection=True)


class Territories(ReflectionBase):
    __odata_collection__ = "Territories"
    __odata_type__ = "NorthwindModel.Territory"
  
    # Simple properties
    TerritoryID: str = StringProperty("TerritoryID", primary_key=True)
    TerritoryDescription: str = StringProperty("TerritoryDescription")
    RegionID: int = IntegerProperty("RegionID")

    # Navigation properties
    Region: "Region" = NavigationProperty(name="Region", entity_package="generated.northwind", entitycls="Region", foreign_key=RegionID)
    Employees: list["Employee"] = NavigationProperty(name="Employees", entity_package="generated.northwind", entitycls="Employee", collection=True)


class Alphabetical_list_of_products(ReflectionBase):
    __odata_collection__ = "Alphabetical_list_of_products"
    __odata_type__ = "NorthwindModel.Alphabetical_list_of_product"
  
    # Simple properties
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    SupplierID: int = IntegerProperty("SupplierID")
    CategoryID: int = IntegerProperty("CategoryID")
    QuantityPerUnit: str = StringProperty("QuantityPerUnit")
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice")
    UnitsInStock: int = IntegerProperty("UnitsInStock")
    UnitsOnOrder: int = IntegerProperty("UnitsOnOrder")
    ReorderLevel: int = IntegerProperty("ReorderLevel")
    Discontinued: bool = BooleanProperty("Discontinued", primary_key=True)
    CategoryName: str = StringProperty("CategoryName", primary_key=True)

    # Navigation properties


class Category_Sales_for_1997(ReflectionBase):
    __odata_collection__ = "Category_Sales_for_1997"
    __odata_type__ = "NorthwindModel.Category_Sales_for_1997"
  
    # Simple properties
    CategoryName: str = StringProperty("CategoryName", primary_key=True)
    CategorySales: decimal.Decimal = DecimalProperty("CategorySales")

    # Navigation properties


class Current_Product_Lists(ReflectionBase):
    __odata_collection__ = "Current_Product_Lists"
    __odata_type__ = "NorthwindModel.Current_Product_List"
  
    # Simple properties
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)

    # Navigation properties


class Customer_and_Suppliers_by_Cities(ReflectionBase):
    __odata_collection__ = "Customer_and_Suppliers_by_Cities"
    __odata_type__ = "NorthwindModel.Customer_and_Suppliers_by_City"
  
    # Simple properties
    City: str = StringProperty("City")
    CompanyName: str = StringProperty("CompanyName", primary_key=True)
    ContactName: str = StringProperty("ContactName")
    Relationship: str = StringProperty("Relationship", primary_key=True)

    # Navigation properties


class Invoices(ReflectionBase):
    __odata_collection__ = "Invoices"
    __odata_type__ = "NorthwindModel.Invoice"
  
    # Simple properties
    ShipName: str = StringProperty("ShipName")
    ShipAddress: str = StringProperty("ShipAddress")
    ShipCity: str = StringProperty("ShipCity")
    ShipRegion: str = StringProperty("ShipRegion")
    ShipPostalCode: str = StringProperty("ShipPostalCode")
    ShipCountry: str = StringProperty("ShipCountry")
    CustomerID: str = StringProperty("CustomerID")
    CustomerName: str = StringProperty("CustomerName", primary_key=True)
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")
    Salesperson: str = StringProperty("Salesperson", primary_key=True)
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    OrderDate: datetime.datetime = DatetimeProperty("OrderDate")
    RequiredDate: datetime.datetime = DatetimeProperty("RequiredDate")
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    ShipperName: str = StringProperty("ShipperName", primary_key=True)
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice", primary_key=True)
    Quantity: int = IntegerProperty("Quantity", primary_key=True)
    Discount: decimal.Decimal = DecimalProperty("Discount", primary_key=True)
    ExtendedPrice: decimal.Decimal = DecimalProperty("ExtendedPrice")
    Freight: decimal.Decimal = DecimalProperty("Freight")

    # Navigation properties


class Order_Details_Extendeds(ReflectionBase):
    __odata_collection__ = "Order_Details_Extendeds"
    __odata_type__ = "NorthwindModel.Order_Details_Extended"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    ProductID: int = IntegerProperty("ProductID", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice", primary_key=True)
    Quantity: int = IntegerProperty("Quantity", primary_key=True)
    Discount: decimal.Decimal = DecimalProperty("Discount", primary_key=True)
    ExtendedPrice: decimal.Decimal = DecimalProperty("ExtendedPrice")

    # Navigation properties


class Order_Subtotals(ReflectionBase):
    __odata_collection__ = "Order_Subtotals"
    __odata_type__ = "NorthwindModel.Order_Subtotal"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    Subtotal: decimal.Decimal = DecimalProperty("Subtotal")

    # Navigation properties


class Orders_Qries(ReflectionBase):
    __odata_collection__ = "Orders_Qries"
    __odata_type__ = "NorthwindModel.Orders_Qry"
  
    # Simple properties
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    CustomerID: str = StringProperty("CustomerID")
    EmployeeID: int = IntegerProperty("EmployeeID")
    OrderDate: datetime.datetime = DatetimeProperty("OrderDate")
    RequiredDate: datetime.datetime = DatetimeProperty("RequiredDate")
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    ShipVia: int = IntegerProperty("ShipVia")
    Freight: decimal.Decimal = DecimalProperty("Freight")
    ShipName: str = StringProperty("ShipName")
    ShipAddress: str = StringProperty("ShipAddress")
    ShipCity: str = StringProperty("ShipCity")
    ShipRegion: str = StringProperty("ShipRegion")
    ShipPostalCode: str = StringProperty("ShipPostalCode")
    ShipCountry: str = StringProperty("ShipCountry")
    CompanyName: str = StringProperty("CompanyName", primary_key=True)
    Address: str = StringProperty("Address")
    City: str = StringProperty("City")
    Region: str = StringProperty("Region")
    PostalCode: str = StringProperty("PostalCode")
    Country: str = StringProperty("Country")

    # Navigation properties


class Product_Sales_for_1997(ReflectionBase):
    __odata_collection__ = "Product_Sales_for_1997"
    __odata_type__ = "NorthwindModel.Product_Sales_for_1997"
  
    # Simple properties
    CategoryName: str = StringProperty("CategoryName", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    ProductSales: decimal.Decimal = DecimalProperty("ProductSales")

    # Navigation properties


class Products_Above_Average_Prices(ReflectionBase):
    __odata_collection__ = "Products_Above_Average_Prices"
    __odata_type__ = "NorthwindModel.Products_Above_Average_Price"
  
    # Simple properties
    ProductName: str = StringProperty("ProductName", primary_key=True)
    UnitPrice: decimal.Decimal = DecimalProperty("UnitPrice")

    # Navigation properties


class Products_by_Categories(ReflectionBase):
    __odata_collection__ = "Products_by_Categories"
    __odata_type__ = "NorthwindModel.Products_by_Category"
  
    # Simple properties
    CategoryName: str = StringProperty("CategoryName", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    QuantityPerUnit: str = StringProperty("QuantityPerUnit")
    UnitsInStock: int = IntegerProperty("UnitsInStock")
    Discontinued: bool = BooleanProperty("Discontinued", primary_key=True)

    # Navigation properties


class Sales_by_Categories(ReflectionBase):
    __odata_collection__ = "Sales_by_Categories"
    __odata_type__ = "NorthwindModel.Sales_by_Category"
  
    # Simple properties
    CategoryID: int = IntegerProperty("CategoryID", primary_key=True)
    CategoryName: str = StringProperty("CategoryName", primary_key=True)
    ProductName: str = StringProperty("ProductName", primary_key=True)
    ProductSales: decimal.Decimal = DecimalProperty("ProductSales")

    # Navigation properties


class Sales_Totals_by_Amounts(ReflectionBase):
    __odata_collection__ = "Sales_Totals_by_Amounts"
    __odata_type__ = "NorthwindModel.Sales_Totals_by_Amount"
  
    # Simple properties
    SaleAmount: decimal.Decimal = DecimalProperty("SaleAmount")
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    CompanyName: str = StringProperty("CompanyName", primary_key=True)
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")

    # Navigation properties


class Summary_of_Sales_by_Quarters(ReflectionBase):
    __odata_collection__ = "Summary_of_Sales_by_Quarters"
    __odata_type__ = "NorthwindModel.Summary_of_Sales_by_Quarter"
  
    # Simple properties
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    Subtotal: decimal.Decimal = DecimalProperty("Subtotal")

    # Navigation properties


class Summary_of_Sales_by_Years(ReflectionBase):
    __odata_collection__ = "Summary_of_Sales_by_Years"
    __odata_type__ = "NorthwindModel.Summary_of_Sales_by_Year"
  
    # Simple properties
    ShippedDate: datetime.datetime = DatetimeProperty("ShippedDate")
    OrderID: int = IntegerProperty("OrderID", primary_key=True)
    Subtotal: decimal.Decimal = DecimalProperty("Subtotal")

    # Navigation properties


# ************ End entity definitions ************

