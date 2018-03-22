import pytest

from action_test_params import (CREATE_OBJECTS_DICT,
                                CREATE_OBJECTS_NO_TYPE,
                                INVALID_ACTION_1,
                                INVALID_ACTION_2,
                                INVALID_ACTION_3,
                                ORDER_CREATE,
                                ORDER_SELECT_1,
                                ORDER_SELECT_2,
                                ORDER_STORE_1,
                                ORDER_STORE_2,
                                ORDER_STORE_3,
                                RETRIEVE_CONFLICT_1,
                                RETRIEVE_CONFLICT_2,
                                RETRIEVE_BEFORE_STORE,
                                RETRIEVE_NO_FIELD,
                                RETRIEVE_NO_OBJECT,
                                RETRIEVE_NO_NAME,
                                SELECT_OBJECTS_DICT,
                                SELECT_OBJECTS_NO_FIELD,
                                SELECT_OBJECTS_NO_TYPE,
                                SELECT_OBJECTS_NO_VALUE,
                                SET_VALUES_DICT,
                                SET_VALUES_CONFLICT,
                                SET_VALUES_NO_OBJECT,
                                STORE_NO_FIELD,
                                STORE_NO_OBJECT,
                                STORE_NO_NAME,
                                STORE_RETRIEVE_DICT,
                                STORE_SAME_TWICE)
from levistate.actions import Action
from levistate.errors import (ConflictError,
                              InvalidAttributeError,
                              InvalidObjectError,
                              MissingSelectionError,
                              TemplateActionError,
                              TemplateParseError)
from mock_writer import MockWriter
from template_test_params import (EXPECTED_ACL_TEMPLATE,
                                  EXPECTED_DOMAIN_TEMPLATE,
                                  EXPECTED_ENTERPRISE_TEMPLATE)

CREATE_SELECT_ORDERING_CASES = [
    (ORDER_CREATE, ORDER_SELECT_1, ORDER_SELECT_2),
    (ORDER_CREATE, ORDER_SELECT_2, ORDER_SELECT_1),
    (ORDER_SELECT_1, ORDER_CREATE, ORDER_SELECT_2),
    (ORDER_SELECT_2, ORDER_CREATE, ORDER_SELECT_1),
    (ORDER_SELECT_1, ORDER_SELECT_2, ORDER_CREATE),
    (ORDER_SELECT_2, ORDER_SELECT_1, ORDER_CREATE)]

CREATE_CONFLICT_ORDERING_CASES = [
    (ORDER_CREATE, ORDER_SELECT_1, ORDER_CREATE),
    (ORDER_CREATE, ORDER_SELECT_2, ORDER_CREATE),
    (ORDER_SELECT_1, ORDER_CREATE, ORDER_CREATE),
    (ORDER_SELECT_2, ORDER_CREATE, ORDER_CREATE),
    (ORDER_CREATE, ORDER_CREATE, ORDER_SELECT_1),
    (ORDER_CREATE, ORDER_CREATE, ORDER_SELECT_2)]

ATTR_CONFLICT_ORDERING_CASES = [
    (ORDER_CREATE, ORDER_SELECT_1, ORDER_SELECT_1),
    (ORDER_SELECT_1, ORDER_SELECT_1, ORDER_CREATE),
    (ORDER_SELECT_1, ORDER_CREATE, ORDER_SELECT_1),
    (ORDER_SELECT_2, ORDER_SELECT_1, ORDER_SELECT_1),
    (ORDER_SELECT_1, ORDER_SELECT_1, ORDER_SELECT_2),
    (ORDER_SELECT_1, ORDER_SELECT_2, ORDER_SELECT_1)]

