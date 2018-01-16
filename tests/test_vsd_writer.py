import os
from mock import patch, MagicMock
import pytest

from bambou.exceptions import BambouHTTPError
from levistate.vsd_writer import (Context,
                                  InvalidSpecification,
                                  InvalidAttributeError,
                                  InvalidObjectError,
                                  MissingSelectionError,
                                  MissingSessionParamsError,
                                  MultipleSelectionError,
                                  SessionError,
                                  SessionNotStartedError,
                                  VsdWriter)

FIXTURE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'fixtures')
VALID_SPECS_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                     'valid_vsd_specifications')
INVALID_SPECS_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                       'invalid_vsd_specifications')

SESSION_PARAMS = {
    "url": "https://localhost:8443",
    "username": "testuser",
    "password": "testpass",
    "enterprise": "testent"
}

EXPECTED_SESSION_PARAMS = {
    "api_url": SESSION_PARAMS['url'],
    "username": SESSION_PARAMS['username'],
    "password": SESSION_PARAMS['password'],
    "enterprise": SESSION_PARAMS['enterprise'],
    "version": "5.0",
    "api_prefix": "nuage/api"
}

PARSE_ERROR_CASES = [
    ('noexist.spec', 'not found'),
    ('notjson.spec', 'Error parsing'),
    ('nomodel.spec', "'model' missing"),
    ('noattributes.spec', "'attributes' missing"),
    ('nochildren.spec', "'children' missing"),
    ('noentityname.spec', "'entity_name' missing"),
    ('noresourcename.spec', "'resource_name' missing"),
    ('norestname.spec', "'rest_name' missing"),
]


@patch("levistate.vsd_writer.Session")
def setup_standard_session(vsd_writer, mock_patch):
    vsd_writer.set_session_params(**SESSION_PARAMS)
    vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

    mock_session = MagicMock()
    mock_session.root_object = MagicMock()
    mock_patch.return_value = mock_session
    vsd_writer.start_session()

    mock_patch.assert_called_once_with(spec=vsd_writer.specs['me'],
                                       **EXPECTED_SESSION_PARAMS)
    mock_session.start.assert_called_once()
    mock_session.set_enterprise_spec.assert_called_once_with(
        vsd_writer.specs['enterprise'])
    assert mock_session.root_object.spec == vsd_writer.specs['me']

    mock_session.start.assert_called_once()

    return mock_session


class TestVsdWriterSpecParsing(object):

    def validate_valid_specs(self, vsd_writer):
        assert "me" in vsd_writer.specs
        assert vsd_writer.specs['me']['model']['entity_name'] == "Me"
        assert "enterprise" in vsd_writer.specs
        assert vsd_writer.specs['enterprise']['model']['entity_name'] == (
            "Enterprise")
        assert "domaintemplate" in vsd_writer.specs
        assert vsd_writer.specs['domaintemplate']['model']['entity_name'] == (
            "DomainTemplate")
        assert "domain" in vsd_writer.specs
        assert vsd_writer.specs['domain']['model']['entity_name'] == "Domain"

    def test_read_dir__success(self):
        vsd_writer = VsdWriter()

        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        self.validate_valid_specs(vsd_writer)

    def test_read_files__success(self):
        vsd_writer = VsdWriter()

        vsd_writer.read_api_specifications(os.path.join(VALID_SPECS_DIRECTORY,
                                                        "me.spec"))
        vsd_writer.read_api_specifications(os.path.join(VALID_SPECS_DIRECTORY,
                                                        "enterprise.spec"))
        vsd_writer.read_api_specifications(os.path.join(VALID_SPECS_DIRECTORY,
                                                        "domaintemplate.spec"))
        vsd_writer.read_api_specifications(os.path.join(VALID_SPECS_DIRECTORY,
                                                        "domain.spec"))

        self.validate_valid_specs(vsd_writer)

    @pytest.mark.parametrize("filename, message", PARSE_ERROR_CASES)
    def test_read_files__invalid(self, filename, message):
        vsd_writer = VsdWriter()

        with pytest.raises(InvalidSpecification) as e:
            vsd_writer.read_api_specifications(os.path.join(
                INVALID_SPECS_DIRECTORY,
                filename))

        assert message in str(e)


