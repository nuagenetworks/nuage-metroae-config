import json
import os
import re
import requests

from bambou.exceptions import BambouHTTPError
from bambou_adapter import ConfigObject, Fetcher, Root, Session
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
VERSION_ENDPOINT = "/architect" + LEGACY_VERSION_ENDPOINT
VERSION_TOKEN = "APP_BUILDVERSION"


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


class VsdWriter(DeviceWriterBase):
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
        self.version = "5.0"
        self.api_prefix = "nuage/api"
        self.specs = dict()
        self.root_spec_name = None

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
            version_url = self.session_params['api_url'] + VERSION_ENDPOINT
            resp = requests.get(version_url, verify=False)

            if resp.status_code == 404:
                legacy_version_url = (
                    self.session_params['api_url'] + LEGACY_VERSION_ENDPOINT)
                legacy_resp = requests.get(legacy_version_url, verify=False)

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
            self._validate_values(context.current_object)
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
            raise InvalidSpecification("'%s' missing in specification %s " % (field, section))

    def _get_specification(self, object_name):
        name_key = object_name.lower()
        if name_key not in self.specs:
            raise InvalidObjectError("No specification for " + object_name)

        return self.specs[name_key]

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

    def _validate_values(self, obj):
        if not obj.validate():
            messages = []
            for attr_name, message in obj.errors.iteritems():
                messages.append("%s: %s" % (attr_name, message))
            raise InvalidValueError("Invalid values: " + ', '.join(messages))

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
