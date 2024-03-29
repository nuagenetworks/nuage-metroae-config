import os
import pytest

from tests.action_test_params import (CREATE_FIELD_RETRIEVE_VALUE,
                                      CREATE_OBJECTS_DICT,
                                      CREATE_OBJECTS_NO_TYPE,
                                      CREATE_OBJECTS_SELECT_FIRST,
                                      CREATE_OBJECTS_SELECT_LAST,
                                      FIND_NO_SELECT,
                                      FIND_SINGLE_LEVEL,
                                      FIND_TREE,
                                      INVALID_ACTION_1,
                                      INVALID_ACTION_2,
                                      INVALID_ACTION_3,
                                      ORDER_CREATE,
                                      ORDER_DISABLE_COMBINE_1,
                                      ORDER_DISABLE_COMBINE_2,
                                      ORDER_OVERRIDE_1,
                                      ORDER_OVERRIDE_2,
                                      ORDER_OVERRIDE_3,
                                      ORDER_MULTI_CREATE,
                                      ORDER_MULTI_SELECT_1,
                                      ORDER_MULTI_SELECT_2,
                                      ORDER_SELECT_1,
                                      ORDER_SELECT_2,
                                      ORDER_SELECT_CONFLICT1,
                                      ORDER_STORE_1,
                                      ORDER_STORE_2,
                                      ORDER_STORE_3,
                                      ORDER_STORE_4,
                                      ORDER_STORE_5,
                                      RETRIEVE_AS_LIST,
                                      RETRIEVE_BEFORE_STORE,
                                      RETRIEVE_CONFLICT_1,
                                      RETRIEVE_CONFLICT_2,
                                      RETRIEVE_DEPENDENCY_ONLY,
                                      RETRIEVE_NO_FIELD,
                                      RETRIEVE_NO_OBJECT,
                                      RETRIEVE_NO_NAME,
                                      SAVE_TO_FILE,
                                      SAVE_TO_FILE_AND_CONSOLE,
                                      SAVE_TO_FILE_APPEND,
                                      SAVE_TO_FILE_NO_FILE,
                                      SAVE_TO_FILE_DECODE,
                                      SELECT_MULTIPLE_MISSING,
                                      SELECT_MULTIPLE_SUCCESS_1,
                                      SELECT_MULTIPLE_SUCCESS_2,
                                      SELECT_MULTIPLE_REVERT_SUCCESS_1,
                                      SELECT_MULTIPLE_REVERT_SUCCESS_2,
                                      SELECT_OBJECTS_BY_POSITION_FIRST,
                                      SELECT_OBJECTS_BY_POSITION_LAST,
                                      SELECT_OBJECTS_BY_POSITION_OOB,
                                      SELECT_OBJECTS_DICT,
                                      SELECT_OBJECTS_MULTIPLE,
                                      SELECT_OBJECTS_MULTIPLE_BAD_TYPE,
                                      SELECT_OBJECTS_MULTIPLE_WITH_SINGLE,
                                      SELECT_OBJECTS_MULTIPLE_MISMATCH,
                                      SELECT_OBJECTS_NO_FIELD,
                                      SELECT_OBJECTS_NO_TYPE,
                                      SELECT_OBJECTS_NO_VALUE,
                                      SELECT_RETRIEVE_MISSING_RETRIEVE,
                                      SELECT_RETRIEVE_NOT_RETRIEVE,
                                      SELECT_RETRIEVE_VALUE,
                                      SET_VALUES_DICT,
                                      SET_VALUES_CONFLICT,
                                      SET_VALUES_NO_OBJECT,
                                      STORE_NO_FIELD,
                                      STORE_NO_OBJECT,
                                      STORE_NO_NAME,
                                      STORE_RETRIEVE_DICT,
                                      STORE_RETRIEVE_TO_OBJECT,
                                      STORE_RETRIEVE_TO_OBJECT_ALREADY_SET,
                                      SET_VALUES_FIELD_SAME_VALUE,
                                      SET_VALUES_FIELD_DIFFERENT_VALUE,
                                      STORE_RETRIEVE_TO_OBJECT_NOT_DICT,
                                      STORE_RETRIEVE_TO_OBJECT_NOT_SET,
                                      STORE_SAME_TWICE,
                                      UPDATE_CREATE_CHILD_OBJECT,
                                      UPDATE_CHILD_OBJECT_WITH_FIRST_SELECTOR,
                                      UPDATE_CHILD_OBJECT_WITH_LAST_SELECTOR,
                                      UPDATE_ROOT_OBJECT,
                                      UPDATE_ROOT_UPDATE_NOT_SUPPORTED_OBJECT,
                                      UPDATE_SELECT_ROOT_OBJECT)
from nuage_metroae_config.actions import Action
from nuage_metroae_config.errors import (ConflictError,
                                         InvalidAttributeError,
                                         InvalidObjectError,
                                         MissingSelectionError,
                                         TemplateActionError,
                                         TemplateParseError)
from .mock_writer import MockWriter
from .template_test_params import (EXPECTED_ACL_TEMPLATE,
                                   EXPECTED_DOMAIN_TEMPLATE,
                                   EXPECTED_ENTERPRISE_TEMPLATE)

CREATE_SELECT_ORDERING_CASES = [
    (ORDER_CREATE, ORDER_SELECT_1, ORDER_SELECT_2),
    (ORDER_CREATE, ORDER_SELECT_2, ORDER_SELECT_1),
    (ORDER_SELECT_1, ORDER_CREATE, ORDER_SELECT_2),
    (ORDER_SELECT_2, ORDER_CREATE, ORDER_SELECT_1),
    (ORDER_SELECT_1, ORDER_SELECT_2, ORDER_CREATE),
    (ORDER_SELECT_2, ORDER_SELECT_1, ORDER_CREATE)]

CREATE_SELECT_MULTI_ORDERING_CASES = [
    (ORDER_MULTI_CREATE, ORDER_MULTI_SELECT_1, ORDER_MULTI_SELECT_2),
    (ORDER_MULTI_CREATE, ORDER_MULTI_SELECT_2, ORDER_MULTI_SELECT_1),
    (ORDER_MULTI_SELECT_1, ORDER_MULTI_CREATE, ORDER_MULTI_SELECT_2),
    (ORDER_MULTI_SELECT_2, ORDER_MULTI_CREATE, ORDER_MULTI_SELECT_1),
    (ORDER_MULTI_SELECT_1, ORDER_MULTI_SELECT_2, ORDER_MULTI_CREATE),
    (ORDER_MULTI_SELECT_2, ORDER_MULTI_SELECT_1, ORDER_MULTI_CREATE)]

CREATE_CONFLICT_ORDERING_CASES = [
    (ORDER_CREATE, ORDER_SELECT_1, ORDER_CREATE),
    (ORDER_CREATE, ORDER_SELECT_2, ORDER_CREATE),
    (ORDER_SELECT_1, ORDER_CREATE, ORDER_CREATE),
    (ORDER_SELECT_2, ORDER_CREATE, ORDER_CREATE),
    (ORDER_CREATE, ORDER_CREATE, ORDER_SELECT_1),
    (ORDER_CREATE, ORDER_CREATE, ORDER_SELECT_2)]

ATTR_CONFLICT_ORDERING_CASES = [
    (ORDER_CREATE, ORDER_SELECT_1, ORDER_SELECT_CONFLICT1),
    (ORDER_SELECT_1, ORDER_SELECT_CONFLICT1, ORDER_CREATE),
    (ORDER_SELECT_1, ORDER_CREATE, ORDER_SELECT_CONFLICT1),
    (ORDER_SELECT_2, ORDER_SELECT_CONFLICT1, ORDER_SELECT_1),
    (ORDER_SELECT_1, ORDER_SELECT_CONFLICT1, ORDER_SELECT_2),
    (ORDER_SELECT_1, ORDER_SELECT_2, ORDER_SELECT_CONFLICT1)]

STORE_ORDERING_CASES = [
    (ORDER_STORE_1, ORDER_STORE_2, ORDER_STORE_3),
    (ORDER_STORE_1, ORDER_STORE_3, ORDER_STORE_2),
    (ORDER_STORE_2, ORDER_STORE_1, ORDER_STORE_3),
    (ORDER_STORE_3, ORDER_STORE_1, ORDER_STORE_2),
    (ORDER_STORE_2, ORDER_STORE_3, ORDER_STORE_1),
    (ORDER_STORE_3, ORDER_STORE_2, ORDER_STORE_1)]