STORE_ORDERING_CASES = [
    (ORDER_STORE_1, ORDER_STORE_2, ORDER_STORE_3),
    (ORDER_STORE_1, ORDER_STORE_3, ORDER_STORE_2),
    (ORDER_STORE_2, ORDER_STORE_1, ORDER_STORE_3),
    (ORDER_STORE_3, ORDER_STORE_1, ORDER_STORE_2),
    (ORDER_STORE_2, ORDER_STORE_3, ORDER_STORE_1),
    (ORDER_STORE_3, ORDER_STORE_2, ORDER_STORE_1)]


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


class TestActionsOrdering(object):

    @pytest.mark.parametrize("read_order", CREATE_SELECT_ORDERING_CASES)
    def test_create_select__success(self, read_order):
        root_action = Action(None)

        for template in read_order:
            root_action.read_children_actions(template)

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

    @pytest.mark.parametrize("read_order", CREATE_CONFLICT_ORDERING_CASES)
    def test_create__conflict(self, read_order):
        root_action = Action(None)

        with pytest.raises(ConflictError) as e:
            for template in read_order:
                root_action.read_children_actions(template)

        assert "same object twice" in str(e)
        assert "Level1" in str(e)

        assert "In Level1" in e.value.get_display_string()

    @pytest.mark.parametrize("read_order", ATTR_CONFLICT_ORDERING_CASES)
    def test_attribute__conflict(self, read_order):
        root_action = Action(None)

        with pytest.raises(ConflictError) as e:
            for template in read_order:
                root_action.read_children_actions(template)

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