class TestVsdWriterSession(object):

    def test_start__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_session.start.assert_called_once()
        mock_session.set_enterprise_spec.assert_called_once_with(
            vsd_writer.specs['enterprise'])

    def test_start__no_params(self):
        vsd_writer = VsdWriter()

        with pytest.raises(MissingSessionParamsError) as e:
            vsd_writer.start_session()

        assert "session without parameters" in str(e)

    def test_start__no_root_spec(self):
        vsd_writer = VsdWriter()

        vsd_writer.set_session_params(**SESSION_PARAMS)

        with pytest.raises(InvalidSpecification) as e:
            vsd_writer.start_session()

        assert "No root specification" in str(e)

    def test_start__no_enterprise_spec(self):
        vsd_writer = VsdWriter()

        vsd_writer.set_session_params(**SESSION_PARAMS)

        vsd_writer.read_api_specifications(os.path.join(VALID_SPECS_DIRECTORY,
                                                        "me.spec"))

        with pytest.raises(InvalidSpecification) as e:
            vsd_writer.start_session()

        assert "No enterprise specification" in str(e)

    @patch("levistate.vsd_writer.Session")
    def test_start__bambou_error(self, mock_patch):
        vsd_writer = VsdWriter()
        vsd_writer.set_session_params(**SESSION_PARAMS)
        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        mock_session = MagicMock()
        mock_patch.return_value = mock_session
        fake_exception = BambouHTTPError(
            type('', (object,), {
                'response': type('', (object,), {'status_code': 403,
                                                 'reason': 'forbidden',
                                                 'errors': 'forbidden'})()})())
        mock_session.start.side_effect = fake_exception
        with pytest.raises(SessionError) as e:
            vsd_writer.start_session()

        assert "403" in str(e)
        assert "forbidden" in str(e)

    def test_stop__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_session.start.assert_called_once()

        vsd_writer.stop_session()
        mock_session.reset.assert_called_once()


