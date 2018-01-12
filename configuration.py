from .template import (TemplateError,
                       TemplateParseError)


class ConflictError(TemplateError):
    """
    Exception class when there is a conflict during template processing
    """
    pass


class TemplateActionError(TemplateError):
    """
    Exception class when there is a problem with an action in a template
    """
    pass


class Configuration(object):
    """
    Container for template instances.
    """
    def __init__(self, template_store):
        """
        Requires a TemplateStore object to be provided.
        """
        self.store = template_store
        self.software_version = None
        self.software_type = None
        self.data = dict()

    def set_software_version(self, software_version, software_type=None):
        """
        Sets the current software version of templates that is desired.
        If not called, the latest software version of templates will be
        used.
        """
        raise NotImplementedError(
            "Template software versioning not yet implemented")

    def get_template_names(self):
        """
        Returns a list of all template names currently loaded in store.
        In reality, this just calls the template_store function with
        the currently set software_version and software_type.
        """
        return self.store.get_template_names(self.software_version,
                                             self.software_type)

    def get_template(self, name):
        """
        Returns a Template object of the specified name.  In reality,
        this just calls the template_store function with the currently
        set software_version and software_type.
        """
        return self.store.get_template(name,
                                       self.software_version,
                                       self.software_type)

    def add_template_data(self, template_name, **template_data):
        """
        Adds template data (user data) for the specified template name.
        Data is specified in a kwargs dictionary with keys as the
        attribute/variable name.  The data is validated against the
        corresponding template schema.  An id is returned for reference.
        """
        self.get_template(template_name)
        # TODO: verify data with template.get_schema()
        return self._append_data(template_name, dict(template_data))

    def get_template_data(self, id):
        """
        Returns the template data in dictionary form.  The id comes
        from the corresponding add_template_data call.
        """
        data = self._get_data(id)
        if data is not None:
            return dict(data)

        return None

    def update_template_data(self, id, **template_data):
        """
        Updates the specified template data.  Data is specified in a kwargs
        dictionary with keys as the attribute/variable name.  The data is
        validated against the corresponding template schema.  The id comes
        from the corresponding add_template_data call.
        """
        self.get_template(self._get_template_key(id))
        # TODO: verify data with template.get_schema()
        return self._set_data(id, dict(template_data))

    def remove_template_data(self, id):
        """
        Removes the specified template data.  The id comes
        from the corresponding add_template_data call.
        """
        return self._set_data(id, None)

    def validate(self, writer):
        """
        Validates this configuration against the provided device
        writer.  Returns True if ok, otherwise an exception is
        raised.
        """
        raise NotImplementedError("Template validation not yet implemented")

    def apply(self, writer):
        """
        Applies this configuration to the provided device
        writer.  Returns True if ok, otherwise an exception is
        raised.
        """
        self.root_action = Action(None)
        self.writer = writer
        self._walk_data(self._apply_data)

    def update(self, writer):
        """
        Applies this configuration to the provided device
        writer as an update.  This means objects that exist will
        not be considered conflicts.  Returns True if ok, otherwise
        an exception is raised.
        """
        pass

    def revert(self, writer):
        """
        Reverts (removes or undo) this configuration from the
        provided device writer.  Returns True if ok, otherwise
        an exception is raised.
        """
        pass

    #
    # Private functions to do the work
    #

    def _append_data(self, template_name, template_data):
        key = template_name.lower()
        index = 0
        if key in self.data:
            index = len(self.data[key])
        else:
            self.data[key] = list()

        self.data[key].append(template_data)

        return {"key": key, "index": index}

    def _set_data(self, id, template_data):
        key, index = self._get_data_index(id)

        self.data[key][index] = template_data

        return id

    def _get_data(self, id):
        key, index = self._get_data_index(id)

        return self.data[key][index]

    def _get_data_index(self, id):
        key = id['key']
        index = id['index']
        if key not in self.data:
            raise IndexError("Invalid template data id")

        length = len(self.data[key])
        if (index >= length):
            raise IndexError("Invalid template data id")

        return key, index

    def _get_template_key(self, id):
        return id['key']

    def _walk_data(self, callback_func):
        for template_name, data_list in self.data.iteritems():
            template = self.get_template(template_name)
            for data in data_list:
                if data is not None:
                    callback_func(template, data)

    def _apply_data(self, template, data):
        template_dict = template._parse_with_vars(**data)
        self.root_action.read_children_actions(template_dict)


#
# Private classes to do the work
#

class Action(object):
    """
    Private class to track and perform the actions required to write the
    configuration to the device
    """
    def __init__(self, parent):
        self.parent = parent
        self.children = list()

    def __str__(self):
        return self._to_string(0)

    def _to_string(self, indent_level):
        if indent_level == 0:
            cur_output = "Configuration\n"
        else:
            cur_output = "%s[Unknown action]\n" % Action._indent(indent_level)

        for child in self.children:
            cur_output += child._to_string(indent_level + 1)

        return cur_output

    @staticmethod
    def _indent(level):
        return "    " * level

    @staticmethod
    def get_dict_field(action_dict, field):
        if type(action_dict) != dict:
            raise TemplateParseError("Invalid action: " + str(action_dict))

        for key, value in action_dict.iteritems():
            if str(key).lower() == field:
                return value

        return None

    @staticmethod
    def new(action_dict, parent):
        if type(action_dict) != dict:
            raise TemplateParseError("Invalid action: " + str(action_dict))

        action_keys = action_dict.keys()
        if (len(action_keys) != 1):
            raise TemplateParseError("Invalid action: " + str(action_keys))

        action_key = action_keys[0]
        action_type = str(action_key).lower()
        if action_type == "create-object":
            new_action = CreateObjectAction(parent)
        elif action_type == "select-object":
            new_action = SelectObjectAction(parent)
        elif action_type == "set-values":
            new_action = SetValuesAction(parent)
        elif action_type == "store-value":
            new_action = StoreValueAction(parent)
        elif action_type == "retrieve-value":
            new_action = RetrieveValueAction(parent)
        else:
            raise TemplateParseError("Invalid action: " + str(action_key))

        new_action.read(action_dict[action_key])
        return new_action

    def read_children_actions(self, current_dict):
        child_actions = Action.get_dict_field(current_dict, 'actions')
        if child_actions is None:
            return

        if type(child_actions) != list:
            raise TemplateParseError("Invalid actions: " + str(child_actions))

        for action_dict in child_actions:
            new_action = Action.new(action_dict, self)
            self.add_child_action_sorted(new_action)

    def add_child_action_sorted(self, new_action):
        if len(self.children) > 0 and new_action.is_set_values():
            # A single set values action must always be at position 0
            if self.children[0].is_set_values():
                self.children[0].combine(new_action)
            else:
                self.children.insert(0, new_action)
        else:
            self.children.append(new_action)

    def is_set_values(self):
        return False


