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
