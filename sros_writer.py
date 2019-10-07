import netmiko
import os
import re
import yaml

from device_writer_base import DeviceWriterBase
from errors import (DeviceWriterError,
                    InvalidAttributeError,
                    InvalidObjectError,
                    InvalidValueError,
                    SessionError,
                    SessionNotStartedError)
from util import get_dict_field_no_case

WBX_DEVICE_TYPE_STR = "NUAGE 210"
DEVICE_VERSION_PATTERN = r'-([0-9]+\.[0-9]+\.[0-9]+)-'
SOFTWARE_TYPE = "Nuage Networks WBX"
SPEC_EXTENSION = ".yml"
SROS_PROMPT = r'[#$]'


class MissingSessionParamsError(DeviceWriterError):
    """
    Exception claSROS_PROMPT session is started without parameters specified
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
            # 'blocking_timeout': 60,
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

        try:
            session = netmiko.ConnectHandler(**self.session_params)

            output = session.send_command("show version")

            session.disconnect()

            if WBX_DEVICE_TYPE_STR in output:
                software_type = SOFTWARE_TYPE
            else:
                raise Exception("No device string found")

            match = re.search(DEVICE_VERSION_PATTERN, output)

            if match is not None:
                version = match.group(1)
            else:
                raise Exception("No version string found")

            self.log.output("Device: %s %s" % (software_type, version))

            return {
                "software_version": version,
                "software_type": software_type}

        except Exception as e:
            self.log.output("WARNING: Could not determine SROS version")
            self.log.error("Could not determine SROS version: %s" % str(e))
            return {
                "software_version": None,
                "software_type": None}

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
                if self.validate_only is not True:
                    try:
                        self.session = netmiko.ConnectHandler(
                            **self.session_params)
                    except Exception as e:
                        raise SrosError("Could not establish session: " +
                                        str(e))
                else:
                    self.session = None

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

    def delete_object(self, context, attribute_dict):
        """
        Deletes the object selected in the current context
        """
        location = "Delete object [%s]" % context
        self.log.debug(location)
        self._check_session()

        if context is None or not context.has_current_object():
            raise SessionError("No object for deletion", location)

        self._delete_object(context, attribute_dict)

        return context

    def set_values(self, context, **kwargs):
        """
        Sets values in the object selected in the current context and saves it
        """
        location = "Set value [%s] = %s" % (context, kwargs)
        self.log.debug(location)
        self._check_session()

        if context is None or not context.has_current_object():
            raise SessionError("No object for setting values", location)

        self._set_values(context, kwargs)

        self.log.debug("Saved [%s]" % context)

        return context

    def get_value(self, field, context):
        """
        Gets a value from the object selected in the current context
        """
        location = "Get value %s [%s]" % (field, context)
        self.log.debug(location)
        self._check_session()

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
        if self.validate_only is True:
            return

        if self.session is None or not self.session.is_alive():
            raise SessionNotStartedError("Session is not started")

    def _check_child_object(self, object_name, context):
        parent_name = None
        if context is not None:
            parent_name = context.get_obj_name()

        spec = self._get_specification(object_name)

        if parent_name is None:
            if spec['parent'] is not None:
                raise InvalidObjectError(
                    "Object %s is not defined at root level" % object_name)
        else:
            if (spec['parent'] is None or
                    spec['parent'].lower() != parent_name.lower()):
                raise InvalidObjectError(
                    "Object %s is not defined as a child of %s" % (
                        object_name, parent_name))

    def _get_new_child_context(self, old_context):
        new_context = Context()
        new_context.set_child_context(old_context)

        return new_context

    def _create_object(self, object_name, context):
        self._check_child_object(object_name, context)
        new_context = self._get_new_child_context(context)

        new_context.set_current_obj(object_name, None, object_exists=False)

        return new_context

    def _select_object(self, object_name, field, key, context):
        self._check_child_object(object_name, context)
        new_context = self._get_new_child_context(context)

        spec = self._get_specification(object_name)
        config = self._build_object_config(spec, {field: key})

        new_context.set_current_obj(object_name, config, object_exists=True)

        return new_context

    def _delete_object(self, context, attribute_dict):
        object_name = context.get_obj_name()
        spec = self._get_specification(object_name)

        if 'pre-delete-configs' in spec:
            self._apply_pre_delete_configs(context, spec,
                                           attribute_dict)

        config_list = list()

        attribute_dict['no'] = "no"
        object_config = self._build_object_config(spec, attribute_dict)
        context.set_current_config(object_config)
        config_list.append(context.get_path_config())

        if self.validate_only is False:
            self._apply_config_list(config_list)
        else:
            for config in config_list:
                self.log.debug(config)

        context.clear_current_object()

    def _apply_pre_delete_configs(self, context, spec, attribute_dict):
        config_list = list()
        object_config = self._build_object_config(spec, attribute_dict)
        context.set_current_config(object_config)
        config_list.append(context.get_path_config())

        attribute_dict['no'] = "no"
        for config_format in spec['pre-delete-configs']:
            config = config_format.format(**attribute_dict).strip()
            config_list.append(config)

        if self.validate_only is False:
            self._apply_config_list(config_list)
        else:
            for config in config_list:
                self.log.debug(config)

    def _set_values(self, context, attribute_dict):
        object_name = context.get_obj_name()
        spec = self._get_specification(object_name)
        self._validate_attributes(spec, attribute_dict)
        config_list = self._build_config_list(spec, context, attribute_dict)
        if self.validate_only is False:
            self._apply_config_list(config_list)
        else:
            for config in config_list:
                self.log.debug(config)
        context.object_exists = True

    def _validate_attributes(self, spec, attribute_dict):
        for name in attribute_dict.keys():
            if name[0] != "$":
                attr_spec = self._get_attribute_spec(spec, name)
                attr_type = attr_spec['type'].lower()
                value = attribute_dict[name]

                if attr_type == "choice":
                    choices = get_dict_field_no_case(attr_spec, "choices")
                    if value not in choices:
                        raise InvalidValueError(
                            "Value %s not a valid choice for attribute %s" % (
                                value, name))
                elif attr_type == "integer":
                    try:
                        int(value)
                    except ValueError:
                        raise InvalidValueError(
                            "Value %s is not an integer for attribute %s" % (
                                value, name))
                elif attr_type == "boolean":
                    if value is not True and value is not False:
                        raise InvalidValueError(
                            "Value %s is not a boolean for attribute %s" % (
                                value, name))
                else:
                    InvalidSpecification("Invalid type %s for attribute %s" % (
                        attr_type, name))

    def _build_config_list(self, spec, context, attribute_dict):
        config_list = list()

        self.log.debug(str(attribute_dict))

        object_config = self._build_object_config(spec, attribute_dict)
        context.set_current_config(object_config)

        parent_config = context.get_path_config()
        if parent_config is not None:
            config_list.append(parent_config)

        for name in attribute_dict.keys():
            if name[0] != "$":
                config = self._build_attribute_config(spec, name,
                                                      attribute_dict)
                if config is not None:
                    config_list.append(config)

        return config_list

    def _build_object_config(self, spec, attribute_dict):
        attribute_dict_copy = dict(attribute_dict)
        if 'no' not in attribute_dict_copy:
            attribute_dict_copy['no'] = ""
        return spec['config'].format(**attribute_dict_copy).strip()

    def _build_attribute_config(self, spec, name, attribute_dict):
        attribute_dict_copy = dict(attribute_dict)
        if 'no' not in attribute_dict_copy:
            attribute_dict_copy['no'] = ""
        attr_spec = self._get_attribute_spec(spec, name)
        name = name.lower()
        value = get_dict_field_no_case(attribute_dict, name)
        if value is None:
            raise InvalidValueError("Value not set for %s" % name)
        attr_type = attr_spec['type'].lower()
        if "config" in attr_spec:
            if attr_spec["config"] is None:
                return None
            else:
                return attr_spec["config"].format(
                    **attribute_dict_copy).strip()

        if attr_type == "string":
            return '%s "%s"' % (name, value)
        elif attr_type == "choice":
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
        output = ""
        try:
            # output = self.session.send_config_set(command_list)
            output += self.session.send_command("configure",
                                                strip_prompt=False,
                                                strip_command=False,
                                                expect_string=SROS_PROMPT)
            for command in command_list:
                output += self.session.send_command(command,
                                                    strip_prompt=False,
                                                    strip_command=False,
                                                    expect_string=SROS_PROMPT)
            output += self.session.send_command("exit all",
                                                strip_prompt=False,
                                                strip_command=False,
                                                expect_string=SROS_PROMPT)

        except Exception as e:
            raise SrosError(str(e))

        self.log.debug(output)

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
        self.parent_configs = list()
        self.parent_object = None
        self.current_object = None
        self.object_exists = False

    def __str__(self):
        current = self._get_object_string(self.current_object)

        if self.object_exists:
            marker = ''
        else:
            marker = ' **'
        if self.parent_configs == list():
            parent = "Root"
        else:
            parent = self.get_path_config()

        return "%s / %s%s" % (parent, current, marker)

    def get_obj_config(self, obj):
        if obj is not None:
            if obj['config'] is not None:
                return obj['config']

        return None

    def has_current_object(self):
        return self.current_object is not None

    def clear_current_object(self):
        self.current_object = None
        self.object_exists = False

    def get_obj_name(self):
        if self.current_object is None:
            return None
        else:
            return self.current_object['name']

    def get_path_config(self):
        path_config = list()
        for config in self.parent_configs:
            path_config.append(config)

        if (self.current_object is not None and
                self.current_object['config'] is not None):
            path_config.append(self.current_object["config"])

        if path_config == list():
            return None
        else:
            return " ".join(path_config)

    def set_current_obj(self, object_name, config, object_exists):

        config_object = {
            "name": object_name,
            "config": config
        }

        self.current_object = config_object
        self.object_exists = object_exists

    def set_current_config(self, config):
        self.current_object['config'] = config

    def set_child_context(self, parent_context):
        if parent_context is not None:
            if parent_context.current_object is not None:
                self.parent_object = parent_context.current_object
                if self.parent_object['config'] is not None:
                    self.parent_configs.append(self.parent_object['config'])

    def _get_object_string(self, obj):
        obj_str = "(none)"

        if obj is not None:
            if obj['config'] is not None:
                obj_str = obj['config']
            else:
                obj_str = obj['name']

        return obj_str