class TestActionsExecute(object):

    def run_execute_test(self, template_dict, expected_actions,
                         is_revert=False):
        root_action = Action(None)
        writer = MockWriter()

        root_action.set_revert(is_revert)
        root_action.read_children_actions(template_dict)
        writer.start_session()
        root_action.execute(writer)
        writer.stop_session()

        assert writer.get_recorded_actions() == expected_actions

    def run_execute_with_exception(self, template_dict, expected_actions,
                                   exception, on_action):
        root_action = Action(None)
        writer = MockWriter()
        writer.raise_exception(exception, on_action)

        root_action.read_children_actions(template_dict)
        writer.start_session()
        with pytest.raises(exception.__class__) as e:
            root_action.execute(writer)
        writer.stop_session()

        assert writer.get_recorded_actions() == expected_actions
        assert e.value == exception

        return e

    def test_enterprise__success(self):

        expected_actions = [
            'start-session',
            'create-object Enterprise [None]',
            'set-values name=test_enterprise [context_1]',
            'stop-session'
        ]

        self.run_execute_test(EXPECTED_ENTERPRISE_TEMPLATE,
                              expected_actions)

    def test_enterprise__revert(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise name = test_enterprise [None]',
            'delete-object [context_1]', 'stop-session']

        self.run_execute_test(EXPECTED_ENTERPRISE_TEMPLATE,
                              expected_actions, is_revert=True)

    def test_domain__success(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise name = test_enterprise [None]',
            'create-object DomainTemplate [context_1]',
            'set-values name=template_test_domain [context_2]',
            'get-value id [context_2]',
            'create-object Domain [context_1]',
            'set-values name=test_domain,templateID=value_1 [context_4]',
            'stop-session']

        self.run_execute_test(EXPECTED_DOMAIN_TEMPLATE,
                              expected_actions)

    def test_domain__revert(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise name = test_enterprise [None]',
            'select-object Domain name = test_domain [context_1]',
            'delete-object [context_2]',
            'select-object DomainTemplate name = template_test_domain '
            '[context_1]',
            'delete-object [context_4]',
            'stop-session']

        self.run_execute_test(EXPECTED_DOMAIN_TEMPLATE,
                              expected_actions, is_revert=True)

    def test_acl__success(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise name = test_enterprise [None]',
            'select-object Domain name = test_domain [context_1]',
            'select-object Subnet name = test_subnet [context_2]',
            'get-value id [context_3]',
            'create-object IngressACLTemplate [context_2]',
            'set-values allowAddressSpoof=False,defaultAllowIP=True,'
            'defaultAllowNonIP=False,name=test_acl,priority=100 [context_4]',
            'create-object IngressACLEntryTemplate [context_4]',
            'set-values DSCP=*,action=FORWARD,description=Test ACL,'
            'destinationPort=*,etherType=0x0800,flowLoggingEnabled=True,'
            'locationID=value_1,locationType=SUBNET,networkID=,networkType=ANY'
            ',priority=200,protocol=tcp,sourcePort=80,stateful=True,'
            'statsLoggingEnabled=True [context_6]',
            'create-object EgressACLTemplate [context_2]',
            'set-values defaultAllowIP=True,defaultAllowNonIP=False,'
            'defaultInstallACLImplicitRules=True,name=test_acl,priority=100 '
            '[context_8]',
            'create-object EgressACLEntryTemplate [context_8]',
            'set-values DSCP=*,action=FORWARD,description=Test ACL,'
            'destinationPort=*,etherType=0x0800,flowLoggingEnabled=True,'
            'locationID=value_1,locationType=SUBNET,networkID=,'
            'networkType=ANY,priority=200,protocol=tcp,sourcePort=80,'
            'stateful=True,statsLoggingEnabled=True [context_10]',
            'stop-session']

        self.run_execute_test(EXPECTED_ACL_TEMPLATE,
                              expected_actions)

    def test_acl__revert(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise name = test_enterprise [None]',
            'select-object Domain name = test_domain [context_1]',
            'select-object EgressACLTemplate name = test_acl [context_2]',
            'delete-object [context_3]',
            'select-object IngressACLTemplate name = test_acl [context_2]',
            'delete-object [context_5]',
            'select-object Subnet name = test_subnet [context_2]',
            'stop-session']

        self.run_execute_test(EXPECTED_ACL_TEMPLATE,
                              expected_actions, is_revert=True)

    def test_create__success(self):

        expected_actions = [
            'start-session',
            'create-object Enterprise [None]',
            'create-object DomainTemplate [context_1]',
            'create-object Domain [context_1]',
            'create-object Enterprise [None]',
            'create-object DomainTemplate [context_4]',
            'create-object Domain [context_4]',
            'stop-session']

        self.run_execute_test(CREATE_OBJECTS_DICT,
                              expected_actions)

    def test_create__revert(self):

        # There are no set-values in this template, so there are no name
        # fields to select and thus nothing to do
        expected_actions = [
            'start-session',
            'stop-session']

        self.run_execute_test(CREATE_OBJECTS_DICT,
                              expected_actions, is_revert=True)

    def test_create__invalid_object(self):

        expected_actions = [
            'start-session',
            'create-object Enterprise [None]',
            'create-object DomainTemplate [context_1]',
            'create-object Domain [context_1]',
            'create-object Enterprise [None]',
            'create-object DomainTemplate [context_4]',
            'create-object Domain [context_4]',
            'stop-session']

        e = self.run_execute_with_exception(
            CREATE_OBJECTS_DICT,
            expected_actions,
            InvalidObjectError("test exception"),
            'create-object Domain [context_4]')

        assert "In Enterprise" in e.value.get_display_string()
        assert "In Domain" in e.value.get_display_string()

    def test_select__success(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise name = test_enterprise [None]',
            'select-object DomainTemplate test_field_1 = test_value_1 '
            '[context_1]',
            'select-object Domain test_field_2 = test_value_2 [context_1]',
            'select-object Enterprise name = test_enterprise_2 [None]',
            'select-object DomainTemplate test_field_3 = test_value_3 '
            '[context_4]',
            'select-object Domain test_field_4 = test_value_4 [context_4]',
            'stop-session']

        self.run_execute_test(SELECT_OBJECTS_DICT,
                              expected_actions)

    def test_select__revert(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise name = test_enterprise_2 [None]',
            'select-object Domain test_field_4 = test_value_4 [context_1]',
            'select-object DomainTemplate test_field_3 = test_value_3 '
            '[context_1]',
            'select-object Enterprise name = test_enterprise [None]',
            'select-object Domain test_field_2 = test_value_2 [context_4]',
            'select-object DomainTemplate test_field_1 = test_value_1 '
            '[context_4]',
            'stop-session']

        self.run_execute_test(SELECT_OBJECTS_DICT,
                              expected_actions, is_revert=True)

    def test_select__missing_select(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise name = test_enterprise [None]',
            'select-object DomainTemplate test_field_1 = test_value_1 '
            '[context_1]',
            'select-object Domain test_field_2 = test_value_2 [context_1]',
            'select-object Enterprise name = test_enterprise_2 [None]',
            'select-object DomainTemplate test_field_3 = test_value_3 '
            '[context_4]',
            'select-object Domain test_field_4 = test_value_4 [context_4]',
            'stop-session']

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

        expected_actions = [
            'start-session',
            'create-object Enterprise [None]',
            'set-values field1=value1,field2=True,field4=4 [context_1]',
            'create-object DomainTemplate [context_1]',
            'create-object Domain [context_1]',
            'stop-session']

        self.run_execute_test(SET_VALUES_DICT,
                              expected_actions)

    def test_set_values__revert(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise field1 = value1 [None]',
            'delete-object [context_1]',
            'stop-session']

        self.run_execute_test(SET_VALUES_DICT,
                              expected_actions, is_revert=True)

    def test_set_values__bad_attr(self):

        expected_actions = [
            'start-session',
            'create-object Enterprise [None]',
            'set-values field1=value1,field2=True,field4=4 [context_1]',
            'stop-session']

        e = self.run_execute_with_exception(
            SET_VALUES_DICT,
            expected_actions,
            InvalidAttributeError("test exception"),
            'set-values field1=value1,field2=True,field4=4 [context_1]')

        assert "In Enterprise" in e.value.get_display_string()
        assert "[set values]" in e.value.get_display_string()

    def test_store_retrieve__success(self):

        expected_actions = [
            'start-session',
            'create-object Enterprise [None]',
            'set-values name=enterprise1 [context_1]',
            'create-object DomainTemplate [context_1]',
            'set-values name=domain_template [context_3]',
            'get-value id [context_3]',
            'create-object Domain [context_1]',
            'set-values name=domain1,templateID=value_1 [context_5]',
            'create-object Domain [context_1]',
            'set-values name=domain2,templateID=value_1 [context_7]',
            'stop-session']

        self.run_execute_test(STORE_RETRIEVE_DICT,
                              expected_actions)

    def test_store_retrieve__revert(self):

        expected_actions = [
            'start-session',
            'select-object Enterprise name = enterprise1 [None]',
            'select-object Domain name = domain2 [context_1]',
            'delete-object [context_2]',
            'select-object Domain name = domain1 [context_1]',
            'delete-object [context_4]',
            'select-object DomainTemplate name = domain_template [context_1]',
            'delete-object [context_6]',
            'delete-object [context_1]',
            'stop-session']

        self.run_execute_test(STORE_RETRIEVE_DICT,
                              expected_actions, is_revert=True)

    def test_store_retrieve__bad_attr(self):

        expected_actions = [
            'start-session',
            'create-object Enterprise [None]',
            'set-values name=enterprise1 [context_1]',
            'create-object DomainTemplate [context_1]',
            'set-values name=domain_template [context_3]',
            'get-value id [context_3]',
            'stop-session']

        e = self.run_execute_with_exception(
            STORE_RETRIEVE_DICT,
            expected_actions,
            InvalidAttributeError("test exception"),
            'get-value id [context_3]')

        assert "In Enterprise" in e.value.get_display_string()
        assert "In DomainTemplate" in e.value.get_display_string()
        assert ("In [store id to name template_id]" in
                e.value.get_display_string())
