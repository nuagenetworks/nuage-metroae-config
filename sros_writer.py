import yaml
import netmiko
import os

from device_writer_base import DeviceWriterBase
from errors import (DeviceWriterError,
                    InvalidAttributeError,
                    InvalidObjectError,
                    InvalidValueError,
                    MissingSelectionError,
                    MultipleSelectionError,
                    SessionError,
                    SessionNotStartedError)

SOFTWARE_TYPE = "Nuage Networks WBX"
SPEC_EXTENSION = ".yml"


class MissingSessionParamsError(DeviceWriterError):
    """
    Exception class when session is started without parameters specified
    """
    pass


class InvalidSpecification(DeviceWriterError):
    """
    Exception class when there is an error parsing an SROS API specification
    """
    pass


class SrosError(SessionError):
    """
    Exception class when there is an error from SROS
    """

    def __init__(self, output, location=None):
        message = "SROS returned error:\n %s" % (output)

        super(SrosError, self).__init__(message)
        self.add_location(message)
        if location is not None:
            self.add_location(location)


class SrosWriter(DeviceWriterBase):
    """
    Writes configuration to a SROS device.  This class is a derived class from
    the DeviceWriterBase Abstract Base Class.
    """

    def __init__(self):
        """
        Derived class from DeviceWriterBase.
        """
        super(SrosWriter, self).__init__()
        self.session_params = None
        self.session = None
        self.specs = dict()

    def set_session_params(self, hostname, port=22, username="admin",
                           password=None):
        """
        Sets the parameters necessary to connect to the SROS device.  This must
        be called before writing or an exception will be raised.
        """
        self.session_params = {
            'device_type': 'alcatel_sros',
            'ssh_config_file': "/etc/ssh/ssh_config",
            'secret': '',
            'verbose': False,
            'username': username,
            'password': password,
            'port': port,
            'ip': hostname}

    def read_api_specifications(self, path_or_file_name):
        """
        Reads the SROS configuration API specifications from YAML files
        in the specified path or file name.  This must be called before
        writing or an exception will be raised.
        """
        if (os.path.isdir(path_or_file_name)):
            for file_name in os.listdir(path_or_file_name):
                if (file_name.endswith(SPEC_EXTENSION)):
                    spec_yaml = self._read_specification(os.path.join(
                        path_or_file_name, file_name))
                    try:
                        self._register_specification(spec_yaml)
                    except InvalidSpecification as e:
                        self.log.error(
                            "Could not parse SROS API specification %s: %s" % (
                                file_name, str(e)))
        elif (os.path.isfile(path_or_file_name)):
            spec_yaml = self._read_specification(path_or_file_name)
            self._register_specification(spec_yaml)
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

        return {
            "software_version": "9.9.9",
            "software_type": SOFTWARE_TYPE}

    def start_session(self):
        """
        Starts a session with the SROS device
        """
        location = "Session start %s" % str(self.session_params)

        if self.session is None or not self.session.is_alive():
            if self.session_params is None:
                raise MissingSessionParamsError(
                    "Cannot start session without parameters")
            else:
                try:
                    self.session = netmiko.ConnectHandler(
                        **self.session_params)
                except Exception as e:
                    raise SessionError("Could not establish session: " +
                                       str(e))

            self.log.debug(location)

    def stop_session(self):
        """
        Stops the session with the SROS device
        """
        self.log.debug("Session stopping")

        if self.session is not None and self.session.is_alive():
            if self.validate_only is False:
                self.session.disconnect()
            self.session = None

    def update_object(self, object_name, by_field, select_value, context=None):
        """
        Update an object in the current context, object is not saved to SROS
        """
        location = "Update object %s %s = %s [%s]" % (object_name,
                                                      by_field,
                                                      select_value,
                                                      context)
        self.log.debug(location)
        self._check_session()

        try:

            new_context = self._select_object(object_name, by_field,
                                              select_value, context)
            new_context.object_exists = True

        except DeviceWriterError as e:
            e.reraise_with_location(location)

        return new_context

    def create_object(self, object_name, context=None):
        """
        Creates an object in the current context, object is not saved to SROS
        """
        location = "Create object %s [%s]" % (object_name, context)
        self.log.debug(location)
        self._check_session()

        try:

            new_context = self._create_object(object_name, context)
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

            new_context = self._select_object(object_name, by_field, value,
                                              context)
            new_context.object_exists = True

        except DeviceWriterError as e:
            e.reraise_with_location(location)

        return new_context

    def get_object_list(self, object_name, context=None):
        """
        Gets a list of objects of specified type in the current context
        """
        location = "Get object list %s [%s]" % (object_name, context)
        self.log.debug(location)
        self._check_session()

        return list()

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

        self._set_values(context, kwargs)

        # commands = list()

        # if context.current_object["name"] == "Port":

        #     context.current_object["key"] = kwargs['identifier']

        #     commands.append("port %s" % kwargs['identifier'])
        #     commands.append('description "%s"' % kwargs['description'])
        #     if kwargs['shutdown']:
        #         commands.append("shutdown")
        #     else:
        #         commands.append("no shutdown")

        # elif context.current_object["name"] == "Ethernet":

        #     context.current_object["key"] = ""

        #     commands.append("port %s" % context.parent_object['key'])
        #     commands.append("ethernet")
        #     commands.append("mtu %d" % kwargs['mtu'])
        #     commands.append("speed %d" % kwargs['speed'])

        # elif context.current_object["name"] == "Lag":

        #     context.current_object["key"] = kwargs['identifier']

        #     commands.append("lag %d" % kwargs['identifier'])
        #     commands.append('description "%s"' % kwargs['description'])
        #     if kwargs['shutdown']:
        #         commands.append("shutdown")
        #     else:
        #         commands.append("no shutdown")

        #     commands.append("mode %s" % kwargs['mode'])
        #     commands.append("port %s" % kwargs['port'])

        # if self.validate_only is False:

        #     output = self.session.send_config_set(commands)

        #     print(output)
        #     print("lines: " + str(len(output.split("\n"))))

        # try:
        #     self._set_attributes(context.current_object, **kwargs)
        #     self._validate_values(context.current_object)
        # except DeviceWriterError as e:
        #     e.reraise_with_location(location)

        # if context.object_exists:
        #     location = "Saving [%s]" % context
        #     self.log.debug(location)
        #     if self.validate_only is False:
        #         try:
        #             context.current_object.save()
        #         except BambouHTTPError as e:
        #             raise VsdError(e, location)
        # else:
        #     location = "Creating child [%s]" % context
        #     self.log.debug(location)
        #     try:
        #         self._add_object(context.current_object, context.parent_object)
        #     except BambouHTTPError as e:
        #         raise VsdError(e, location)
        #     except DeviceWriterError as e:
        #         e.reraise_with_location(location)

        #     context.object_exists = True

        self.log.debug("Saved [%s]" % context)

        return context

    def get_value(self, field, context):
        """
        Gets a value from the object selected in the current context
        """
        location = "Get value %s [%s]" % (field, context)
        self.log.debug(location)
        self._check_session()

        # if (context is None or context.current_object is None or
        #         not context.object_exists):
        #     raise SessionError("No object for getting values", location)

        # try:
        #     value = self._get_attribute(context.current_object, field)
        # except BambouHTTPError as e:
        #     raise VsdError(e, location)
        # except DeviceWriterError as e:
        #     e.reraise_with_location(location)

        # self.log.debug("Value %s = %s" % (field, str(value)))

        # return value

        return "< GET NOT SUPPORTED >"

    def does_object_exist(self, context=None):
        return context is not None and context.object_exists

    #
    # Private functions to do the work
    #
    def _read_specification(self, file_name):
        try:
            with open(file_name, 'r') as file:
                return file.read()
        except Exception as e:
            raise InvalidSpecification("Error reading spec: " + str(e))

    def _register_specification(self, yaml_str):
        try:
            spec = yaml.safe_load(yaml_str)
        except yaml.YAMLError as e:
            raise InvalidSpecification("Error parsing spec: " + str(e))

        self._validate_specification(spec)

        name_key = spec['name'].lower()
        self.specs[name_key] = spec

    def _validate_specification(self, spec):
        self._validate_specification_field('name', spec)
        self._validate_specification_field('attributes', spec)
        if 'parent' not in spec:
            self._validate_specification_field('parent', spec)
        self._validate_specification_field('software-type', spec)
        self._validate_specification_field('config', spec)

    def _validate_specification_field(self, field, section):
        if field not in section or section[field] is None:
            raise InvalidSpecification("'%s' missing in specification %s " % (
                field, section))

    def _get_specification(self, object_name):
        name_key = object_name.lower()
        if name_key not in self.specs:
            raise InvalidObjectError("No specification for " + object_name)

        return self.specs[name_key]

    def _get_attribute_spec(self, spec, local_name):
        for attribute in spec['attributes']:
            remote_name = attribute['name']
            if remote_name.lower() == local_name.lower():
                return attribute

        raise InvalidAttributeError("%s spec does not define an attribute %s" %
                                    (spec['name'], local_name))

    def _check_session(self):
        if self.session is None:
            raise SessionNotStartedError("Session is not started")

        if not self.session.is_alive():
            raise SessionNotStartedError("Session is not alive")

    def _check_child_object(self, object_name, context):
        parent_name = None
        if context is not None and context.current_object is not None:
            parent_name = context.current_object['name']

        spec = self._get_specification(object_name)

        if parent_name is None:
            if spec['parent'] is not None:
                raise InvalidObjectError(
                    "Object %s is not defined at root level" % object_name)
        else:
            if spec['parent'].lower() != parent_name.lower():
                raise InvalidObjectError(
                    "Object %s is not defined as a child of %s" % (
                        object_name, parent_name))

    def _get_new_child_context(self, old_context):
        new_context = Context()
        if old_context is not None:
            if old_context.current_object is not None:
                new_context.parent_object = old_context.current_object

        return new_context

    def _create_object(self, object_name, context):
        self._check_child_object(object_name, context)
        new_context = self._get_new_child_context(context)

        config_object = {
            "name": object_name,
            "config": None
        }

        new_context.current_object = config_object
        new_context.object_exists = True

        return new_context

    def _select_object(self, object_name, field, key, context):
        self._check_child_object(object_name, context)
        new_context = self._get_new_child_context(context)

        spec = self._get_specification(object_name)
        config = self._build_object_config(spec, {field: key})

        config_object = {
            "name": object_name,
            "config": config
        }

        new_context.current_object = config_object
        new_context.object_exists = True

        return new_context

    def _set_values(self, context, attribute_dict):
        object_name = context.current_object['name']
        spec = self._get_specification(object_name)
        config_list = self._build_config_list(spec, context, attribute_dict)
        if self.validate_only is False:
            self._apply_config_list(config_list)

    def _build_config_list(self, spec, context, attribute_dict):
        config_list = list()

        if (context.parent_object is not None and
                context.parent_object["config"] is not None):
            config_list.append(context.parent_object["config"])

        object_config = self._build_object_config(spec, attribute_dict)
        config_list.append(object_config)
        context.current_object['config'] = object_config

        for name in attribute_dict.keys():
            if name.lower() != "$dependency":
                config = self._build_attribute_config(spec, name,
                                                      attribute_dict)
                if config is not None:
                    config_list.append(config)

        return config_list

    def _build_object_config(self, spec, attribute_dict):
        attribute_dict_copy = dict(attribute_dict)
        attribute_dict_copy['no'] = ""
        return spec['config'].format(**attribute_dict_copy)

    def _build_attribute_config(self, spec, name, attribute_dict):
        attr_spec = self._get_attribute_spec(spec, name)
        name = name.lower()
        value = attribute_dict[name]
        attr_type = attr_spec['type'].lower()
        if "config" in attr_spec:
            if attr_spec["config"] is None:
                return None
            else:
                return attr_spec["config"].format(**attribute_dict)

        if attr_type == "string":
            return '%s "%s"' % (name, value)
        elif attr_type == "integer":
            return "%s %d" % (name, value)
        elif attr_type == "boolean":
            if value is True:
                return name
            elif value is False:
                return "no %s" % name
            else:
                InvalidValueError(
                    "Invalid value %s for boolean attribute %s" % (
                        value, name))
        else:
            InvalidSpecification("Invalid type %s for attribute %s" % (
                attr_type, name))

    def _apply_config_list(self, command_list):
        try:
            output = self.session.send_config_set(command_list)
        except Exception as e:
            raise SrosError(str(e))

        self.log.output(output)

        self._check_output_for_errors(command_list, output)

    def _check_output_for_errors(self, config_list, output):

        config_list_copy = list(config_list)
        config_list_copy.append("exit all")

        for cmd, out in zip(config_list_copy, output.split("\n")[1:]):
            if cmd not in out:
                raise SrosError(output)

#
# Private classes to do the work
#


class Context(object):
    """
    The current object context to track the state of the current and parent
    objects.  This class is intended to be private and should not be directly
    modified by external callers of the SROS Writer.
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
