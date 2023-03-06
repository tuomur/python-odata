<%page args="property, values"/>\
<%
    property_type = type(property)
    simple_type = property_type.__name__.split(".")[-1]
    full_type = type_translations[simple_type]
    if property.is_collection:
        full_type = "list[" + simple_type + "]"
%>\
    ${values['name']}: ${full_type} = ${simple_type}("${values['name']}"\
  % if property.primary_key:
, primary_key=True\
  % endif
  % if property.is_collection:
, is_collection=True\
  % endif
  % if property.is_computed_value:
, is_computed_value=True\
  % endif
)