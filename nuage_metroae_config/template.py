import jinja2
import jinja2.ext
import json
import os
import re
import sys
import yaml

from .document_template_md import DOCUMENT_TEMPLATE_MD
from .errors import (MissingTemplateError,
                     TemplateParseError,
                     UndefinedVariableError,
                     VariableValueError)
from .util import get_dict_field_no_case

JSON_SCHEMA_URL = "http://json-schema.org/draft-04/schema#"
JSON_SCHEMA_ID_PREFIX = "urn:nuage-metro:config:template:"
JSON_SCHEMA_TITLE = "Nuage Metro Config template "
VALID_VARIABLE_TYPES = ["string", "reference", "integer", "float", "boolean",
                        "ipv4", "ipv6", "ipv4_or_6", "choice", "list"]
JSON_SCHEMA_STRING_TYPES = ["string", "reference", "ipv4", "ipv6", "ipv4_or_6"]
EXAMPLE_COMMENT_SPACING = 40


class Template(object):
    """
    Configuration template.  This class is read-only.
    """
    def __init__(self):
        """
        Standard constructor.
        """
        self.filename = "(unknown)"
        self.template_string = None
        self.name = "Unknown"
        self.description = None
        self.template_version = "1.0"
        self.engine_version = "1.0"
        self.software_type = None
        self.software_version = None
        self.variables = None
        self.property_order = 10

        self.documentation = None

    def __str__(self):
        return self.get_name() + " template"

    def get_name(self):
        """
        Returns the name of this template.
        """
        return self.name

    def get_template_version(self):
        """
        Returns the template version
        """
        return self.template_version

    def get_software_version(self):
        """
        Returns a dictionary of {"software_version": "xxx",
                                 "software_type": "xxx"}
        """
        return {"software_version": self.software_version,
                "software_type": self.software_type}

    def get_engine_version(self):
        """
        Returns the engine version required for the template
        """
        return self.engine_version

    def is_supported_by_engine(self, engine_version):
        if engine_version is not None:
            return self._version_compare(self.engine_version,
                                         engine_version) <= 0
        else:
            return True

    def is_matching_version(self, device_version):
        """
        Returns True if template is valid for given device version
        """
        if device_version["software_type"] is not None:
            if (self.software_type is None or
                    device_version["software_type"].lower() !=
                    self.software_type.lower()):
                return False

            if device_version["software_version"] is not None:
                if (self.software_version is not None and
                    self._version_compare(
                        self.software_version,
                        device_version["software_version"]) <= 0):
                    return True
                else:
                    return False
            else:
                return True
        else:
            return True

    def is_newer_than(self, other_template):
        """
        Returns True if this template is a newer version than the other
        specified template
        """
        if (other_template.software_version is not None and
                self.software_version is not None):
            compare = self._version_compare(self.software_version,
                                            other_template.software_version)
            if (compare < 0):
                return False
            elif (compare > 0):
                return True
        elif (other_template.software_version is not None):
            return False
        elif (self.software_version is not None):
            return True

        other_template_version = other_template.get_template_version()
        compare = self._version_compare(self.template_version,
                                        other_template_version)

        return compare > 0

    def get_schema(self):
        """
        Returns the schema for the template variables in json-schema form.
        """
        schema = self._convert_variables_to_schema()
        return json.dumps(schema, indent=2)

    def get_example(self):
        """
        Returns example user-data for template variables in YAML format.
        """
        return self._convert_variables_to_example()

    def get_documentation(self):
        """
        Returns template documentation in MarkDown format.
        """
        return self._generate_md_documentation()

    def get_doc_file_name(self):
        file_name = None
        if (self.documentation is not None and
                "document_file" in self.documentation):
            file_name = self.documentation["document_file"]

        # return file_name[:-3] + "-example" + file_name[-3:]
        return file_name

    def validate_template_data(self, **template_data):
        """
        Validates that the template_data provided matches the variables schema.
        Returns True if ok, otherwise an exception is raised.
        """
        self._validate_data(template_data)
        return True

    #
    # Private functions to do the work
    #

    def _parse_without_vars(self, template_string, filename):
        self.filename = filename
        self.template_string = template_string
        filled_template = self._replace_vars_with_null()
        template_dict = self._decode_to_dict(filled_template)
        self._parse_headers(template_dict)
        self._parse_documentation(template_dict)

    def _decode_to_dict(self, filled_template):
        try:
            template_dict = yaml.safe_load(filled_template)
        except yaml.YAMLError as e:
            if hasattr(e, 'problem_mark'):
                lineno = str(e.problem_mark.line)
            else:
                lineno = '?'
            raise TemplateParseError("Syntax error in %s:%s: %s" %
                                     (self.filename, lineno, str(e)))
        return template_dict

    def _replace_vars_with_null(self):
        try:
            template = jinja2.Template(
                self.template_string,
                extensions=(RegularExpressionExtension,),
                autoescape=False,
                undefined=NullUndefined)

            return template.render()
        except jinja2.TemplateSyntaxError as e:
            raise TemplateParseError("Syntax error in %s:%d: %s" %
                                     (self.filename, e.lineno, e.message))

    def _parse_headers(self, template_dict):
        self.name = self._get_required_field(template_dict, "name")
        self.description = get_dict_field_no_case(template_dict, "description")
        version = get_dict_field_no_case(template_dict, "template-version")
        if version is not None:
            self.template_version = str(version)
        version = get_dict_field_no_case(template_dict, "engine-version")
        if version is not None:
            self.engine_version = str(version)
        self.software_type = \
            self._get_required_field(template_dict, "software-type")
        self.software_version = \
            self._get_required_field(template_dict, "software-version")
        self.variables = \
            self._get_required_field(template_dict, "variables")
        self._get_required_field(template_dict, "actions")
        # Convert the variables to a schema even though we are not going to
        # use it right now.  This validates the variables.
        self._convert_variables_to_schema()

    def _get_required_field(self, template_dict, field):
        try:
            value = get_dict_field_no_case(template_dict, field)
            if value is not None:
                return value
        except TypeError:
            pass

        raise TemplateParseError(
            "In template %s, Required field %s missing" % (self.filename,
                                                           field))

    def _version_compare(self, version_l, version_r):
        version_l_list = version_l.split(".")
        version_r_list = version_r.split(".")

        for pair in zip(version_l_list, version_r_list):
            try:
                if int(pair[0]) < int(pair[1]):
                    return -1
                if int(pair[0]) > int(pair[1]):
                    return 1
            except ValueError:
                break

        return len(version_l_list) - len(version_r_list)

    def _convert_variables_to_schema(self):
        new_schema = dict()
        self._generate_schema_headers(new_schema)
        item_schema = dict()
        self._generate_item_headers(item_schema)
        new_schema["items"] = item_schema
        self._generate_schema_properties(item_schema)
        self._generate_schema_required(item_schema)

        return new_schema

    def _generate_schema_headers(self, new_schema):
        new_schema['$schema'] = JSON_SCHEMA_URL
        name = self.get_name()
        new_schema['$id'] = (JSON_SCHEMA_ID_PREFIX +
                             name.lower().replace(' ', '-'))
        new_schema['title'] = JSON_SCHEMA_TITLE + name
        if self.description is not None:
            new_schema['description'] = self.description
        else:
            new_schema['description'] = "(no description)"
        new_schema['type'] = "array"

    def _generate_item_headers(self, item_schema):
        item_schema["type"] = "object"
        item_schema["title"] = self.get_name()
        item_schema["additionalProperties"] = False

    def _generate_schema_properties(self, new_schema):
        props = dict()
        new_schema['properties'] = props

        self.property_order = 10

        for variable in self.variables:
            self._generate_schema_property(props, variable)
            self.property_order += 10

    def _generate_schema_property(self, props, variable):
        name = self._get_required_field(variable, "name")
        var_type = self._get_required_field(variable, "type")

        info = dict()
        props[name] = info

        title = name.lower().replace('_', ' ')
        title = title[0].upper() + title[1:]
        info['title'] = title
        info['propertyOrder'] = self.property_order

        description = get_dict_field_no_case(variable, "description")
        if description is not None:
            info['description'] = description

        default = get_dict_field_no_case(variable, "default")
        if default is not None:
            info['default'] = default

        self._validate_variable_type(var_type, name)

        if var_type.lower() == "list":
            new_info = dict()
            info['type'] = "array"
            info['items'] = new_info

            info = new_info
            var_type = self._get_required_field(variable, "item-type")

        self._generate_schema_value(info, variable, var_type, name)

    def _generate_schema_value(self, info, variable, var_type, var_name):
        self._validate_variable_type(var_type, var_name)
        lower_type = var_type.lower()

        if lower_type in JSON_SCHEMA_STRING_TYPES:
            info['type'] = "string"
        elif lower_type == "choice":
            choices = self._get_required_field(variable, "choices")
            if type(choices) != list:
                raise TemplateParseError(
                    "In template %s, variable %s: choices must be a list" %
                    (self.filename, var_name))
            info['enum'] = choices
        else:
            info['type'] = lower_type

    def _validate_variable_type(self, var_type, var_name):
        lower_type = var_type.lower()

        if lower_type not in VALID_VARIABLE_TYPES:
            raise TemplateParseError(
                "In template %s, variable %s: Invalid type %s" %
                (self.filename, var_name, var_type))

    def _generate_schema_required(self, new_schema):
        required = list()
        new_schema['required'] = required

        for variable in self.variables:
            if 'optional' not in variable or variable['optional'] is False:
                name = self._get_required_field(variable, "name")
                required.append(name)

    def _convert_variables_to_example(self, indent=2):
        lines = []

        if self.description is not None:
            lines.append("# " + self.description)
        lines.append("- template: " + self.get_name())
        lines.append("  values:")

        first = True
        for variable in self.variables:
            if first is True:
                first = False
                prefix = " " * (indent * 2) + "- "
            else:
                prefix = " " * ((indent * 2) + 2)

            lines.append(prefix + self._generate_value_example(variable))

        lines.append("")

        return '\n'.join(lines)

    def _generate_value_example(self, variable):
        name = self._get_required_field(variable, "name")
        var_type = self._get_required_field(variable, "type").lower()
        descr = get_dict_field_no_case(variable, "description")
        optional = get_dict_field_no_case(variable, "optional")
        type_info = var_type

        if var_type in ["string", "reference"]:
            value = '""'
        elif var_type == "integer":
            value = "0"
            type_info += self._generate_range_example(variable)
        elif var_type == "float":
            value = "0.0"
            type_info += self._generate_range_example(variable)
        elif var_type == "boolean":
            value = "False"
        elif var_type in ["ipv4", "ipv4_or_6"]:
            value = "0.0.0.0"
        elif var_type == "ipv6":
            value = "0::0"
        elif var_type == "choice":
            choices = self._get_required_field(variable, "choices")
            value = choices[0]
            type_info = str(choices)
        elif var_type == "list":
            item_type = self._get_required_field(variable, "item-type")
            value = "[]"
            type_info = "list of " + item_type
        else:
            value = "null"

        entry_str = "%s: %s" % (name, value)
        spacing = EXAMPLE_COMMENT_SPACING - len(entry_str)
        opt_str = ""
        if optional is True:
            opt_str = "opt "
        descr_str = ""
        if descr is not None:
            descr_str = " " + descr
        comment = "(%s%s)%s" % (opt_str, type_info, descr_str)

        return "%s %s# %s" % (entry_str, " " * spacing, comment)

    def _generate_range_example(self, variable):
        ranges = get_dict_field_no_case(variable, "range")
        if ranges is not None:
            if type(ranges) != list:
                ranges = [ranges]

            range_strs = [str(x) for x in ranges]
            return " " + ", ".join(range_strs)
        else:
            return ""

    def _replace_vars_with_kwargs(self, **kwargs):
        try:
            self._verify_all_vars_defined(**kwargs)
            template = jinja2.Template(self.template_string,
                                       extensions=(JSONEscapingExtension,
                                                   RegularExpressionExtension),
                                       autoescape=False,
                                       undefined=jinja2.StrictUndefined)

            return template.render(**kwargs)
        except jinja2.TemplateSyntaxError as e:
            raise TemplateParseError("Syntax error in %s:%d: %s" %
                                     (self.filename, e.lineno, e.message))
        except jinja2.UndefinedError as e:
            raise UndefinedVariableError("In template %s: Variable value %s" %
                                         (self.get_name(), e.message))

    def _verify_all_vars_defined(self, **kwargs):
        template = jinja2.Template(self.template_string,
                                   extensions=(RegularExpressionExtension,),
                                   autoescape=False,
                                   undefined=jinja2.StrictUndefined)
        template.render(**kwargs)

    def _parse_with_vars(self, **kwargs):
        filled_template = self._replace_vars_with_kwargs(**kwargs)
        return self._decode_to_dict(filled_template)

    def _validate_data(self, data):
        var_info = self._generate_variable_info()

        for name, value in data.items():
            self._validate_against_variable_info(var_info, name, value)

        self._validate_required_data(var_info, data)

    def _generate_variable_info(self):
        var_info = dict()

        for variable in self.variables:
            var_name = self._get_required_field(variable, "name")
            var_info[var_name] = variable

        return var_info

    def _validate_against_variable_info(self, var_info, var_name, value):
        if var_name in var_info:
            var_schema = var_info[var_name]
        else:
            # No variable definition for given data.  Extra variables are ok.
            return True

        var_type = self._get_required_field(var_schema, "type").lower()

        if var_type == "list":
            if type(value) != list:
                self._raise_value_error(var_name, "is not a list")

            item_type = self._get_required_field(var_schema,
                                                 "item-type").lower()

            for item in value:
                self._validate_variable_value(var_schema, var_name, item,
                                              item_type)
        else:
            self._validate_variable_value(var_schema, var_name, value,
                                          var_type)

        return True

    def _validate_variable_value(self, var_schema, var_name, value, var_type):
        if var_type in JSON_SCHEMA_STRING_TYPES:
            if isinstance(value, str) or (
                    sys.version_info < (3,) and isinstance(value, unicode)):
                return True
            else:
                allow_int = get_dict_field_no_case(var_schema, "allow-integer")
                if allow_int is True and type(value) == int:
                    return True
                else:
                    self._raise_value_error(var_name, "is not a string")
        elif var_type == "integer":
            if type(value) == int:
                self._validate_range(var_schema, var_name, value)
                return True
            else:
                self._raise_value_error(var_name, "is not an integer")
        elif var_type == "float":
            if type(value) == int or type(value) == float:
                self._validate_range(var_schema, var_name, value)
                return True
            else:
                self._raise_value_error(var_name, "is not a float")
        elif var_type == "boolean":
            if value is True or value is False:
                return True
            else:
                self._raise_value_error(var_name, "is not a boolean")
        elif var_type == "choice":
            if not isinstance(value, str):
                self._raise_value_error(var_name, "is not a string")
            choices = self._get_required_field(var_schema, "choices")
            upper_choices = [x.upper() for x in choices]
            if value.upper() in upper_choices:
                return True
            else:
                self._raise_value_error(var_name, "is not a valid choice")

    def _validate_range(self, var_schema, var_name, value):
        ranges = get_dict_field_no_case(var_schema, "range")
        if ranges is not None:
            if type(ranges) != list:
                ranges = [ranges]

            for r in ranges:
                if isinstance(r, str):
                    try:
                        low, high = r.split("..")
                        low = float(low)
                        high = float(high)
                        if high < low:
                            raise ValueError("High of range greater than low")
                        if value >= low and value <= high:
                            return True
                    except ValueError:
                        self._raise_value_error(
                            var_name, "invalid range, format is <low>..<high>")
                elif r == value:
                    return True

            self._raise_value_error(var_name, "is not in valid range")

    def _validate_required_data(self, var_info, data):
        missing = []
        for var_name, var_schema in var_info.items():
            optional = get_dict_field_no_case(var_schema, "optional")
            if optional is not True and var_name not in data:
                missing.append(var_name)

        if len(missing) == 0:
            return True
        else:
            raise UndefinedVariableError(
                "In template %s, missing required variables: %s" %
                (self.get_name(), ', '.join(missing)))

    def _raise_value_error(self, var_name, message):
        raise VariableValueError("In template %s, variable %s: %s" % (
            self.get_name(), var_name, message))

    def _parse_documentation(self, template_dict):
        self.documentation = dict()

        self.documentation["document_file"] = None
        self.documentation["usage"] = "(documentation missing)"
        self.documentation["restrictions"] = []
        self.documentation["examples"] = []

        file = get_dict_field_no_case(template_dict, "doc-file")
        if file is not None:
            self.documentation["document_file"] = file

        usage = get_dict_field_no_case(template_dict, "usage")
        if usage is not None:
            self.documentation["usage"] = usage

        restrictions = get_dict_field_no_case(template_dict, "restrictions")
        if restrictions is not None:
            self.documentation["restrictions"] = restrictions

        examples = get_dict_field_no_case(template_dict, "examples")
        if examples is not None:
            self.documentation["examples"] = examples

    def _generate_md_documentation(self):
        doc_vars = dict(self.documentation)
        doc_vars["name"] = self.name
        if self.description is not None:
            doc_vars["description"] = self.description
        else:
            doc_vars["description"] = "(missing documentation)"
        doc_vars["variables"] = self.variables
        doc_vars["template_file_name"] = self.filename

        doc_vars["user_data"] = self.get_example()

        try:
            template = jinja2.Template(
                DOCUMENT_TEMPLATE_MD,
                autoescape=False,
                undefined=jinja2.StrictUndefined)

            return template.render(**doc_vars)
        except jinja2.TemplateSyntaxError as e:
            raise TemplateParseError("Syntax error in %s:%d: %s" %
                                     (self.filename, e.lineno, e.message))


