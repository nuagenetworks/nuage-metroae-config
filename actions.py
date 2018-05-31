from errors import (ConflictError,
                    MissingSelectionError,
                    LevistateError,
                    TemplateActionError,
                    TemplateParseError)
from logger import Logger
from util import get_dict_field_no_case

DEFAULT_SELECTION_FIELD = 'name'


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
        self.store_marks = set()
        self.retrieve_marks = set()
        self.template_name = None
        if parent is None:
            self.level = 0
            self.log = Logger()
            self.log.set_to_stdout("ERROR", enabled=True)
        else:
            self.level = parent.level + 1
            self.log = parent.log

    def __str__(self):
        return self._to_string_with_children()

    def _to_string_with_children(self):
        cur_output = self._to_string(self.level)

        cur_output += "\n"

        for child in self.children:
            cur_output += child._to_string_with_children()

        return cur_output

    def _to_string(self, indent_level):
        if self.level == 0:
            cur_output = "Configuration"
        else:
            cur_output = "%s[Unknown action]" % Action._indent(indent_level)

        return cur_output

    def _get_location(self, prefix="In "):
        location = prefix + self._to_string(0)
        if self.template_name is not None:
            location = "%s (template: %s)" % (location, self.template_name)

        return location

    @staticmethod
    def _indent(level):
        return "    " * level

    def set_logger(self, logger):
        self.log = logger

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

        if parent is not None:
            new_action.set_template_name(parent.template_name)

        try:
            new_action.read(action_dict[action_key])
        except LevistateError as e:
            e.reraise_with_location(new_action._get_location())

        return new_action

    def reset_state(self):
        self.state = dict()

    def set_revert(self, is_revert=True):
        self.state['is_revert'] = is_revert

    def set_template_name(self, name):
        self.template_name = name

    def execute(self, writer, context=None):
        self.execute_children(writer, context=None)

    def execute_children(self, writer, context=None):
        if self.is_revert() is True:
            for child in reversed(self.children):
                try:
                    child.execute(writer, context)
                except LevistateError as e:
                    e.reraise_with_location(child._get_location())
        else:
            for child in self.children:
                if not writer.is_validate_only():
                    child.log.output(child._to_string(child.level))
                try:
                    child.execute(writer, context)
                except LevistateError as e:
                    e.reraise_with_location(child._get_location())

    def is_set_values(self):
        return False

    def is_create(self):
        return False

    def is_retrieve(self):
        return False

    def get_object_selector(self):
        return None

    def is_same_object(self, other_action):
        return False

    def get_child_value(self, field):
        if len(self.children) > 0 and self.children[0].is_set_values():
            return self.children[0].get_value(field)
        else:
            return None

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
        try:
            if len(self.children) > 0 and new_action.is_set_values():
                # A single set values action must always be at position 0
                if self.children[0].is_set_values():
                    self.children[0].combine(new_action)
                else:
                    self.children.insert(0, new_action)
            else:
                match_indicies = self.find_same_object_indicies_in_children(
                    new_action)
                if len(match_indicies) > 0:
                    self.combine_same_objects(match_indicies[0], new_action)
                    self.combine_children_indicies(match_indicies[0],
                                                   match_indicies[1:])
                else:
                    self.children.append(new_action)

            self.reorder_retrieve()

        except LevistateError as e:
            e.reraise_with_location(new_action._get_location())

    def find_same_object_indicies_in_children(self, new_action):
        indicies = []
        for i, child in enumerate(self.children):
            if (child.is_same_object(new_action) or
                    new_action.is_same_object(child)):
                indicies.append(i)
        return indicies

    def combine_same_objects(self, existing_index, combine_action):
        if combine_action.is_create():
            combine_action.combine(self.children[existing_index])
            self.children[existing_index] = combine_action
        else:
            self.children[existing_index].combine(combine_action)

    def combine_children_indicies(self, first_index, remaining_indicies):
        for remaining_index in remaining_indicies:
            self.combine_same_objects(first_index,
                                      self.children[remaining_index])
        for remaining_index in reversed(remaining_indicies):
            del self.children[remaining_index]

    def mark_ancestors_for_reorder(self, mark, is_store):
        if self.parent is not None:
            if is_store is True:
                self.parent.store_marks.add(mark)
            else:
                self.parent.retrieve_marks.add(mark)
            self.parent.mark_ancestors_for_reorder(mark, is_store)

    def reorder_retrieve(self):
        for mark in self.retrieve_marks:
            self.reorder_ancestors(mark)

    def reorder_ancestors(self, mark):
        store_indicies = self.find_marked_indicies_in_children(
            mark, is_store=True)
        retrieve_indicies = self.find_marked_indicies_in_children(
            mark, is_store=False)

        if len(store_indicies) > 0 and len(retrieve_indicies) > 0:
            first_retrieve_index = retrieve_indicies[0]

            # Move store actions just before first receive
            for store_index in store_indicies:
                if store_index > first_retrieve_index:
                    store_action = self.children[store_index]
                    del self.children[store_index]
                    self.children.insert(first_retrieve_index, store_action)

        if self.parent is not None:
            self.parent.reorder_ancestors(mark)

    def find_marked_indicies_in_children(self, mark, is_store):
        indicies = []
        for i, child in enumerate(self.children):
            if is_store is True:
                if mark in child.store_marks:
                    indicies.append(i)
            else:
                if mark in child.retrieve_marks:
                    indicies.append(i)

        return indicies


