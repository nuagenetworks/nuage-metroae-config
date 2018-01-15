from mock import call, patch, MagicMock
import os
import pytest

from levistate.actions import TemplateActionError
from levistate.configuration import Configuration
from levistate.template import (MissingTemplateError,
                                TemplateStore)

FIXTURE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'fixtures')
VALID_TEMPLATE_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                        'valid_templates')


def load_standard_configuration():
    store = TemplateStore()
    store.read_templates(VALID_TEMPLATE_DIRECTORY)
    return Configuration(store)


class TestConfigurationTemplates(object):

    def test__success(self):
        config = load_standard_configuration()
        assert set(config.get_template_names()) == set(["Enterprise", "Domain",
                                                        "Bidirectional ACL"])
        enterprise_template = config.get_template("enterprise")
        assert enterprise_template.get_name() == "Enterprise"

        domain_template = config.get_template("domain")
        assert domain_template.get_name() == "Domain"

        acl_template = config.get_template("bidirectional acl")
        assert acl_template.get_name() == "Bidirectional ACL"

    def test__missing(self):
        config = load_standard_configuration()

        with pytest.raises(MissingTemplateError) as e:
            config.get_template("Foobar")

        assert "No template" in str(e)
        assert "Foobar" in str(e)


class TestConfigurationData(object):

    def test_add_get__success(self):
        config = load_standard_configuration()

        data1 = {"enterprise_name": "enterprise1"}
        data2 = {"enterprise_name": "enterprise2",
                 "domain_name": "domain2"}

        id1 = config.add_template_data("Enterprise", **data1)
        id2 = config.add_template_data("Domain", **data2)

        assert config.get_template_data(id2) == data2
        assert config.get_template_data(id1) == data1

    def test_add__invalid(self):
        config = load_standard_configuration()

        data1 = {"enterprise_name": "enterprise1",
                 "domain_name": "domain1"}

        with pytest.raises(MissingTemplateError) as e:
            config.add_template_data("Foobar", **data1)

        assert "No template" in str(e)
        assert "Foobar" in str(e)

    def test_get__invalid(self):
        config = load_standard_configuration()

        data1 = {"enterprise_name": "enterprise1",
                 "domain_name": "domain1"}

        id1 = config.add_template_data("Domain", **data1)
        bad_template_id = dict(id1)
        bad_template_id['key'] = 'foobar'
        bad_index_id = dict(id1)
        bad_index_id['index'] = 1

        with pytest.raises(IndexError) as e:
            config.get_template_data(bad_template_id)

        assert "Invalid template data id" in str(e)

        with pytest.raises(IndexError) as e:
            config.get_template_data(bad_index_id)

        assert "Invalid template data id" in str(e)

    def test_update__success(self):
        config = load_standard_configuration()

        data1 = {"enterprise_name": "enterprise1"}
        data2 = {"enterprise_name": "enterprise2",
                 "domain_name": "domain2"}
        data3 = {"enterprise_name": "enterprise3"}
        data4 = {"enterprise_name": "enterprise4",
                 "domain_name": "domain4"}

        id1 = config.add_template_data("Enterprise", **data1)
        id2 = config.add_template_data("Domain", **data2)

        assert config.get_template_data(id2) == data2
        assert config.get_template_data(id1) == data1

        id4 = config.update_template_data(id2, **data4)
        assert config.get_template_data(id2) == data4
        assert config.get_template_data(id1) == data1
        assert id4 == id2

        id3 = config.update_template_data(id1, **data3)
        assert config.get_template_data(id2) == data4
        assert config.get_template_data(id1) == data3
        assert id3 == id1

    def test_update__invalid(self):
        config = load_standard_configuration()

        data1 = {"enterprise_name": "enterprise1"}

        id1 = config.add_template_data("Enterprise", **data1)
        bad_template_id = dict(id1)
        bad_template_id['key'] = 'foobar'
        bad_index_id = dict(id1)
        bad_index_id['index'] = 1

        with pytest.raises(MissingTemplateError) as e:
            config.update_template_data(bad_template_id, **data1)

        assert "No template" in str(e)
        assert "foobar" in str(e)

        bad_template_id['key'] = 'domain'

        with pytest.raises(IndexError) as e:
            config.update_template_data(bad_template_id, **data1)

        assert "Invalid template data id" in str(e)

        with pytest.raises(IndexError) as e:
            config.update_template_data(bad_index_id, **data1)

        assert "Invalid template data id" in str(e)

    def test_remove__success(self):
        config = load_standard_configuration()

        data1 = {"enterprise_name": "enterprise1"}
        data2 = {"enterprise_name": "enterprise2",
                 "domain_name": "domain2"}

        id1 = config.add_template_data("Enterprise", **data1)

        assert config.get_template_data(id1) == data1

        remove_id1 = config.remove_template_data(id1)

        assert config.get_template_data(id1) is None
        assert remove_id1 == id1

        id2 = config.add_template_data("Domain", **data2)

        assert config.get_template_data(id1) is None
        assert config.get_template_data(id2) == data2

        remove_id2 = config.remove_template_data(id2)

        assert config.get_template_data(id1) is None
        assert config.get_template_data(id2) is None
        assert remove_id2 == id2

        update_id1 = config.update_template_data(id1, **data1)

        assert config.get_template_data(id1) == data1
        assert config.get_template_data(id2) is None
        assert update_id1 == id1

        update_id2 = config.update_template_data(id2, **data2)

        assert config.get_template_data(id1) == data1
        assert config.get_template_data(id2) == data2
        assert update_id2 == id2

    def test_remove__invalid(self):
        config = load_standard_configuration()

        data1 = {"enterprise_name": "enterprise1",
                 "domain_name": "domain1"}

        id1 = config.add_template_data("Domain", **data1)
        bad_template_id = dict(id1)
        bad_template_id['key'] = 'foobar'
        bad_index_id = dict(id1)
        bad_index_id['index'] = 1

        with pytest.raises(IndexError) as e:
            config.remove_template_data(bad_template_id)

        assert "Invalid template data id" in str(e)

        with pytest.raises(IndexError) as e:
            config.remove_template_data(bad_index_id)

        assert "Invalid template data id" in str(e)


