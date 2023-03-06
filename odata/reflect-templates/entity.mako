<%page args="name, entity"/>\
<% short_name = name.split(".")[-1] %>\
class ${short_name}(ReflectionBase):
    __odata_collection__ = \
    %if entity.__odata_collection__:
"${entity.__odata_collection__}"
    %else:
None
    %endif
    __odata_type__ = "${entity.__odata_type__}"
  <%
    schema = entity.__odata_schema__
  %>
    # Simple properties
  %for prop in schema['properties']:
<% attr = getattr(entity, prop['name']) %>\
<%include file="property.mako" args="property=attr, values=prop"/>
  %endfor

    # Navigation properties
  %for nav_prop in schema['navigation_properties']:
<% attr = getattr(entity, nav_prop['name']) %>\
<%include file="nav_property.mako" args="nav_property=attr, values=nav_prop"/>
  %endfor

