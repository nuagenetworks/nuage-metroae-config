#!/usr/bin/env python
template = """## Feature Template: {{ name }}
#### Description
{{ description }}

#### Usage
{{ usage }}

#### Template File Name
{{ file_name }}

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
- template: {{ name }}
  values:
{% for variable in variables %}
{% if loop.index == 1 %}    - {% else %}      {% endif %}{{ "%-50s"|format(variable.name+": \\\"\\\"") }}# ({% if variable.optional %}opt {% endif %}{{ variable.type}})
{% endfor %}
```

#### Parameters
{% for variable in variables %}
*{{ variable.name }}:* {{ variable.description }}<br>
{% endfor %}

#### Restrictions
{% for restriction in restrictions %}
**{{ restriction.operation }}:**
{% for item in restriction.restriction_list %}
* {{ item }}

{% endfor %}
{% endfor %}

#### Examples
{% for example in examples %}
##### {{ example.name }}
{{ example.description }}
User input file {{ example.user_input.file_name }}:

```
{{ example.user_input.user_data }}
```

```
{{ example.user_input.sample_run }}
```
{% endfor %}
"""
