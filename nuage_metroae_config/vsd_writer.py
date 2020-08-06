import json
import os
import re
import requests

from bambou.exceptions import BambouHTTPError
from bambou_adapter import ConfigObject, Fetcher, Root, Session
from device_reader_base import DeviceReaderBase
from device_writer_base import DeviceWriterBase
from errors import (DeviceWriterError,
                    InvalidAttributeError,
                    InvalidObjectError,
                    InvalidValueError,
                    MissingSelectionError,
                    MultipleSelectionError,
                    SessionError,
                    SessionNotStartedError)

SPEC_EXTENSION = ".spec"
SOFTWARE_TYPE = "Nuage Networks VSD"
LEGACY_VERSION_ENDPOINT = "/Resources/app-version.js"
VERSION_ENDPOINT_6 = "/nuage"
VERSION_ENDPOINT_5 = "/architect" + LEGACY_VERSION_ENDPOINT
VERSION_TOKEN = "APP_BUILDVERSION"
ASSIGN_TOKEN = "assign("


class MissingSessionParamsError(DeviceWriterError):
    """
    Exception class when session is started without parameters specified
    """
    pass


class InvalidSpecification(DeviceWriterError):
    """
    Exception class when there is an error parsing a VSD API specification
    """
    pass


class VsdError(SessionError):
    """
    Exception class when there is an error from VSD
    """

    def __init__(self, bambou_error, location=None):
        response = bambou_error.connection.response
        message = "VSD returned error response: %s %s" % (response.status_code,
                                                          response.reason)

        super(VsdError, self).__init__(message)
        self.add_location(str(bambou_error))
        if location is not None:
            self.add_location(location)


