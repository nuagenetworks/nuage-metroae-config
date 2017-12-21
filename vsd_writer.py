import json
import os

from bambou import NURESTFetcher, NURESTSession, NURESTObject, NURESTRootObject
from bambou.exceptions import BambouHTTPError
# import vspk.v5_0 as vspk

SPEC_EXTENSION = ".spec"

# session = vspk.NUVSDSession(username='csproot',password='csproot',
# enterprise='csp', api_url='https://localhost:8080')
# session.start()


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


class SelectionError(TemplateWriterError):
    """
    Exception class when there is an error selecting an object
    """
    pass


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

    def set_session_params(self, url, user="csproot",
                           password="csproot", org="csp"):
        """
        Sets the parameters necessary to connect to the VSD.  This must
        be called before writing or an exception will be raised.
        """
        self.session_params = {
            'username': user,
            'password': password,
            'enterprise': org,
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

    # TBD - Implement all required Abstract Base Class prototype functions.

    def start_session(self):
        if self.session is None:
            if self.session_params is None:
                raise MissingSessionParamsError(
                    "Cannot start session without parameters")

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
        if self.session is not None:
            self.session.reset()
            self.session = None

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

    def _get_new_config_object(self, object_name):
        spec = self._get_specification(object_name)
        self._check_session()

        return ConfigObject(spec)

    def _get_fetcher(self, object_name, parent_object=None):
        spec = self._get_specification(object_name)
        self._check_session()

        if parent_object is None:
            parent_object = self.session.root_object

        return Fetcher(parent_object, spec)

    def _add_object(self, obj, parent_object=None):
        self._check_session()

        if parent_object is None:
            parent_object = self.session.root_object

        parent_object.current_child_name = obj.__resource_name__
        parent_object.create_child(obj)

    def _select_object(self, object_name, by_field, field_value,
                       parent_object=None):
        self._check_session()

        fetcher = self._get_fetcher(object_name, parent_object)
        spec = self._get_specification(object_name)
        remote_name = self._get_attribute_name(spec, by_field)

        selector = '%s is "%s"' % (remote_name, field_value)
        objects = fetcher.get(filter=selector)
        if len(objects) == 0:
            raise SelectionError("No %s object exists with %s = %s" %
                                 (object_name, by_field, field_value))
        if len(objects) > 1:
            raise SelectionError("Multiple %s objects exist with %s = %s" %
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
                                    obj.spec['model']['entity_name']))

class Session(NURESTSession):

    def __init__(self, spec, username, password, enterprise, api_url,
                 api_prefix, version):
        self.spec = spec
        super(Session, self).__init__(username, password, enterprise,
                                      api_url, api_prefix, version)

    def create_root_object(self):
        """ Returns a new instance
        """
        return Root(self.spec, self.enterprise_spec)

    def get_root_object(self):
        root_object = ConfigObject(self.spec)
        # root_object.id = self.root_object.id
        # root_object.id = ""
        print str(self.root_object.get_resource_url())
        print str(root_object.get_resource_url())
        root_object.fetch()
        return root_object

    def set_enterprise_spec(self, enterprise_spec):
        self.enterprise_spec = enterprise_spec


class ConfigObject(NURESTObject):

    def __init__(self, spec):
        super(ConfigObject, self).__init__()

        # self.obj = NURESTObject()
        self.spec = spec
        self.current_child_name = None

        self.__resource_name__ = self.spec['model']['resource_name']
        self.__rest_name__ = self.spec['model']['rest_name']

        self._build_attributes()

    def __str__(self):
        """ Prints a ConfigObject """

        return "%s (ID=%s)" % (self.spec['model']['entity_name'], str(self.id))

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
        """ Get resource complete url """

        name = self.__resource_name__
        url = self.__class__.rest_base_url()

        if self.id is not None:
            return "%s/%s/%s" % (url, name, self.id)

        return "%s/%s" % (url, name)

    def get_resource_url_for_child_type(self, nurest_object_type):

        # return "%s/%s" % (self.get_resource_url(),
        #                   nurest_object_type.resource_name)
        if self.current_child_name is None:
            raise SessionError("No child name set")
        return self.get_resource_url_for_child_name(self.current_child_name)

    def get_resource_url_for_child_name(self, child_name):
        return "%s/%s" % (self.get_resource_url(), child_name)

    def fetcher_for_rest_name(self, rest_name):
        return list()


class Fetcher(NURESTFetcher):

    def __init__(self, parent_object, spec):
        super(Fetcher, self).__init__()

        self.spec = spec
        self.resource_name = spec['model']['resource_name']
        self.parent_object = parent_object


    # @classmethod
    # def managed_object_rest_name(cls):
    #     return "enterprise"

    # @classmethod
    # def managed_class(cls):

    #     return ConfigObject

    def new(self):

        # managed_class = self.managed_class(self.spec)
        return ConfigObject(self.spec)

    def _prepare_url(self):
        """ Prepare url for request """
        return self.parent_object.get_resource_url_for_child_name(
            self.resource_name)

    # def set_spec(self, spec):
    #     self.spec = spec


class Root(NURESTRootObject):

    __rest_name__ = "me"
    __resource_name__ = "me"

    def __init__(self, spec, enterprise_spec):
        Root.__rest_name__ = spec['model']['rest_name']
        Root.__resource_name__ = spec['model']['resource_name']
        self.__rest_name__ = spec['model']['rest_name']
        self.__resource_name__ = spec['model']['resource_name']

        super(Root, self).__init__()

        # self.enterprises = Fetcher.fetcher_with_object(parent_object=self,
        #                                                relationship="root")
        # self.enterprises.set_spec(enterprise_spec)

    def get_resource_url_for_child_type(self, nurest_object_type):

        # return "%s/%s" % (self.get_resource_url(),
        #                   nurest_object_type.resource_name)
        if self.current_child_name is None:
            raise SessionError("No child name set")
        return self.get_resource_url_for_child_name(self.current_child_name)

    def get_resource_url_for_child_name(self, child_name):
        return "%s/%s" % (self.rest_base_url(), child_name)

    def fetcher_for_rest_name(self, rest_name):
        return list()
