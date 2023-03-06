<%page args="nav_property, values"/>\
<%
    property_type = nav_property.entitycls
    simple_type = full_type = property_type.__name__.split(".")[-1]
    full_type = '"' + full_type + '"'
    if nav_property.is_collection:
        full_type = "list[" + full_type + "]"
%>\
    ${values['name']}: ${full_type} = NavigationProperty(name="${values['name']}", entity_package="${package}", entitycls="${simple_type}"\
  % if nav_property.is_collection:
, collection=True\
  % endif
  % if nav_property.foreign_key:
, foreign_key=${nav_property.foreign_key}\
  % endif
)