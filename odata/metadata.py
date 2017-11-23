# -*- coding: utf-8 -*-

import logging
import sys
has_lxml = False
try:
    from lxml import etree as ET
    has_lxml = True
except ImportError:
    if sys.version_info < (2, 7):
        raise ImportError('lxml required for Python versions older than 2.7')
    from xml.etree import ElementTree as ET

from .entity import declarative_base, EntityBase
from .exceptions import ODataReflectionError
from .property import StringProperty, IntegerProperty, DecimalProperty, \
    DatetimeProperty, BooleanProperty, NavigationProperty, UUIDProperty
from .enumtype import EnumType, EnumTypeProperty


class MetaData(object):

    log = logging.getLogger('odata.metadata')
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

    _annotation_term_computed = 'Org.OData.Core.V1.Computed'

    def __init__(self, service):
        self.url = service.url + '$metadata/'
        self.connection = service.default_context.connection
        self.service = service

    def property_type_to_python(self, edm_type):
        return self.property_types.get(edm_type, StringProperty)

    def _type_is_collection(self, typename):
        if typename.startswith('Collection('):
            stripped = typename[11:-1]
            return True, stripped
        else:
            return False, typename

    def _get_entities_from_types(self, all_types):
        return [entity for entity in all_types.values() if issubclass(entity, EntityBase)]

    def _set_object_relationships(self, all_types):
        entities = self._get_entities_from_types(all_types)
        for entity in entities:  # type: EntityBase
            schema = entity.__odata_schema__

            for schema_nav in schema.get('navigation_properties', []):
                name = schema_nav['name']
                type_ = schema_nav['type']
                foreign_key = schema_nav['foreign_key']

                is_collection, type_ = self._type_is_collection(type_)

                for _search_entity in entities:
                    _search_type = _search_entity.__odata_schema__['type']
                    _search_type_alias = _search_entity.__odata_schema__.get('type_alias')
                    if type_ in (_search_type, _search_type_alias):
                        nav = NavigationProperty(
                            name,
                            _search_entity,
                            collection=is_collection,
                            foreign_key=foreign_key,
                        )
                        setattr(entity, name, nav)

    def _create_entities(self, all_types, entity_base_class, schemas, depth=1):
        orphan_entities = []
        for schema in schemas:
            for entity_dict in schema.get('entities'):
                entity_type = entity_dict['type']
                entity_type_alias = entity_dict.get('type_alias')
                entity_name = entity_dict['name']

                if entity_type in all_types:
                    continue

                parent_entity_class = None

                if entity_dict.get('base_type'):
                    base_type = entity_dict.get('base_type')
                    parent_entity_class = all_types.get(base_type)

                    if parent_entity_class is None:
                        # base class not yet created
                        orphan_entities.append(entity_type)
                        continue

                super_class = parent_entity_class or entity_base_class
                object_dict = dict(
                    __odata_schema__=entity_dict,
                    __odata_type__=entity_type,
                )
                entity_class = type(entity_name, (super_class,), object_dict)

                all_types[entity_type] = entity_class
                if entity_type_alias:
                    all_types[entity_type_alias] = entity_class

                for prop in entity_dict.get('properties'):
                    prop_name = prop['name']

                    if hasattr(entity_class, prop_name):
                        # do not replace existing properties (from Base)
                        continue

                    property_type = all_types.get(prop['type'])

                    if property_type and issubclass(property_type, EnumType):
                        property_instance = EnumTypeProperty(prop_name, enum_class=property_type)
                        property_instance.is_computed_value = prop['is_computed_value']
                    else:
                        type_ = self.property_type_to_python(prop['type'])
                        type_options = {
                            'primary_key': prop['is_primary_key'],
                            'is_collection': prop['is_collection'],
                            'is_computed_value': prop['is_computed_value'],
                        }
                        property_instance = type_(prop_name, **type_options)
                    setattr(entity_class, prop_name, property_instance)

        if len(orphan_entities) > 0:
            if depth > 10:
                errmsg = ('Types could not be resolved. '
                          'Orphaned types: {0}').format(', '.join(orphan_entities))
                raise ODataReflectionError(errmsg)
            depth += 1
            self._create_entities(all_types, entity_base_class, schemas, depth)

    def _create_actions(self, all_types, actions, get_entity_or_prop_from_type):
        entities = self._get_entities_from_types(all_types)
        for action in actions:
            entity_type = action['is_bound_to']
            bind_entity = None
            bound_to_collection = False
            if entity_type:
                bound_to_collection, entity_type = self._type_is_collection(entity_type)
                for entity in entities:
                    schema = entity.__odata_schema__
                    if entity_type in (schema['type'], schema.get('type_alias')):
                        bind_entity = entity

            parameters_dict = {}
            for param in action['parameters']:
                parameters_dict[param['name']] = self.property_type_to_python(param['type'])

            object_dict = dict(
                __odata_service__=self.service,
                name=action['fully_qualified_name'],
                parameters=parameters_dict,
                return_type=get_entity_or_prop_from_type(action['return_type']),
                return_type_collection=get_entity_or_prop_from_type(action['return_type_collection']),
                bound_to_collection=bound_to_collection,
            )
            action_class = type(action['name'], (self.service.Action,), object_dict)

            if bind_entity:
                setattr(bind_entity, action['name'], action_class())
            else:
                self.service.actions[action['name']] = action_class()

    def _create_functions(self, all_types, functions, get_entity_or_prop_from_type):
        entities = self._get_entities_from_types(all_types)
        for function in functions:
            entity_type = function['is_bound_to']
            bind_entity = None
            bound_to_collection = False
            if entity_type:
                bound_to_collection, entity_type = self._type_is_collection(entity_type)
                for entity in entities:
                    schema = entity.__odata_schema__
                    if entity_type in (schema['type'], schema.get('type_alias')):
                        bind_entity = entity

            parameters_dict = {}
            for param in function['parameters']:
                parameters_dict[param['name']] = self.property_type_to_python(param['type'])

            object_dict = dict(
                __odata_service__=self.service,
                name=function['fully_qualified_name'],
                parameters=parameters_dict,
                return_type=get_entity_or_prop_from_type(function['return_type']),
                return_type_collection=get_entity_or_prop_from_type(function['return_type_collection']),
                bound_to_collection=bound_to_collection,
            )
            function_class = type(function['name'], (self.service.Function,), object_dict)

            if bind_entity:
                setattr(bind_entity, function['name'], function_class())
            else:
                self.service.functions[function['name']] = function_class()

    def get_entity_sets(self, base=None):
        document = self.load_document()
        schemas, entity_sets, actions, functions = self.parse_document(document)

        base_class = base or declarative_base()
        all_types = {}

        def get_entity_or_prop_from_type(typename):
            if typename is None:
                return

            type_ = all_types.get(typename)
            if type_ is not None:
                return type_

            return self.property_type_to_python(typename)

        for schema in schemas:
            for enum_type in schema['enum_types']:
                names = [(i['name'], i['value']) for i in enum_type['members']]
                created_enum = EnumType(enum_type['name'], names=names)
                all_types[enum_type['fully_qualified_name']] = created_enum

        self._create_entities(all_types, base_class, schemas)

        sets = {}
        for entity_set in entity_sets.values():
            entity_class = all_types.get(entity_set.get('type'))
            set_name = entity_set.get('name')
            is_singleton = entity_set.get('singleton', False)
            set_class = type('EntitySet' + set_name, (entity_class,), dict(__odata_collection__=set_name, __odata_singleton__=is_singleton))
            sets[set_name] = set_class

        self._set_object_relationships(all_types)
        self._create_actions(all_types, actions, get_entity_or_prop_from_type)
        self._create_functions(all_types, functions, get_entity_or_prop_from_type)

        self.log.info('Loaded {0} entity sets, total {1} types'.format(len(sets), len(all_types)))
        return base_class, sets, all_types

    def load_document(self):
        self.log.info('Loading metadata document: {0}'.format(self.url))
        response = self.connection._do_get(self.url)
        return ET.fromstring(response.content)

    def _parse_action(self, xmlq, action_element, schema_name):
        action = {
            'name': action_element.attrib['Name'],
            'fully_qualified_name': action_element.attrib['Name'],
            'is_bound': action_element.attrib.get('IsBound') == 'true',
            'is_bound_to': None,
            'parameters': [],
            'return_type': None,
            'return_type_collection': None,
        }

        if action['is_bound']:
            # bound actions are named SchemaNamespace.ActionName
            action['fully_qualified_name'] = '.'.join([schema_name, action['name']])

        for parameter_element in xmlq(action_element, 'edm:Parameter'):
            parameter_name = parameter_element.attrib['Name']
            if action['is_bound'] and parameter_name == 'bindingParameter':
                action['is_bound_to'] = parameter_element.attrib['Type']
                continue

            parameter_type = parameter_element.attrib['Type']

            action['parameters'].append({
                'name': parameter_name,
                'type': parameter_type,
            })

        for return_type_element in xmlq(action_element, 'edm:ReturnType'):
            type_name = return_type_element.attrib['Type']
            is_collection, type_name = self._type_is_collection(type_name)
            if is_collection:
                action['return_type_collection'] = type_name
            else:
                action['return_type'] = type_name
        return action

    def _parse_function(self, xmlq, function_element, schema_name):
        function = {
            'name': function_element.attrib['Name'],
            'fully_qualified_name': function_element.attrib['Name'],
            'is_bound': function_element.attrib.get('IsBound') == 'true',
            'is_bound_to': None,
            'parameters': [],
            'return_type': None,
            'return_type_collection': None,
        }

        if function['is_bound']:
            # bound functions are named SchemaNamespace.FunctionName
            function['fully_qualified_name'] = '.'.join(
                [schema_name, function['name']])

        for parameter_element in xmlq(function_element, 'edm:Parameter'):
            parameter_name = parameter_element.attrib['Name']
            if function['is_bound'] and parameter_name == 'bindingParameter':
                function['is_bound_to'] = parameter_element.attrib['Type']
                continue

            parameter_type = parameter_element.attrib['Type']

            function['parameters'].append({
                'name': parameter_name,
                'type': parameter_type,
            })

        for return_type_element in xmlq(function_element, 'edm:ReturnType'):
            type_name = return_type_element.attrib['Type']
            is_collection, type_name = self._type_is_collection(type_name)
            if is_collection:
                function['return_type_collection'] = type_name
            else:
                function['return_type'] = type_name
        return function

    def _parse_entity(self, xmlq, entity_element, schema_name, schema_alias):
        entity_name = entity_element.attrib['Name']

        entity_type_name = '.'.join([schema_name, entity_name])

        entity = {
            'name': entity_name,
            'type': entity_type_name,
            'properties': [],
            'navigation_properties': [],
        }

        if schema_alias:
            entity_type_name_alias = '.'.join([schema_alias, entity_name])
            entity['type_alias'] = entity_type_name_alias

        base_type = entity_element.attrib.get('BaseType')
        if base_type:
            entity['base_type'] = base_type

        entity_pks = {}
        for pk_property in xmlq(entity_element, 'edm:Key/edm:PropertyRef'):
            pk_property_name = pk_property.attrib['Name']
            entity_pks[pk_property_name] = 0

        for entity_property in xmlq(entity_element, 'edm:Property'):
            p_name = entity_property.attrib['Name']
            p_type = entity_property.attrib['Type']

            is_collection, p_type = self._type_is_collection(p_type)
            is_computed_value = False

            for annotation in xmlq(entity_property, 'edm:Annotation'):
                annotation_term = annotation.attrib.get('Term', '')
                annotation_bool = annotation.attrib.get('Bool') == 'true'
                if annotation_term == self._annotation_term_computed:
                    is_computed_value = annotation_bool

            entity['properties'].append({
                'name': p_name,
                'type': p_type,
                'is_primary_key': p_name in entity_pks,
                'is_collection': is_collection,
                'is_computed_value': is_computed_value,
            })

        for nav_property in xmlq(entity_element, 'edm:NavigationProperty'):
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
        return entity

    def _parse_enumtype(self, xmlq, enumtype_element, schema_name):
        enum_name = enumtype_element.attrib['Name']
        enum = {
            'name': enum_name,
            'fully_qualified_name': '.'.join([schema_name, enum_name]),
            'members': []
        }
        for enum_member in xmlq(enumtype_element, 'edm:Member'):
            member_name = enum_member.attrib['Name']
            member_value = int(enum_member.attrib['Value'])
            enum['members'].append({
                'name': member_name,
                'value': member_value,
            })
        return enum

    def parse_document(self, doc):
        schemas = []
        container_sets = {}
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
            schema_alias = schema.attrib.get('Alias')

            schema_dict = {
                'name': schema_name,
                'alias': schema_alias,
                'entities': [],
                'enum_types': [],
                'complex_types': [],
            }

            for enum_type in xmlq(schema, 'edm:EnumType'):
                enum = self._parse_enumtype(xmlq, enum_type, schema_name)
                schema_dict['enum_types'].append(enum)

            for entity_type in xmlq(schema, 'edm:EntityType'):
                entity = self._parse_entity(xmlq, entity_type, schema_name, schema_alias)
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
                        if set_type in (entity.get('type'), entity.get('type_alias')):
                            set_dict['schema'] = entity

                container_sets[set_name] = set_dict

            for entity_set in xmlq(schema, 'edm:EntityContainer/edm:Singleton'):
                set_name = entity_set.attrib['Name']
                set_type = entity_set.attrib['Type']

                set_dict = {
                    'name': set_name,
                    'type': set_type,
                    'schema': None,
                    'singleton': True,
                }

                for schema_ in schemas:
                    for entity in schema_.get('entities', []):
                        if set_type in (entity.get('type'), entity.get('type_alias')):
                            set_dict['schema'] = entity

                container_sets[set_name] = set_dict

            for action_def in xmlq(schema, 'edm:Action'):
                action = self._parse_action(xmlq, action_def, schema_name)
                actions.append(action)

            for function_def in xmlq(schema, 'edm:Function'):
                function = self._parse_function(xmlq, function_def, schema_name)
                functions.append(function)

        return schemas, container_sets, actions, functions