class VsdWriter(DeviceWriterBase, DeviceReaderBase):
    """
    Writes configuration to a VSD.  This class is a derived class from
    the DeviceWriterBase Abstract Base Class.
    """

    def __init__(self):
        """
        Derived class from DeviceWriterBase.
        """
        super(VsdWriter, self).__init__()
        self.session_params = None
        self.session = None
        self.version = "6"
        self.api_prefix = "nuage/api"
        self.specs = dict()
        self.specs_by_restname = dict()
        self.root_spec_name = None
        self.spec_paths = list()
        self.read_spec_paths = list()
        self.query_cache = dict()

    def set_session_params(self, url, username="csproot",
                           password=None, enterprise="csp",
                           certificate=None):
        """
        Sets the parameters necessary to connect to the VSD.  This must
        be called before writing or an exception will be raised.
        """
        self.session_params = {
            'username': username,
            'password': password,
            'enterprise': enterprise,
            'api_url': url}

        if certificate is not None and certificate[0] is not None:
            self.session_params['certificate'] = certificate

    def set_software_version(self, software_version):
        major_version = int(software_version.split(".")[0])
        if (major_version < 6):
            self.version = "5.0"
        else:
            self.version = "6"

    def read_api_specifications(self, path_or_file_name):
        """
        Reads the VSD configuration API specifications from JSON files
        in the specified path or file name.  This must be called before
        writing or an exception will be raised.
        """
        if path_or_file_name in self.read_spec_paths:
            return

        if (os.path.isdir(path_or_file_name)):
            for file_name in os.listdir(path_or_file_name):
                if (file_name.endswith(SPEC_EXTENSION) and
                        not file_name.startswith('@')):
                    spec_json = self._read_specification(os.path.join(
                        path_or_file_name, file_name))
                    try:
                        self._register_specification(spec_json)
                    except InvalidSpecification as e:
                        self.log.error(
                            "Could not parse VSD API specification %s: %s" % (
                                file_name, str(e)))
        elif (os.path.isfile(path_or_file_name)):
            spec_json = self._read_specification(path_or_file_name)
            self._register_specification(spec_json)
        else:
            raise InvalidSpecification("File or path not found: " +
                                       path_or_file_name)

        self.read_spec_paths.append(path_or_file_name)

    def add_api_specification_path(self, path):
        self.spec_paths.append(path)

    #
    # Implement all required Abstract Base Class prototype functions.
    #
    def get_version(self):
        """
        Returns the version running on the device in format:
            {"software_version": "xxx",
             "software_type": "xxx"}
        """
        try:
            version_url = self.session_params['api_url'] + VERSION_ENDPOINT_6
            resp = requests.get(version_url, verify=False)

            version_dict = dict()
            if resp.status_code == 200:
                version_dict = resp.json()

            if "vsdVersion" in version_dict:
                version = version_dict["vsdVersion"]
            else:

                version_url = (self.session_params['api_url'] +
                               VERSION_ENDPOINT_5)
                resp = requests.get(version_url, verify=False)

                if resp.status_code == 404:
                    legacy_version_url = (
                        self.session_params['api_url'] +
                        LEGACY_VERSION_ENDPOINT)
                    legacy_resp = requests.get(legacy_version_url,
                                               verify=False)

                    if legacy_resp.status_code == 200:
                        resp = legacy_resp

                if resp.status_code != 200:
                    raise Exception("Status code %d from URL %s" % (
                        resp.status_code, version_url))

                version = self._parse_version_output(resp.text)

            self.log.output("Device: %s %s" % (SOFTWARE_TYPE, version))

            return {
                "software_version": version,
                "software_type": SOFTWARE_TYPE}

        except Exception as e:
            self.log.output("WARNING: Could not determine VSD version")
            self.log.error("Could not determine VSD version: %s" % str(e))
            return {
                "software_version": None,
                "software_type": None}

    def start_session(self):
        """
        Starts a session with the VSD
        """
        location = "Session start %s" % str(self.session_params)

        if self.session is None:
            if self.session_params is None:
                raise MissingSessionParamsError(
                    "Cannot start session without parameters")
            else:
                if (self.session_params['password'] is None and
                   ('certificate' not in self.session_params or
                       self.session_params['certificate'][0] is None or
                       self.session_params['certificate'][1] is None)):
                    raise MissingSessionParamsError(
                        """Cannot start session without password or certificate
                         parameter""")

            self.log.debug(location)

            if (self.root_spec_name is None or
                    self.root_spec_name not in self.specs):
                raise InvalidSpecification("No root specification loaded")

            if ("enterprise" not in self.specs):
                raise InvalidSpecification(
                    "No enterprise specification loaded")

            self.session = Session(spec=self.specs[self.root_spec_name],
                                   api_prefix=self.api_prefix,
                                   version=self.version,
                                   **self.session_params)
            self.session.set_enterprise_spec(self.specs['enterprise'])

        try:
            if self.validate_only is True:
                self.session._root_object = Root(
                    self.specs[self.root_spec_name],
                    self.specs["enterprise"])
            else:
                self.session.start()

            self.session.root_object.spec = self.specs[self.root_spec_name]
        except BambouHTTPError as e:
            self.session = None
            raise VsdError(e, location)
        except DeviceWriterBase as e:
            e.reraise_with_location(location)

        self.query_cache = dict()

    def stop_session(self):
        """
        Stops the session with the VSD
        """
        self.log.debug("Session stopping")

        if self.session is not None:
            if self.validate_only is False:
                self.session.reset()
            self.session = None

    def update_object(self, object_name, by_field, select_value, context=None):
        """
        Update an object in the current context, object is not saved to VSD
        """
        location = "Update object %s %s = %s [%s]" % (object_name,
                                                      by_field,
                                                      select_value,
                                                      context)
        self.log.debug(location)
        self._check_session()
        try:
            if select_value is not None:
                new_context = self.select_object(object_name,
                                                 by_field,
                                                 select_value,
                                                 context)
                selectedId = new_context.current_object.id

                new_context = self._get_new_child_context(context)

                new_context.current_object = self._get_new_config_object(
                    object_name)
                new_context.current_object.id = selectedId
                new_context.object_exists = True

                return new_context
            else:
                return self.create_object(object_name, context)
        except MissingSelectionError:
            return self.create_object(object_name, context)

    def create_object(self, object_name, context=None):
        """
        Creates an object in the current context, object is not saved to VSD
        """
        location = "Create object %s [%s]" % (object_name, context)
        self.log.debug(location)
        self._check_session()

        try:
            new_context = self._get_new_child_context(context)

            new_context.current_object = self._get_new_config_object(
                object_name)
            new_context.object_exists = False
        except DeviceWriterError as e:
            e.reraise_with_location(location)

        return new_context

    def select_object(self, object_name, by_field, value, context=None):
        """
        Selects an object in the current context
        """
        location = "Select object %s %s = %s [%s]" % (object_name,
                                                      by_field,
                                                      value,
                                                      context)
        self.log.debug(location)
        self._check_session()

        try:
            new_context = self._get_new_child_context(context)

            new_context.current_object = self._get_new_config_object(
                object_name)

            new_context.current_object = self._select_object(
                object_name, by_field, value, new_context.parent_object)
        except BambouHTTPError as e:
            raise VsdError(e, location)
        except DeviceWriterError as e:
            e.reraise_with_location(location)

        new_context.object_exists = True

        return new_context

    def get_object_list(self, object_name, context=None):
        """
        Gets a list of objects of specified type in the current context
        """
        location = "Get object list %s [%s]" % (object_name, context)
        self.log.debug(location)
        self._check_session()

        contexts = list()

        try:
            new_context = self._get_new_child_context(context)
            objects = self._get_object_list(object_name,
                                            new_context.parent_object)
            for current_object in objects:
                new_context = self._get_new_child_context(context)

                new_context.current_object = current_object

                new_context.object_exists = True

                contexts.append(new_context)

        except BambouHTTPError as e:
            raise VsdError(e, location)
        except DeviceWriterError as e:
            e.reraise_with_location(location)

        return contexts

    def delete_object(self, context):
        """
        Deletes the object selected in the current context
        """
        location = "Delete object [%s]" % context
        self.log.debug(location)
        self._check_session()

        if (context is None or context.current_object is None or
                not context.object_exists):
            raise SessionError("No object for deletion", location)

        if self.validate_only is False:
            try:
                context.current_object.delete()
            except BambouHTTPError as e:
                raise VsdError(e, location)

        context.current_object = None
        context.object_exists = False

        return context

    def set_values(self, context, **kwargs):
        """
        Sets values in the object selected in the current context and saves it
        """
        location = "Set value [%s] = %s" % (context, kwargs)
        self.log.debug(location)
        self._check_session()

        if context is None or context.current_object is None:
            raise SessionError("No object for setting values", location)

        try:
            self._set_attributes(context.current_object, **kwargs)
            self._validate_values(context.current_object,
                                  skip_required_check=context.object_exists)
        except DeviceWriterError as e:
            e.reraise_with_location(location)

        if context.object_exists:
            location = "Saving [%s]" % context
            self.log.debug(location)
            if self.validate_only is False:
                try:
                    context.current_object.save()
                except BambouHTTPError as e:
                    raise VsdError(e, location)
        else:
            location = "Creating child [%s]" % context
            self.log.debug(location)
            try:
                self._add_object(context.current_object, context.parent_object)
            except BambouHTTPError as e:
                raise VsdError(e, location)
            except DeviceWriterError as e:
                e.reraise_with_location(location)

            context.object_exists = True

        self.log.debug("Saved [%s]" % context)

        try:
            self._assign_attributes(context.current_object, **kwargs)
        except BambouHTTPError as e:
            raise VsdError(e, location)
        except DeviceWriterError as e:
            e.reraise_with_location(location)

        return context

    def unset_values(self, context, **kwargs):
        """
        Unsets values of a selected object when being reverted
        """
        location = "Unset value [%s] = %s" % (context, kwargs)
        self.log.debug(location)
        self._check_session()

        try:
            self._unassign_attributes(context.current_object, **kwargs)
        except BambouHTTPError as e:
            raise VsdError(e, location)
        except DeviceWriterError as e:
            e.reraise_with_location(location)

        return context

    def get_value(self, field, context):
        """
        Gets a value from the object selected in the current context
        """
        location = "Get value %s [%s]" % (field, context)
        self.log.debug(location)
        self._check_session()

        if (context is None or context.current_object is None or
                not context.object_exists):
            raise SessionError("No object for getting values", location)

        try:
            value = self._get_attribute(context.current_object, field)
        except BambouHTTPError as e:
            raise VsdError(e, location)
        except DeviceWriterError as e:
            e.reraise_with_location(location)

        self.log.debug("Value %s = %s" % (field, str(value)))

        return value

    def does_object_exist(self, context=None):
        return context is not None and context.object_exists

    def connect(self, *args):
        """
        Creates a new connection with another device
        """
        for path in self.spec_paths:
            self.read_api_specifications(path)

        if len(args) < 1:
            raise SessionError("url parameter is required for connect")
        url = args[0]

        if len(args) < 2:
            username = "csproot"
        else:
            username = args[1]

        if len(args) < 3:
            password = "csproot"
        else:
            password = args[2]

        if len(args) < 4:
            enterprise = "csp"
        else:
            enterprise = args[3]

        certificate = None
        if len(args) == 6:
            certificate = (args[4], args[5])
        elif len(args) == 5:
            raise SessionError("certificate key parameter is required when"
                               " using certificate for connect")
        elif len(args) > 6:
            raise SessionError("Too many arguments to connect")

        if self.session is not None:
            self.stop_session()

        self.set_session_params(url, username, password, enterprise,
                                certificate)

        self.start_session()

    def query(self, objects, attributes):
        """
        Reads attributes from device
        """
        location = "Query %s : %s" % (objects, attributes)
        self.log.debug(location)
        self._check_session()

        try:
            return self._query(objects, attributes)
        except BambouHTTPError as e:
            raise VsdError(e, location)
        except DeviceWriterError as e:
            e.reraise_with_location(location)

    def query_attribute(self, obj, attribute):
        """
        Reads an attribute from an object
        """
        local_name = attribute.lower()

        value = None
        if hasattr(obj, local_name):
            value = getattr(obj, local_name)

        return value

    #
    # Private functions to do the work
    #

    def _parse_version_output(self, version_text):
        match = re.search(VERSION_TOKEN + "=.([0-9.]+)", version_text)
        if match is None:
            raise Exception("Could not find version from endpoint text: %s" %
                            version_text)

        return match.group(1)

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
        if "rest_name" in spec['model']:
            rest_name_key = spec['model']['rest_name'].lower()
            self.specs_by_restname[rest_name_key] = spec

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
            raise InvalidSpecification("'%s' missing in specification %s " % (
                                       field, section))

    def _get_specification(self, object_name):
        name_key = object_name.lower()
        if name_key not in self.specs:
            raise InvalidObjectError("No specification for " + object_name)

        return self.specs[name_key]

    def _get_specification_by_rest_name(self, rest_name):
        name_key = rest_name.lower()
        if name_key not in self.specs_by_restname:
            raise InvalidObjectError("No specification for " + rest_name)

        return self.specs_by_restname[name_key]

    def _get_attribute_name(self, spec, local_name):
        if local_name.lower() == "id":
            return "ID"

        spec = self._get_attribute_spec(spec, local_name)
        return spec['name']

    def _get_attribute_type(self, spec, local_name):
        if local_name.lower() == "id":
            return "string"

        spec = self._get_attribute_spec(spec, local_name)
        return spec['type']

    def _get_attribute_spec(self, spec, local_name):
        for attribute in spec['attributes']:
            remote_name = attribute['name']
            if remote_name.lower() == local_name.lower():
                return attribute

        raise InvalidAttributeError("%s spec does not define an attribute %s" %
                                    (spec['model']['entity_name'], local_name))

    def _check_session(self):
        if self.session is None:
            raise SessionNotStartedError("Session is not started")

        if self.session.root_object is None:
            raise SessionNotStartedError("Session is invalid")

    def _check_child_object(self, parent_spec, child_spec):
        child_rest_name = child_spec['model']['rest_name']
        for child_section in parent_spec['children']:
            if child_section['rest_name'] == child_rest_name:
                return

        raise InvalidObjectError("Parent object %s has no child object %s" %
                                 (parent_spec['model']['entity_name'],
                                  child_spec['model']['entity_name']))

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

        self._check_child_object(parent_object.spec, spec)

        return Fetcher(parent_object, spec)

    def _add_object(self, obj, parent_object=None):
        if parent_object is None:
            parent_object = self.session.root_object

        self._check_child_object(parent_object.spec, obj.spec)

        if self.validate_only is False:
            parent_object.current_child_name = obj.__resource_name__
            parent_object.create_child(obj)

    def _select_object(self, object_name, by_field, field_value,
                       parent_object=None):

        spec = self._get_specification(object_name)
        fetcher = self._get_fetcher(object_name, parent_object)
        remote_name = self._get_attribute_name(spec, by_field)

        if self.validate_only is True:
            return self._get_new_config_object(object_name)

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

    def _get_object_list(self, object_name, parent_object=None):

        self._get_specification(object_name)
        fetcher = self._get_fetcher(object_name, parent_object)

        if self.validate_only is True:
            return [self._get_new_config_object(object_name)]

        objects = fetcher.get()

        return objects

    def _set_attributes(self, obj, **kwargs):
        for field, value in kwargs.iteritems():
            local_name = field.lower()
            if not self._is_assign_attribute(local_name):
                self._get_attribute_name(obj.spec, field)
                setattr(obj, local_name, value)

    def _get_attribute(self, obj, field):
        self._get_attribute_name(obj.spec, field)
        local_name = field.lower()

        value = None
        if hasattr(obj, local_name):
            value = getattr(obj, local_name)

        if value is not None:
            return value

        if self.validate_only is True:
            attr_type = self._get_attribute_type(obj.spec, field)
            return self._get_placeholder_validation_value(attr_type)
        else:
            raise SessionError("Missing field %s in %s object" %
                               (field, obj.get_name()))

    def _assign_attributes(self, obj, **kwargs):
        for field, value in kwargs.iteritems():
            local_name = field.lower()
            if self._is_assign_attribute(local_name):
                self._assign_attribute(obj, local_name, value)

    def _is_assign_attribute(self, field):
        return field.startswith(ASSIGN_TOKEN)

    def _assign_attribute(self, parent_object, local_name, new_ids):
        rest_name = local_name[len(ASSIGN_TOKEN):-1]
        child_spec = self._find_child_assign_spec(parent_object.spec,
                                                  rest_name)
        child_name = child_spec['model']['entity_name']
        existing_objects = self._get_object_list(child_name, parent_object)

        new_objects = self._create_assign_objects(existing_objects, new_ids,
                                                  child_name)

        if (self.validate_only is not True and
                len(new_objects) > len(existing_objects)):
            parent_object.current_child_name = (
                child_spec['model']['resource_name'])
            parent_object.assign(new_objects, nurest_object_type=None)

    def _create_assign_objects(self, existing_objects, new_ids, child_name):
        if type(new_ids) != list:
            new_ids = [new_ids]

        new_objects = list(existing_objects)
        for new_id in new_ids:
            if not self._is_object_in_list(existing_objects, new_id):
                self.log.debug("Assigning %s ID = %s" % (child_name, new_id))
                child_object = self._get_new_config_object(child_name)
                child_object.id = new_id
                new_objects.append(child_object)

        return new_objects

    def _is_object_in_list(self, object_list, object_id):
        for obj in object_list:
            if obj.id == object_id:
                return True

        return False

    def _unassign_attributes(self, obj, **kwargs):
        for field, value in kwargs.iteritems():
            local_name = field.lower()
            if self._is_assign_attribute(local_name):
                self._unassign_attribute(obj, local_name, value)

    def _unassign_attribute(self, parent_object, local_name, new_ids):
        rest_name = local_name[len(ASSIGN_TOKEN):-1]
        child_spec = self._find_child_assign_spec(parent_object.spec,
                                                  rest_name)
        child_name = child_spec['model']['entity_name']
        existing_objects = self._get_object_list(child_name, parent_object)

        new_objects = self._create_unassign_objects(existing_objects, new_ids,
                                                    child_name)

        if (self.validate_only is not True and
                len(new_objects) < len(existing_objects)):
            parent_object.current_child_name = (
                child_spec['model']['resource_name'])
            parent_object.assign(new_objects, nurest_object_type=None)

    def _create_unassign_objects(self, existing_objects, new_ids, child_name):
        if type(new_ids) != list:
            new_ids = [new_ids]

        new_objects = list()
        for existing_object in existing_objects:
            if existing_object.id not in new_ids:
                new_objects.append(existing_object)
            else:
                self.log.debug("Unassigning %s ID = %s" %
                               (child_name, existing_object.id))

        return new_objects

    def _find_child_assign_spec(self, parent_spec, child_rest_name):
        for child_section in parent_spec['children']:
            if child_section['rest_name'] == child_rest_name:
                return self._get_specification_by_rest_name(child_rest_name)

        raise InvalidObjectError(
            "Parent object %s has no member assignment child %s" %
            (parent_spec['model']['entity_name'], child_rest_name))

    def _get_placeholder_validation_value(self, attr_type):
        # For validation, we don't have a real object to work with, but we
        # are required to return a value for the "get_value" operations.
        # The value returned here may be used to set attributes in other
        # objects later, so we will need to return a placeholder value which
        # is compatible with the attribute type.
        if attr_type == "string":
            return "ValidatePlaceholder"
        elif attr_type == "boolean":
            return False
        elif attr_type == "integer":
            return 0
        elif attr_type == "float":
            return 0.0
        elif attr_type == "list":
            return []
        else:
            return None

    def _validate_values(self, obj, skip_required_check):
        if not obj.validate(skip_required_check):
            messages = []
            for attr_name, message in obj.errors.iteritems():
                messages.append("%s: %s" % (attr_name, message))
            raise InvalidValueError("Invalid values: " + ', '.join(messages))

    def _query(self, objects, attributes):
        if len(attributes) > 0:
            return self._query_objects(objects, attributes, 0, None, list())
        else:
            return list()

    def _query_objects(self, objects, attributes, level, parent_object,
                       groups):
        if parent_object is None:
            parent_object = self.session.root_object

        if level < len(objects):
            object_set = objects[level]
            object_name = object_set["name"]
            filter = object_set["filter"]
            spec = self._get_specification(object_name)
            self._check_child_object(parent_object.spec, spec)
            object_list = self._get_object_list_with_cache(object_name,
                                                           parent_object)

            filter_list = self.build_filter_list(filter, object_list)

            values = list()
            for cur_filter in filter_list:
                self.log.debug("Current filter: " + str(cur_filter))
                if type(filter) != dict or "%group" not in filter:
                    child_group = groups
                else:
                    child_group = list()
                values = list()
                for parent_object in self.filter_results(object_list,
                                                         cur_filter):
                    values.extend(self._query_objects(objects,
                                                      attributes,
                                                      level + 1,
                                                      parent_object,
                                                      child_group))
                if child_group != []:
                    self.group_results(groups, cur_filter, child_group)
                    values = child_group
                else:
                    self.group_results(groups, cur_filter, values)

            if groups != []:
                return groups
            return values
        else:
            return self._query_attributes(parent_object, attributes)

    def _query_attributes(self, parent_object, attributes):
        if type(attributes) == list:
            attribute_dict = dict()
            if attributes[0] == "*":
                for attr_name, attr in parent_object._attributes.items():
                    if hasattr(parent_object, attr_name):
                        attribute_dict[attr_name] = getattr(parent_object,
                                                            attr_name)
            else:
                for attribute in attributes:
                    value = self.query_attribute(parent_object, attribute)
                    if value is not None:
                        attribute_dict[attribute] = value
            return [attribute_dict]
        else:
            value = self.query_attribute(parent_object, attributes)
            if value is not None:
                return [value]
            else:
                return list()

    def _get_object_list_with_cache(self, object_name, parent_object):

        if parent_object is None:
            cache_key = "root:" + object_name.lower()
        else:
            cache_key = parent_object.id + ":" + object_name.lower()

        if cache_key in self.query_cache:
            return self.query_cache[cache_key]

        object_list = self._get_object_list(object_name,
                                            parent_object)

        self.query_cache[cache_key] = list(object_list)

        return object_list

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
