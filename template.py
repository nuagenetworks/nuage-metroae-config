import jinja2
import jinja2.ext
import os
import yaml


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
        self.schema = None

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
        Returns the schema for the template variables in dictionary form.
        Format:
            {"schema": [{"name": "Field name",
             "type": "Data type",
             ...}, ...]}
        """
        return {"schema": self.schema}

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
        self._validate_field(template_dict, "name")
        self._validate_field(template_dict, "software-type")
        self._validate_field(template_dict, "software-version")
        self._validate_field(template_dict, "variables")
        self._validate_field(template_dict, "actions")

        self.name = template_dict["name"]
        self.software_type = template_dict["software-type"]
        self.software_version = template_dict["software-version"]
        self.schema = template_dict["variables"]

    def _validate_field(self, template_dict, field):
        if field not in template_dict or template_dict[field] is None:
            raise TemplateParseError(
                "Required field %s missing from template %s" % (field,
                                                                self.filename))

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
            raise UndefinedVariableError("For template %s: Variable value %s" %
                                         (self.get_name(), e.message))

    def _verify_all_vars_defined(self, **kwargs):
        template = jinja2.Template(self.template_string,
                                   autoescape=False,
                                   undefined=jinja2.StrictUndefined)
        template.render(**kwargs)

    def _parse_with_vars(self, **kwargs):
        filled_template = self._replace_vars_with_kwargs(**kwargs)
        return self._decode_to_dict(filled_template)


class TemplateStore(object):
    """
    Reads and parses configuration templates.
    """
    def __init__(self):
        """
        Standard constructor.
        """
        self.templates = {}

    def read_templates(self, path_or_file_name):
        """
        Reads and parses templates from either all templates in a
        directory path, or a single template specified by filename.
        The file extension determines the file type. Either yaml (.yml)
        or JSON (.json).
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