class TestVsdWriterCreateObject(object):

    def test__no_session(self):
        vsd_writer = VsdWriter()

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.create_object("Enterprise")

        assert "not started" in str(e)

    @patch("levistate.vsd_writer.ConfigObject")
    def test_parent__success(self, mock_object):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object.return_value = "new object"
        new_context = vsd_writer.create_object("Enterprise")

        mock_object.assert_called_once_with(vsd_writer.specs['enterprise'])
        assert new_context.parent_object is None
        assert new_context.current_object == "new object"
        assert new_context.object_exists is False

    @patch("levistate.vsd_writer.ConfigObject")
    def test_child__success(self, mock_object):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = "grandparent object"
        context.current_object = "parent object"
        context.object_exists = True

        mock_object.return_value = "new object"
        new_context = vsd_writer.create_object("Domain", context)

        mock_object.assert_called_once_with(vsd_writer.specs['domain'])
        assert new_context.parent_object == "parent object"
        assert new_context.current_object == "new object"
        assert new_context.object_exists is False

    def test__bad_object(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.create_object("Foobar")

        assert "No specification" in str(e)
        assert "Foobar" in str(e)


class TestVsdWriterSelectObject(object):

    def test__no_session(self):
        vsd_writer = VsdWriter()

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.select_object("Enterprise", "name", "test_enterprise")

        assert "not started" in str(e)

    @patch("levistate.vsd_writer.Fetcher")
    def test_parent__success(self, mock_fetcher):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = ["selected object"]
        new_context = vsd_writer.select_object("Enterprise", "Name",
                                               "test_enterprise")

        mock_fetcher.assert_called_once_with(mock_session.root_object,
                                             vsd_writer.specs['enterprise'])
        mock_fetcher.get.assert_called_once_with(
            filter='name is "test_enterprise"')
        assert new_context.parent_object is None
        assert new_context.current_object == "selected object"
        assert new_context.object_exists is True

    @patch("levistate.vsd_writer.Fetcher")
    def test_child__success(self, mock_fetcher):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = "grandparent object"
        mock_parent = MagicMock()
        context.current_object = mock_parent
        context.current_object.spec = vsd_writer.specs['enterprise']
        context.object_exists = True

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = ["selected object"]
        new_context = vsd_writer.select_object("Domain", "Name",
                                               "test_domain",
                                               context)

        mock_fetcher.assert_called_once_with(mock_parent,
                                             vsd_writer.specs['domain'])
        mock_fetcher.get.assert_called_once_with(
            filter='name is "test_domain"')
        assert new_context.parent_object == mock_parent
        assert new_context.current_object == "selected object"
        assert new_context.object_exists is True

    def test__bad_object(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.select_object("Foobar", "Name", "test_enterprise")

        assert "No specification" in str(e)
        assert "Foobar" in str(e)

    def test__bad_child(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.select_object("BridgeInterface", "Name", "test_child")

        assert "no child" in str(e)
        assert "Me" in str(e)
        assert "BridgeInterface" in str(e)

        context = Context()
        context.parent_object = "grandparent object"
        mock_parent = MagicMock()
        context.current_object = mock_parent
        context.current_object.spec = vsd_writer.specs['enterprise']
        context.object_exists = True

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.select_object("BridgeInterface", "Name", "test_child",
                                     context)

        assert "no child" in str(e)
        assert "Enterprise" in str(e)
        assert "BridgeInterface" in str(e)

    @patch("levistate.vsd_writer.Fetcher")
    def test__not_found(self, mock_fetcher):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = []

        with pytest.raises(MissingSelectionError) as e:
            vsd_writer.select_object("Enterprise", "Name", "test_enterprise")

        mock_fetcher.assert_called_once_with(mock_session.root_object,
                                             vsd_writer.specs['enterprise'])
        mock_fetcher.get.assert_called_once_with(
            filter='name is "test_enterprise"')
        assert "object exists" in str(e)
        assert "Enterprise" in str(e)
        assert "Name" in str(e)
        assert "test_enterprise" in str(e)

    @patch("levistate.vsd_writer.Fetcher")
    def test__multiple_found(self, mock_fetcher):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = ["enterprise_1", "enterprise_2"]

        with pytest.raises(MultipleSelectionError) as e:
            vsd_writer.select_object("Enterprise", "Name", "test_enterprise")

        mock_fetcher.assert_called_once_with(mock_session.root_object,
                                             vsd_writer.specs['enterprise'])
        mock_fetcher.get.assert_called_once_with(
            filter='name is "test_enterprise"')
        assert "Multiple" in str(e)
        assert "Enterprise" in str(e)
        assert "Name" in str(e)
        assert "test_enterprise" in str(e)


class TestVsdWriterDeleteObject(object):

    def test__no_session(self):
        vsd_writer = VsdWriter()

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.delete_object("context")

        assert "not started" in str(e)

    def test__success(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        new_context = vsd_writer.delete_object(context)

        mock_object.delete.assert_called_once()
        assert new_context.current_object is None
        assert new_context.object_exists is False

    def test__no_object(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = None
        context.current_object = "object"
        context.object_exists = False

        with pytest.raises(SessionError) as e:
            vsd_writer.delete_object(context)

        assert "No object" in str(e)

        context.current_object = None
        context.object_exists = True

        with pytest.raises(SessionError) as e:
            vsd_writer.delete_object(context)

        assert "No object" in str(e)


class TestVsdWriterSetValues(object):

    def test__no_session(self):
        vsd_writer = VsdWriter()

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.set_values("context", name="test_enterprise")

        assert "not started" in str(e)

    def test_parent_new__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = False

        new_context = vsd_writer.set_values(context,
                                            BGPEnabled=True,
                                            DHCPLeaseInterval=10,
                                            encryptionManagementMode='managed',
                                            name='test_enterprise')

        assert mock_object.bgpenabled is True
        assert mock_object.dhcpleaseinterval == 10
        assert mock_object.encryptionmanagementmode == 'managed'
        assert mock_object.name == 'test_enterprise'
        mock_session.root_object.current_child_name == "enterprises"
        mock_session.root_object.create_child.assert_called_once_with(
            mock_object)
        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    def test_parent_update__success(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        new_context = vsd_writer.set_values(context,
                                            BGPEnabled=True,
                                            DHCPLeaseInterval=10,
                                            encryptionManagementMode='managed',
                                            name='test_enterprise')

        assert mock_object.bgpenabled is True
        assert mock_object.dhcpleaseinterval == 10
        assert mock_object.encryptionmanagementmode == 'managed'
        assert mock_object.name == 'test_enterprise'
        mock_object.save.assert_called_once()
        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    def test_child_new__success(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['domain']
        mock_object.__resource_name__ = "domains"

        mock_parent = MagicMock()

        context = Context()
        context.parent_object = mock_parent
        mock_parent.spec = vsd_writer.specs['enterprise']
        context.current_object = mock_object
        context.object_exists = False

        new_context = vsd_writer.set_values(context,
                                            BGPEnabled=True,
                                            ECMPCount=10,
                                            DPI='enabled',
                                            name='test_domain')

        assert mock_object.bgpenabled is True
        assert mock_object.ecmpcount == 10
        assert mock_object.dpi == 'enabled'
        assert mock_object.name == 'test_domain'
        mock_parent.current_child_name == "domains"
        mock_parent.create_child.assert_called_once_with(mock_object)
        assert new_context.parent_object == mock_parent
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    def test_child_update__success(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['domain']

        mock_parent = MagicMock()

        context = Context()
        context.parent_object = mock_parent
        context.current_object = mock_object
        context.object_exists = True

        new_context = vsd_writer.set_values(context,
                                            BGPEnabled=True,
                                            ECMPCount=10,
                                            DPI='enabled',
                                            name='test_domain')

        assert mock_object.bgpenabled is True
        assert mock_object.ecmpcount == 10
        assert mock_object.dpi == 'enabled'
        assert mock_object.name == 'test_domain'
        mock_object.save.assert_called_once()
        assert new_context.parent_object == mock_parent
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    def test__no_object(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = None
        context.current_object = None
        context.object_exists = False

        with pytest.raises(SessionError) as e:
            vsd_writer.set_values(context, name="test")

        assert "No object" in str(e)

    def test__invalid_attr(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['domain']

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = False

        with pytest.raises(InvalidAttributeError) as e:
            vsd_writer.set_values(context, FooBar="test")

        assert "not define" in str(e)
        assert "FooBar" in str(e)

    def test__bad_child(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = None
        mock_object = MagicMock()
        context.current_object = mock_object
        context.current_object.spec = vsd_writer.specs['bridgeinterface']
        context.object_exists = False

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.set_values(context, name="test")

        assert "no child" in str(e)
        assert "Me" in str(e)
        assert "BridgeInterface" in str(e)

        context.parent_object = None
        mock_object = MagicMock()
        context.parent_object = mock_object
        context.parent_object.spec = vsd_writer.specs['enterprise']

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.set_values(context, name="test")

        assert "no child" in str(e)
        assert "Enterprise" in str(e)
        assert "BridgeInterface" in str(e)


class TestVsdWriterGetValue(object):

    def test__no_session(self):
        vsd_writer = VsdWriter()

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.get_value("field", "context")

        assert "not started" in str(e)

    def test__success(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.name = "test_name"
        mock_object.id = "test_id"

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        name_value = vsd_writer.get_value("Name", context)
        id_value = vsd_writer.get_value("Id", context)

        assert name_value == "test_name"
        assert id_value == "test_id"

    def test__no_object(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = None
        context.current_object = "object"
        context.object_exists = False

        with pytest.raises(SessionError) as e:
            vsd_writer.get_value("name", context)

        assert "No object" in str(e)

        context.current_object = None
        context.object_exists = True

        with pytest.raises(SessionError) as e:
            vsd_writer.get_value("name", context)

        assert "No object" in str(e)

    def test__invalid_attr(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.name = "test_name"
        mock_object.id = "test_id"

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        with pytest.raises(InvalidAttributeError) as e:
            vsd_writer.get_value("FooBar", context)

        assert "not define" in str(e)
        assert "FooBar" in str(e)
