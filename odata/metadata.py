# -*- coding: utf-8 -*-

from lxml import etree

from .entity import declarative_base
from .property import StringProperty, IntegerProperty, DecimalProperty


class MetaData(object):

    namespaces = {
        'edm': 'http://docs.oasis-open.org/odata/ns/edm',
        'edmx': 'http://docs.oasis-open.org/odata/ns/edmx'
    }

    property_types = {
        'Edm.Int32': IntegerProperty,
        'Edm.Int64': IntegerProperty,
        'Edm.String': StringProperty,
        'Edm.Decimal': DecimalProperty,
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
            schema_name = schema.xpath('@Namespace')[0]

            schema_dict = {
                'name': schema_name,
                'entities': [],
            }

            for entity_type in xmlq(schema, 'edm:EntityType'):
                entity_name = entity_type.xpath('@Name')[0]

                entity_type_name = '.'.join([schema_name, entity_name])

                entity = {
                    'name': entity_name,
                    'type': entity_type_name,
                    'properties': []
                }

                entity_pk_name = None
                pk_property = entity_type.xpath('edm:Key/edm:PropertyRef', namespaces=self.namespaces)
                if pk_property:
                    entity_pk_name = pk_property[0].xpath('@Name')[0]

                for entity_property in xmlq(entity_type, 'edm:Property'):
                    p_name = entity_property.xpath('@Name')[0]
                    p_type = entity_property.xpath('@Type')[0]

                    entity['properties'].append({
                        'name': p_name,
                        'type': p_type,
                        'is_primary_key': entity_pk_name == p_name,
                    })

                schema_dict['entities'].append(entity)

            schemas.append(schema_dict)

        for schema in xmlq(doc, 'edmx:DataServices/edm:Schema'):
            for entity_set in xmlq(schema, 'edm:EntityContainer/edm:EntitySet'):
                set_name = entity_set.xpath('@Name')[0]
                set_type = entity_set.xpath('@EntityType')[0]

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