class CreateObjectAction(Action):

    def __init__(self, parent):
        super(CreateObjectAction, self).__init__(parent)
        self.object_type = None

    def _to_string(self, indent_level):
        cur_output = ""
        indent = Action._indent(indent_level)

        cur_output = "%s%s\n" % (indent, str(self.object_type))

        for child in self.children:
            cur_output += child._to_string(indent_level + 1)

        return cur_output

    def read(self, create_dict):
        self.object_type = Action.get_dict_field(create_dict, 'type')
        if self.object_type is None:
            raise TemplateParseError(
                "Create object action missing required 'type' field")

        self.read_children_actions(create_dict)


class SelectObjectAction(Action):

    def __init__(self, parent):
        super(SelectObjectAction, self).__init__(parent)
        self.object_type = None
        self.field = None
        self.value = None

    def _to_string(self, indent_level):
        cur_output = ""
        indent = Action._indent(indent_level)

        cur_output = "%s[select %s (%s of %s)]\n" % (indent,
                                                     str(self.object_type),
                                                     str(self.field),
                                                     str(self.value))

        for child in self.children:
            cur_output += child._to_string(indent_level + 1)

        return cur_output

    def read(self, select_dict):
        self.object_type = Action.get_dict_field(select_dict, 'type')
        if self.object_type is None:
            raise TemplateParseError(
                "Select object action missing required 'type' field")

        self.field = Action.get_dict_field(select_dict, 'by-field')
        if self.field is None:
            raise TemplateParseError(
                "Select object action missing required 'by-field' field")

        self.value = Action.get_dict_field(select_dict, 'value')
        if self.value is None:
            raise TemplateParseError(
                "Select object action missing required 'value' field")

        self.read_children_actions(select_dict)


class SetValuesAction(Action):

    def __init__(self, parent):
        super(SetValuesAction, self).__init__(parent)
        self.attributes = dict()

    def _to_string(self, indent_level):
        cur_output = ""
        indent = Action._indent(indent_level)

        for field, value in self.attributes.iteritems():
            if value == '':
                value = '""'
            cur_output += "%s%s = %s\n" % (indent, str(field), str(value))

        return cur_output

    def is_set_values(self):
        return True

    def read(self, set_values_dict):
        if type(set_values_dict) != dict:
            raise TemplateParseError("Invalid action: " + str(set_values_dict))

        if self.parent is None or self.parent.parent is None:
            raise TemplateActionError("No object exists for setting values")

        for key, value in set_values_dict.iteritems():
            self.add_attribute(key, value)

    def add_attribute(self, field, value):
        existing_value = Action.get_dict_field(self.attributes, field.lower())
        if existing_value is not None:
            raise ConflictError("Setting field '%s' of object %s to '%s' "
                                "when it is already set to '%s'" %
                                (str(value), str(self.object_type),
                                 str(value), str(existing_value)))

        self.attributes[field] = value

    def combine(self, new_set_values_action):
        for key, value in new_set_values_action.attributes.iteritems():
            self.add_attribute(key, value)


class StoreValueAction(Action):

    def __init__(self, parent):
        super(StoreValueAction, self).__init__(parent)
        self.as_name = None
        self.from_field = None

    def _to_string(self, indent_level):
        cur_output = ""
        indent = Action._indent(indent_level)

        cur_output += "%s[store %s to name %s]\n" % (indent,
                                                     str(self.from_field),
                                                     str(self.as_name))
        return cur_output

    def read(self, set_value_dict):
        self.from_field = Action.get_dict_field(set_value_dict, 'from-field')
        if self.from_field is None:
            raise TemplateParseError(
                "Store value action missing required 'from-field' field")

        self.as_name = Action.get_dict_field(set_value_dict, 'as-name')
        if self.as_name is None:
            raise TemplateParseError(
                "Store value action missing required 'as-name' field")


class RetrieveValueAction(Action):

    def __init__(self, parent):
        super(RetrieveValueAction, self).__init__(parent)
        self.from_name = None
        self.to_field = None

    def _to_string(self, indent_level):
        cur_output = ""
        indent = Action._indent(indent_level)

        cur_output += "%s%s = [retrieve %s]\n" % (indent,
                                                  str(self.to_field),
                                                  str(self.from_name))
        return cur_output

    def read(self, set_value_dict):
        self.to_field = Action.get_dict_field(set_value_dict, 'to-field')
        if self.to_field is None:
            raise TemplateParseError(
                "Retrieve value action missing required 'to-field' field")

        self.from_name = Action.get_dict_field(set_value_dict, 'from-name')
        if self.from_name is None:
            raise TemplateParseError(
                "Retrieve value action missing required 'from-name' field")
