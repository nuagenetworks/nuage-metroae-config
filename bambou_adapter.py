import sys

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
                                  self._get_attribute_type(attribute['type']),
                                  remote_name=attribute['name'],
                                  is_required=attribute['required'],
                                  is_readonly=attribute['read_only'],
                                  max_length=attribute['max_length'],
                                  min_length=attribute['min_length'],
                                  choices=attribute['allowed_choices'],
                                  is_unique=attribute['unique'],
                                  can_order=attribute['orderable'],
                                  can_search=attribute['filterable'])

            self._attributes[local_name].max_value = (
                attribute['max_value'] if 'max_value' in attribute else None)
            self._attributes[local_name].min_value = (
                attribute['min_value'] if 'min_value' in attribute else None)

            if not hasattr(self, local_name):
                setattr(self, local_name, None)

    def _get_attribute_type(self, label):
        if label == "string":
            return str
        elif label == "enum":
            return str
        elif label == "boolean":
            return bool
        elif label == "integer":
            return int
        elif label == "long":
            return int
        elif label == "float":
            return float
        elif label == "list":
            return list
        elif label == "object":
            return dict
        elif label == "time":
            return float
        else:
            raise InternalConsitencyError("Unknown attribute type " +
                                          str(label))

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

    def validate(self):
        # Unfortunately, the Bambou validation function is not working
        # properly. It has the following problems and thus it is being
        # overridden here in the adapter:
        #   1) Handling list values as lists
        #   2) Checking min and max values

        self._attribute_errors = dict()  # Reset validation errors

        for local_name, attribute in self._attributes.items():

            value = getattr(self, local_name, None)

            if attribute.is_required and (value is None or value == ""):
                self._attribute_errors[local_name] = {
                    'title': 'Invalid input',
                    'description': 'This value is mandatory.',
                    'remote_name': attribute.remote_name}
                continue

            if value is None:
                continue  # without error

            if type(value) != attribute.attribute_type:
                # On python 2, we accept unicode input when attribute_type
                # is set to str
                if not (sys.version_info < (3,) and
                        attribute.attribute_type == str and
                        type(value) == unicode) and not (
                        attribute.attribute_type == float and
                        type(value) == int):
                    self._attribute_errors[local_name] = {
                        'title': 'Wrong type',
                        'description':
                            'Attribute %s type should be %s but is %s' %
                            (attribute.remote_name, attribute.attribute_type,
                             type(value)),
                        'remote_name': attribute.remote_name}
                    continue

            if (attribute.min_length is not None and
                    len(value) < attribute.min_length):
                self._attribute_errors[local_name] = {
                    'title': 'Invalid length',
                    'description':
                        'Attribute %s minimum length should be %s but is %s' %
                        (attribute.remote_name, attribute.min_length,
                         len(value)),
                    'remote_name': attribute.remote_name}
                continue

            if (attribute.max_length is not None and
                    len(value) > attribute.max_length):
                self._attribute_errors[local_name] = {
                    'title': 'Invalid length',
                    'description':
                        'Attribute %s maximum length should be %s but is %s' %
                        (attribute.remote_name, attribute.max_length,
                         len(value)),
                    'remote_name': attribute.remote_name}
                continue

            if attribute.attribute_type == list:
                valid = True
                for item in value:
                    if valid is True:
                        valid = self._validate_value(local_name, attribute,
                                                     item)
            else:
                self._validate_value(local_name, attribute, value)

        return self.is_valid()

    def _validate_value(self, local_name, attribute, value):

        if attribute.min_value is not None and value < attribute.min_value:
            self._attribute_errors[local_name] = {
                'title': 'Invalid value',
                'description':
                    'Attribute %s minimum value should be %s but is %s' %
                    (attribute.remote_name, attribute.min_value, value),
                'remote_name': attribute.remote_name}
            return False

        if attribute.max_value is not None and value > attribute.max_value:
            self._attribute_errors[local_name] = {
                'title': 'Invalid value',
                'description':
                    'Attribute %s maximum value should be %s but is %s' %
                    (attribute.remote_name, attribute.max_value, value),
                'remote_name': attribute.remote_name}
            return False

        if attribute.choices and value not in attribute.choices:
            self._attribute_errors[local_name] = {
                'title': 'Invalid input',
                'description': 'Value %s not a valid choice' % value,
                'remote_name': attribute.remote_name}
            return False

        return True


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
