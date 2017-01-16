# -*- coding: utf-8 -*-

import sys
has_lxml = False
try:
    from lxml import etree as ET
    has_lxml = True
except ImportError:
    if sys.version_info < (2, 7):
        raise ImportError('lxml required for Python versions older than 2.7')
    from xml.etree import ElementTree as ET

from .entity import declarative_base
from .property import StringProperty, IntegerProperty, DecimalProperty, \
    DatetimeProperty, BooleanProperty, NavigationProperty, UUIDProperty


class MetaData(object):

    namespaces = {
        'edm': 'http://docs.oasis-open.org/odata/ns/edm',
        'edmx': 'http://docs.oasis-open.org/odata/ns/edmx'
    }

    property_types = {
        'Edm.Int16': IntegerProperty,
        'Edm.Int32': IntegerProperty,
        'Edm.Int64': IntegerProperty,
        'Edm.String': StringProperty,
        'Edm.Single': DecimalProperty,
        'Edm.Decimal': DecimalProperty,
        'Edm.DateTimeOffset': DatetimeProperty,
        'Edm.Boolean': BooleanProperty,
        'Edm.Guid': UUIDProperty,
    }

    def __init__(self, service):
        self.url = service.url + '$metadata/'
        self.connection = service.default_context.connection
        self.service = service

    def property_type_to_python(self, edm_type):
        return self.property_types.get(edm_type, StringProperty)

    def get_entity_sets(self, base=None):
        document = self.load_document()
        schemas, entity_sets, actions, functions = self.parse_document(document)

        entities = {}
        base_class = base or declarative_base()

        subclasses = []

        for schema in schemas:
            for entity_type in schema.get('entities', []):
                if entity_type.get('base_type'):
                    subclasses.append({
                        'name': entity_type['name'],
                        'schema': entity_type,
                    })

        for entity_set in entity_sets + subclasses:
            schema = entity_set['schema']
            collection_name = entity_set['name']

            entity_name = schema['name']

            if schema.get('base_type'):
                base_type = schema.get('base_type')
                for entity in entities.values():
                    if entity.__odata_type__ == base_type:
                        class Entity(entity):
                            __odata_schema__ = schema
                            __odata_type__ = schema['type']
                        Entity.__name__ = schema['name']
            else:
                class Entity(base_class):
                    __odata_schema__ = schema
                    __odata_type__ = schema['type']
                    __odata_collection__ = collection_name

                Entity.__name__ = entity_name

            for prop in schema.get('properties'):
                prop_name = prop['name']

                if hasattr(Entity, prop_name):
                    # do not replace existing properties (from Base)
                    continue

                type_ = self.property_type_to_python(prop['type'])
                type_options = {
                    'primary_key': prop['is_primary_key']
                }
                setattr(Entity, prop_name, type_(prop_name, **type_options))

            entities[entity_name] = Entity

        # Set up relationships
        for entity in entities.values():
            schema = entity.__odata_schema__

            for schema_nav in schema.get('navigation_properties', []):
                name = schema_nav['name']
                type_ = schema_nav['type']
                foreign_key = schema_nav['foreign_key']

                is_collection = False
                if type_.startswith('Collection('):
                    is_collection = True
                    search_type = type_.lstrip('Collection(').strip(')')
                else:
                    search_type = type_

                for _search_entity in entities.values():
                    if _search_entity.__odata_schema__['type'] == search_type:
                        nav = NavigationProperty(
                            name,
                            _search_entity,
                            collection=is_collection,
                            foreign_key=foreign_key,
                        )
                        setattr(entity, name, nav)

        def get_entity_or_prop_from_type(typename):
            if typename is None:
                return

            for entity in entities.values():
                schema = entity.__odata_schema__
                if schema['type'] == typename:
                    return entity

            return self.property_type_to_python(typename)

        for action in actions:
            entity_type = action['is_bound_to']
            bind_entity = None
            if entity_type:
                entity_type = entity_type.lstrip('Collection(').strip(')')
                for entity in entities.values():
                    schema = entity.__odata_schema__
                    if schema['type'] == entity_type:
                        bind_entity = entity

            parameters_dict = {}
            for param in action['parameters']:
                parameters_dict[param['name']] = self.property_type_to_python(param['type'])

            class _Action(self.service.Action):
                __odata_service__ = self.service
                name = action['fully_qualified_name']
                parameters = parameters_dict
                return_type = get_entity_or_prop_from_type(action['return_type'])
                return_type_collection = get_entity_or_prop_from_type(action['return_type_collection'])

            if bind_entity:
                setattr(bind_entity, action['name'], _Action())
            else:
                self.service.actions[action['name']] = _Action()

        for function in functions:
            entity_type = function['is_bound_to']
            bind_entity = None
            if entity_type:
                entity_type = entity_type.lstrip('Collection(').strip(')')
                for entity in entities.values():
                    schema = entity.__odata_schema__
                    if schema['type'] == entity_type:
                        bind_entity = entity

            parameters_dict = {}
            for param in function['parameters']:
                parameters_dict[param['name']] = self.property_type_to_python(param['type'])

            class _Function(self.service.Function):
                __odata_service__ = self.service
                name = function['fully_qualified_name']
                parameters = parameters_dict
                return_type = get_entity_or_prop_from_type(function['return_type'])
                return_type_collection = get_entity_or_prop_from_type(function['return_type_collection'])

            if bind_entity:
                setattr(bind_entity, function['name'], _Function())
            else:
                self.service.functions[function['name']] = _Function()

        return base_class, entities

    def load_document(self):
        response = self.connection._do_get(self.url)
        return ET.fromstring(response.content)

    def parse_document(self, doc):
        schemas = []
        container_sets = []
        actions = []
        functions = []

        if has_lxml:
            def xmlq(node, xpath):
                return node.xpath(xpath, namespaces=self.namespaces)
        else:
            def xmlq(node, xpath):
                return node.findall(xpath, namespaces=self.namespaces)

        for schema in xmlq(doc, 'edmx:DataServices/edm:Schema'):
            schema_name = schema.attrib['Namespace']

            schema_dict = {
                'name': schema_name,
                'entities': [],
            }

            for entity_type in xmlq(schema, 'edm:EntityType'):
                entity_name = entity_type.attrib['Name']

                entity_type_name = '.'.join([schema_name, entity_name])

                entity = {
                    'name': entity_name,
                    'type': entity_type_name,
                    'properties': [],
                    'navigation_properties': [],
                }

                base_type = entity_type.attrib.get('BaseType')
                if base_type:
                    base_type = base_type
                    entity['base_type'] = base_type

                entity_pk_name = None
                pk_property = xmlq(entity_type, 'edm:Key/edm:PropertyRef')
                if pk_property:
                    entity_pk_name = pk_property[0].attrib['Name']

                for entity_property in xmlq(entity_type, 'edm:Property'):
                    p_name = entity_property.attrib['Name']
                    p_type = entity_property.attrib['Type']

                    entity['properties'].append({
                        'name': p_name,
                        'type': p_type,
                        'is_primary_key': entity_pk_name == p_name,
                    })

                for nav_property in xmlq(entity_type, 'edm:NavigationProperty'):
                    p_name = nav_property.attrib['Name']
                    p_type = nav_property.attrib['Type']
                    p_foreign_key = None

                    ref_constraint = xmlq(nav_property, 'edm:ReferentialConstraint')
                    if ref_constraint:
                        ref_constraint = ref_constraint[0]
                        p_foreign_key = ref_constraint.attrib['Property']

                    entity['navigation_properties'].append({
                        'name': p_name,
                        'type': p_type,
                        'foreign_key': p_foreign_key,
                    })

                schema_dict['entities'].append(entity)

            schemas.append(schema_dict)

        for schema in xmlq(doc, 'edmx:DataServices/edm:Schema'):
            schema_name = schema.attrib['Namespace']
            for entity_set in xmlq(schema, 'edm:EntityContainer/edm:EntitySet'):
                set_name = entity_set.attrib['Name']
                set_type = entity_set.attrib['EntityType']

                set_dict = {
                    'name': set_name,
                    'type': set_type,
                    'schema': None,
                }

                for schema_ in schemas:
                    for entity in schema_.get('entities', []):
                        if entity.get('type') == set_type:
                            set_dict['schema'] = entity

                container_sets.append(set_dict)

            for action_def in xmlq(schema, 'edm:Action'):
                action = {
                    'name': action_def.attrib['Name'],
                    'fully_qualified_name': action_def.attrib['Name'],
                    'is_bound': action_def.attrib['IsBound'] == 'true',
                    'is_bound_to': None,
                    'parameters': [],
                    'return_type': None,
                    'return_type_collection': None,
                }

                if action['is_bound']:
                    # bound actions are named SchemaNamespace.ActionName
                    action['fully_qualified_name'] = '.'.join([schema_name, action['name']])

                for def_parameter in xmlq(action_def, 'edm:Parameter'):
                    parameter_name = def_parameter.attrib['Name']
                    if action['is_bound'] and parameter_name == 'bindingParameter':
                        action['is_bound_to'] = def_parameter.attrib['Type']
                        continue

                    parameter_type = def_parameter.attrib['Type']

                    action['parameters'].append({
                        'name': parameter_name,
                        'type': parameter_type,
                    })

                for def_return_type in xmlq(action_def, 'edm:ReturnType'):
                    type_name = def_return_type.attrib['Type']
                    if 'Collection(' in type_name:
                        action['return_type_collection'] = type_name.lstrip('Collection(').rstrip(')')
                    else:
                        action['return_type'] = type_name

                actions.append(action)

            for function_def in xmlq(schema, 'edm:Function'):
                function = {
                    'name': function_def.attrib['Name'],
                    'fully_qualified_name': function_def.attrib['Name'],
                    'is_bound': function_def.attrib.get('IsBound') == 'true',
                    'is_bound_to': None,
                    'parameters': [],
                    'return_type': None,
                    'return_type_collection': None,
                }

                if function['is_bound']:
                    # bound functions are named SchemaNamespace.FunctionName
                    function['fully_qualified_name'] = '.'.join([schema_name, function['name']])

                for def_parameter in xmlq(function_def, 'edm:Parameter'):
                    parameter_name = def_parameter.attrib['Name']
                    if function['is_bound'] and parameter_name == 'bindingParameter':
                        function['is_bound_to'] = def_parameter.attrib['Type']
                        continue

                    parameter_type = def_parameter.attrib['Type']

                    function['parameters'].append({
                        'name': parameter_name,
                        'type': parameter_type,
                    })

                for def_return_type in xmlq(function_def, 'edm:ReturnType'):
                    type_name = def_return_type.attrib['Type']
                    if 'Collection(' in type_name:
                        function['return_type_collection'] = type_name.lstrip('Collection(').rstrip(')')
                    else:
                        function['return_type'] = type_name

                functions.append(function)

        return schemas, container_sets, actions, functions
