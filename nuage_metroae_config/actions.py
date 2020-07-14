from errors import (ConflictError,
                    MissingSelectionError,
                    MultipleSelectionError,
                    MetroConfigError,
                    TemplateActionError,
                    TemplateParseError)
from logger import Logger
from util import get_dict_field_no_case

DEFAULT_SELECTION_FIELD = "name"
FIRST_SELECTOR = "$first"
LAST_SELECTOR = "$last"
POSITION_SELECTOR = "$position"
CHILD_SELECTOR = "$child"
RETRIEVE_VALUE_SELECTOR = "$retrieve-value"
DEPENDENCY_ONLY = "$dependency-only"


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

        self.disable_combine = False

        self.children = list()
        self.store_marks = set()
        self.retrieve_marks = set()
        self.template_name = None
        self.order = 0
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
        elif action_type == "save-to-file":
            new_action = SaveToFileAction(parent, state)
        else:
            raise TemplateParseError("Invalid action: " + str(action_key))

        if parent is not None:
            new_action.set_template_name(parent.template_name)

        try:
            new_action.read(action_dict[action_key])
        except MetroConfigError as e:
            e.reraise_with_location(new_action._get_location())

        return new_action

    def reset_state(self):
        self.state.clear()

    def set_revert(self, is_revert=True):
        self.state['is_revert'] = is_revert

    def set_update(self, is_update=True):
        self.state['is_update'] = is_update

    def set_store_only(self, store_only=True):
        self.state['is_store_only'] = store_only

    def set_template_name(self, name):
        self.template_name = name

    def execute(self, writer, context=None):
        if self.is_revert():
            self.log.debug("Gather store values before revert")
            self.set_store_only()
            self.execute_children(writer, context=None)
            self.log.debug("Perform revert")
            self.set_store_only(False)

        self.execute_children(writer, context=None)

    def execute_children(self, writer, context=None):
        if self.is_revert() is True:
            if self.is_store_only():
                ordered_list = self.children
            else:
                ordered_list = reversed(self.children)

            for child in ordered_list:
                try:
                    child.execute(writer, context)
                except MetroConfigError as e:
                    e.reraise_with_location(child._get_location())
        else:
            for child in self.children:
                if not writer.is_validate_only():
                    child.log.output(child._to_string(child.level))
                try:
                    child.execute(writer, context)
                except MetroConfigError as e:
                    e.reraise_with_location(child._get_location())

    def is_set_values(self):
        return False

    def is_create(self):
        return False

    def is_select(self):
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

    def is_update(self):
        return 'is_update' in self.state and self.state['is_update'] is True

    def is_store_only(self):
        return ('is_store_only' in self.state and
                self.state['is_store_only'] is True)

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

        except MetroConfigError as e:
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

    def reorder(self):
        self.reorder_orders()
        self.reorder_retrieve()

    def reorder_orders(self):

        sort_dict = dict()

        for child in self.children:
            if child.order not in sort_dict:
                sort_dict[child.order] = list()
            sort_dict[child.order].append(child)

        self.children = list()
        for order in sorted(sort_dict):
            self.children.extend(sort_dict[order])

    def reorder_retrieve(self):
        complete = False

        for i in range(len(self.retrieve_marks)):
            if not complete:
                complete = True
                for mark in self.retrieve_marks:
                    if self.reorder_children(mark):
                        complete = False

        for child in self.children:
            child.reorder_retrieve()

    def reorder_children(self, mark):
        store_indicies = self.find_marked_indicies_in_children(
            mark, is_store=True)
        retrieve_indicies = self.find_marked_indicies_in_children(
            mark, is_store=False)

        did_move = False

        if len(store_indicies) > 0 and len(retrieve_indicies) > 0:
            first_retrieve_index = retrieve_indicies[0]

            # Move store actions just before first receive
            for store_index in store_indicies:
                if store_index > first_retrieve_index:
                    store_action = self.children[store_index]
                    del self.children[store_index]
                    self.children.insert(first_retrieve_index, store_action)
                    did_move = True

        return did_move

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
        self.is_updatable = True

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

        updatable = Action.get_dict_field(create_dict, 'update-supported')
        if updatable is not None:
            self.is_updatable = updatable

        self.log.debug(self._get_location("Reading "))

        self.read_children_actions(create_dict)

    def execute(self, writer, context=None):
        if self.is_revert() is False:
            if not self.is_update():
                new_context = writer.create_object(self.object_type, context)
            else:
                if self.select_by_field.lower() in [FIRST_SELECTOR,
                                                    LAST_SELECTOR]:
                    context_list = writer.get_object_list(self.object_type,
                                                          context)

                    if len(context_list) < 1:
                        new_context = writer.update_object(
                            self.object_type,
                            self.select_by_field,
                            self.get_select_value(),
                            context)
                    else:
                        if self.select_by_field.lower() == FIRST_SELECTOR:
                            new_context = context_list[0]
                        else:
                            new_context = context_list[-1]
                else:
                    new_context = writer.update_object(self.object_type,
                                                       self.select_by_field,
                                                       self.get_select_value(),
                                                       context)
            self.execute_children(writer, new_context)
        else:
            self.delete_object(writer, context)

    def delete_object(self, writer, context=None):
        select_value = self.get_select_value()
        if (select_value is not None or
            self.select_by_field.lower() in [FIRST_SELECTOR,
                                             LAST_SELECTOR]):
            try:
                if self.select_by_field.lower() in [FIRST_SELECTOR,
                                                    LAST_SELECTOR]:
                    context_list = writer.get_object_list(self.object_type,
                                                          context)

                    if len(context_list) < 1:
                        raise MissingSelectionError("No objects selected")

                    if self.select_by_field.lower() == FIRST_SELECTOR:
                        new_context = context_list[0]
                    else:
                        new_context = context_list[-1]
                else:
                    if isinstance(select_value, Action):
                        if self.is_store_only():
                            return
                        select_value = select_value.get_stored_value()

                    new_context = writer.select_object(self.object_type,
                                                       self.select_by_field,
                                                       select_value,
                                                       context)

                # Always delete children first
                self.execute_children(writer, new_context)

                if not self.is_store_only():
                    if not writer.is_validate_only():
                        self.log.output(self._get_location("Revert "))

                    writer.delete_object(new_context)
            except MissingSelectionError:
                # Skip deletion if object is not present (not created)
                self.log.debug("Selection failed for revert")

    def get_select_value(self):
        return self.get_child_value(self.select_by_field.lower())

    def get_object_selector(self):
        if self.select_by_field.lower() == FIRST_SELECTOR:
            return {'type': self.object_type.lower(),
                    'field': POSITION_SELECTOR,
                    'value': 0}
        elif self.select_by_field.lower() == LAST_SELECTOR:
            return {'type': self.object_type.lower(),
                    'field': POSITION_SELECTOR,
                    'value': -1}
        else:
            select_value = self.get_select_value()
            return {'type': self.object_type.lower(),
                    'field': self.select_by_field.lower(),
                    'value': select_value}

    def is_same_object(self, other_action):
        if other_action.disable_combine is True:
            return False

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
        self.is_child_find = False
        self.is_updatable = True

    def is_select(self):
        return True

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

        updatable = Action.get_dict_field(select_dict, 'update-supported')
        if updatable is not None:
            self.is_updatable = updatable

        order = Action.get_dict_field(select_dict, 'order')
        if order is not None:
            self.order = order

        if type(self.field) == list:
            if type(self.value) != list:
                raise TemplateParseError(
                    "Select action value must be a list if by-field is a list")
            if len(self.field) != len(self.value):
                raise TemplateParseError(
                    "Select action value has different length than by-field")
            if len(self.field) == 1:
                self.field = self.field[0]
                self.value = self.value[0]
        else:
            if self.field.lower() == CHILD_SELECTOR:
                self.disable_combine = True

        disable_combine = Action.get_dict_field(select_dict, 'disable-combine')
        if disable_combine is True:
            self.disable_combine = True

        self.log.debug(self._get_location("Reading "))

        self.read_children_actions(select_dict)

    def execute(self, writer, context=None):
        try:
            if type(self.field) == list:

                new_context = self.select_multiple(writer, context)

            elif self.field.lower() == POSITION_SELECTOR:

                new_context = self.select_by_position(writer, context)

            elif self.field.lower() == CHILD_SELECTOR:

                new_context = self.select_child(writer, context)

            elif self.field.lower() == RETRIEVE_VALUE_SELECTOR:

                new_context = self.select_retrieve_value(writer, context)

            else:
                new_context = writer.select_object(self.object_type,
                                                   self.field,
                                                   self.value,
                                                   context)
            if self.is_child_find is not True:
                self.execute_children(writer, new_context)

        except MissingSelectionError as e:
            if self.is_revert() is not True or self.is_child_find is True:
                raise e

    def select_multiple(self, writer, context):

        context_list = writer.get_object_list(self.object_type,
                                              context)
        self.log.debug("Searching for multiple criteria %s = %s" %
                       (str(self.field), str(self.value)))

        match_count = 0
        for item_context in context_list:
            match = True
            for field, value in zip(self.field, self.value):
                other_value = writer.get_value(field, item_context)
                if value != other_value:
                    match = False

            if match or writer.is_validate_only():
                new_context = item_context
                match_count += 1
                self.log.debug("Found " + str(new_context))

        if match_count == 0:
            raise MissingSelectionError(
                "No object matches selection criteria")

        if match_count > 1:
            raise MultipleSelectionError(
                "Multiple objects match selection criteria")

        return new_context

    def select_by_position(self, writer, context):

        context_list = writer.get_object_list(self.object_type,
                                              context)

        if len(context_list) <= self.value or len(context_list) == 0:
            raise MissingSelectionError(
                "No object present at position %d" % self.value)

        return context_list[self.value]

    def select_child(self, writer, context):

        child_select = self.get_child_selector(self.value.lower())
        child_select.is_child_find = True
        context_list = writer.get_object_list(self.object_type,
                                              context)

        self.log.debug("Searching for child " +
                       str(child_select).strip())

        new_context = None
        for item_context in context_list:
            if new_context is None:
                try:
                    child_select.execute(writer, item_context)
                    new_context = item_context
                    self.log.debug("Found " + str(new_context))
                except MissingSelectionError:
                    pass

        child_select.is_child_find = False

        if new_context is None:
            raise MissingSelectionError(
                "Could not find matching child selection " +
                str(child_select).strip())

        return new_context

    def select_retrieve_value(self, writer, context):

        selector = self.get_child_value(self.value.lower())

        if selector is None:
            raise MissingSelectionError("No retrieve-value present"
                                        " for attribute %s" %
                                        self.value)

        if not isinstance(selector, Action):
            raise MissingSelectionError("Action not retrieve-value"
                                        " for attribute %s" %
                                        self.value)

        select_value = selector.get_stored_value()

        return writer.select_object(self.object_type,
                                    self.value,
                                    select_value,
                                    context)

    def get_object_selector(self):
        if type(self.field) == list:
            fields = sorted([x.lower() for x in self.field])
            values = sorted(self.value)
        else:
            fields = self.field.lower()
            values = self.value

        return {'type': self.object_type.lower(),
                'field': fields,
                'value': values}

    def is_same_object(self, other_action):
        if self.disable_combine is True:
            return False

        if other_action.disable_combine is True:
            return False

        other_selector = other_action.get_object_selector()
        if other_selector is None:
            return False

        if other_selector['type'] != self.object_type.lower():
            return False

        if type(self.field) == list:
            fields = self.field
            values = self.value
        else:
            fields = [self.field]
            values = [self.value]

        # Find the selected field in the other action
        match = True
        for field, value in zip(fields, values):
            other_value = other_action.get_child_value(field)
            if value != other_value:
                match = False

        this_selector = self.get_object_selector()

        return match or (other_selector['field'] == this_selector["field"] and
                         other_selector['value'] == this_selector["value"])

    def combine(self, other_action):
        self.store_marks.update(other_action.store_marks)
        self.retrieve_marks.update(other_action.retrieve_marks)

        for child in other_action.children:
            child.parent = self
            self.add_child_action_sorted(child)

    def get_child_selector(self, child_type):
        for child in self.children:
            if child.is_select() and child.object_type.lower() == child_type:
                return child

        raise MissingSelectionError(
            "No select-object child of specified object type")

    def _to_string(self, indent_level):
        indent = Action._indent(indent_level)

        if type(self.field) == list and type(self.value) == list:
            selection = list()
            for field, value in zip(self.field, self.value):
                selection.append("%s of %s" % (str(field), str(value)))

            selection = ", ".join(selection)
        else:
            selection = "%s of %s" % (str(self.field), str(self.value))

        cur_output = "%s[select %s (%s)]" % (indent,
                                             str(self.object_type),
                                             selection)

        return cur_output


