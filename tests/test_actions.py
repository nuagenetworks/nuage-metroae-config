from mock import patch, MagicMock
import pytest

from action_test_params import (CREATE_OBJECTS_DICT,
                                CREATE_OBJECTS_NO_TYPE,
                                INVALID_ACTION_1,
                                INVALID_ACTION_2,
                                INVALID_ACTION_3,
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
from levistate.actions import (Action,
                               ConflictError,
                               TemplateActionError,
                               TemplateParseError)
from template_test_params import (EXPECTED_ACL_TEMPLATE,
                                  EXPECTED_DOMAIN_TEMPLATE,
                                  EXPECTED_ENTERPRISE_TEMPLATE)


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

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(INVALID_ACTION_2)

        assert "Invalid action" in str(e)

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(INVALID_ACTION_3)

        assert "Invalid action" in str(e)

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

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(SELECT_OBJECTS_NO_FIELD)

        assert "missing required 'by-field' field" in str(e)

        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(SELECT_OBJECTS_NO_VALUE)

        assert "missing required 'value' field" in str(e)

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

        with pytest.raises(ConflictError) as e:
            root_action.read_children_actions(SET_VALUES_CONFLICT)

        assert "already set" in str(e)
        assert "field2" in str(e)
        assert "Enterprise" in str(e)
        assert "'False'" in str(e)
        assert "'True'" in str(e)

    def test_store_retrieve__success(self):
        root_action = Action(None)

        root_action.read_children_actions(STORE_RETRIEVE_DICT)

        current_action = root_action.children[0]
        assert current_action.object_type == "Enterprise"

        current_action = root_action.children[0].children[0]
        assert current_action.object_type == "DomainTemplate"

        # The set-values is always pushed to the front of the children
        # list and combined into a single action.  Also, fields set to None
        # are stripped.
        current_action = root_action.children[0].children[0].children[0]
        assert current_action.attributes == {"name": "domain_template"}

        current_action = root_action.children[0].children[0].children[1]
        store_action = current_action
        assert current_action.from_field == "id"
        assert current_action.as_name == "template_id"

        current_action = root_action.children[0].children[1]
        assert current_action.object_type == "Domain"

        # The set-values is always pushed to the front of the children
        # list and combined into a single action.  The retrieve action is
        # also combined into the single set-values
        current_action = root_action.children[0].children[1].children[0]
        assert current_action.attributes == {"name": "domain1",
                                             "templateID": store_action}

        current_action = root_action.children[0].children[2]
        assert current_action.object_type == "Domain"

        # The set-values is always pushed to the front of the children
        # list and combined into a single action.  The retrieve action is
        # also combined into the single set-values
        current_action = root_action.children[0].children[2].children[0]
        assert current_action.attributes == {"name": "domain2",
                                             "templateID": store_action}

    def test_store_retrieve__invalid(self):
        root_action = Action(None)

        root_action.reset_state()
        with pytest.raises(TemplateActionError) as e:
            root_action.read_children_actions(STORE_NO_OBJECT)

        assert "No object exists" in str(e)

        root_action.reset_state()
        with pytest.raises(TemplateActionError) as e:
            root_action.read_children_actions(RETRIEVE_NO_OBJECT)

        assert "No object exists" in str(e)

        root_action.reset_state()
        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(STORE_NO_FIELD)

        assert "missing required 'from-field' field" in str(e)

        root_action.reset_state()
        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(RETRIEVE_NO_FIELD)

        assert "missing required 'to-field' field" in str(e)

        root_action.reset_state()
        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(STORE_NO_NAME)

        assert "missing required 'as-name' field" in str(e)

        root_action.reset_state()
        with pytest.raises(TemplateParseError) as e:
            root_action.read_children_actions(RETRIEVE_NO_NAME)

        assert "missing required 'from-name' field" in str(e)

        root_action.reset_state()
        with pytest.raises(TemplateActionError) as e:
            root_action.read_children_actions(RETRIEVE_BEFORE_STORE)

        assert "No value" in str(e)
        assert "template_id" in str(e)

        root_action.reset_state()
        with pytest.raises(TemplateActionError) as e:
            root_action.read_children_actions(STORE_SAME_TWICE)

        assert "already stored" in str(e)
        assert "template_id" in str(e)

        root_action.reset_state()
        with pytest.raises(ConflictError) as e:
            root_action.read_children_actions(RETRIEVE_CONFLICT_1)

        assert "already set" in str(e)
        assert "templateID" in str(e)
        assert "Domain" in str(e)
        assert "'id1'" in str(e)
        assert "template_id" in str(e)

        root_action.reset_state()
        with pytest.raises(ConflictError) as e:
            root_action.read_children_actions(RETRIEVE_CONFLICT_2)

        assert "already set" in str(e)
        assert "templateid" in str(e)
        assert "Domain" in str(e)
        assert "'id1'" in str(e)
        assert "template_id" in str(e)
