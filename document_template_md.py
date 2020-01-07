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
{% for variable in variables -%}
*{{ variable.name }}:* {{ variable.description }}<br>
{% endfor %}

#### Restrictions
{% for restriction in restrictions -%}
**{{ restriction.operation }}:**
{% for item in restriction['restriction-list'] -%}
* {{ item }}
{% endfor %}
{% endfor -%}
#### Examples
{% for example in examples %}
##### {{ example.name }}
{{ example.description }}
{% if 'user-data' in example -%}
```
{{ example['user-data'] }}
```
{% endif -%}
{% if 'sample-run' in example -%}

```
{{ example['sample-run'] }}
```
{% endif -%}
{% endfor %}
"""