class SetValuesAction(Action):

    def __init__(self, parent, state):
        super(SetValuesAction, self).__init__(parent, state)
        self.attributes = dict()
        self.as_list = False

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
            if existing_value is not None and existing_value != value:
                raise ConflictError("Setting field '%s' of object %s to '%s' "
                                    "when it is already set to '%s'" %
                                    (str(field), str(self.parent.object_type),
                                     str(value).strip(),
                                     str(existing_value).strip()))

            self.attributes[field] = value

    def append_list_attribute(self, field, value):
        if value is not None:
            existing_value = Action.get_dict_field(self.attributes,
                                                   field.lower())
            if existing_value is not None:
                if type(existing_value) != list:
                    raise ConflictError("Appending field '%s' of object %s"
                                        " to '%s', but is not a list: '%s'" %
                                        (str(field),
                                         str(self.parent.object_type),
                                         str(value).strip(),
                                         str(existing_value).strip()))
            else:
                self.attributes[field] = list()

            if type(value) == list:
                self.attributes[field].extend(value)
            else:
                self.attributes[field].append(value)

    def combine(self, new_set_values_action):
        for key, value in new_set_values_action.attributes.iteritems():
            if self.as_list or new_set_values_action.as_list:
                self.append_list_attribute(key, value)
            else:
                self.add_attribute(key, value)

    def execute(self, writer, context=None):
        if self.is_store_only() is False:
            resolved_attributes = None
            if (self.parent.is_select() and
                    self.parent.field.lower() == RETRIEVE_VALUE_SELECTOR):
                attributes_copy = dict(self.resolve_attributes())
                field = self.parent.value.lower()
                if field in attributes_copy:
                    del attributes_copy[field]
                resolved_attributes = attributes_copy
            else:
                resolved_attributes = self.resolve_attributes()
            if resolved_attributes != dict():
                if self.is_revert() is False:
                    if (not self.parent.is_update() or
                            self.parent.is_updatable or
                            not writer.does_object_exist(context)):
                        writer.set_values(context, **resolved_attributes)
                else:
                    writer.unset_values(context, **resolved_attributes)

    def resolve_attributes(self):
        attributes_copy = dict()
        for key, value in self.attributes.iteritems():
            if isinstance(value, Action):
                resolved_value = value.get_stored_value()
            elif (type(value) == list and
                    len(value) > 0 and
                    isinstance(value[0], Action)):
                resolved_list = list()
                for item in value:
                    resolved_item = item.get_stored_value()
                    resolved_list.append(resolved_item)
                resolved_value = resolved_list
            else:
                resolved_value = value

            if "." in key:
                obj_name, param = key.split(".")
                if obj_name not in attributes_copy:
                    if obj_name not in self.attributes:
                        raise ConflictError("Field '%s' of object %s"
                                            " is not set" %
                                            (str(obj_name),
                                             str(self.parent.object_type)))
                    if type(self.attributes[obj_name]) is not dict:
                        raise ConflictError("Field '%s' of object %s"
                                            " is not a dictionary" %
                                            (str(obj_name),
                                             str(self.parent.object_type)))

                    attributes_copy[obj_name] = dict(self.attributes[obj_name])

                if param in attributes_copy[obj_name]:
                    raise ConflictError("Param '%s' in field '%s' of object %s"
                                        " is already set" %
                                        (str(param),
                                         str(obj_name),
                                         str(self.parent.object_type)))
                attributes_copy[obj_name][param] = resolved_value
            elif key.lower().startswith(DEPENDENCY_ONLY):
                pass
            else:
                if (type(resolved_value) is not dict or
                        key not in attributes_copy):
                    attributes_copy[key] = resolved_value

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
            elif (type(value) == list and
                    len(value) > 0 and
                    isinstance(value[0], Action)):
                value = "[" + ", ".join(
                    ["retrieve %s" %
                     x._get_reference_string() for x in value]) + "]"

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

        self.mark_ancestors_for_reorder(self, is_store=True)

    def get_stored_value(self):
        if self.stored_value is not None:
            return self.stored_value
        else:
            raise TemplateActionError("No value stored as name %s" %
                                      self.as_name)

    def execute(self, writer, context=None):
        if self.is_revert() is False or self.is_store_only():
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

        as_list = Action.get_dict_field(set_value_dict, 'as-list')
        if as_list is not None:
            self.as_list = as_list

        self.log.debug(self._get_location("Reading "))

        if self.parent is None or self.parent.parent is None:
            raise TemplateActionError("No object exists for retrieving values")

        if (type(self.state) != dict or
                'stored_values' not in self.state or
                self.from_name not in self.state['stored_values']):
            raise TemplateActionError(
                'No value of name %s stored to be retrieved' % self.from_name)

        stored_action = self.state['stored_values'][self.from_name]
        if self.as_list:
            self.append_list_attribute(self.to_field, stored_action)
        else:
            self.add_attribute(self.to_field, stored_action)
        self.mark_ancestors_for_reorder(stored_action, is_store=False)


