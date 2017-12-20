import json
import os

from bambou import NURESTFetcher, NURESTSession, NURESTObject, NURESTRootObject
from bambou.exceptions import BambouHTTPError
# import vspk.v5_0 as vspk

SPEC_EXTENSION = ".spec"

# session = vspk.NUVSDSession(username='csproot',password='csproot',
# enterprise='csp', api_url='https://localhost:8080')
# session.start()


class MissingSessionParamsError(Exception):
    """
    Exception class when session is started without parameters specified
    """
    pass


class SessionNotStartedError(Exception):
    """
    Exception class when session is used when not started.
    """
    pass


class SessionError(Exception):
    """
    Exception class when there is an error in the session
    """
    pass


class InvalidSpecification(Exception):
    """
    Exception class when there is an error parsing a VSD API specification
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
            raise IOError("File or path not found: " + path_or_file_name)

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
        with open(file_name, 'r') as file:
            return file.read()

    def _register_specification(self, json_str):
        try:
            spec = json.loads(json_str)
        except Exception as e:
            raise InvalidSpecification("Error parsing spec: " + str(e))

        if 'model' not in spec:
            raise InvalidSpecification("'model' missing in spec")

        if ('entity_name' not in spec['model'] or
                spec['model']['entity_name'] is None):
            raise InvalidSpecification("'entity_name' missing in spec")

        name_key = spec['model']['entity_name'].lower()
        self.specs[name_key] = spec

        if 'root' in spec['model'] and spec['model']['root'] is True:
            self.root_spec_name = name_key

    def _get_new_config_object(self, name):
        name_key = name.lower()
        if name_key not in self.specs:
            raise InvalidSpecification("No specification for " + name)

        return ConfigObject(self.specs[name_key])


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

        if 'model' not in self.spec:
            raise InvalidSpecification("'model' missing in spec")

        if ('entity_name' not in self.spec['model'] or
                self.spec['model']['entity_name'] is None):
            raise InvalidSpecification("'entity_name' missing in spec")

        if ('rest_name' not in self.spec['model'] or
                self.spec['model']['rest_name'] is None):
            raise InvalidSpecification("'rest_name' missing in spec")

        self.__resource_name__ = self.spec['model']['resource_name']
        self.__rest_name__ = self.spec['model']['rest_name']

        self._build_attributes()

    def _build_attributes(self):
        if ('attributes' not in self.spec or
                self.spec['attributes'] is None):
            raise InvalidSpecification("'attributes' missing in spec")

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

    def get_resource_url_for_child_name(self, child_name):
        return "%s/%s" % (self.get_resource_url(), child_name)


class Fetcher(NURESTFetcher):

    @classmethod
    def managed_object_rest_name(cls):
        return "enterprise"

    @classmethod
    def managed_class(cls):

        return ConfigObject

    def new(self):

        # managed_class = self.managed_class(self.spec)
        return ConfigObject(self.spec)

    def _prepare_url(self):
        """ Prepare url for request """

        return self.parent_object.get_resource_url_for_child_name("enterprises")

    def set_spec(self, spec):
        self.spec = spec


class Root(NURESTRootObject):

    __rest_name__ = "me"
    __resource_name__ = "me"

    def __init__(self, spec, enterprise_spec):
        if 'model' not in spec:
            raise InvalidSpecification("'model' missing in spec")

        if ('rest_name' not in spec['model'] or
                spec['model']['rest_name'] is None):
            raise InvalidSpecification("'rest_name' missing in spec")

        if ('resource_name' not in spec['model'] or
                spec['model']['resource_name'] is None):
            raise InvalidSpecification("'resource_name' missing in spec")

        Root.__rest_name__ = spec['model']['rest_name']
        Root.__resource_name__ = spec['model']['resource_name']

        super(Root, self).__init__()

        self.enterprises = Fetcher.fetcher_with_object(parent_object=self,
                                                       relationship="root")
        self.enterprises.set_spec(enterprise_spec)

    def get_resource_url_for_child_name(self, child_name):
        return "%s/%s" % (self.rest_base_url(), child_name)
