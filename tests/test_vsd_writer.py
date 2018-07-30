from mock import patch, MagicMock
import os
import pytest

from bambou.exceptions import BambouHTTPError
from levistate.vsd_writer import (Context,
                                  InvalidSpecification,
                                  InvalidAttributeError,
                                  InvalidObjectError,
                                  InvalidValueError,
                                  MissingSelectionError,
                                  MissingSessionParamsError,
                                  MultipleSelectionError,
                                  SessionError,
                                  SessionNotStartedError,
                                  VsdError,
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

VALIDATE_ONLY_CASES = [False, True]


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
    if vsd_writer.validate_only is True:
        mock_session.start.assert_not_called()
    else:
        mock_session.start.assert_called_once()

    mock_session.set_enterprise_spec.assert_called_once_with(
        vsd_writer.specs['enterprise'])
    assert mock_session.root_object.spec == vsd_writer.specs['me']

    return mock_session


def get_mock_bambou_error(status_code, reason):
    return BambouHTTPError(
        type('', (object,), {
            'response': type('', (object,), {'status_code': status_code,
                                             'reason': reason,
                                             'errors': reason})()})())

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

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_start__success(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        if validate_only is True:
            mock_session.start.assert_not_called()
        else:
            mock_session.start.assert_called_once()

        mock_session.set_enterprise_spec.assert_called_once_with(
            vsd_writer.specs['enterprise'])

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_start__no_params(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(MissingSessionParamsError) as e:
            vsd_writer.start_session()

        assert "session without parameters" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_start__no_root_spec(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        vsd_writer.set_session_params(**SESSION_PARAMS)

        with pytest.raises(InvalidSpecification) as e:
            vsd_writer.start_session()

        assert "No root specification" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_start__no_enterprise_spec(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

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
        fake_exception = get_mock_bambou_error(403, 'forbidden')
        mock_session.start.side_effect = fake_exception

        with pytest.raises(VsdError) as e:
            vsd_writer.start_session()

        assert "403" in str(e)
        assert "forbidden" in str(e)

        assert "Session start" in e.value.get_display_string()
        assert "HTTP 403" in e.value.get_display_string()

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_stop__success(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        mock_session = setup_standard_session(vsd_writer)

        if validate_only is True:
            mock_session.start.assert_not_called()
        else:
            mock_session.start.assert_called_once()

        vsd_writer.stop_session()

        if validate_only is True:
            mock_session.reset.assert_not_called()
        else:
            mock_session.reset.assert_called_once()


class TestVsdWriterCreateObject(object):

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_session(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.create_object("Enterprise")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("levistate.vsd_writer.ConfigObject")
    def test_parent__success(self, mock_object, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        mock_object.return_value = "new object"
        new_context = vsd_writer.create_object("Enterprise")

        mock_object.assert_called_once_with(vsd_writer.specs['enterprise'])
        assert new_context.parent_object is None
        assert new_context.current_object == "new object"
        assert new_context.object_exists is False

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("levistate.vsd_writer.ConfigObject")
    def test_child__success(self, mock_object, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
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

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__bad_object(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.create_object("Foobar")

        assert "No specification" in str(e)
        assert "Foobar" in str(e)

        assert "Create object Foobar" in e.value.get_display_string()


class TestVsdWriterSelectObject(object):

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_session(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.select_object("Enterprise", "name", "test_enterprise")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("levistate.vsd_writer.ConfigObject")
    @patch("levistate.vsd_writer.Fetcher")
    def test_parent__success(self, mock_fetcher, mock_object, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = ["selected object"]

        mock_object.return_value = "selected object"

        new_context = vsd_writer.select_object("Enterprise", "Name",
                                               "test_enterprise")

        mock_fetcher.assert_called_once_with(mock_session.root_object,
                                             vsd_writer.specs['enterprise'])

        if validate_only is True:
            mock_fetcher.get.assert_not_called()
        else:
            mock_fetcher.get.assert_called_once_with(
                filter='name is "test_enterprise"')

        assert new_context.parent_object is None
        assert new_context.current_object == "selected object"
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("levistate.vsd_writer.ConfigObject")
    @patch("levistate.vsd_writer.Fetcher")
    def test_child__success(self, mock_fetcher, mock_object, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = "grandparent object"
        mock_parent = MagicMock()
        context.current_object = mock_parent
        context.current_object.spec = vsd_writer.specs['enterprise']
        context.object_exists = True

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = ["selected object"]
        mock_object.return_value = "selected object"

        new_context = vsd_writer.select_object("Domain", "Name",
                                               "test_domain",
                                               context)

        mock_fetcher.assert_called_once_with(mock_parent,
                                             vsd_writer.specs['domain'])

        if validate_only is True:
            mock_fetcher.get.assert_not_called()
        else:
            mock_fetcher.get.assert_called_once_with(
                filter='name is "test_domain"')

        assert new_context.parent_object == mock_parent
        assert new_context.current_object == "selected object"
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__bad_object(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.select_object("Foobar", "Name", "test_enterprise")

        assert "No specification" in str(e)
        assert "Foobar" in str(e)

        assert ("Select object Foobar Name = test_enterprise" in
                e.value.get_display_string())

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__bad_child(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
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

        assert ("Select object BridgeInterface Name = test_child" in
                e.value.get_display_string())

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

        assert ("Select object Enterprise Name = test_enterprise" in
                e.value.get_display_string())

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

        assert ("Select object Enterprise Name = test_enterprise" in
                e.value.get_display_string())

    @patch("levistate.vsd_writer.Fetcher")
    def test__bambou_error(self, mock_fetcher):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_error = get_mock_bambou_error(404, "Not Found")
        mock_fetcher.get.side_effect = mock_error

        with pytest.raises(VsdError) as e:
            vsd_writer.select_object("Enterprise", "Name", "test_enterprise")

        mock_fetcher.assert_called_once_with(mock_session.root_object,
                                             vsd_writer.specs['enterprise'])
        mock_fetcher.get.assert_called_once_with(
            filter='name is "test_enterprise"')

        assert "404" in str(e)
        assert "Not Found" in str(e)

        assert ("Select object Enterprise Name = test_enterprise" in
                e.value.get_display_string())
        assert "HTTP 404" in e.value.get_display_string()


class TestVsdWriterGetObjectList(object):

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_session(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.get_object_list("Enterprise")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("levistate.vsd_writer.ConfigObject")
    @patch("levistate.vsd_writer.Fetcher")
    def test_parent__success(self, mock_fetcher, mock_object, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = ["selected object"]

        mock_object.return_value = "selected object"

        objects = vsd_writer.get_object_list("Enterprise")

        mock_fetcher.assert_called_once_with(mock_session.root_object,
                                             vsd_writer.specs['enterprise'])

        if validate_only is True:
            mock_fetcher.get.assert_not_called()
            assert len(objects) == 0
        else:
            mock_fetcher.get.assert_called_once_with()

            assert len(objects) == 1
            assert objects[0].parent_object is None
            assert objects[0].current_object == "selected object"
            assert objects[0].object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("levistate.vsd_writer.ConfigObject")
    @patch("levistate.vsd_writer.Fetcher")
    def test_child__success(self, mock_fetcher, mock_object, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = "grandparent object"
        mock_parent = MagicMock()
        context.current_object = mock_parent
        context.current_object.spec = vsd_writer.specs['enterprise']
        context.object_exists = True

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = ["selected object"]
        mock_object.return_value = "selected object"

        objects = vsd_writer.get_object_list("Domain", context)

        mock_fetcher.assert_called_once_with(mock_parent,
                                             vsd_writer.specs['domain'])

        if validate_only is True:
            mock_fetcher.get.assert_not_called()
            assert len(objects) == 0
        else:
            mock_fetcher.get.assert_called_once_with()

            assert len(objects) == 1
            assert objects[0].parent_object == mock_parent
            assert objects[0].current_object == "selected object"
            assert objects[0].object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__bad_object(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.get_object_list("Foobar")

        assert "No specification" in str(e)
        assert "Foobar" in str(e)

        assert ("Get object list Foobar" in
                e.value.get_display_string())

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__bad_child(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.get_object_list("BridgeInterface")

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
            vsd_writer.get_object_list("BridgeInterface", context)

        assert "no child" in str(e)
        assert "Enterprise" in str(e)
        assert "BridgeInterface" in str(e)

        assert ("Get object list BridgeInterface" in
                e.value.get_display_string())

    @patch("levistate.vsd_writer.Fetcher")
    def test__not_found(self, mock_fetcher):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = []

        objects = vsd_writer.get_object_list("Enterprise")

        mock_fetcher.assert_called_once_with(mock_session.root_object,
                                             vsd_writer.specs['enterprise'])
        mock_fetcher.get.assert_called_once_with()

        assert len(objects) == 0

    @patch("levistate.vsd_writer.Fetcher")
    def test__multiple_found(self, mock_fetcher):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = ["enterprise_1", "enterprise_2"]

        objects = vsd_writer.get_object_list("Enterprise")

        mock_fetcher.assert_called_once_with(mock_session.root_object,
                                             vsd_writer.specs['enterprise'])
        mock_fetcher.get.assert_called_once_with()

        assert len(objects) == 2
        assert objects[0].parent_object is None
        assert objects[0].current_object == "enterprise_1"
        assert objects[0].object_exists is True

        assert objects[1].parent_object is None
        assert objects[1].current_object == "enterprise_2"
        assert objects[1].object_exists is True

    @patch("levistate.vsd_writer.Fetcher")
    def test__bambou_error(self, mock_fetcher):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_error = get_mock_bambou_error(404, "Not Found")
        mock_fetcher.get.side_effect = mock_error

        with pytest.raises(VsdError) as e:
            vsd_writer.get_object_list("Enterprise")

        mock_fetcher.assert_called_once_with(mock_session.root_object,
                                             vsd_writer.specs['enterprise'])
        mock_fetcher.get.assert_called_once_with()

        assert "404" in str(e)
        assert "Not Found" in str(e)

        assert ("Get object list Enterprise" in
                e.value.get_display_string())
        assert "HTTP 404" in e.value.get_display_string()


class TestVsdWriterDeleteObject(object):

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_session(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.delete_object("context")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__success(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        new_context = vsd_writer.delete_object(context)

        if validate_only is True:
            mock_object.delete.assert_not_called()
        else:
            mock_object.delete.assert_called_once()

        assert new_context.current_object is None
        assert new_context.object_exists is False

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_object(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = None
        context.current_object = "object"
        context.object_exists = False

        with pytest.raises(SessionError) as e:
            vsd_writer.delete_object(context)

        assert "No object" in str(e)

        assert "Delete object" in e.value.get_display_string()

        context.current_object = None
        context.object_exists = True

        with pytest.raises(SessionError) as e:
            vsd_writer.delete_object(context)

        assert "No object" in str(e)

        assert "Delete object" in e.value.get_display_string()

    def test__bambou_error(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        fake_exception = get_mock_bambou_error(403, "forbidden")
        mock_object.delete.side_effect = fake_exception

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        with pytest.raises(SessionError) as e:
            vsd_writer.delete_object(context)

        assert "403" in str(e)
        assert "forbidden" in str(e)

        assert "Delete object" in e.value.get_display_string()
        assert "HTTP 403" in e.value.get_display_string()


class TestVsdWriterSetValues(object):

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_session(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.set_values("context", name="test_enterprise")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent_new__success(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        if validate_only is True:
            mock_session.root_object = MagicMock()
            mock_session.root_object.spec = vsd_writer.specs['me']

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"
        mock_object.validate.return_value = True

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
        mock_object.validate.assert_called_once()

        if validate_only is True:
            mock_session.root_object.create_child.assert_not_called()
        else:
            mock_session.root_object.current_child_name == "enterprises"
            mock_session.root_object.create_child.assert_called_once_with(
                mock_object)

        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent_update__success(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.validate.return_value = True

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
        mock_object.validate.assert_called_once()

        if validate_only is True:
            mock_object.save.assert_not_called()
        else:
            mock_object.save.assert_called_once()

        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child_new__success(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['domain']
        mock_object.__resource_name__ = "domains"
        mock_object.validate.return_value = True

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
        mock_object.validate.assert_called_once()

        if validate_only is True:
            mock_parent.create_child.assert_not_called()
        else:
            mock_parent.current_child_name == "domains"
            mock_parent.create_child.assert_called_once_with(mock_object)

        assert new_context.parent_object == mock_parent
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child_update__success(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['domain']
        mock_object.validate.return_value = True

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
        mock_object.validate.assert_called_once()

        if validate_only is True:
            mock_object.save.assert_not_called()
        else:
            mock_object.save.assert_called_once()

        assert new_context.parent_object == mock_parent
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_object(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = None
        context.current_object = None
        context.object_exists = False

        with pytest.raises(SessionError) as e:
            vsd_writer.set_values(context, name="test")

        assert "No object" in str(e)

        assert "Set value" in e.value.get_display_string()

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__invalid_attr(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
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

        assert "Set value" in e.value.get_display_string()

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__bad_child(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
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

        assert "Creating child" in e.value.get_display_string()

        context.parent_object = None
        mock_object = MagicMock()
        context.parent_object = mock_object
        context.parent_object.spec = vsd_writer.specs['enterprise']

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.set_values(context, name="test")

        assert "no child" in str(e)
        assert "Enterprise" in str(e)
        assert "BridgeInterface" in str(e)

        assert "Creating child" in e.value.get_display_string()

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__invalid_values(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['domain']
        mock_object.validate.return_value = False
        mock_object.errors = {
            'name': {'title': 'Invalid input',
                     'description': "Name is invalid",
                     'remote_name': "name"},
            'bgpenabled': {'title': 'Invalid input',
                           'description': "BGPEnabled is invalid",
                           'remote_name': "BGPEnabled"}}

        mock_parent = MagicMock()

        context = Context()
        context.parent_object = mock_parent
        context.current_object = mock_object
        context.object_exists = True

        with pytest.raises(InvalidValueError) as e:
            vsd_writer.set_values(context,
                                  BGPEnabled=True,
                                  name='test_domain')

        assert mock_object.bgpenabled is True
        assert mock_object.name == 'test_domain'
        mock_object.validate.assert_called_once()
        mock_object.save.assert_not_called()

        assert "name" in str(e)
        assert "Name is invalid" in str(e)
        assert "bgpenabled" in str(e)
        assert "BGPEnabled is invalid" in str(e)

        assert "Set value" in e.value.get_display_string()

    def test_child_update__bambou_error(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['domain']
        mock_object.validate.return_value = True
        fake_exception = get_mock_bambou_error(403, "forbidden")
        mock_object.save.side_effect = fake_exception

        mock_parent = MagicMock()

        context = Context()
        context.parent_object = mock_parent
        context.current_object = mock_object
        context.object_exists = True

        with pytest.raises(VsdError) as e:
            vsd_writer.set_values(context,
                                  BGPEnabled=True,
                                  ECMPCount=10,
                                  DPI='enabled',
                                  name='test_domain')

        assert "403" in str(e)
        assert "forbidden" in str(e)

        assert "Saving" in e.value.get_display_string()
        assert "HTTP 403" in e.value.get_display_string()


class TestVsdWriterGetValue(object):

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_session(self, validate_only):
        vsd_writer = VsdWriter()

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.get_value("field", "context")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__success(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        if validate_only is True:
            # Anonymous object (does not override getattr like mock does)
            mock_object = type('', (object,), {})()
        else:
            mock_object = MagicMock()
            mock_object.name = "test_name"
            mock_object.id = "test_id"
            mock_object.bgpenabled = True

        mock_object.spec = vsd_writer.specs['enterprise']

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        name_value = vsd_writer.get_value("Name", context)
        id_value = vsd_writer.get_value("Id", context)
        bgp_value = vsd_writer.get_value("BGPEnabled", context)

        if validate_only is True:
            assert name_value == "ValidatePlaceholder"
            assert id_value == "ValidatePlaceholder"
            assert bgp_value is False
        else:
            assert name_value == "test_name"
            assert id_value == "test_id"
            assert bgp_value is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_object(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        setup_standard_session(vsd_writer)

        context = Context()
        context.parent_object = None
        context.current_object = "object"
        context.object_exists = False

        with pytest.raises(SessionError) as e:
            vsd_writer.get_value("name", context)

        assert "No object" in str(e)

        assert "Get value" in e.value.get_display_string()

        context.current_object = None
        context.object_exists = True

        with pytest.raises(SessionError) as e:
            vsd_writer.get_value("name", context)

        assert "No object" in str(e)

        assert "Get value" in e.value.get_display_string()

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__invalid_attr(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
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

        assert "Get value FooBar" in e.value.get_display_string()