class SaveToFileAction(Action):

    def __init__(self, parent, state):
        super(SaveToFileAction, self).__init__(parent, state)
        self.file_path = None
        self.from_field = None
        self.append_to_file = True
        self.prefix_string = None
        self.suffix_string = None
        self.write_to_console = False

    def read(self, save_to_file_dict):
        self.file_path = Action.get_dict_field(save_to_file_dict,
                                               'file-path')
        if self.file_path is None:
            raise TemplateParseError(
                "Save to file action missing required 'file-path' field")

        self.from_field = Action.get_dict_field(save_to_file_dict,
                                                'from-field')

        append_to_file = Action.get_dict_field(save_to_file_dict,
                                               'append-to-file')
        if append_to_file is not None:
            self.append_to_file = append_to_file

        self.prefix_string = Action.get_dict_field(save_to_file_dict,
                                                   'prefix-string')

        self.suffix_string = Action.get_dict_field(save_to_file_dict,
                                                   'suffix-string')

        self.write_to_console = Action.get_dict_field(save_to_file_dict,
                                                      'write-to-console')

        self.log.debug(self._get_location("Reading "))

        if self.parent is None or self.parent.parent is None:
            raise TemplateActionError("No object exists for saving values")

    def execute(self, writer, context=None):
        if self.is_revert() is False and not writer.is_validate_only():
            if self.from_field is not None:
                field_value = writer.get_value(self.from_field, context)

            file_mode = "w" if self.append_to_file is False else "a"
            console_text = ""
            with open(self.file_path, file_mode) as f:
                if self.prefix_string is not None:
                    console_text += self.prefix_string
                    f.write(self.prefix_string)
                if self.from_field is not None:
                    console_text += field_value
                    f.write(field_value)
                if self.suffix_string is not None:
                    console_text += self.suffix_string
                    f.write(self.suffix_string)

                if self.write_to_console:
                    self.log.output(console_text)

    def _to_string(self, indent_level):
        indent = Action._indent(indent_level)

        cur_output = "%s[save %s to file %s]" % (indent,
                                                 str(self.from_field),
                                                 str(self.file_path))
        return cur_output
