from device_writer_base import MissingSelectionError
from template import (TemplateError,
                      TemplateParseError)
from util import get_dict_field_no_case

DEFAULT_SELECTION_FIELD = 'name'


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
    def __init__(self, parent, state=None):
        self.parent = parent
        if state is None:
            self.state = dict()
        else:
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
        try:
            return get_dict_field_no_case(action_dict, field)
        except TypeError:
            raise TemplateParseError("Invalid action: " + str(action_dict))

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

    def set_revert(self, is_revert=True):
        self.state['is_revert'] = is_revert

    def is_revert(self):
        return 'is_revert' in self.state and self.state['is_revert'] is True

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

    def execute(self, writer, context=None):
        self.execute_children(writer, context=None)

    def execute_children(self, writer, context=None):
        if self.is_revert() is True:
            for child in reversed(self.children):
                child.execute(writer, context)
        else:
            for child in self.children:
                child.execute(writer, context)


class CreateObjectAction(Action):

    def __init__(self, parent, state):
        super(CreateObjectAction, self).__init__(parent, state)
        self.object_type = None
        self.select_by_field = DEFAULT_SELECTION_FIELD

    def read(self, create_dict):
        self.object_type = Action.get_dict_field(create_dict, 'type')
        if self.object_type is None:
            raise TemplateParseError(
                "Create object action missing required 'type' field")

        field = Action.get_dict_field(create_dict, 'select-by-field')
        if field is not None:
            self.select_by_field = field

        self.read_children_actions(create_dict)

    def execute(self, writer, context=None):
        if self.is_revert() is False:
            new_context = writer.create_object(self.object_type, context)
            self.execute_children(writer, new_context)
        else:
            self.delete_object(writer, context)

    def delete_object(self, writer, context=None):
        select_value = self.get_select_value()
        if select_value is not None:
            try:
                new_context = writer.select_object(self.object_type,
                                                   self.select_by_field,
                                                   select_value,
                                                   context)

                # Always delete children first
                self.execute_children(writer, new_context)
                writer.delete_object(new_context)
            except MissingSelectionError:
                # Skip deletion if object is not present (not created)
                pass

    def get_select_value(self):
        if len(self.children) > 0 and self.children[0].is_set_values():
            return self.children[0].get_value(self.select_by_field)
        else:
            return None

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

    def execute(self, writer, context=None):
        try:
            new_context = writer.select_object(self.object_type,
                                               self.field,
                                               self.value,
                                               context)
            self.execute_children(writer, new_context)
        except MissingSelectionError as e:
            if self.is_revert() is not True:
                raise e

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
        if value is not None:
            existing_value = Action.get_dict_field(self.attributes,
                                                   field.lower())
            if existing_value is not None:
                raise ConflictError("Setting field '%s' of object %s to '%s' "
                                    "when it is already set to '%s'" %
                                    (str(field), str(self.parent.object_type),
                                     str(value).strip(),
                                     str(existing_value).strip()))

            self.attributes[field] = value

    def combine(self, new_set_values_action):
        for key, value in new_set_values_action.attributes.iteritems():
            self.add_attribute(key, value)

    def execute(self, writer, context=None):
        if self.is_revert() is False:
            resolved_attributes = self.resolve_attributes()
            writer.set_values(context, **resolved_attributes)

    def resolve_attributes(self):
        attributes_copy = dict()
        for key, value in self.attributes.iteritems():
            if isinstance(value, Action):
                resolved_value = value.get_stored_value()
                attributes_copy[key] = resolved_value
            else:
                attributes_copy[key] = value

        return attributes_copy

    def get_value(self, field):
        if field in self.attributes:
            return self.attributes[field]

        return None

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
                'Value of name %s already stored' % self.as_name)

    def get_stored_value(self):
        if self.stored_value is not None:
            return self.stored_value
        else:
            raise TemplateActionError("No value stored as name %s" %
                                      self.as_name)

    def execute(self, writer, context=None):
        if self.is_revert() is False:
            self.stored_value = writer.get_value(self.from_field, context)

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
