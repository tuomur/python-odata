# -*- coding: utf-8 -*-

from odata.property import PropertyBase


class ComplexType(dict):
    properties = dict()

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __repr__(self):
        keys = ','.join(self.keys())
        return '<ComplexType({0})>'.format(keys)


class ComplexTypeProperty(PropertyBase):
    """
    A property that contains a ComplexType object

    :param name: Name of the property in the endpoint
    :param type_class: A subclass of ComplexType
    """

    def __init__(self, name, type_class=ComplexType):
        """
        :type name: str
        """
        super(ComplexTypeProperty, self).__init__(name)
        self.type_class = type_class

    def serialize(self, value):
        if isinstance(value, list):
            data = []
            for i in value:
                data.append(self._serialize(i))
            return data
        else:
            return self._serialize(value)

    def _serialize(self, value):
        data = dict()
        for name, prop in value.properties.items():
            prop_value = value.get(name)

            if prop_value is None:
                continue

            if isinstance(prop_value, ComplexType):
                serialized_value = self.serialize(prop_value)
            else:
                serialized_value = prop('temp').serialize(prop_value)
            data[name] = serialized_value
        return data

    def deserialize(self, value):
        if isinstance(value, list):
            data = []
            for i in value:
                data.append(self._deserialize(i))
            return data
        else:
            return self._deserialize(value)

    def _deserialize(self, value):
        data = self.type_class()

        for name, prop in data.properties.items():
            prop_value = value.get(name)

            if prop_value is None:
                continue

            if issubclass(prop, ComplexType):
                ctprop = ComplexTypeProperty('temp', type_class=prop)
                deserialized_value = ctprop.deserialize(prop_value)
            else:
                deserialized_value = prop('temp').deserialize(prop_value)
            data[name] = deserialized_value
        return data

    def escape_value(self, value):
        raise NotImplementedError()

    def __getattr__(self, item):
        # allows ComplexType key usage in filters etc
        subkey = '{0}/{1}'.format(self.name, item)
        prop = self.type_class.properties[item]
        if issubclass(prop, ComplexType):
            return ComplexTypeProperty(subkey, type_class=prop)
        return prop(subkey)
