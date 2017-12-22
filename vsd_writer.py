import json
import os

from bambou import NURESTFetcher, NURESTSession, NURESTObject, NURESTRootObject
from bambou.exceptions import BambouHTTPError

SPEC_EXTENSION = ".spec"


class TemplateWriterError(Exception):
    """
    Exception class for all template writing errors
    """
    pass


class MissingSessionParamsError(TemplateWriterError):
    """
    Exception class when session is started without parameters specified
    """
    pass


class SessionNotStartedError(TemplateWriterError):
    """
    Exception class when session is used when not started.
    """
    pass


class SessionError(TemplateWriterError):
    """
    Exception class when there is an error in the session
    """
    pass


class InvalidSpecification(TemplateWriterError):
    """
    Exception class when there is an error parsing a VSD API specification
    """
    pass


class MissingSelectionError(TemplateWriterError):
    """
    Exception class when an object was not found during selection
    """
    pass


class MultipleSelectionError(TemplateWriterError):
    """
    Exception class when multiple objects were found during selection
    """
    pass


# TODO:
# class VsdWriter(DeviceWriterBase):
class VsdWriter(object):
    """
    Writes configuration to a VSD.  This class is a derived class from
    the DeviceWriterBase Abstract Base Class.
    """
    def __init__(self):
        """
        Derived class from DeviceWriterBase.
        """
        self.session_params = None
        self.session = None
        self.version = "5.0"
        self.api_prefix = "nuage/api"
        self.specs = dict()
        self.root_spec_name = None
        self.log_entries = []

    def set_session_params(self, url, username="csproot",
                           password="csproot", enterprise="csp"):
        """
        Sets the parameters necessary to connect to the VSD.  This must
        be called before writing or an exception will be raised.
        """
        self.session_params = {
            'username': username,
            'password': password,
            'enterprise': enterprise,
            'api_url': url}

    def read_api_specifications(self, path_or_file_name):
        """
        Reads the VSD configuration API specifications from JSON files
        in the specified path or file name.  This must be called before
        writing or an exception will be raised.
        """
        if (os.path.isdir(path_or_file_name)):
            for file_name in os.listdir(path_or_file_name):
                if (file_name.endswith(SPEC_EXTENSION) and
                        not file_name.startswith('@')):
                    spec_json = self._read_specification(os.path.join(
                        path_or_file_name, file_name))
                    self._register_specification(spec_json)
        elif (os.path.isfile(path_or_file_name)):
            spec_json = self._read_specification(path_or_file_name)
            self._register_specification(spec_json)
        else:
            raise InvalidSpecification("File or path not found: " +
                                       path_or_file_name)

    #
    # Implement all required Abstract Base Class prototype functions.
    #

    def log(self, log_type, message):
        self.log_entries.append((log_type, message))

    def log_error(self, message):
        self.log('ERROR', message)

    def log_debug(self, message):
        self.log('DEBUG', message)

    def get_logs(self):
        log_output = []
        for entry in self.log_entries:
            log_output.append("%s: %s" % entry)

        return '\n'.join(log_output)

    def start_session(self):
        """
        Starts a session with the VSD
        """
        if self.session is None:
            if self.session_params is None:
                raise MissingSessionParamsError(
                    "Cannot start session without parameters")

            self.log_debug("Session start %s" % self.session_params)

            if (self.root_spec_name is None or
                    self.root_spec_name not in self.specs):
                raise InvalidSpecification("No root specification loaded")

            self.session = Session(spec=self.specs[self.root_spec_name],
                                   api_prefix=self.api_prefix,
                                   version=self.version,
                                   **self.session_params)
            self.session.set_enterprise_spec(self.specs['enterprise'])

        try:
            self.session.start()
        except BambouHTTPError as e:
            self.session = None
            raise SessionError(str(e))

    def stop_session(self):
        """
        Stops the session with the VSD
        """
        self.log_debug("Session stopping")

        if self.session is not None:
            self.session.reset()
            self.session = None

    def create_object(self, object_name, context=None):
        """
        Creates an object in the current context, object is not saved to VSD
        """
        self.log_debug("Create object %s [%s]" % (object_name, context))
        self._check_session()

        new_context = self._get_new_child_context(context)

        new_context.current_object = self._get_new_config_object(object_name)
        new_context.object_exists = False

        return new_context

    def select_object(self, object_name, by_field, value, context=None):
        """
        Selects an object in the current context
        """
        self.log_debug("Select object %s %s = %s [%s]" % (object_name,
                                                          by_field,
                                                          value,
                                                          context))
        self._check_session()

        new_context = self._get_new_child_context(context)

        new_context.current_object = self._get_new_config_object(object_name)

        new_context.current_object = self._select_object(
            object_name, by_field, value, new_context.parent_object)
        new_context.object_exists = True

        return new_context

    def delete_object(self, context):
        """
        Deletes the object selected in the current context
        """
        self.log_debug("Delete object [%s]" % context)
        self._check_session()

        if context is None or context.current_object is None:
            raise SessionError("No object for deletion")

        context.current_object.delete()
        context.current_object = None
        context.object_exists = False

        return context

    def set_values(self, context, **kwargs):
        """
        Sets values in the object selected in the current context and saves it
        """
        self.log_debug("Set values [%s] = %s" % (context, kwargs))
        self._check_session()

        if context is None or context.current_object is None:
            raise SessionError("No object for setting values")

        self._set_attributes(context.current_object, **kwargs)

        if context.object_exists:
            self.log_debug("Saving [%s]" % context)
            context.current_object.save()
        else:
            self.log_debug("Creating child [%s]" % context)
            self._add_object(context.current_object, context.parent_object)

        self.log_debug("Saved [%s]" % context)

        return context

    #
    # Private functions to do the work
    #

    def _read_specification(self, file_name):
        try:
            with open(file_name, 'r') as file:
                return file.read()
        except Exception as e:
            raise InvalidSpecification("Error reading spec: " + str(e))

    def _register_specification(self, json_str):
        try:
            spec = json.loads(json_str)
        except Exception as e:
            raise InvalidSpecification("Error parsing spec: " + str(e))

        self._validate_specification(spec)

        name_key = spec['model']['entity_name'].lower()
        self.specs[name_key] = spec

        if 'root' in spec['model'] and spec['model']['root'] is True:
            self.root_spec_name = name_key

    def _validate_specification(self, spec):
        self._validate_specification_field('model', spec)
        self._validate_specification_field('attributes', spec)
        self._validate_specification_field('children', spec)
        self._validate_specification_field('entity_name', spec['model'])
        self._validate_specification_field('resource_name', spec['model'])
        self._validate_specification_field('rest_name', spec['model'])

    def _validate_specification_field(self, field, section):
        if field not in section or section[field] is None:
            raise InvalidSpecification("'%s' missing in specification" % field)

    def _get_specification(self, object_name):
        name_key = object_name.lower()
        if name_key not in self.specs:
            raise InvalidSpecification("No specification for" + object_name)

        return self.specs[name_key]

    def _get_attribute_name(self, spec, local_name):
        if local_name.lower() == "id":
            return "ID"

        for attribute in spec['attributes']:
            remote_name = attribute['name']
            if remote_name.lower() == local_name.lower():
                return remote_name

        raise InvalidSpecification("%s spec does not define an attribute %s" %
                                   (spec['model']['entity_name'],
                                    local_name))

    def _check_session(self):
        if self.session is None:
            raise SessionNotStartedError("Session is not started")

        if self.session.root_object is None:
            raise SessionNotStartedError("Session is invalid")

    def _get_new_child_context(self, old_context):
        new_context = Context()
        if old_context is not None:
            if old_context.current_object is not None:
                new_context.parent_object = old_context.current_object

        return new_context

    def _get_new_config_object(self, object_name):
        spec = self._get_specification(object_name)

        return ConfigObject(spec)

    def _get_fetcher(self, object_name, parent_object=None):
        spec = self._get_specification(object_name)

        if parent_object is None:
            parent_object = self.session.root_object

        return Fetcher(parent_object, spec)

    def _add_object(self, obj, parent_object=None):
        if parent_object is None:
            parent_object = self.session.root_object

        parent_object.current_child_name = obj.__resource_name__
        parent_object.create_child(obj)

    def _select_object(self, object_name, by_field, field_value,
                       parent_object=None):

        fetcher = self._get_fetcher(object_name, parent_object)
        spec = self._get_specification(object_name)
        remote_name = self._get_attribute_name(spec, by_field)

        selector = '%s is "%s"' % (remote_name, field_value)
        objects = fetcher.get(filter=selector)
        if len(objects) == 0:
            raise MissingSelectionError("No %s object exists with %s = %s" %
                                        (object_name, by_field, field_value))
        if len(objects) > 1:
            raise MultipleSelectionError(
                "Multiple %s objects exist with %s = %s" %
                (object_name, by_field, field_value))

        return objects[0]

    def _set_attributes(self, obj, **kwargs):
        for field, value in kwargs.iteritems():
            local_name = field.lower()
            self._get_attribute_name(obj.spec, local_name)
            if hasattr(obj, local_name):
                setattr(obj, local_name, value)
            else:
                raise SessionError("Missing field %s in %s object" %
                                   (local_name,
                                    obj.get_name()))


