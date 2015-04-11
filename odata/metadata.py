# -*- coding: utf-8 -*-

from lxml import etree

from .entity import declarative_base
from .property import StringProperty, IntegerProperty, DecimalProperty, \
    DatetimeProperty, BooleanProperty, Relationship


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
    }

    def __init__(self, service):
        self.url = service.url + '$metadata/'
        self.connection = service.connection

    def property_type_to_python(self, edm_type):
        return self.property_types.get(edm_type, StringProperty)

    def get_entity_sets(self, base=None):
        document = self.load_document()
        schemas, entity_sets = self.parse_document(document)

        entities = {}
        Base = base or declarative_base()

        for entity_set in entity_sets:
            schema = entity_set['schema']
            if schema:
                collection_name = entity_set['name']
                entity_name = schema['name']

                class Entity(Base):
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

                is_collection = False
                if type_.startswith('Collection('):
                    is_collection = True
                    search_type = type_.lstrip('Collection(').strip(')')
                else:
                    search_type = type_

                for _search_entity in entities.values():
                    if _search_entity.__odata_schema__['type'] == search_type:
                        setattr(entity, name, Relationship(name, _search_entity, collection=is_collection))

        return Base, entities

    def load_document(self):
        response = self.connection._do_get(self.url)
        return etree.fromstring(response.content)

    def parse_document(self, doc):
        schemas = []
        container_sets = []

        def xmlq(node, xpath):
            return node.xpath(xpath, namespaces=self.namespaces)

        for schema in xmlq(doc, 'edmx:DataServices/edm:Schema'):
            schema_name = xmlq(schema, '@Namespace')[0]

            schema_dict = {
                'name': schema_name,
                'entities': [],
            }

            for entity_type in xmlq(schema, 'edm:EntityType'):
                entity_name = xmlq(entity_type, '@Name')[0]

                entity_type_name = '.'.join([schema_name, entity_name])

                entity = {
                    'name': entity_name,
                    'type': entity_type_name,
                    'properties': [],
                    'navigation_properties': [],
                }

                entity_pk_name = None
                pk_property = xmlq(entity_type, 'edm:Key/edm:PropertyRef')
                if pk_property:
                    entity_pk_name = xmlq(pk_property[0], '@Name')[0]

                for entity_property in xmlq(entity_type, 'edm:Property'):
                    p_name = xmlq(entity_property, '@Name')[0]
                    p_type = xmlq(entity_property, '@Type')[0]

                    entity['properties'].append({
                        'name': p_name,
                        'type': p_type,
                        'is_primary_key': entity_pk_name == p_name,
                    })

                for nav_property in xmlq(entity_type, 'edm:NavigationProperty'):
                    p_name = xmlq(nav_property, '@Name')[0]
                    p_type = xmlq(nav_property, '@Type')[0]

                    entity['navigation_properties'].append({
                        'name': p_name,
                        'type': p_type,
                    })

                schema_dict['entities'].append(entity)

            schemas.append(schema_dict)

        for schema in xmlq(doc, 'edmx:DataServices/edm:Schema'):
            for entity_set in xmlq(schema, 'edm:EntityContainer/edm:EntitySet'):
                set_name = xmlq(entity_set, '@Name')[0]
                set_type = xmlq(entity_set, '@EntityType')[0]

                set_dict = {
                    'name': set_name,
                    'type': set_type,
                    'schema': None,
                }

                for schema in schemas:
                    for entity in schema.get('entities', []):
                        if entity.get('type') == set_type:
                            set_dict['schema'] = entity

                container_sets.append(set_dict)

        return schemas, container_sets