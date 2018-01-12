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


class Action(object):
    """
    Private class to track and perform the actions required to write the
    configuration to the device
    """
    def __init__(self, parent, state=dict()):
        self.parent = parent
        self.state = state
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
    def new(action_dict, parent, state):
        if type(action_dict) != dict:
            raise TemplateParseError("Invalid action: " + str(action_dict))

        action_keys = action_dict.keys()
        if (len(action_keys) != 1):
            raise TemplateParseError("Invalid action: " + str(action_keys))

        action_key = action_keys[0]
        action_type = str(action_key).lower()
        if action_type == "create-object":
            new_action = CreateObjectAction(parent, state)
        elif action_type == "select-object":
            new_action = SelectObjectAction(parent, state)
        elif action_type == "set-values":
            new_action = SetValuesAction(parent, state)
        elif action_type == "store-value":
            new_action = StoreValueAction(parent, state)
        elif action_type == "retrieve-value":
            new_action = RetrieveValueAction(parent, state)
        else:
            raise TemplateParseError("Invalid action: " + str(action_key))

        new_action.read(action_dict[action_key])
        return new_action

    def is_set_values(self):
        return False

    def reset_state(self):
        self.state = dict()

    def read_children_actions(self, current_dict):
        child_actions = Action.get_dict_field(current_dict, 'actions')
        if child_actions is None:
            return

        if type(child_actions) != list:
            raise TemplateParseError("Invalid actions: " + str(child_actions))

        for action_dict in child_actions:
            new_action = Action.new(action_dict, self, self.state)
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


class CreateObjectAction(Action):

    def __init__(self, parent, state):
        super(CreateObjectAction, self).__init__(parent, state)
        self.object_type = None

    def read(self, create_dict):
        self.object_type = Action.get_dict_field(create_dict, 'type')
        if self.object_type is None:
            raise TemplateParseError(
                "Create object action missing required 'type' field")

        self.read_children_actions(create_dict)

    def _to_string(self, indent_level):
        cur_output = ""
        indent = Action._indent(indent_level)

        cur_output = "%s%s\n" % (indent, str(self.object_type))

        for child in self.children:
            cur_output += child._to_string(indent_level + 1)

        return cur_output


class SelectObjectAction(Action):

    def __init__(self, parent, state):
        super(SelectObjectAction, self).__init__(parent, state)
        self.object_type = None
        self.field = None
        self.value = None

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


class SetValuesAction(Action):

    def __init__(self, parent, state):
        super(SetValuesAction, self).__init__(parent, state)
        self.attributes = dict()

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

    def _to_string(self, indent_level):
        cur_output = ""
        indent = Action._indent(indent_level)

        for field, value in self.attributes.iteritems():
            if isinstance(value, basestring):
                if "'" in value:
                    value = '"' + value + '"'
                else:
                    value = "'" + value + "'"
            elif isinstance(value, Action):
                value = "[retrieve %s]" % value._get_reference_string()

            cur_output += "%s%s = %s\n" % (indent, str(field), str(value))

        return cur_output


class StoreValueAction(Action):

    def __init__(self, parent, state):
        super(StoreValueAction, self).__init__(parent, state)
        self.as_name = None
        self.from_field = None
        self.stored_value = None

    def read(self, store_value_dict):
        self.from_field = Action.get_dict_field(store_value_dict, 'from-field')
        if self.from_field is None:
            raise TemplateParseError(
                "Store value action missing required 'from-field' field")

        self.as_name = Action.get_dict_field(store_value_dict, 'as-name')
        if self.as_name is None:
            raise TemplateParseError(
                "Store value action missing required 'as-name' field")

        if self.parent is None or self.parent.parent is None:
            raise TemplateActionError("No object exists for storing values")

        if type(self.state) != dict:
            raise TemplateActionError('Invalid state for store value')

        if 'stored_values' not in self.state:
            self.state['stored_values'] = dict()

        if self.as_name not in self.state['stored_values']:
            self.state['stored_values'][self.as_name] = self
        else:
            raise TemplateActionError(
                'Value of name %s already stored' % self.from_name)

    def get_stored_value(self):
        if self.stored_value is not None:
            return self.stored_value
        else:
            raise TemplateActionError("No value stored as name %s" %
                                      self.as_name)

    def _to_string(self, indent_level):
        cur_output = ""
        indent = Action._indent(indent_level)

        cur_output += "%s[store %s to name %s]\n" % (indent,
                                                     str(self.from_field),
                                                     str(self.as_name))
        return cur_output

    def _get_reference_string(self):
        object_type = self.parent.object_type
        return "%s (%s:%s)" % (str(self.as_name),
                               str(object_type),
                               str(self.from_field))


class RetrieveValueAction(SetValuesAction):

    def __init__(self, parent, state):
        super(RetrieveValueAction, self).__init__(parent, state)
        self.from_name = None
        self.to_field = None

    def read(self, set_value_dict):
        self.to_field = Action.get_dict_field(set_value_dict, 'to-field')
        if self.to_field is None:
            raise TemplateParseError(
                "Retrieve value action missing required 'to-field' field")

        self.from_name = Action.get_dict_field(set_value_dict, 'from-name')
        if self.from_name is None:
            raise TemplateParseError(
                "Retrieve value action missing required 'from-name' field")

        if self.parent is None or self.parent.parent is None:
            raise TemplateActionError("No object exists for retrieving values")

        if (type(self.state) != dict or
                'stored_values' not in self.state or
                self.from_name not in self.state['stored_values']):
            raise TemplateActionError(
                'No value of name %s stored to be retrieved' % self.from_name)

        self.add_attribute(self.to_field,
                           self.state['stored_values'][self.from_name])