#
# Private classes to do the work
#

class Context(object):
    """
    The current object context to track the state of the current and parent
    objects.  This class is intended to be private and should not be directly
    modified by external callers of the VSD Writer.
    """
    def __init__(self):
        self.parent_object = None
        self.current_object = None
        self.object_exists = False

    def __str__(self):
        if self.object_exists:
            marker = ''
        else:
            marker = ' **'
        if self.parent_object is None:
            parent = "Root"
        else:
            parent = str(self.parent_object)

        return "%s / %s%s" % (parent, self.current_object, marker)


class Session(NURESTSession):
    """
    Wrapper class around Bambou session needed to override with levistate
    specific methods
    """

    def __init__(self, spec, username, password, enterprise, api_url,
                 api_prefix, version):
        self.spec = spec
        super(Session, self).__init__(username, password, enterprise,
                                      api_url, api_prefix, version)

    def create_root_object(self):
        return Root(self.spec, self.enterprise_spec)

    def set_enterprise_spec(self, enterprise_spec):
        self.enterprise_spec = enterprise_spec


class ConfigObject(NURESTObject):
    """
    Wrapper class around Bambou object needed to override with levistate
    specific methods.  This class is effectively a generic config object of any
    type.
    """
    def __init__(self, spec):
        super(ConfigObject, self).__init__()

        self.spec = spec
        self.current_child_name = None

        self.__resource_name__ = self.spec['model']['resource_name']
        self.__rest_name__ = self.spec['model']['rest_name']

        self._build_attributes()

    def __str__(self):
        obj_name = ''
        if hasattr(self, 'name') and getattr(self, 'name') is not None:
            obj_name = "name=%s, " % getattr(self, 'name')

        return "%s (%sID=%s)" % (self.get_name(), obj_name, str(self.id))

    def get_name(self):
        return self.spec['model']['entity_name']

    def _build_attributes(self):
        for attribute in self.spec['attributes']:
            local_name = attribute['name'].lower()

            self.expose_attribute(local_name,
                                  attribute['type'],
                                  remote_name=attribute['name'],
                                  is_required=attribute['required'],
                                  is_readonly=attribute['read_only'],
                                  max_length=attribute['max_length'],
                                  min_length=attribute['min_length'],
                                  choices=attribute['allowed_choices'],
                                  is_unique=attribute['unique'],
                                  can_order=attribute['orderable'],
                                  can_search=attribute['filterable'])

            if not hasattr(self, local_name):
                setattr(self, local_name, None)

    @property
    def resource_name(self):
        return self.__resource_name__

    @property
    def rest_name(self):
        return self.__rest_name__

    def get_resource_url(self):
        name = self.__resource_name__
        url = self.__class__.rest_base_url()

        if self.id is not None:
            return "%s/%s/%s" % (url, name, self.id)

        return "%s/%s" % (url, name)

    def get_resource_url_for_child_type(self, nurest_object_type):
        if self.current_child_name is None:
            raise SessionError("No child name set for object")
        return self.get_resource_url_for_child_name(self.current_child_name)

    def get_resource_url_for_child_name(self, child_name):
        return "%s/%s" % (self.get_resource_url(), child_name)

    def fetcher_for_rest_name(self, rest_name):
        return list()