OVERRIDE_ORDERING_CASES = [
    (ORDER_OVERRIDE_1, ORDER_OVERRIDE_2, ORDER_OVERRIDE_3),
    (ORDER_OVERRIDE_1, ORDER_OVERRIDE_3, ORDER_OVERRIDE_2),
    (ORDER_OVERRIDE_2, ORDER_OVERRIDE_1, ORDER_OVERRIDE_3),
    (ORDER_OVERRIDE_3, ORDER_OVERRIDE_1, ORDER_OVERRIDE_2),
    (ORDER_OVERRIDE_2, ORDER_OVERRIDE_3, ORDER_OVERRIDE_1),
    (ORDER_OVERRIDE_3, ORDER_OVERRIDE_2, ORDER_OVERRIDE_1)]


class TestActionsRead(object):

    def test_enterprise__success(self):
        root_action = Action(None)

        root_action.read_children_actions(EXPECTED_ENTERPRISE_TEMPLATE)

        current_action = root_action.children[0]
        assert current_action.object_type == "Enterprise"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[0].children[0]
        assert current_action.attributes == {'name': 'test_enterprise'}

    def test_domain__success(self):
        root_action = Action(None)

        root_action.read_children_actions(EXPECTED_DOMAIN_TEMPLATE)

        current_action = root_action.children[0]
        assert current_action.object_type == "Enterprise"
        assert current_action.field == "name"
        assert current_action.value == "test_enterprise"

        current_action = root_action.children[0].children[0]
        assert current_action.object_type == "DomainTemplate"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[0].children[0].children[0]
        assert current_action.attributes == {'name': 'template_test_domain'}

        current_action = root_action.children[0].children[0].children[1]
        store_id = current_action
        assert current_action.from_field == "id"
        assert current_action.as_name == "domain_template_id"

        current_action = root_action.children[0].children[1]
        assert current_action.object_type == "Domain"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[0].children[1].children[0]
        assert current_action.attributes == {'name': 'test_domain',
                                             'templateID': store_id}

        current_action = root_action.children[0].children[1]
        assert current_action.is_updatable is False

    def test_acl__success(self):
        root_action = Action(None)

        root_action.read_children_actions(EXPECTED_ACL_TEMPLATE)

        current_action = root_action.children[0]
        assert current_action.object_type == "Enterprise"
        assert current_action.field == "name"
        assert current_action.value == "test_enterprise"

        current_action = root_action.children[0].children[0]
        assert current_action.object_type == "Domain"
        assert current_action.field == "name"
        assert current_action.value == "test_domain"

        current_action = root_action.children[0].children[0].children[0]
        assert current_action.object_type == "Subnet"
        assert current_action.field == "name"
        assert current_action.value == "test_subnet"

        current_action = \
            root_action.children[0].children[0].children[0].children[0]
        store_location_id = current_action
        assert current_action.from_field == "id"
        assert current_action.as_name == "location_id"

        current_action = root_action.children[0].children[0].children[1]
        assert current_action.object_type == "IngressACLTemplate"
        assert current_action.select_by_field == "name"

        current_action = \
            root_action.children[0].children[0].children[1].children[0]
        assert current_action.attributes == {'priority': 100,
                                             'allowAddressSpoof': False,
                                             'defaultAllowIP': True,
                                             'defaultAllowNonIP': False,
                                             'name': 'test_acl'}

        current_action = \
            root_action.children[0].children[0].children[1].children[1]
        assert current_action.object_type == "IngressACLEntryTemplate"
        assert current_action.select_by_field == "name"

        current_action = \
            root_action.children[0].children[0].children[1].children[1]\
            .children[0]
        assert current_action.attributes == {'priority': 200,
                                             'protocol': 'tcp',
                                             'description': 'Test ACL',
                                             'etherType': '0x0800',
                                             'statsLoggingEnabled': True,
                                             'DSCP': '*',
                                             'stateful': True,
                                             'sourcePort': 80,
                                             'destinationPort': '*',
                                             'locationType': 'SUBNET',
                                             'action': 'FORWARD',
                                             'networkType': 'ANY',
                                             'flowLoggingEnabled': True,
                                             'locationID': store_location_id,
                                             'networkID': ''}

        current_action = root_action.children[0].children[0].children[2]
        assert current_action.object_type == "EgressACLTemplate"
        assert current_action.select_by_field == "name"

        current_action = \
            root_action.children[0].children[0].children[2].children[0]
        assert current_action.attributes == {'priority': 100,
                                             'defaultInstallACLImplicitRules':
                                             True,
                                             'defaultAllowIP': True,
                                             'defaultAllowNonIP': False,
                                             'name': 'test_acl'}

        current_action = \
            root_action.children[0].children[0].children[2].children[1]
        assert current_action.object_type == "EgressACLEntryTemplate"
        assert current_action.select_by_field == "name"

        current_action = \
            root_action.children[0].children[0].children[2].children[1]\
            .children[0]
        assert current_action.attributes == {'priority': 200,
                                             'protocol': 'tcp',
                                             'description': 'Test ACL',
                                             'etherType': '0x0800',
                                             'statsLoggingEnabled': True,
                                             'DSCP': '*',
                                             'stateful': True,
                                             'sourcePort': 80,
                                             'destinationPort': '*',
                                             'locationType': 'SUBNET',
                                             'action': 'FORWARD',
                                             'networkType': 'ANY',
                                             'flowLoggingEnabled': True,
                                             'locationID': store_location_id,
                                             'networkID': ''}

    def test__invalid_action(self):
        root_action = Action(None)

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(INVALID_ACTION_1)

        assert "Invalid action" in str(e)

        assert "In Enterprise" in e.value.get_display_string()

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(INVALID_ACTION_2)

        assert "Invalid action" in str(e)

        assert "In Enterprise" in e.value.get_display_string()

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(INVALID_ACTION_3)

        assert "Invalid action" in str(e)

        assert "In Enterprise" in e.value.get_display_string()

    def test_create__success(self):
        root_action = Action(None)

        root_action.read_children_actions(CREATE_OBJECTS_DICT)

        current_action = root_action.children[0]
        assert current_action.object_type == "Enterprise"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[0].children[0]
        assert current_action.object_type == "DomainTemplate"
        assert current_action.select_by_field == "test_select_1"

        current_action = root_action.children[0].children[1]
        assert current_action.object_type == "Domain"
        assert current_action.select_by_field == "test_select_2"

        current_action = root_action.children[1]
        assert current_action.object_type == "Enterprise"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[1].children[0]
        assert current_action.object_type == "DomainTemplate"
        assert current_action.select_by_field == "test_select_3"

        current_action = root_action.children[1].children[1]
        assert current_action.object_type == "Domain"
        assert current_action.select_by_field == "test_select_4"

    def test_create__invalid(self):
        root_action = Action(None)

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(CREATE_OBJECTS_NO_TYPE)

        assert "missing required 'type' field" in str(e)

        assert "In None" in e.value.get_display_string()

    def test_select__success(self):
        root_action = Action(None)

        root_action.read_children_actions(SELECT_OBJECTS_DICT)

        current_action = root_action.children[0]
        assert current_action.object_type == "Enterprise"
        assert current_action.field == "name"
        assert current_action.value == "test_enterprise"

        current_action = root_action.children[0].children[0]
        assert current_action.object_type == "DomainTemplate"
        assert current_action.field == "test_field_1"
        assert current_action.value == "test_value_1"

        current_action = root_action.children[0].children[1]
        assert current_action.object_type == "Domain"
        assert current_action.field == "test_field_2"
        assert current_action.value == "test_value_2"

        current_action = root_action.children[1]
        assert current_action.object_type == "Enterprise"
        assert current_action.field == "name"
        assert current_action.value == "test_enterprise_2"

        current_action = root_action.children[1].children[0]
        assert current_action.object_type == "DomainTemplate"
        assert current_action.field == "test_field_3"
        assert current_action.value == "test_value_3"

        current_action = root_action.children[1].children[1]
        assert current_action.object_type == "Domain"
        assert current_action.field == "test_field_4"
        assert current_action.value == "test_value_4"

    def test_select_multiple__success(self):
        root_action = Action(None)

        root_action.read_children_actions(SELECT_OBJECTS_MULTIPLE)

        current_action = root_action.children[0]
        assert current_action.object_type == "Enterprise"
        assert current_action.field == ["name", "count"]
        assert current_action.value == ["enterprise1", 5]

        root_action.read_children_actions(SELECT_OBJECTS_MULTIPLE_WITH_SINGLE)

        current_action = root_action.children[1]
        assert current_action.object_type == "Enterprise"
        assert current_action.field == "name"
        assert current_action.value == "enterprise1"

    def test_select_multiple__invalid(self):
        root_action = Action(None)

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(SELECT_OBJECTS_MULTIPLE_MISMATCH)

        assert "different length" in str(e)

        assert ("In [select Enterprise (name of enterprise1, count of 5)]" in
                e.value.get_display_string())

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(SELECT_OBJECTS_MULTIPLE_BAD_TYPE)

        assert "must be a list" in str(e)

        assert ("In [select Enterprise (['name'] of 5)]" in
                e.value.get_display_string())

    def test_select__invalid(self):
        root_action = Action(None)

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(SELECT_OBJECTS_NO_TYPE)

        assert "missing required 'type' field" in str(e)

        assert ("In [select None (None of None)]" in
                e.value.get_display_string())

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(SELECT_OBJECTS_NO_FIELD)

        assert "missing required 'by-field' field" in str(e)

        assert ("In [select Enterprise (None of None)]" in
                e.value.get_display_string())

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(SELECT_OBJECTS_NO_VALUE)

        assert "missing required 'value' field" in str(e)

        assert ("In [select Enterprise (name of None)]" in
                e.value.get_display_string())

    def test_set_values__success(self):
        root_action = Action(None)

        root_action.read_children_actions(SET_VALUES_DICT)

        current_action = root_action.children[0]
        assert current_action.object_type == "Enterprise"

        # The set-values is always pushed to the front of the children
        # list and combined into a single action.  Also, fields set to None
        # are stripped.
        current_action = root_action.children[0].children[0]
        assert current_action.attributes == {"field1": "value1",
                                             "field2": True,
                                             "field4": 4}

        # Ensure create-object actions are pushed after set-values preserving
        # their order.
        current_action = root_action.children[0].children[1]
        assert current_action.object_type == "DomainTemplate"

        current_action = root_action.children[0].children[2]
        assert current_action.object_type == "Domain"

    def test_set_values__invalid(self):
        root_action = Action(None)

        with pytest.raises(TemplateActionError) as e:
            root_action.read_children_actions(SET_VALUES_NO_OBJECT)

        assert "No object exists" in str(e)

        assert "In [set values]" in e.value.get_display_string()

        with pytest.raises(ConflictError) as e:
            root_action.read_children_actions(SET_VALUES_CONFLICT)

        assert "already set" in str(e)
        assert "field2" in str(e)
        assert "Enterprise" in str(e)
        assert "'False'" in str(e)
        assert "'True'" in str(e)

        assert "In Enterprise" in e.value.get_display_string()
        assert "In [set values]" in e.value.get_display_string()

    def test_store_retrieve__success(self):
        root_action = Action(None)

        root_action.read_children_actions(STORE_RETRIEVE_DICT)

        current_action = root_action.children[0]
        assert current_action.object_type == "Enterprise"

        current_action = root_action.children[0].children[1]
        assert current_action.object_type == "DomainTemplate"

        # The set-values is always pushed to the front of the children
        # list and combined into a single action.  Also, fields set to None
        # are stripped.
        current_action = root_action.children[0].children[1].children[0]
        assert current_action.attributes == {"name": "domain_template"}

        current_action = root_action.children[0].children[1].children[1]
        store_action = current_action
        assert current_action.from_field == "id"
        assert current_action.as_name == "template_id"

        current_action = root_action.children[0].children[2]
        assert current_action.object_type == "Domain"

        # The set-values is always pushed to the front of the children
        # list and combined into a single action.  The retrieve action is
        # also combined into the single set-values
        current_action = root_action.children[0].children[2].children[0]
        assert current_action.attributes == {"name": "domain1",
                                             "templateID": store_action}

        current_action = root_action.children[0].children[3]
        assert current_action.object_type == "Domain"

        # The set-values is always pushed to the front of the children
        # list and combined into a single action.  The retrieve action is
        # also combined into the single set-values
        current_action = root_action.children[0].children[3].children[0]
        assert current_action.attributes == {"name": "domain2",
                                             "templateID": store_action}

    def test_store_retrieve__invalid(self):
        root_action = Action(None)

        root_action.reset_state()
        with pytest.raises(TemplateActionError) as e:
            root_action.read_children_actions(STORE_NO_OBJECT)

        assert "No object exists" in str(e)

        assert ("In [store id to name template_id]" in
                e.value.get_display_string())

        root_action.reset_state()
        with pytest.raises(TemplateActionError) as e:
            root_action.read_children_actions(RETRIEVE_NO_OBJECT)

        assert "No object exists" in str(e)

        assert "In [set values]" in e.value.get_display_string()

        root_action.reset_state()
        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(STORE_NO_FIELD)

        assert "missing required 'from-field' field" in str(e)

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()
        assert "In [store None to name None]" in e.value.get_display_string()

        root_action.reset_state()
        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(RETRIEVE_NO_FIELD)

        assert "missing required 'to-field' field" in str(e)

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()
        assert "In [set values]" in e.value.get_display_string()

        root_action.reset_state()
        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(STORE_NO_NAME)

        assert "missing required 'as-name' field" in str(e)

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()
        assert "In [store id to name None]" in e.value.get_display_string()

        root_action.reset_state()
        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(RETRIEVE_NO_NAME)

        assert "missing required 'from-name' field" in str(e)

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()
        assert "In [set values]" in e.value.get_display_string()

        root_action.reset_state()
        with pytest.raises(TemplateActionError) as e:
            root_action.read_children_actions(RETRIEVE_BEFORE_STORE)

        assert "No value" in str(e)
        assert "template_id" in str(e)

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()
        assert "In [set values]" in e.value.get_display_string()

        root_action.reset_state()
        with pytest.raises(TemplateActionError) as e:
            root_action.read_children_actions(STORE_SAME_TWICE)

        assert "already stored" in str(e)
        assert "template_id" in str(e)

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()
        assert ("In [store templateID to name template_id]" in
                e.value.get_display_string())

        root_action.reset_state()
        with pytest.raises(ConflictError) as e:
            root_action.read_children_actions(RETRIEVE_CONFLICT_1)

        assert "already set" in str(e)
        assert "templateID" in str(e)
        assert "Domain" in str(e)
        assert "'id1'" in str(e)
        assert "template_id" in str(e)

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()
        assert "In [set values]" in e.value.get_display_string()

        root_action.reset_state()
        with pytest.raises(ConflictError) as e:
            root_action.read_children_actions(RETRIEVE_CONFLICT_2)

        assert "already set" in str(e)
        assert "templateid" in str(e)
        assert "Domain" in str(e)
        assert "'id1'" in str(e)
        assert "template_id" in str(e)

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()
        assert "In [set values]" in e.value.get_display_string()

    def test_save_to_file__success(self):
        root_action = Action(None)

        root_action.read_children_actions(SAVE_TO_FILE)

        current_action = root_action.children[0]
        assert current_action.object_type == "Job"

        current_action = root_action.children[0].children[1]
        assert current_action.file_path == "/tmp/pytest_save_to_file.txt"
        assert current_action.append_to_file is False
        assert current_action.from_field == "result"

    def test_save_to_file_and_console__success(self):
        root_action = Action(None)

        root_action.read_children_actions(SAVE_TO_FILE_AND_CONSOLE)

        current_action = root_action.children[0]
        assert current_action.object_type == "Job"

        current_action = root_action.children[0].children[1]
        assert current_action.file_path == "/tmp/pytest_save_to_file.txt"
        assert current_action.append_to_file is False
        assert current_action.from_field == "result"
        assert current_action.write_to_console is True

    def test_save_to_file__invalid(self):
        root_action = Action(None)

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(SAVE_TO_FILE_NO_FILE)

        assert "missing required 'file-path' field" in str(e)
        assert "In Job" in e.value.get_display_string()