class TestConfigurationApplyRevert(object):

    def setup_mock(self, mock_patch):
        self.mock_root_action = MagicMock()
        mock_patch.return_value = self.mock_root_action
        self.mock_store = MagicMock()
        self.mock_ent_template = MagicMock()
        self.mock_ent_template._parse_with_vars.return_value = (
            "ent_template_dict")
        self.mock_domain_template = MagicMock()
        self.mock_domain_template._parse_with_vars.return_value = (
            "domain_template_dict")
        self.mock_writer = MagicMock()

    def setup_data(self, config):
        self.data1 = {"enterprise_name": "enterprise1"}
        deleted_ent_data = {"enterprise_name": "enterprise_deleted"}
        self.data2 = {"enterprise_name": "enterprise2"}
        self.data3 = {"enterprise_name": "enterprise1",
                      "domain_name": "domain1"}
        deleted_dom_data = {"enterprise_name": "enterprise_deleted",
                            "domain_name": "domain_deleted"}
        self.data4 = {"enterprise_name": "enterprise2",
                      "domain_name": "domain2"}

        config.add_template_data("Enterprise", **self.data1)
        config.add_template_data("Enterprise", **self.data2)
        id_ent = config.add_template_data("Enterprise", **deleted_ent_data)
        config.add_template_data("Domain", **self.data3)
        config.add_template_data("Domain", **self.data4)
        id_dom = config.add_template_data("Domain", **deleted_dom_data)

        config.remove_template_data(id_ent)
        config.remove_template_data(id_dom)

        self.mock_store.reset_mock()

    def verify_mock_calls(self, mock_patch):
        mock_patch.assert_called_once_with(None)
        self.mock_store.get_template.assert_has_calls([
            call("enterprise", None, None),
            call("domain", None, None)])
        self.mock_ent_template._parse_with_vars.assert_has_calls([
            call(**self.data1),
            call(**self.data2)])
        self.mock_domain_template._parse_with_vars.assert_has_calls([
            call(**self.data3),
            call(**self.data4)])
        assert self.mock_root_action.reset_state.call_count == 4
        self.mock_root_action.read_children_actions.assert_has_calls([
            call("ent_template_dict"),
            call("ent_template_dict"),
            call("domain_template_dict"),
            call("domain_template_dict")])

        self.mock_writer.start_session.assert_called_once()
        self.mock_root_action.execute.assert_called_once_with(self.mock_writer)
        self.mock_writer.stop_session.assert_called_once()

    @patch('levistate.configuration.Action')
    def test_apply__success(self, mock_patch):
        self.setup_mock(mock_patch)

        config = Configuration(self.mock_store)

        self.setup_data(config)

        self.mock_store.get_template.side_effect = [self.mock_ent_template,
                                                    self.mock_domain_template]

        config.apply(self.mock_writer)

        self.mock_root_action.set_revert.assert_has_calls([
            call(False), call(False), call(False), call(False)])
        self.verify_mock_calls(mock_patch)

    @patch('levistate.configuration.Action')
    def test_apply__action_error(self, mock_patch):
        self.setup_mock(mock_patch)
        self.mock_root_action.execute.side_effect = \
            TemplateActionError("Mock execute error")

        config = Configuration(self.mock_store)

        self.setup_data(config)

        self.mock_store.get_template.side_effect = [self.mock_ent_template,
                                                    self.mock_domain_template]

        with pytest.raises(TemplateActionError) as e:
            config.apply(self.mock_writer)

        assert "Mock execute error" in str(e)

        self.mock_store.reset_mock()
        self.mock_domain_template._parse_with_vars.side_effect = \
            TemplateActionError("Mock reading error")

        self.mock_store.get_template.side_effect = [self.mock_ent_template,
                                                    self.mock_domain_template]

        with pytest.raises(TemplateActionError) as e:
            config.apply(self.mock_writer)

        assert "Mock reading error" in str(e)

    @patch('levistate.configuration.Action')
    def test_revert__success(self, mock_patch):
        self.setup_mock(mock_patch)

        config = Configuration(self.mock_store)

        self.setup_data(config)

        self.mock_store.get_template.side_effect = [self.mock_ent_template,
                                                    self.mock_domain_template]

        config.revert(self.mock_writer)

        self.mock_root_action.set_revert.assert_has_calls([
            call(True), call(True), call(True), call(True)])
        self.verify_mock_calls(mock_patch)

    @patch('levistate.configuration.Action')
    def test_revert__action_error(self, mock_patch):
        self.setup_mock(mock_patch)
        self.mock_root_action.execute.side_effect = \
            TemplateActionError("Mock execute error")

        config = Configuration(self.mock_store)

        self.setup_data(config)

        self.mock_store.get_template.side_effect = [self.mock_ent_template,
                                                    self.mock_domain_template]

        with pytest.raises(TemplateActionError) as e:
            config.revert(self.mock_writer)

        assert "Mock execute error" in str(e)

        self.mock_store.reset_mock()
        self.mock_domain_template._parse_with_vars.side_effect = \
            TemplateActionError("Mock reading error")

        self.mock_store.get_template.side_effect = [self.mock_ent_template,
                                                    self.mock_domain_template]

        with pytest.raises(TemplateActionError) as e:
            config.revert(self.mock_writer)

        assert "Mock reading error" in str(e)