class CreateObjectAction(Action):

    def __init__(self, parent, state):
        super(CreateObjectAction, self).__init__(parent, state)
        self.object_type = None
        self.select_by_field = DEFAULT_SELECTION_FIELD

    def is_create(self):
        return True

    def read(self, create_dict):
        self.object_type = Action.get_dict_field(create_dict, 'type')
        if self.object_type is None:
            raise TemplateParseError(
                "Create object action missing required 'type' field")

        field = Action.get_dict_field(create_dict, 'select-by-field')
        if field is not None:
            self.select_by_field = field

        self.log.debug(self._get_location("Reading "))

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

                if not writer.is_validate_only():
                    self.log.output(self._get_location("Revert "))

                writer.delete_object(new_context)
            except MissingSelectionError:
                # Skip deletion if object is not present (not created)
                pass

    def get_select_value(self):
        return self.get_child_value(self.select_by_field)

    def get_object_selector(self):
        select_value = self.get_select_value()
        return {'type': self.object_type.lower(),
                'field': self.select_by_field.lower(),
                'value': select_value}

    def is_same_object(self, other_action):
        other_selector = other_action.get_object_selector()
        if other_selector is None:
            return False

        if other_selector['type'] != self.object_type.lower():
            return False

        other_value = other_action.get_child_value(self.select_by_field)
        this_value = self.get_select_value()
        return this_value is not None and this_value == other_value

    def combine(self, other_action):
        if other_action.is_create():
            select_value = self.get_select_value()
            raise ConflictError("Creating the same object twice %s: %s = %s" %
                                (self.object_type, self.select_by_field,
                                 str(select_value)))

        self.store_marks.update(other_action.store_marks)
        self.retrieve_marks.update(other_action.retrieve_marks)

        for child in other_action.children:
            child.parent = self
            self.add_child_action_sorted(child)

    def _to_string(self, indent_level):
        indent = Action._indent(indent_level)

        return indent + str(self.object_type)


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

        self.log.debug(self._get_location("Reading "))

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

    def get_object_selector(self):
        return {'type': self.object_type.lower(),
                'field': self.field.lower(),
                'value': self.value}

    def is_same_object(self, other_action):
        other_selector = other_action.get_object_selector()
        if other_selector is None:
            return False

        if other_selector['type'] != self.object_type.lower():
            return False

        other_value = other_action.get_child_value(self.field)
        if self.value == other_value:
            return True

        return (other_selector['field'] == self.field.lower() and
                other_selector['value'] == self.value)

    def combine(self, other_action):
        self.store_marks.update(other_action.store_marks)
        self.retrieve_marks.update(other_action.retrieve_marks)

        for child in other_action.children:
            child.parent = self
            self.add_child_action_sorted(child)

    def _to_string(self, indent_level):
        indent = Action._indent(indent_level)

        cur_output = "%s[select %s (%s of %s)]" % (indent,
                                                   str(self.object_type),
                                                   str(self.field),
                                                   str(self.value))

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

        self.log.debug(self._get_location("Reading "))

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
        return Action.get_dict_field(self.attributes, field.lower())

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

        return cur_output.rstrip()

    def _get_location(self, prefix="In "):
        location = prefix + "[set values]"
        if self.template_name is not None:
            location = "%s (template: %s)" % (location, self.template_name)

        return location


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

        self.log.debug(self._get_location("Reading "))

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

        self.mark_ancestors_for_reorder(self.as_name, is_store=True)

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
        indent = Action._indent(indent_level)

        cur_output = "%s[store %s to name %s]" % (indent,
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

    def is_retrieve(self):
        return True

    def read(self, set_value_dict):
        self.to_field = Action.get_dict_field(set_value_dict, 'to-field')
        if self.to_field is None:
            raise TemplateParseError(
                "Retrieve value action missing required 'to-field' field")

        self.from_name = Action.get_dict_field(set_value_dict, 'from-name')
        if self.from_name is None:
            raise TemplateParseError(
                "Retrieve value action missing required 'from-name' field")

        self.log.debug(self._get_location("Reading "))

        if self.parent is None or self.parent.parent is None:
            raise TemplateActionError("No object exists for retrieving values")

        if (type(self.state) != dict or
                'stored_values' not in self.state or
                self.from_name not in self.state['stored_values']):
            raise TemplateActionError(
                'No value of name %s stored to be retrieved' % self.from_name)

        stored_action = self.state['stored_values'][self.from_name]
        self.add_attribute(self.to_field, stored_action)
        self.mark_ancestors_for_reorder(self.from_name, is_store=False)
