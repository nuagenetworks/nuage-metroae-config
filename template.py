import jinja2
import jinja2.ext
import json
import os
import yaml

from util import get_dict_field_no_case

JSON_SCHEMA_URL = "http://json-schema.org/draft-04/schema#"
JSON_SCHEMA_ID_PREFIX = "urn:nuage-metro:levistate:template:"
JSON_SCHEMA_TITLE = "Schema validator for Nuage Metro Levistate template "
VALID_VARIABLE_TYPES = ["string", "reference", "integer", "boolean", "ipv4",
                        "ipv6", "ipv4_or_6", "choice", "list"]
JSON_SCHEMA_STRING_TYPES = ["string", "reference", "ipv4", "ipv6", "ipv4_or_6"]


class TemplateError(Exception):
    """
    Exception class for all template errors
    """
    pass


class TemplateParseError(TemplateError):
    """
    Exception class for errors parsing a template
    """
    pass


class MissingTemplateError(TemplateError):
    """
    Exception class when a template of specified name is not defined
    """
    pass


class UndefinedVariableError(TemplateError):
    """
    Exception class when a required variable value is not defined
    """
    pass


class VariableValueError(TemplateError):
    """
    Exception class when a variable contains the wrong value
    """
    pass


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
        self.template_version = "1.0"
        self.software_type = None
        self.software_version = None
        self.variables = None

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

    def get_schema(self):
        """
        Returns the schema for the template variables in json-schema form.
        """
        schema = self._convert_variables_to_schema()
        return json.dumps(schema, indent=2)

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
            template = jinja2.Template(self.template_string,
                                       autoescape=False,
                                       undefined=NullUndefined)

            return template.render()
        except jinja2.TemplateSyntaxError as e:
            raise TemplateParseError("Syntax error in %s:%d: %s" %
                                     (self.filename, e.lineno, e.message))

    def _parse_headers(self, template_dict):
        self.name = self._get_required_field(template_dict, "name")
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

    def _convert_variables_to_schema(self):
        new_schema = dict()
        self._generate_schema_headers(new_schema)
        self._generate_schema_properties(new_schema)
        self._generate_schema_required(new_schema)

        return new_schema

    def _generate_schema_headers(self, new_schema):
        new_schema['$schema'] = JSON_SCHEMA_URL
        name = self.get_name()
        new_schema['$id'] = (JSON_SCHEMA_ID_PREFIX +
                             name.lower().replace(' ', '-'))
        new_schema['title'] = JSON_SCHEMA_TITLE + name
        new_schema['type'] = "object"

    def _generate_schema_properties(self, new_schema):
        props = dict()
        new_schema['properties'] = props

        for variable in self.variables:
            self._generate_schema_property(props, variable)

    def _generate_schema_property(self, props, variable):
        name = self._get_required_field(variable, "name")
        var_type = self._get_required_field(variable, "type")

        info = dict()
        props[name] = info

        title = name.lower().replace('_', ' ')
        title = title[0].upper() + title[1:]
        info['title'] = title

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

    def _replace_vars_with_kwargs(self, **kwargs):
        try:
            self._verify_all_vars_defined(**kwargs)
            template = jinja2.Template(self.template_string,
                                       extensions=(JSONEscapingExtension,),
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
                                   autoescape=False,
                                   undefined=jinja2.StrictUndefined)
        template.render(**kwargs)

    def _parse_with_vars(self, **kwargs):
        filled_template = self._replace_vars_with_kwargs(**kwargs)
        return self._decode_to_dict(filled_template)

    def _validate_data(self, data):
        var_info = self._generate_variable_info()

        for name, value in data.iteritems():
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
            if isinstance(value, basestring):
                return True
            else:
                self._raise_value_error(var_name, "is not a string")
        elif var_type == "integer":
            if type(value) == int:
                return True
            else:
                self._raise_value_error(var_name, "is not an integer")
        elif var_type == "boolean":
            if value is True or value is False:
                return True
            else:
                self._raise_value_error(var_name, "is not a boolean")
        elif var_type == "choice":
            choices = self._get_required_field(var_schema, "choices")
            if value in choices:
                return True
            else:
                self._raise_value_error(var_name, "is not a valid choice")

    def _validate_required_data(self, var_info, data):
        missing = []
        for var_name, var_schema in var_info.iteritems():
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


class TemplateStore(object):
    """
    Reads and parses configuration templates.
    """
    def __init__(self):
        """
        Standard constructor.
        """
        self.templates = dict()

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

    def get_template_names(self, software_version=None, software_type=None):
        """
        Returns a list of all template names currently loaded in store.
        If software_version and/or software_type is provided, names will
        be filtered by the specified version/type.
        """
        if software_version is not None or software_type is not None:
            raise NotImplementedError(
                "Template software versioning not yet implemented")

        names = []
        for key, value in self.templates.iteritems():
            names.append(self.templates[key].get_name())

        return names

    def get_template(self, name, software_version=None, software_type=None):
        """
        Returns a Template object of the specified name.  If software_version
        and/or software_type is provided, template of specified version/type
        will be returned.
        """
        if software_version is not None or software_type is not None:
            raise NotImplementedError(
                "Template software versioning not yet implemented")

        if name.lower() not in self.templates:
            raise MissingTemplateError("No template with name " + name)

        return self.templates[name.lower()]

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
        template_name = template.get_name()
        if template_name.lower() in self.templates:
            raise NotImplementedError(
                "Template versioning not yet implemented")

        self.templates[template_name.lower()] = template


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
