# -*- coding: utf-8 -*-

from enum import Enum

from odata.property import PropertyBase


class EnumType(Enum):
    pass


class EnumTypeProperty(PropertyBase):
    """
    A property that contains a ComplexType object

    :param name: Name of the property in the endpoint
    :param enum_class: A subclass of EnumType
    """

    def __init__(self, name, enum_class=EnumType):
        super(EnumTypeProperty, self).__init__(name)
        self.enum_class = enum_class

    def serialize(self, value):
        return value.name

    def deserialize(self, value):
        return self.enum_class[value]
