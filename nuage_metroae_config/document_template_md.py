DOCUMENT_TEMPLATE_MD = """## Feature Template: {{ name }}
#### Description
{{ description }}

#### Usage
{{ usage }}

#### Template File Name
{{ template_file_name }}

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
{{ user_data }}
```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
{% for variable in variables -%}
{{ variable.name }} | {% if variable.optional | default(False) %}optional{% else %}required{% endif %} | {{ variable.type }} | {{ variable.description | default("") }}
{% endfor %}

#### Restrictions
{% for restriction in restrictions -%}
**{{ restriction.operation }}:**
{% for item in restriction['restriction-list'] -%}
* {{ item }}
{% endfor %}
{% endfor -%}
"""

DOCUMENT_README_MD = """# Standard Template Documentation

{% for template in template_info | sort(attribute="name") -%}
[{{ template.name }}]({{ template.file }})<br>
{% endfor %}

"""
