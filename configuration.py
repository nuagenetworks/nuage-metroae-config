from .template import (TemplateError,
                       TemplateParseError)


class ConflictError(TemplateError):
    """
    Exception class when there is a conflict during template processing
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
        template_dict = template._apply(**data)
        child_actions = Action.get_dict_field(template_dict, 'actions')
        if child_actions is not None:
            self.root_action.read_children_actions(child_actions)
        else:
            raise TemplateParseError("Template %s missing actions" %
                                     template.get_name())


#
# Private classes to do the work
#

class Action(object):
    """
    Private class to track and perform the actions required to write the
    configuration to the device
    """
    def __init__(self, root):
        self.root = root
        self.object_type = None
        self.context = None
        self.children = list()
        self.is_select = False
        self.is_delete = False
        self.is_get = False
        self.select_field = None
        self.select_value = None
        self.attributes = dict()

    def __str__(self):
        return self._to_string(0)

    def _to_string(self, indent_level):
        cur_output = ""
        indent = "    " * indent_level

        if self.object_type is not None:
            if self.is_select is True:
                cur_output = "%s[select %s (%s = %s)]\n" % (
                    indent,
                    str(self.object_type),
                    str(self.select_field),
                    str(self.select_value))
            else:
                cur_output = "%s%s\n" % (indent, str(self.object_type))

        for field, value in self.attributes.iteritems():
            cur_output += "%s%s = %s\n" % (indent, str(field), str(value))

        for child in self.children:
            cur_output += child._to_string(indent_level + 1)

        return cur_output

    @staticmethod
    def get_dict_field(action_dict, field):
        if type(action_dict) != dict:
            raise TemplateParseError("Invalid action: " + str(action_dict))

        for key, value in action_dict.iteritems():
            if str(key).lower() == field:
                return value

        return None

    def read(self, action_dict):
        if type(action_dict) != dict:
            raise TemplateParseError("Invalid action: " + str(action_dict))

        action_keys = action_dict.keys()
        if (len(action_keys) != 1):
            raise TemplateParseError("Invalid action: " + str(action_keys))

        action_key = action_keys[0]
        action_type = str(action_key).lower()
        if action_type == "create-object":
            self.read_create_object(action_dict[action_key])
        elif action_type == "select-object":
            self.read_select_object(action_dict[action_key])
        elif action_type == "set-values":
            self.read_set_values(action_dict[action_key])
        elif action_type == "set-value-from-object":
            self.read_set_value_from_object(action_dict[action_key])
        else:
            raise TemplateParseError("Invalid action: " + str(action_key))

    def read_create_object(self, create_dict):
        self.object_type = Action.get_dict_field(create_dict, 'type')
        if self.object_type is None:
            raise TemplateParseError(
                "Create object action missing required 'type' field")

        child_actions = Action.get_dict_field(create_dict, 'actions')
        if child_actions is not None:
            self.read_children_actions(child_actions)

    def read_select_object(self, select_dict):
        self.object_type = Action.get_dict_field(select_dict, 'type')
        if self.object_type is None:
            raise TemplateParseError(
                "Select object action missing required 'type' field")

        self.select_field = Action.get_dict_field(select_dict, 'by-field')
        if self.select_field is None:
            raise TemplateParseError(
                "Select object action missing required 'by-field' field")

        self.select_value = Action.get_dict_field(select_dict, 'value')
        if self.select_value is None:
            raise TemplateParseError(
                "Select object action missing required 'value' field")

        self.is_select = True
        child_actions = Action.get_dict_field(select_dict, 'actions')
        if child_actions is not None:
            self.read_children_actions(child_actions)

    def read_set_values(self, set_values_dict):
        if type(set_values_dict) != dict:
            raise TemplateParseError("Invalid action: " + str(set_values_dict))

        for key, value in set_values_dict.iteritems():
            self.add_attribute(key, value)

    def read_set_value_from_object(self, set_value_dict):
        self.select_field = Action.get_dict_field(set_value_dict, 'from-field')
        if self.select_field is None:
            raise TemplateParseError(
                "Set value from object action missing required "
                "'from-field' field")

        self.select_value = Action.get_dict_field(set_value_dict, 'to-field')
        if self.select_value is None:
            raise TemplateParseError(
                "Set value from object action missing required "
                "'to-field' field")

        child_actions = Action.get_dict_field(set_value_dict, 'actions')
        if child_actions is not None:
            self.read_children_actions(child_actions)

    def read_children_actions(self, child_actions):
        if type(child_actions) != list:
            raise TemplateParseError("Invalid actions: " + str(child_actions))

        for action_dict in child_actions:
            new_action = Action(self.root)
            self.children.append(new_action)
            new_action.read(action_dict)

    def add_attribute(self, field, value):
        existing_value = Action.get_dict_field(self.attributes, field.lower())
        if existing_value is not None:
            raise ConflictError("Setting attribute '%s' of object %s to '%s' "
                                "when it is already set to '%s'" %
                                (str(value), str(self.object_type),
                                 str(value), str(existing_value)))

        self.attributes[field] = value
