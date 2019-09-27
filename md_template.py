#!/usr/bin/env python
template = """## Feature Template: {{ data['name'] }}
#### Description
{{ data['description'] }}

#### Usage
{{ data['usage'] }}

#### Template File Name
{{ data['template-file-name'] }}

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
- template: {{ data['name'] }}
  values:
{% for variable in data['variables'] %}
{% if loop.index == 1 %}    - {% else %}      {% endif %}{{ "%-50s"|format(variable.name+": \\\"\\\"") }}# ({% if variable.optional %}opt {% endif %}{{ variable.type }})
{% endfor %}
```

#### Parameters
{% for variable in data['variables'] %}
*{{ variable.name }}:* {{ variable.description }}<br>
{% endfor %}

#### Restrictions
{% for restriction in data['restrictions'] %}
**{{ restriction.operation }}:**
{% for item in restriction['restriction-list'] %}
* {{ item }}

{% endfor %}
{% endfor %}

#### Examples
{% for example in data['examples'] %}
##### {{ example.name }}
{{ example.description }}
User input file {{ example['user-input']['file-name'] }}:

```
{{ example['user-input']['user-data'] }}
```

```
{{ example['user-input']['sample-run'] }}
```
{% endfor %}
"""
