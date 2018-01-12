import os
import pytest

from levistate.configuration import (Configuration)
from levistate.template import (MissingTemplateError,
                                TemplateStore)
from .template_test_params import ACL_TEMPLATE_VARS

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


class TestConfigurationApply(object):

    def test__success(self):
        pass