class TestActionsOrdering(object):

    @pytest.mark.parametrize("read_order", CREATE_SELECT_ORDERING_CASES)
    def test_create_select__success(self, read_order):
        root_action = Action(None)

        for template in read_order:
            root_action.read_children_actions(template)

        root_action.reorder()

        current_action = root_action.children[0]
        assert current_action.object_type == "Level1"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[0].children[0]
        assert current_action.attributes == {'field1': 'value1',
                                             'field2': 'value2',
                                             'field3': 'value3',
                                             'name': 'L1-O1'}

        current_action = root_action.children[0].children[1]
        assert current_action.object_type == "Level2"
        assert current_action.select_by_field == "field1"

        current_action = root_action.children[0].children[1].children[0]
        assert current_action.attributes == {'field1': 'L2-O1'}

        current_action = root_action.children[0].children[2]
        assert current_action.object_type == "Level2"
        assert current_action.select_by_field == "field1"

        current_action = root_action.children[0].children[2].children[0]
        assert current_action.attributes == {'field1': 'L2-O2',
                                             'field2': 'value2'}

        current_action = root_action.children[0].children[2].children[1]
        assert current_action.object_type == "Level3"
        assert current_action.select_by_field == "field1"

        current_action = \
            root_action.children[0].children[2].children[1].children[0]
        assert current_action.attributes == {'field1': 'L3-O1'}

        current_action = root_action.children[0].children[3].children[0]
        assert current_action.attributes == {'field1': 'L2-O3',
                                             'field3': 'value3'}

        current_action = root_action.children[0].children[3].children[1]
        assert current_action.object_type == "Level3"
        assert current_action.select_by_field == "field1"

        current_action = \
            root_action.children[0].children[3].children[1].children[0]
        assert current_action.attributes == {'field1': 'L3-O2'}

        current_action = root_action.children[0].children[4]
        assert current_action.object_type == "Level2"
        assert current_action.select_by_field == "field1"

        current_action = root_action.children[0].children[4].children[0]
        assert current_action.attributes == {'field1': 'L2-O4'}

    @pytest.mark.parametrize("read_order", CREATE_SELECT_MULTI_ORDERING_CASES)
    def test_create_select_multi__success(self, read_order):
        root_action = Action(None)

        for template in read_order:
            root_action.read_children_actions(template)

        root_action.reorder()

        current_action = root_action.children[0]
        assert current_action.object_type == "Level1"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[0].children[0]
        assert current_action.attributes == {'field1': 'value1',
                                             'field2': 'value2',
                                             'field3': 'value3',
                                             'name': 'L1-O1'}

        current_action = root_action.children[0].children[1]
        assert current_action.object_type == "Level2"
        assert current_action.select_by_field == "field1"

        current_action = root_action.children[0].children[1].children[0]
        assert current_action.attributes == {'field1': 'L2-O1',
                                             'field2': 'value2'}

        current_action = root_action.children[0].children[2]
        assert current_action.object_type == "Level2"
        assert current_action.select_by_field == "field1"

        current_action = root_action.children[0].children[2].children[0]
        assert current_action.attributes == {'field1': 'L2-O2',
                                             'field2': 'value2',
                                             'field3': 'value3'}

        current_action = root_action.children[0].children[2].children[1]
        assert current_action.object_type == "Level3"
        assert current_action.select_by_field == "field1"

        current_action = \
            root_action.children[0].children[2].children[1].children[0]
        assert current_action.attributes == {'field1': 'L3-O1'}

        current_action = root_action.children[0].children[3].children[0]
        assert current_action.attributes == {'field1': 'L2-O3',
                                             'field2': 'value2',
                                             'field3': 'value3'}

        current_action = root_action.children[0].children[3].children[1]
        assert current_action.object_type == "Level3"
        assert current_action.select_by_field == "field1"

        current_action = \
            root_action.children[0].children[3].children[1].children[0]
        assert current_action.attributes == {'field1': 'L3-O2'}

        current_action = root_action.children[0].children[4]
        assert current_action.object_type == "Level2"
        assert current_action.select_by_field == "field1"

        current_action = root_action.children[0].children[4].children[0]
        assert current_action.attributes == {'field1': 'L2-O4'}

    @pytest.mark.parametrize("read_order", CREATE_CONFLICT_ORDERING_CASES)
    def test_create__conflict(self, read_order):
        root_action = Action(None)

        with pytest.raises(ConflictError) as e:
            for template in read_order:
                root_action.read_children_actions(template)

        root_action.reorder()

        assert "same object twice" in str(e)
        assert "Level1" in str(e)

        assert "In Level1" in e.value.get_display_string()

    @pytest.mark.parametrize("read_order", ATTR_CONFLICT_ORDERING_CASES)
    def test_attribute__conflict(self, read_order):
        root_action = Action(None)

        with pytest.raises(ConflictError) as e:
            for template in read_order:
                root_action.read_children_actions(template)

        root_action.reorder()

        assert "already set" in str(e)
        assert "Level1" in str(e)

        assert ("In [select Level1 (name of L1-O1)]" in
                e.value.get_display_string())
        assert "In [set values]" in e.value.get_display_string()

    @pytest.mark.parametrize("read_order", STORE_ORDERING_CASES)
    def test_store__success(self, read_order):
        root_action = Action(None)

        for template in read_order:
            root_action.reset_state()
            root_action.read_children_actions(template)

        root_action.reorder()

        current_action = root_action.children[0]
        assert current_action.object_type == "Level1"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[0].children[0]
        assert current_action.attributes == {'name': 'L1-O2'}

        current_action = root_action.children[0].children[1]
        assert current_action.object_type == "Level2"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[0].children[1].children[0]
        assert current_action.attributes == {'name': 'L2-O3'}

        current_action = root_action.children[0].children[1].children[1]
        store_action_1 = current_action
        assert current_action.as_name == 'store_1'
        assert current_action.from_field == 'field1'

        current_action = root_action.children[0].children[2]
        assert current_action.object_type == "Level2"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[0].children[2].children[0]
        assert current_action.attributes == {'name': 'L2-O2',
                                             'field1': store_action_1}

        current_action = root_action.children[0].children[2].children[1]
        store_action_2 = current_action
        assert current_action.as_name == 'store_1'
        assert current_action.from_field == 'field1'

        current_action = root_action.children[1]
        assert current_action.object_type == "Level1"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[1].children[1]
        assert current_action.object_type == "Level2"
        assert current_action.select_by_field == "name"

        current_action = root_action.children[1].children[1].children[0]
        assert current_action.attributes == {'name': 'L2-O1',
                                             'field1': store_action_2}

    def test_store_combine_reorder__success(self):
        root_action = Action(None)

        root_action.reset_state()
        root_action.read_children_actions(ORDER_STORE_4)

        root_action.reset_state()
        root_action.read_children_actions(ORDER_STORE_5)

        root_action.reorder()

        current_action = root_action.children[0]
        assert current_action.object_type == "Level1"
        assert current_action.field == "name"
        assert current_action.value == "L1-O2"

        current_action = root_action.children[0].children[0]
        store_action = current_action
        assert current_action.as_name == 'store_1'
        assert current_action.from_field == 'field1'

        current_action = root_action.children[1]
        assert current_action.object_type == "Level1"

        current_action = root_action.children[1].children[0]
        assert current_action.attributes == {'name': 'L1-O1'}

        current_action = root_action.children[1].children[1]
        assert current_action.object_type == "Level2"

        current_action = root_action.children[1].children[1].children[0]
        assert current_action.attributes == {'name': 'L2-O1',
                                             'field1': store_action}

    def test_disable_combine__success(self):
        root_action = Action(None)

        root_action.reset_state()
        root_action.read_children_actions(ORDER_DISABLE_COMBINE_1)

        root_action.read_children_actions(ORDER_DISABLE_COMBINE_2)

        root_action.reorder()

        current_action = root_action.children[0]
        assert current_action.object_type == "Level1"

        current_action = root_action.children[0].children[0]
        assert current_action.attributes == {'name': 'L1-O1'}

        current_action = root_action.children[1]
        assert current_action.object_type == "Level1"

        current_action = root_action.children[1].children[0]
        assert current_action.attributes == {'name': 'L1-O2'}

        current_action = root_action.children[2]
        assert current_action.object_type == "Level1"
        assert current_action.field == "name"
        assert current_action.value == "L1-O1"

    @pytest.mark.parametrize("read_order", OVERRIDE_ORDERING_CASES)
    def test_override__success(self, read_order):
        root_action = Action(None)

        for template in read_order:
            root_action.read_children_actions(template)

        root_action.reorder_orders()

        for i in range(9):

            current_action = root_action.children[i]
            assert current_action.value == "L1-O" + str(i + 1)

            current_action = root_action.children[i].children[0]
            assert current_action.value == "L2-O" + str(i + 1)