class Fetcher(NURESTFetcher):
    """
    Wrapper class around Bambou fetcher needed to override with levistate
    specific methods.  This class is effectively a generic fetcher of any type.
    """
    def __init__(self, parent_object, spec):
        super(Fetcher, self).__init__()

        self.spec = spec
        self.resource_name = spec['model']['resource_name']
        self.parent_object = parent_object

    def new(self):
        return ConfigObject(self.spec)

    def _prepare_url(self):
        return self.parent_object.get_resource_url_for_child_name(
            self.resource_name)


class Root(NURESTRootObject):
    """
    Wrapper class around Bambou root object needed to override with levistate
    specific methods.
    """
    __rest_name__ = "me"
    __resource_name__ = "me"

    def __init__(self, spec, enterprise_spec):
        Root.__rest_name__ = spec['model']['rest_name']
        Root.__resource_name__ = spec['model']['resource_name']
        self.__rest_name__ = spec['model']['rest_name']
        self.__resource_name__ = spec['model']['resource_name']

        super(Root, self).__init__()

    def get_name(self):
        return "Root"

    def get_resource_url_for_child_type(self, nurest_object_type):
        if self.current_child_name is None:
            raise SessionError("No child name set")
        return self.get_resource_url_for_child_name(self.current_child_name)

    def get_resource_url_for_child_name(self, child_name):
        return "%s/%s" % (self.rest_base_url(), child_name)

    def fetcher_for_rest_name(self, rest_name):
        return list()
