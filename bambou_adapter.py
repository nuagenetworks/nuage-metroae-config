from bambou import NURESTFetcher, NURESTSession, NURESTObject, NURESTRootObject
from bambou.exceptions import InternalConsitencyError


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
            raise InternalConsitencyError("No child name set for object")
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
            raise InternalConsitencyError("No child name set")
        return self.get_resource_url_for_child_name(self.current_child_name)

    def get_resource_url_for_child_name(self, child_name):
        return "%s/%s" % (self.rest_base_url(), child_name)

    def fetcher_for_rest_name(self, rest_name):
        return list()