class TemplateStore(object):
    """
    Reads and parses configuration templates.
    """
    def __init__(self, engine_version=None):
        """
        Standard constructor.
        """
        self.templates = dict()
        self.engine_version = engine_version

    def read_templates(self, path_or_file_name):
        """
        Reads and parses templates from either all templates in a
        directory path, or a single template specified by filename.
        Both yaml (.yml) and JSON (.json) files are supported.
        """
        if (os.path.isdir(path_or_file_name)):
            for file_name in os.listdir(path_or_file_name):
                if (file_name.endswith(".yml") or
                        file_name.endswith(".yaml") or
                        file_name.endswith(".json")):
                    full_path = os.path.join(path_or_file_name, file_name)
                    template_string = self._read_template(full_path)
                    self.add_template(template_string, full_path)
        elif os.path.isfile(path_or_file_name):
            template_string = self._read_template(path_or_file_name)
            self.add_template(template_string, path_or_file_name)
        else:
            raise TemplateParseError("File or path not found: " +
                                     path_or_file_name)

    def add_template(self, template_string, filename=None):
        """
        Parses the specified string as a template in Yaml or JSON format.
        """
        template = Template()
        if filename is None:
            filename = "(internal)"
        template._parse_without_vars(template_string, filename)
        self._register_template(template)

    def get_template_names(self, software_type=None, software_version=None):
        """
        Returns a list of all template names currently loaded in store.
        If software_version and/or software_type is provided, names will
        be filtered by the specified version/type.
        """
        names = list()
        for key, template_list in self.templates.items():
            template = self._get_latest_template(template_list,
                                                 software_type,
                                                 software_version)
            if (template is not None and
                    template.is_supported_by_engine(self.engine_version)):
                names.append(template.get_name())

        names.sort()
        return names

    def get_template(self, name, software_type=None, software_version=None):
        """
        Returns a Template object of the specified name.  If software_version
        and/or software_type is provided, template of specified version/type
        will be returned.
        """
        if name.lower() not in self.templates:
            raise MissingTemplateError("No template with name " + name)

        template_list = self.templates[name.lower()]
        template = self._get_latest_template(template_list,
                                             software_type,
                                             software_version)

        if template is None:
            raise MissingTemplateError(
                "%s templates do not support software version %s %s" % (
                    name, str(software_type), str(software_version)))

        if not template.is_supported_by_engine(self.engine_version):
            raise MissingTemplateError(
                "%s template requires configuration engine version %s" % (
                    name, str(template.get_engine_version())))

        return template

    #
    # Private functions to do the work
    #

    def _read_template(self, filename):
        try:
            with open(filename, 'r') as file:
                return file.read()
        except Exception as e:
            raise TemplateParseError("Error reading template: " + str(e))

    def _register_template(self, template):
        template_name = template.get_name().lower()

        if template_name not in self.templates:
            self.templates[template_name] = list()

        self.templates[template_name].append(template)

    def _get_latest_template(self, template_list,
                             software_type,
                             software_version):
        latest_template = None
        for template in template_list:
            if template.is_matching_version({
                    "software_version": software_version,
                    "software_type": software_type}):
                if latest_template is not None:
                    if template.is_newer_than(latest_template):
                        latest_template = template
                else:
                    latest_template = template

        return latest_template


#
# Private classes to do the work
#

class NullUndefined(jinja2.Undefined):
    """
    Renders undefined template variables as null
    """
    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __bool__(self):
        return False

    def __unicode__(self):
        return "null"


class JSONEscapingExtension(jinja2.ext.Extension):
    """
    Insert a `|tojson` filter at the end of every variable substitution.

    This will ensure that all injected values are converted to JSON.
    """
    def filter_stream(self, stream):
        # This is based on https://github.com/pallets/jinja/issues/503
        for token in stream:
            if token.type == 'variable_end':
                yield jinja2.lexer.Token(token.lineno, 'pipe', '|')
                yield jinja2.lexer.Token(token.lineno, 'name', 'tojson')
            yield token


def jinja2_match_filter(s, pattern):
    return re.match(pattern, s)


class RegularExpressionExtension(jinja2.ext.Extension):
    # Add regular expression match filter to Jinja2
    def __init__(self, environment):
        environment.filters['match'] = jinja2_match_filter