class TestActionsExecute(object):

    def run_execute_test(self, template_dict, expected_actions,
                         is_revert=False, is_update=False,
                         return_empty_select_list=False,
                         encode=False):
        root_action = Action(None)
        writer = MockWriter()
        writer.set_return_empty_select_list(return_empty_select_list)
        writer.encode_data(encode)

        root_action.set_revert(is_revert)
        root_action.set_update(is_update)
        root_action.read_children_actions(template_dict)
        writer.start_session()
        root_action.execute(writer)
        writer.stop_session()

        expected_actions_formatted = [_f for _f in [x.strip() for x in expected_actions.split("\n")] if _f]

        print("\nExpected actions:")
        print("\n".join(expected_actions_formatted))

        print("\nRecorded actions:")
        print("\n".join(writer.get_recorded_actions()))

        assert writer.get_recorded_actions() == expected_actions_formatted

    def run_execute_with_exception(self, template_dict, expected_actions,
                                   exception, on_action, expect_error=True,
                                   is_revert=False, is_update=False,
                                   return_empty_select_list=False):
        root_action = Action(None)
        writer = MockWriter()
        writer.raise_exception(exception, on_action)
        writer.set_return_empty_select_list(return_empty_select_list)

        root_action.set_revert(is_revert)
        root_action.set_update(is_update)
        root_action.read_children_actions(template_dict)
        writer.start_session()
        if expect_error:
            with pytest.raises(exception.__class__) as e:
                root_action.execute(writer)
        else:
            root_action.execute(writer)
        writer.stop_session()

        expected_actions_formatted = [_f for _f in [x.strip() for x in expected_actions.split("\n")] if _f]

        print("\nExpected actions:")
        print("\n".join(expected_actions_formatted))

        print("\nRecorded actions:")
        print("\n".join(writer.get_recorded_actions()))

        assert writer.get_recorded_actions() == expected_actions_formatted
        if expect_error:
            assert e.value == exception
            return e

    def test_enterprise__success(self):

        expected_actions = """
            start-session
            create-object Enterprise [None]
            set-values name=test_enterprise [context_1]
            stop-session
        """

        self.run_execute_test(EXPECTED_ENTERPRISE_TEMPLATE,
                              expected_actions)

    def test_enterprise__revert(self):

        expected_actions = """
            start-session
            select-object Enterprise name = test_enterprise [None]
            select-object Enterprise name = test_enterprise [None]
            unset-values name=test_enterprise [context_2]
            delete-object [context_2]
            stop-session
        """

        self.run_execute_test(EXPECTED_ENTERPRISE_TEMPLATE,
                              expected_actions, is_revert=True)

    def test_domain__success(self):

        expected_actions = """
            start-session
            select-object Enterprise name = test_enterprise [None]
            create-object DomainTemplate [context_1]
            set-values name=template_test_domain [context_2]
            get-value id [context_2]
            create-object Domain [context_1]
            set-values name=test_domain,templateID=value_1 [context_4]
            stop-session
        """

        self.run_execute_test(EXPECTED_DOMAIN_TEMPLATE,
                              expected_actions)

    def test_domain__revert(self):

        expected_actions = """
            start-session
            select-object Enterprise name = test_enterprise [None]
            select-object DomainTemplate name = template_test_domain [context_1]
            get-value id [context_2]
            select-object Domain name = test_domain [context_1]
            select-object Enterprise name = test_enterprise [None]
            select-object Domain name = test_domain [context_4]
            unset-values name=test_domain,templateID=value_1 [context_5]
            delete-object [context_5]
            select-object DomainTemplate name = template_test_domain [context_4]
            unset-values name=template_test_domain [context_8]
            delete-object [context_8]
            stop-session
        """

        self.run_execute_test(EXPECTED_DOMAIN_TEMPLATE,
                              expected_actions, is_revert=True)

    def test_acl__success(self):

        expected_actions = """
            start-session
            select-object Enterprise name = test_enterprise [None]
            select-object Domain name = test_domain [context_1]
            select-object Subnet name = test_subnet [context_2]
            get-value id [context_3]
            create-object IngressACLTemplate [context_2]
            set-values allowAddressSpoof=False,defaultAllowIP=True,defaultAllowNonIP=False,name=test_acl,priority=100 [context_4]
            create-object IngressACLEntryTemplate [context_4]
            set-values DSCP=*,action=FORWARD,description=Test ACL,destinationPort=*,etherType=0x0800,flowLoggingEnabled=True,locationID=value_1,locationType=SUBNET,networkID=,networkType=ANY,priority=200,protocol=tcp,sourcePort=80,stateful=True,statsLoggingEnabled=True [context_6]
            create-object EgressACLTemplate [context_2]
            set-values defaultAllowIP=True,defaultAllowNonIP=False,defaultInstallACLImplicitRules=True,name=test_acl,priority=100 [context_8]
            create-object EgressACLEntryTemplate [context_8]
            set-values DSCP=*,action=FORWARD,description=Test ACL,destinationPort=*,etherType=0x0800,flowLoggingEnabled=True,locationID=value_1,locationType=SUBNET,networkID=,networkType=ANY,priority=200,protocol=tcp,sourcePort=80,stateful=True,statsLoggingEnabled=True [context_10]
            stop-session
        """

        self.run_execute_test(EXPECTED_ACL_TEMPLATE,
                              expected_actions)

    def test_acl__revert(self):

        expected_actions = """
            start-session
            select-object Enterprise name = test_enterprise [None]
            select-object Domain name = test_domain [context_1]
            select-object Subnet name = test_subnet [context_2]
            get-value id [context_3]
            select-object IngressACLTemplate name = test_acl [context_2]
            select-object EgressACLTemplate name = test_acl [context_2]
            select-object Enterprise name = test_enterprise [None]
            select-object Domain name = test_domain [context_6]
            select-object EgressACLTemplate name = test_acl [context_7]
            unset-values defaultAllowIP=True,defaultAllowNonIP=False,defaultInstallACLImplicitRules=True,name=test_acl,priority=100 [context_8]
            delete-object [context_8]
            select-object IngressACLTemplate name = test_acl [context_7]
            unset-values allowAddressSpoof=False,defaultAllowIP=True,defaultAllowNonIP=False,name=test_acl,priority=100 [context_11]
            delete-object [context_11]
            select-object Subnet name = test_subnet [context_7]
            stop-session
        """

        self.run_execute_test(EXPECTED_ACL_TEMPLATE,
                              expected_actions, is_revert=True)

    def test_create__success(self):

        expected_actions = """
            start-session
            create-object Enterprise [None]
            create-object DomainTemplate [context_1]
            create-object Domain [context_1]
            create-object Enterprise [None]
            create-object DomainTemplate [context_4]
            create-object Domain [context_4]
            stop-session
        """

        self.run_execute_test(CREATE_OBJECTS_DICT,
                              expected_actions)

    def test_create__revert(self):

        # There are no set-values in this template, so there are no name
        # fields to select and thus nothing to do
        expected_actions = """
            start-session
            stop-session
        """

        self.run_execute_test(CREATE_OBJECTS_DICT,
                              expected_actions, is_revert=True)

    def test_create__invalid_object(self):

        expected_actions = """
            start-session
            create-object Enterprise [None]
            create-object DomainTemplate [context_1]
            create-object Domain [context_1]
            create-object Enterprise [None]
            create-object DomainTemplate [context_4]
            create-object Domain [context_4]
            stop-session
        """

        e = self.run_execute_with_exception(
            CREATE_OBJECTS_DICT,
            expected_actions,
            InvalidObjectError("test exception"),
            'create-object Domain [context_4]')

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()

    def test_select__success(self):

        expected_actions = """
            start-session
            select-object Enterprise name = test_enterprise [None]
            select-object DomainTemplate test_field_1 = test_value_1 [context_1]
            select-object Domain test_field_2 = test_value_2 [context_1]
            select-object Enterprise name = test_enterprise_2 [None]
            select-object DomainTemplate test_field_3 = test_value_3 [context_4]
            select-object Domain test_field_4 = test_value_4 [context_4]
            stop-session
        """

        self.run_execute_test(SELECT_OBJECTS_DICT,
                              expected_actions)

    def test_select__revert(self):

        expected_actions = """
            start-session
            select-object Enterprise name = test_enterprise [None]
            select-object DomainTemplate test_field_1 = test_value_1 [context_1]
            select-object Domain test_field_2 = test_value_2 [context_1]
            select-object Enterprise name = test_enterprise_2 [None]
            select-object DomainTemplate test_field_3 = test_value_3 [context_4]
            select-object Domain test_field_4 = test_value_4 [context_4]
            select-object Enterprise name = test_enterprise_2 [None]
            select-object Domain test_field_4 = test_value_4 [context_7]
            select-object DomainTemplate test_field_3 = test_value_3 [context_7]
            select-object Enterprise name = test_enterprise [None]
            select-object Domain test_field_2 = test_value_2 [context_10]
            select-object DomainTemplate test_field_1 = test_value_1 [context_10]
            stop-session
        """

        self.run_execute_test(SELECT_OBJECTS_DICT,
                              expected_actions, is_revert=True)

    def test_select__missing_select(self):

        expected_actions = """
            start-session
            select-object Enterprise name = test_enterprise [None]
            select-object DomainTemplate test_field_1 = test_value_1 [context_1]
            select-object Domain test_field_2 = test_value_2 [context_1]
            select-object Enterprise name = test_enterprise_2 [None]
            select-object DomainTemplate test_field_3 = test_value_3 [context_4]
            select-object Domain test_field_4 = test_value_4 [context_4]
            stop-session
        """

        e = self.run_execute_with_exception(
            SELECT_OBJECTS_DICT,
            expected_actions,
            MissingSelectionError("test exception"),
            'select-object Domain test_field_4 = test_value_4 [context_4]')

        assert ("In [select Enterprise (name of test_enterprise_2)]" in
                e.value.get_display_string())
        assert ("In [select Domain (test_field_4 of test_value_4)]" in
                e.value.get_display_string())

    def test_set_values__success(self):

        expected_actions = """
            start-session
            create-object Enterprise [None]
            set-values field1=value1,field2=True,field4=4 [context_1]
            create-object DomainTemplate [context_1]
            create-object Domain [context_1]
            stop-session
        """

        self.run_execute_test(SET_VALUES_DICT,
                              expected_actions)

    def test_set_values__revert(self):

        expected_actions = """
            start-session
            select-object Enterprise field1 = value1 [None]
            select-object Enterprise field1 = value1 [None]
            unset-values field1=value1,field2=True,field4=4 [context_2]
            delete-object [context_2]
            stop-session
        """

        self.run_execute_test(SET_VALUES_DICT,
                              expected_actions, is_revert=True)

    def test_set_values__bad_attr(self):

        expected_actions = """
            start-session
            create-object Enterprise [None]
            set-values field1=value1,field2=True,field4=4 [context_1]
            stop-session
        """

        e = self.run_execute_with_exception(
            SET_VALUES_DICT,
            expected_actions,
            InvalidAttributeError("test exception"),
            'set-values field1=value1,field2=True,field4=4 [context_1]')

        assert "In Enterprise" in e.value.get_display_string()
        assert "[set values]" in e.value.get_display_string()

    def test_store_retrieve__success(self):

        expected_actions = """
            start-session
            create-object Enterprise [None]
            set-values name=enterprise1 [context_1]
            create-object DomainTemplate [context_1]
            set-values name=domain_template [context_3]
            get-value id [context_3]
            create-object Domain [context_1]
            set-values name=domain1,templateID=value_1 [context_5]
            create-object Domain [context_1]
            set-values name=domain2,templateID=value_1 [context_7]
            stop-session
        """

        self.run_execute_test(STORE_RETRIEVE_DICT,
                              expected_actions)

    def test_store_retrieve__revert(self):

        expected_actions = """
            start-session
            select-object Enterprise name = enterprise1 [None]
            select-object DomainTemplate name = domain_template [context_1]
            get-value id [context_2]
            select-object Domain name = domain1 [context_1]
            select-object Domain name = domain2 [context_1]
            select-object Enterprise name = enterprise1 [None]
            select-object Domain name = domain2 [context_5]
            unset-values name=domain2,templateID=value_1 [context_6]
            delete-object [context_6]
            select-object Domain name = domain1 [context_5]
            unset-values name=domain1,templateID=value_1 [context_9]
            delete-object [context_9]
            select-object DomainTemplate name = domain_template [context_5]
            unset-values name=domain_template [context_12]
            delete-object [context_12]
            unset-values name=enterprise1 [context_5]
            delete-object [context_5]
            stop-session
        """

        self.run_execute_test(STORE_RETRIEVE_DICT,
                              expected_actions, is_revert=True)

    def test_store_retrieve__bad_attr(self):

        expected_actions = """
            start-session
            create-object Enterprise [None]
            set-values name=enterprise1 [context_1]
            create-object DomainTemplate [context_1]
            set-values name=domain_template [context_3]
            get-value id [context_3]
            stop-session
        """

        e = self.run_execute_with_exception(
            STORE_RETRIEVE_DICT,
            expected_actions,
            InvalidAttributeError("test exception"),
            'get-value id [context_3]')

        assert "In Enterprise" in e.value.get_display_string()
        assert "In DomainTemplate" in e.value.get_display_string()
        assert ("In [store id to name template_id]" in
                e.value.get_display_string())

    def test_store_retrieve_to_object__success(self):

        expected_actions = """
            start-session
            create-object Enterprise [None]
            set-values name=enterprise1 [context_1]
            create-object NSGatewayTemplate [context_1]
            set-values name=nsg_template [context_3]
            get-value id [context_3]
            create-object Job [context_1]
            set-values parameters={'entityID': 'value_1', 'type': 'ISO'} [context_5]
            stop-session
        """

        self.run_execute_test(STORE_RETRIEVE_TO_OBJECT,
                              expected_actions)

    def test_store_retrieve_to_object__not_set(self):

        with pytest.raises(ConflictError) as e:
            self.run_execute_test(STORE_RETRIEVE_TO_OBJECT_NOT_SET, list())

        assert "is not set" in str(e)
        assert "parameters" in str(e)
        assert "Job" in str(e)

    def test_store_retrieve_to_object__not_dict(self):

        with pytest.raises(ConflictError) as e:
            self.run_execute_test(STORE_RETRIEVE_TO_OBJECT_NOT_DICT, list())

        assert "is not a dictionary" in str(e)
        assert "parameters" in str(e)
        assert "Job" in str(e)

    def test_store_retrieve_to_object__already_set(self):

        with pytest.raises(ConflictError) as e:
            self.run_execute_test(STORE_RETRIEVE_TO_OBJECT_ALREADY_SET, list())

        assert "is already set" in str(e)
        assert "parameters" in str(e)
        assert "Job" in str(e)

    def test_set_values_field__same_value(self):

        expected_actions = """
            start-session
            create-object Enterprise [None]
            set-values name=enterprise1 [context_1]
            create-object Infrastructure Access Profile [context_1]
            set-values name=access1,ssh_key_names=['key1'],ssh_keys=['japudofiuasdfoiudpfou'] [context_3]
            stop-session
        """
        self.run_execute_test(SET_VALUES_FIELD_SAME_VALUE,
                              expected_actions)

    def test_set_values_field__different_value(self):

        with pytest.raises(ConflictError) as e:
            self.run_execute_test(SET_VALUES_FIELD_DIFFERENT_VALUE,
                                  list())
        assert "is already set" in str(e)
        assert "ConflictError" in str(e)

    def test_create_objects_select_first__revert(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            select-object Level2 name = L2-O1 [context_1]
            get-object-list Level1 [None]
            select-object Level2 name = L2-O1 [context_4]
            unset-values name=L2-O1 [context_6]
            delete-object [context_6]
            delete-object [context_4]
            stop-session
        """

        self.run_execute_test(CREATE_OBJECTS_SELECT_FIRST,
                              expected_actions, is_revert=True)

    def test_create_objects_select_last__revert(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            select-object Level2 name = L2-O1 [context_2]
            get-object-list Level1 [None]
            select-object Level2 name = L2-O1 [context_5]
            unset-values name=L2-O1 [context_6]
            delete-object [context_6]
            delete-object [context_5]
            stop-session
        """

        self.run_execute_test(CREATE_OBJECTS_SELECT_LAST,
                              expected_actions, is_revert=True)

    def test_select_objects_by_position__first(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            create-object Level2 [context_1]
            set-values name=L2-O1 [context_3]
            stop-session
        """

        self.run_execute_test(SELECT_OBJECTS_BY_POSITION_FIRST,
                              expected_actions)

    def test_select_objects_by_position__last(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            create-object Level2 [context_2]
            set-values name=L2-O1 [context_3]
            stop-session
        """

        self.run_execute_test(SELECT_OBJECTS_BY_POSITION_LAST,
                              expected_actions)

    def test_select_objects_by_position__oob(self):

        with pytest.raises(MissingSelectionError) as e:
            self.run_execute_test(SELECT_OBJECTS_BY_POSITION_OOB, list())

        assert "No object present at position" in str(e)

    def test_retrieve_as_list__success(self):

        expected_actions = """
            start-session
            create-object Level1 [None]
            set-values name=L1-O1 [context_1]
            get-value name [context_1]
            create-object Level1 [None]
            set-values name=L1-O2 [context_3]
            get-value name [context_3]
            create-object Level1 [None]
            set-values field1=['value_1', 'value_2'],name=L1-O3 [context_5]
            stop-session
        """

        self.run_execute_test(RETRIEVE_AS_LIST,
                              expected_actions)

    def test_retrieve_depend_only__success(self):

        expected_actions = """
            start-session
            create-object Level1 [None]
            set-values name=L1-O1 [context_1]
            get-value name [context_1]
            create-object Level1 [None]
            set-values name=L1-O2 [context_3]
            stop-session
        """

        self.run_execute_test(RETRIEVE_DEPENDENCY_ONLY,
                              expected_actions)

    def test_find_single_level__success(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            select-object Find name = L2-O2 [context_1]
            create-object Level2 [context_1]
            set-values name=L2-O1 [context_4]
            select-object Find name = L2-O2 [context_1]
            stop-session
        """

        self.run_execute_test(FIND_SINGLE_LEVEL, expected_actions)

    def test_find_single_level__revert(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            select-object Find name = L2-O2 [context_1]
            select-object Level2 name = L2-O1 [context_1]
            select-object Find name = L2-O2 [context_1]
            get-object-list Level1 [None]
            select-object Find name = L2-O2 [context_6]
            select-object Find name = L2-O2 [context_6]
            select-object Level2 name = L2-O1 [context_6]
            unset-values name=L2-O1 [context_10]
            delete-object [context_10]
            stop-session
        """

        self.run_execute_test(FIND_SINGLE_LEVEL, expected_actions,
                              is_revert=True)

    def test_find_tree__success(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            get-object-list Level2 [context_1]
            select-object Find name = L3-O2 [context_3]
            get-object-list Level2 [context_1]
            select-object Find name = L3-O2 [context_6]
            create-object Level3 [context_6]
            set-values name=L3-O1 [context_9]
            select-object Find name = L3-O2 [context_6]
            stop-session
        """

        self.run_execute_test(FIND_TREE, expected_actions)

    def test_find_tree__revert(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            get-object-list Level2 [context_1]
            select-object Find name = L3-O2 [context_3]
            get-object-list Level2 [context_1]
            select-object Find name = L3-O2 [context_6]
            select-object Level3 name = L3-O1 [context_6]
            select-object Find name = L3-O2 [context_6]
            get-object-list Level1 [None]
            get-object-list Level2 [context_11]
            select-object Find name = L3-O2 [context_13]
            get-object-list Level2 [context_11]
            select-object Find name = L3-O2 [context_16]
            select-object Find name = L3-O2 [context_16]
            select-object Level3 name = L3-O1 [context_16]
            unset-values name=L3-O1 [context_20]
            delete-object [context_20]
            stop-session
        """

        self.run_execute_test(FIND_TREE, expected_actions, is_revert=True)

    def test_find_single_level__second_object(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            select-object Find name = L2-O2 [context_1]
            select-object Find name = L2-O2 [context_2]
            create-object Level2 [context_2]
            set-values name=L2-O1 [context_4]
            select-object Find name = L2-O2 [context_2]
            stop-session
        """

        self.run_execute_with_exception(
            FIND_SINGLE_LEVEL,
            expected_actions,
            MissingSelectionError("Not found"),
            'select-object Find name = L2-O2 [context_1]',
            expect_error=False)

    def test_find_single_level__second_object_revert(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            select-object Find name = L2-O2 [context_1]
            select-object Level2 name = L2-O1 [context_1]
            select-object Find name = L2-O2 [context_1]
            get-object-list Level1 [None]
            select-object Find name = L2-O2 [context_6]
            select-object Find name = L2-O2 [context_6]
            select-object Level2 name = L2-O1 [context_6]
            unset-values name=L2-O1 [context_10]
            delete-object [context_10]
            stop-session
        """

        self.run_execute_with_exception(
            FIND_SINGLE_LEVEL,
            expected_actions,
            MissingSelectionError("Not found"),
            'select-object Find name = L2-O2 [context_5]',
            expect_error=False,
            is_revert=True)

    def test_find_single_level__no_selector(self):

        with pytest.raises(MissingSelectionError) as e:
            self.run_execute_test(FIND_NO_SELECT, list())

        assert "No select-object" in str(e)

    def test_find_single_level__not_found(self):

        expected_actions = []

        with pytest.raises(MissingSelectionError) as e:
            self.run_execute_with_exception(
                FIND_SINGLE_LEVEL,
                expected_actions,
                MissingSelectionError("Not found"),
                'select-object Find name = L2-O2',
                expect_error=False)

        assert "Could not find matching child selection" in str(e)
        assert "Find" in str(e)

    def test_select_multiple__first_success(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            get-value field1 [context_1]
            get-value field2 [context_1]
            get-value field1 [context_2]
            get-value field2 [context_2]
            create-object Level2 [context_1]
            set-values name=L2-O1 [context_3]
            stop-session
        """

        self.run_execute_test(SELECT_MULTIPLE_SUCCESS_1, expected_actions)

    def test_select_multiple__first_revert_success(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            get-value field1 [context_1]
            get-value field2 [context_1]
            get-value field1 [context_2]
            get-value field2 [context_2]
            get-object-list Level1 [None]
            get-value field1 [context_3]
            get-value field2 [context_3]
            get-value field1 [context_4]
            get-value field2 [context_4]
            select-object Level2 name = L2-O1 [context_3]
            unset-values name=L2-O1 [context_5]
            delete-object [context_5]
            stop-session
        """

        self.run_execute_test(SELECT_MULTIPLE_REVERT_SUCCESS_1,
                              expected_actions,
                              is_revert=True)

    def test_select_multiple__last_success(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            get-value field1 [context_1]
            get-value field2 [context_1]
            get-value field1 [context_2]
            get-value field2 [context_2]
            create-object Level2 [context_2]
            set-values name=L2-O1 [context_3]
            stop-session
        """

        self.run_execute_test(SELECT_MULTIPLE_SUCCESS_2, expected_actions)

    def test_select_multiple__last_revert_success(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            get-value field1 [context_1]
            get-value field2 [context_1]
            get-value field1 [context_2]
            get-value field2 [context_2]
            get-object-list Level1 [None]
            get-value field1 [context_3]
            get-value field2 [context_3]
            get-value field1 [context_4]
            get-value field2 [context_4]
            select-object Level2 name = L2-O1 [context_4]
            unset-values name=L2-O1 [context_5]
            delete-object [context_5]
            stop-session
        """

        self.run_execute_test(SELECT_MULTIPLE_REVERT_SUCCESS_2,
                              expected_actions,
                              is_revert=True)

    def test_select_multiple__not_found(self):

        expected_actions = []

        with pytest.raises(MissingSelectionError) as e:
            self.run_execute_test(SELECT_MULTIPLE_MISSING, expected_actions)

        assert "No object matches selection criteria" in str(e)

    def test_select_multiple__revert_not_found(self):

        expected_actions = """
            start-session
            get-object-list Level1 [None]
            get-value field1 [context_1]
            get-value field2 [context_1]
            get-value field1 [context_2]
            get-value field2 [context_2]
            get-object-list Level1 [None]
            get-value field1 [context_3]
            get-value field2 [context_3]
            get-value field1 [context_4]
            get-value field2 [context_4]
            stop-session
        """

        self.run_execute_test(SELECT_MULTIPLE_MISSING, expected_actions,
                              is_revert=True)

    def test_select_retrieve__success(self):

        expected_actions = """
            start-session
            select-object Object1 name = value_1 [None]
            get-value objectId [context_1]
            select-object Object2 id = value_1 [None]
            create-object Level2 [context_2]
            set-values name=L2-O1 [context_3]
            stop-session
        """

        self.run_execute_test(SELECT_RETRIEVE_VALUE, expected_actions)

    def test_select_retrieve__revert(self):

        expected_actions = """
            start-session
            select-object Object1 name = value_1 [None]
            get-value objectId [context_1]
            select-object Object2 id = value_1 [None]
            select-object Level2 name = L2-O1 [context_2]
            select-object Object2 id = value_1 [None]
            select-object Level2 name = L2-O1 [context_4]
            unset-values name=L2-O1 [context_5]
            delete-object [context_5]
            select-object Object1 name = value_1 [None]
            stop-session
        """

        self.run_execute_test(SELECT_RETRIEVE_VALUE, expected_actions,
                              is_revert=True)

    def test_select_retrieve__missing_retrieve(self):

        expected_actions = []

        with pytest.raises(MissingSelectionError) as e:
            self.run_execute_test(SELECT_RETRIEVE_MISSING_RETRIEVE,
                                  expected_actions)

        assert "No retrieve-value present" in str(e)
        assert "WRONG_VALUE" in str(e)

    def test_select_retrieve__not_retrieve(self):

        expected_actions = []

        with pytest.raises(MissingSelectionError) as e:
            self.run_execute_test(SELECT_RETRIEVE_NOT_RETRIEVE,
                                  expected_actions)

        assert "Action not retrieve-value" in str(e)
        assert "id" in str(e)

    def test_create_field_retrieve__revert(self):

        expected_actions = """
            start-session
            select-object Object1 name = L1-O1 [None]
            select-object Object2 name = other_name [context_1]
            get-value objectId [context_2]
            select-object Object3 other_id = value_1 [None]
            select-object Level2 name = L2-O1 [context_3]
            unset-values name=L2-O1 [context_4]
            delete-object [context_4]
            unset-values other_id=value_1 [context_3]
            delete-object [context_3]
            select-object Object1 name = L1-O1 [None]
            select-object Object2 name = other_name [context_9]
            unset-values name=other_name [context_10]
            delete-object [context_10]
            unset-values name=L1-O1 [context_9]
            delete-object [context_9]
            stop-session
        """

        self.run_execute_test(CREATE_FIELD_RETRIEVE_VALUE, expected_actions,
                              is_revert=True)

    def test_save_to_file__success(self, capsys):

        TEST_FILE = "/tmp/pytest_save_to_file.txt"

        expected_actions = """
            start-session
            create-object Job [None]
            set-values command=GET_ZFB_INFO,parameters={'mediaType': 'ISO'} [context_1]
            get-value result [context_1]
            stop-session
        """

        with open(TEST_FILE, "w") as f:
            f.write("SHOULD GET OVERWRITTEN!!")

        self.run_execute_test(SAVE_TO_FILE, expected_actions)

        with open(TEST_FILE, "r") as f:
            assert f.read() == "value_1"

        output = capsys.readouterr()

        assert "value_1" in output.out

        os.remove(TEST_FILE)

    def test_save_to_file__append(self, capsys):

        TEST_FILE = "/tmp/pytest_save_to_file.txt"

        expected_actions = """
            start-session
            create-object Job [None]
            set-values command=GET_ZFB_INFO,parameters={'mediaType': 'ISO'} [context_1]
            get-value result [context_1]
            stop-session
        """

        with open(TEST_FILE, "w") as f:
            f.write("SHOULD BE PRESERVED")

        self.run_execute_test(SAVE_TO_FILE_APPEND, expected_actions)

        with open(TEST_FILE, "r") as f:
            assert f.read() == (
                "SHOULD BE PRESERVEDno::valueprefix:value_1:suffix")

        output = capsys.readouterr()

        assert "value_1" not in output.out

        os.remove(TEST_FILE)

    def test_save_to_file__decode(self, capsys):

        TEST_FILE = "/tmp/pytest_save_to_file.txt"

        expected_actions = """
            start-session
            create-object Job [None]
            set-values command=GET_ZFB_INFO,parameters={'mediaType': 'ISO'} [context_1]
            get-value result [context_1]
            stop-session
        """

        with open(TEST_FILE, "w") as f:
            f.write("SHOULD BE PRESERVED")

        self.run_execute_test(SAVE_TO_FILE_DECODE, expected_actions, encode=True)

        with open(TEST_FILE, "r") as f:
            assert f.read() == (
                "SHOULD BE PRESERVEDno::valueprefix:value_1:suffix")

        output = capsys.readouterr()

        assert "value_1" not in output.out

        os.remove(TEST_FILE)

    def test_update_action__no_new_objects(self):

        expected_actions = """
            start-session
            select-object Level1 name = L1-O1 [None]
            update-object Level1 name = L1-O1 [None]
            set-values name=L1-O1 [context_2]
            stop-session
        """

        self.run_execute_test(UPDATE_ROOT_OBJECT,
                              expected_actions,
                              is_update=True)

    def test_update_action__create_root_object(self):

        expected_actions = """
            start-session
            select-object Level1 name = L1-O1 [None]
            create-object Level1 [None]
            set-values name=L1-O1 [context_1]
            stop-session
        """

        self.run_execute_with_exception(UPDATE_ROOT_OBJECT,
                                        expected_actions,
                                        MissingSelectionError("test exception"),
                                        'select-object Level1 name = L1-O1 [None]',
                                        expect_error=False,
                                        is_update=True)

    def test_update_action__create_root_object_update_not_supported(self):

        expected_actions = """
            start-session
            select-object Level1 name = L1-O1 [None]
            create-object Level1 [None]
            set-values name=L1-O1 [context_1]
            get-value id [context_1]
            stop-session
        """

        self.run_execute_with_exception(UPDATE_ROOT_UPDATE_NOT_SUPPORTED_OBJECT,
                                        expected_actions,
                                        MissingSelectionError("test exception"),
                                        'select-object Level1 name = L1-O1 [None]',
                                        expect_error=False,
                                        is_update=True)

    def test_update_action__select_root_object(self):

        expected_actions = """
            start-session
            select-object Level1 name = L1-01 [None]
            set-values name=L1-O1 [context_1]
            get-value id [context_1]
            stop-session
        """

        self.run_execute_test(UPDATE_SELECT_ROOT_OBJECT,
                              expected_actions,
                              is_update=True)

    def test_update_action__update_child_object(self):

        expected_actions = """
            start-session
            select-object Level1 name = L1-O1 [None]
            update-object Level1 name = L1-O1 [None]
            set-values name=L1-O1 [context_2]
            select-object Level2 name = L2-O1 [context_2]
            update-object Level2 name = L2-O1 [context_2]
            set-values name=L2-O1 [context_5]
            stop-session
        """

        self.run_execute_test(UPDATE_CREATE_CHILD_OBJECT,
                              expected_actions,
                              is_update=True)

    def test_update_action__create_child_object(self):

        expected_actions = """
            start-session
            select-object Level1 name = L1-O1 [None]
            update-object Level1 name = L1-O1 [None]
            set-values name=L1-O1 [context_2]
            select-object Level2 name = L2-O1 [context_2]
            create-object Level2 [context_2]
            set-values name=L2-O1 [context_4]
            stop-session
        """

        self.run_execute_with_exception(UPDATE_CREATE_CHILD_OBJECT,
                                        expected_actions,
                                        MissingSelectionError("test exception"),
                                        'select-object Level2 name = L2-O1 [context_2]',
                                        expect_error=False,
                                        is_update=True)

    def test_update_action__update_child_with_first_selector(self):
        expected_actions = """
            start-session
            select-object Level1 name = L1-O1 [None]
            update-object Level1 name = L1-O1 [None]
            set-values name=L1-O1 [context_2]
            get-object-list Level2 [context_2]
            set-values value=L2 [context_4]
            stop-session
        """

        self.run_execute_test(UPDATE_CHILD_OBJECT_WITH_FIRST_SELECTOR,
                              expected_actions,
                              is_update=True)

    def test_update_action__update_child_with_last_selector(self):
        expected_actions = """
            start-session
            select-object Level1 name = L1-O1 [None]
            update-object Level1 name = L1-O1 [None]
            set-values name=L1-O1 [context_2]
            get-object-list Level2 [context_2]
            set-values value=L2 [context_5]
            stop-session
        """

        self.run_execute_test(UPDATE_CHILD_OBJECT_WITH_LAST_SELECTOR,
                              expected_actions,
                              is_update=True)

    def test_update_action__create_child_with_first_selector(self):
        expected_actions = """
            start-session
            select-object Level1 name = L1-O1 [None]
            update-object Level1 name = L1-O1 [None]
            set-values name=L1-O1 [context_2]
            get-object-list Level2 [context_2]
            select-object Level2 $first = None [context_2]
            create-object Level2 [context_2]
            set-values value=L2 [context_4]
            stop-session
        """

        self.run_execute_with_exception(UPDATE_CHILD_OBJECT_WITH_FIRST_SELECTOR,
                                        expected_actions,
                                        MissingSelectionError("test exception"),
                                        'select-object Level2 $first = None [context_2]',
                                        expect_error=False,
                                        is_update=True,
                                        return_empty_select_list=True)

    def test_update_action__create_child_with_last_selector(self):
        expected_actions = """
            start-session
            select-object Level1 name = L1-O1 [None]
            update-object Level1 name = L1-O1 [None]
            set-values name=L1-O1 [context_2]
            get-object-list Level2 [context_2]
            select-object Level2 $last = None [context_2]
            create-object Level2 [context_2]
            set-values value=L2 [context_4]
            stop-session
        """

        self.run_execute_with_exception(UPDATE_CHILD_OBJECT_WITH_LAST_SELECTOR,
                                        expected_actions,
                                        MissingSelectionError("test exception"),
                                        'select-object Level2 $last = None [context_2]',
                                        expect_error=False,
                                        is_update=True,
                                        return_empty_select_list=True)
