from mock import call, patch, MagicMock
import json
import os
import pytest
import uuid

from bambou.exceptions import BambouHTTPError
from nuage_metroae_config.vsd_writer import (Context,
                                             DeviceWriterError,
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
    "enterprise": "testent",
    "certificate": ("testcertificate", "testKey")
}

EXPECTED_SESSION_PARAMS = {
    "api_url": SESSION_PARAMS['url'],
    "username": SESSION_PARAMS['username'],
    "password": SESSION_PARAMS['password'],
    "enterprise": SESSION_PARAMS['enterprise'],
    "certificate": SESSION_PARAMS['certificate'],
    "version": "6",
    "api_prefix": "nuage/api"
}

SESSION_PARAMS_NO_AUTH = {
    "url": "https://localhost:8443",
    "username": "testuser",
    "enterprise": "testent",
    "password": None,
    "certificate": None
}

EXPECTED_SESSION_PARAMS_NO_AUTH = {
    "api_url": SESSION_PARAMS_NO_AUTH['url'],
    "username": SESSION_PARAMS_NO_AUTH['username'],
    "password": SESSION_PARAMS_NO_AUTH['password'],
    "enterprise": SESSION_PARAMS_NO_AUTH['enterprise'],
    "version": "6",
    "api_prefix": "nuage/api"
}

SESSION_PARAMS_NO_CERTIFICATE = {
    "url": "https://localhost:8443",
    "username": "testuser",
    "enterprise": "testent",
    "password": None,
    "certificate": (None, "certificate_key")
}

EXPECTED_SESSION_PARAMS_NO_CERTIFICATE = {
    "api_url": SESSION_PARAMS_NO_AUTH['url'],
    "username": SESSION_PARAMS_NO_AUTH['username'],
    "password": SESSION_PARAMS_NO_AUTH['password'],
    "enterprise": SESSION_PARAMS_NO_AUTH['enterprise'],
    "certificate": SESSION_PARAMS_NO_CERTIFICATE['certificate'],
    "version": "6",
    "api_prefix": "nuage/api"
}

SESSION_PARAMS_NO_CERTIFICATE_KEY = {
    "url": "https://localhost:8443",
    "username": "testuser",
    "enterprise": "testent",
    "password": None,
    "certificate": ("certificate", None)
}

EXPECTED_SESSION_PARAMS_NO_CERTIFICATE_KEY = {
    "api_url": SESSION_PARAMS_NO_AUTH['url'],
    "username": SESSION_PARAMS_NO_AUTH['username'],
    "password": SESSION_PARAMS_NO_AUTH['password'],
    "enterprise": SESSION_PARAMS_NO_AUTH['enterprise'],
    "certificate": SESSION_PARAMS_NO_CERTIFICATE_KEY['certificate'],
    "version": "6",
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

QUERY_RANGE_SORT_CASES = [
    ({}, ["a1", "a3", "a5", "a2", "a4"]),
    ({"%end": 3}, ["a1", "a3", "a5"]),
    ({"%end": 99}, ["a1", "a3", "a5", "a2", "a4"]),
    ({"%end": 0}, []),
    ({"%end": -2}, ["a1", "a3", "a5"]),
    ({"%end": -5}, []),
    ({"%start": 0}, ["a1", "a3", "a5", "a2", "a4"]),
    ({"%start": 3}, ["a2", "a4"]),
    ({"%start": 99}, []),
    ({"%start": -1}, ["a4"]),
    ({"%start": -2}, ["a2", "a4"]),
    ({"%start": -6}, ["a1", "a3", "a5", "a2", "a4"]),
    ({"%start": 0, "%end": 5}, ["a1", "a3", "a5", "a2", "a4"]),
    ({"%start": 1, "%end": 3}, ["a3", "a5"]),
    ({"%start": 3, "%end": 99}, ["a2", "a4"]),
    ({"%start": 3, "%end": 4}, ["a2"]),
    ({"%start": 3, "%end": 3}, []),
    ({"%start": 4, "%end": 3}, []),
    ({"%start": -5, "%end": -1}, ["a1", "a3", "a5", "a2"]),
    ({"%start": -1, "%end": 0}, []),
    ({"%start": -3, "%end": -1}, ["a5", "a2"]),
    ({"%start": -3, "%end": -2}, ["a5"]),
    ({"%start": -3, "%end": 5}, ["a5", "a2", "a4"]),

    ({"%sort": "name"}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort": "name", "%end": 3}, ["a1", "a2", "a3"]),
    ({"%sort": "name", "%end": 99}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort": "name", "%end": 0}, []),
    ({"%sort": "name", "%end": -2}, ["a1", "a2", "a3"]),
    ({"%sort": "name", "%end": -5}, []),
    ({"%sort": "name", "%start": 0}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort": "name", "%start": 3}, ["a4", "a5"]),
    ({"%sort": "name", "%start": 99}, []),
    ({"%sort": "name", "%start": -1}, ["a5"]),
    ({"%sort": "name", "%start": -2}, ["a4", "a5"]),
    ({"%sort": "name", "%start": -6}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort": "name", "%start": 0, "%end": 5}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort": "name", "%start": 1, "%end": 3}, ["a2", "a3"]),
    ({"%sort": "name", "%start": 3, "%end": 99}, ["a4", "a5"]),
    ({"%sort": "name", "%start": 3, "%end": 4}, ["a4"]),
    ({"%sort": "name", "%start": 3, "%end": 3}, []),
    ({"%sort": "name", "%start": 4, "%end": 3}, []),
    ({"%sort": "name", "%start": -5, "%end": -1}, ["a1", "a2", "a3", "a4"]),
    ({"%sort": "name", "%start": -1, "%end": 0}, []),
    ({"%sort": "name", "%start": -3, "%end": -1}, ["a3", "a4"]),
    ({"%sort": "name", "%start": -3, "%end": -2}, ["a3"]),
    ({"%sort": "name", "%start": -3, "%end": 5}, ["a3", "a4", "a5"]),

    ({"%sort_asc": "name"}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort_asc": "name", "%end": 3}, ["a1", "a2", "a3"]),
    ({"%sort_asc": "name", "%end": 99}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort_asc": "name", "%end": 0}, []),
    ({"%sort_asc": "name", "%end": -2}, ["a1", "a2", "a3"]),
    ({"%sort_asc": "name", "%end": -5}, []),
    ({"%sort_asc": "name", "%start": 0}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort_asc": "name", "%start": 3}, ["a4", "a5"]),
    ({"%sort_asc": "name", "%start": 99}, []),
    ({"%sort_asc": "name", "%start": -1}, ["a5"]),
    ({"%sort_asc": "name", "%start": -2}, ["a4", "a5"]),
    ({"%sort_asc": "name", "%start": -6}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort_asc": "name", "%start": 0, "%end": 5}, ["a1", "a2", "a3", "a4", "a5"]),
    ({"%sort_asc": "name", "%start": 1, "%end": 3}, ["a2", "a3"]),
    ({"%sort_asc": "name", "%start": 3, "%end": 99}, ["a4", "a5"]),
    ({"%sort_asc": "name", "%start": 3, "%end": 4}, ["a4"]),
    ({"%sort_asc": "name", "%start": 3, "%end": 3}, []),
    ({"%sort_asc": "name", "%start": 4, "%end": 3}, []),
    ({"%sort_asc": "name", "%start": -5, "%end": -1}, ["a1", "a2", "a3", "a4"]),
    ({"%sort_asc": "name", "%start": -1, "%end": 0}, []),
    ({"%sort_asc": "name", "%start": -3, "%end": -1}, ["a3", "a4"]),
    ({"%sort_asc": "name", "%start": -3, "%end": -2}, ["a3"]),
    ({"%sort_asc": "name", "%start": -3, "%end": 5}, ["a3", "a4", "a5"]),

    ({"%sort_desc": "name"}, ["a5", "a4", "a3", "a2", "a1"]),
    ({"%sort_desc": "name", "%end": 3}, ["a5", "a4", "a3"]),
    ({"%sort_desc": "name", "%end": 99}, ["a5", "a4", "a3", "a2", "a1"]),
    ({"%sort_desc": "name", "%end": 0}, []),
    ({"%sort_desc": "name", "%end": -2}, ["a5", "a4", "a3"]),
    ({"%sort_desc": "name", "%end": -5}, []),
    ({"%sort_desc": "name", "%start": 0}, ["a5", "a4", "a3", "a2", "a1"]),
    ({"%sort_desc": "name", "%start": 3}, ["a2", "a1"]),
    ({"%sort_desc": "name", "%start": 99}, []),
    ({"%sort_desc": "name", "%start": -1}, ["a1"]),
    ({"%sort_desc": "name", "%start": -2}, ["a2", "a1"]),
    ({"%sort_desc": "name", "%start": -6}, ["a5", "a4", "a3", "a2", "a1"]),
    ({"%sort_desc": "name", "%start": 0, "%end": 5}, ["a5", "a4", "a3", "a2", "a1"]),
    ({"%sort_desc": "name", "%start": 1, "%end": 3}, ["a4", "a3"]),
    ({"%sort_desc": "name", "%start": 3, "%end": 99}, ["a2", "a1"]),
    ({"%sort_desc": "name", "%start": 3, "%end": 4}, ["a2"]),
    ({"%sort_desc": "name", "%start": 3, "%end": 3}, []),
    ({"%sort_desc": "name", "%start": 4, "%end": 3}, []),
    ({"%sort_desc": "name", "%start": -5, "%end": -1}, ["a5", "a4", "a3", "a2"]),
    ({"%sort_desc": "name", "%start": -1, "%end": 0}, []),
    ({"%sort_desc": "name", "%start": -3, "%end": -1}, ["a3", "a2"]),
    ({"%sort_desc": "name", "%start": -3, "%end": -2}, ["a3"]),
    ({"%sort_desc": "name", "%start": -3, "%end": 5}, ["a3", "a2", "a1"]),
]

QUERY_ATTR_FILTER_CASES = [
    ({}, ["a1", "a3", "a5", "a2", "a4"]),
    ({"AvatarType": "URL"}, ["a1", "a3", "a5"]),
    ({"AvatarType": "URL", "%sort_desc": "DHCPLeaseInterval"}, ["a5", "a3", "a1"]),
    ({"AvatarType": "URL", "%start": 1, "%end": 2}, ["a3"]),
    ({"AvatarType": "BASE64"}, ["a2", "a4"]),
    ({"AvatarType": "BASE64", "Name": "a2"}, ["a2"]),
    ({"AvatarType": "URL", "Name": "a2"}, []),
    ({"Name": ["a1", "a2", "a3"]}, ["a1", "a3", "a2"]),
    ({"AvatarType": "BASE64", "Name": ["a1", "a2", "a3"]}, ["a2"]),
]

VERSION_OUTPUT = """
APP_GITVERSION = 'r5.3-2bc6ddd'
APP_BUILDVERSION='5.3.3_99'
"""

VERSION_OUTPUT_6 = """
{"vsdBuild":"6.0.1_8","vsdVersion":"6.0.1",
"versions":[{"version":"V6","status":"CURRENT",
"updated":"2019-02-15T11:30:00Z",
"url":"https://vsd1.example.met:8443/nuage/api/v6"},
{"version":"V5.0","status":"DEPRECATED","updated":"2017-02-16T11:30:00Z",
"url":"https://vsd1.example.met:8443/nuage/api/v5_0"}]}
"""

VERSION_OUTPUT_5 = """
{"versions":[{"version":"V5.0","status":"CURRENT",
"updated":"2017-02-16T11:30:00Z",
"url":"https://vsd1.example.com:8443/nuage/api/v5_0"},
{"version":"V4.0","status":"DEPRECATED","updated":"2017-02-16T11:30:00Z",
"url":"https://vsd1.example.com:8443/nuage/api/v4_0"},
{"version":"V3.2","status":"UNSUPPORTED","updated":"2015-01-27T11:30:00Z",
"url":"https://vsd1.example.com:8443/nuage/api/v3_2"},{"version":"V3.1",
"status":"UNSUPPORTED","updated":"2014-10-17T11:30:00Z",
"url":"https://vsd1.example.com:8443/nuage/api/v3_1"},{"version":"V3.0",
"status":"UNSUPPORTED","updated":"2014-07-15T11:30:00Z",
"url":"https://vsd1.example.com:8443/nuage/api/v3_0"},
{"version":"V1.0","status":"UNSUPPORTED","updated":"2014-07-15T11:30:00Z",
"url":"https://vsd1.example.com:8443/nuage/api/v1_0"}]}
"""


@patch("nuage_metroae_config.vsd_writer.Session")
def setup_standard_session(vsd_writer, mock_patch):
    vsd_writer.set_session_params(**SESSION_PARAMS)
    vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

    mock_session = MagicMock()
    mock_session.root_object = MagicMock()
    mock_session.root_object.id = str(uuid.uuid1())
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


@patch("nuage_metroae_config.vsd_writer.Session")
def setup_authentication_less_session(vsd_writer, mock_patch):
    vsd_writer.set_session_params(**SESSION_PARAMS_NO_AUTH)
    vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

    mock_session = MagicMock()
    mock_session.root_object = MagicMock()
    mock_patch.return_value = mock_session
    vsd_writer.start_session()

    mock_patch.assert_called_once_with(spec=vsd_writer.specs['me'],
                                       **EXPECTED_SESSION_PARAMS_NO_AUTH)
    if vsd_writer.validate_only is True:
        mock_session.start.assert_not_called()
    else:
        mock_session.start.assert_called_once()

    mock_session.set_enterprise_spec.assert_called_once_with(
        vsd_writer.specs['enterprise'])
    assert mock_session.root_object.spec == vsd_writer.specs['me']

    return mock_session


@patch("nuage_metroae_config.vsd_writer.Session")
def setup_authentication_no_certificate_session(vsd_writer, mock_patch):
    vsd_writer.set_session_params(**SESSION_PARAMS_NO_CERTIFICATE)
    vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

    mock_session = MagicMock()
    mock_session.root_object = MagicMock()
    mock_patch.return_value = mock_session
    vsd_writer.start_session()

    mock_patch.assert_called_once_with(spec=vsd_writer.specs['me'],
                                       **EXPECTED_SESSION_PARAMS_NO_CERTIFICATE)
    if vsd_writer.validate_only is True:
        mock_session.start.assert_not_called()
    else:
        mock_session.start.assert_called_once()

    mock_session.set_enterprise_spec.assert_called_once_with(
        vsd_writer.specs['enterprise'])
    assert mock_session.root_object.spec == vsd_writer.specs['me']

    return mock_session


@patch("nuage_metroae_config.vsd_writer.Session")
def setup_authentication_no_certificate_key_session(vsd_writer, mock_patch):
    vsd_writer.set_session_params(**SESSION_PARAMS_NO_CERTIFICATE_KEY)
    vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

    mock_session = MagicMock()
    mock_session.root_object = MagicMock()
    mock_patch.return_value = mock_session
    vsd_writer.start_session()

    mock_patch.assert_called_once_with(spec=vsd_writer.specs['me'],
                                       **EXPECTED_SESSION_PARAMS_NO_CERTIFICATE_KEY)
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
    def test_start__no_certificate__no_password(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(MissingSessionParamsError) as e:
            setup_authentication_less_session(vsd_writer)

        assert "without password or certificate" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_start__no_certificate_file__no_password(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(MissingSessionParamsError) as e:
            setup_authentication_no_certificate_session(vsd_writer)

        assert "without password or certificate" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_start__no_certificate_key__no_password(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(MissingSessionParamsError) as e:
            setup_authentication_no_certificate_key_session(vsd_writer)

        assert "without password or certificate" in str(e)

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

    @patch("nuage_metroae_config.vsd_writer.Session")
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
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
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
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
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
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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

    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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

    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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

    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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
            assert len(objects) == 1
        else:
            mock_fetcher.get.assert_called_once_with()

            assert len(objects) == 1
            assert objects[0].parent_object is None
            assert objects[0].current_object == "selected object"
            assert objects[0].object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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
            assert len(objects) == 1
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

    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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

    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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

    @patch("nuage_metroae_config.vsd_writer.Fetcher")
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

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
    def test_assign_new__success(self, mock_fetcher, mock_object,
                                 validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = []

        child_object = MagicMock()
        mock_object.return_value = child_object

        if validate_only is True:
            mock_session.root_object = MagicMock()
            mock_session.root_object.spec = vsd_writer.specs['me']

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"
        mock_object.validate.return_value = True
        mock_object.assign.return_value = True

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = False

        values = {
            "name": "test_enterprise",
            "assign(domain)": "abcd-1234"
        }

        new_context = vsd_writer.set_values(context, **values)

        assert mock_object.name == 'test_enterprise'
        mock_object.validate.assert_called_once()

        if validate_only is True:
            mock_session.root_object.create_child.assert_not_called()
            mock_object.assign.assert_not_called()
        else:
            mock_session.root_object.current_child_name == "enterprises"
            mock_session.root_object.create_child.assert_called_once_with(
                mock_object)
            mock_object.assign.assert_called_once_with([child_object],
                                                       nurest_object_type=None)
            assert mock_object.current_child_name == "domains"
            assert child_object.id == "abcd-1234"

        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
    def test_assign_update__success(self, mock_fetcher, mock_object,
                                    validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = []

        child_object = MagicMock()
        mock_object.return_value = child_object

        if validate_only is True:
            mock_session.root_object = MagicMock()
            mock_session.root_object.spec = vsd_writer.specs['me']

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"
        mock_object.validate.return_value = True
        mock_object.assign.return_value = True

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        values = {
            "name": "test_enterprise",
            "assign(domain)": "abcd-1234"
        }

        new_context = vsd_writer.set_values(context, **values)

        assert mock_object.name == 'test_enterprise'
        mock_object.validate.assert_called_once()

        if validate_only is True:
            mock_session.root_object.save.assert_not_called()
            mock_object.assign.assert_not_called()
        else:
            mock_session.root_object.current_child_name == "enterprises"
            mock_object.save.assert_called_once_with()
            mock_object.assign.assert_called_once_with([child_object],
                                                       nurest_object_type=None)
            assert mock_object.current_child_name == "domains"
            assert child_object.id == "abcd-1234"

        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
    def test_assign_skip_save__success(self, mock_fetcher, mock_object,
                                       validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = []

        child_object = MagicMock()
        mock_object.return_value = child_object

        if validate_only is True:
            mock_session.root_object = MagicMock()
            mock_session.root_object.spec = vsd_writer.specs['me']

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"
        mock_object.validate.return_value = True
        mock_object.assign.return_value = True

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        values = {
            "assign(domain)": "abcd-1234"
        }

        new_context = vsd_writer.set_values(context, **values)

        mock_object.validate.assert_called_once()

        if validate_only is True:
            mock_session.root_object.save.assert_not_called()
            mock_object.assign.assert_not_called()
        else:
            mock_session.root_object.current_child_name == "enterprises"
            mock_object.save.assert_not_called()
            mock_object.assign.assert_called_once_with([child_object],
                                                       nurest_object_type=None)
            assert mock_object.current_child_name == "domains"
            assert child_object.id == "abcd-1234"

        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
    def test_assign_multiple__success(self, mock_fetcher, mock_object,
                                      validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        existing_object_1 = MagicMock()
        existing_object_1.id = "existing1"
        existing_object_2 = MagicMock()
        existing_object_2.id = "existing2"

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = [existing_object_1, existing_object_2]

        new_object_1 = MagicMock()
        new_object_2 = MagicMock()
        new_object_3 = MagicMock()
        new_object_4 = MagicMock()
        mock_object.side_effect = [new_object_1,
                                   new_object_2,
                                   new_object_3,
                                   new_object_4]

        if validate_only is True:
            mock_session.root_object = MagicMock()
            mock_session.root_object.spec = vsd_writer.specs['me']

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"
        mock_object.validate.return_value = True
        mock_object.assign.return_value = True

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        values = {
            "name": "test_enterprise",
            "assign(domain)": ["existing2", "new1", "new2"]
        }

        new_context = vsd_writer.set_values(context, **values)

        assert mock_object.name == 'test_enterprise'
        mock_object.validate.assert_called_once()

        if validate_only is True:
            mock_session.root_object.save.assert_not_called()
            mock_object.assign.assert_not_called()
        else:
            mock_session.root_object.current_child_name == "enterprises"
            mock_object.save.assert_called_once_with()
            mock_object.assign.assert_called_once_with([existing_object_1,
                                                        existing_object_2,
                                                        new_object_1,
                                                        new_object_2],
                                                       nurest_object_type=None)
            assert mock_object.current_child_name == "domains"
            assert new_object_1.id == "new1"
            assert new_object_2.id == "new2"

        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
    def test_assign__bambou_error(self, mock_fetcher, mock_object):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = []

        child_object = MagicMock()
        mock_object.return_value = child_object

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"
        mock_object.validate.return_value = True

        fake_exception = get_mock_bambou_error(404, "not found")
        mock_object.assign.side_effect = fake_exception

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        values = {
            "name": "test_enterprise",
            "assign(domain)": "abcd-1234"
        }

        with pytest.raises(VsdError) as e:
            vsd_writer.set_values(context, **values)

        assert "404" in str(e)
        assert "not found" in str(e)

        assert "Saving" in e.value.get_display_string()
        assert "HTTP 404" in e.value.get_display_string()

        assert mock_object.name == 'test_enterprise'
        mock_object.validate.assert_called_once()

        mock_session.root_object.current_child_name == "enterprises"
        mock_object.save.assert_called_once_with()


class TestVsdWriterUnsetValues(object):

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_session(self, validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.unset_values("context", name="test_enterprise")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
    def test_unassign__success(self, mock_fetcher, mock_object,
                               validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        existing_object_1 = MagicMock()
        existing_object_1.id = "abcd-1234"

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = [existing_object_1]

        child_object = MagicMock()
        mock_object.return_value = child_object

        if validate_only is True:
            mock_session.root_object = MagicMock()
            mock_session.root_object.spec = vsd_writer.specs['me']

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"
        mock_object.validate.return_value = True
        mock_object.assign.return_value = True

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        values = {
            "name": "test_enterprise",
            "assign(domain)": "abcd-1234"
        }

        new_context = vsd_writer.unset_values(context, **values)

        if validate_only is True:
            mock_object.assign.assert_not_called()
        else:
            mock_object.assign.assert_called_once_with([],
                                                       nurest_object_type=None)
            assert mock_object.current_child_name == "domains"

        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
    def test_unassign_multiple__success(self, mock_fetcher, mock_object,
                                        validate_only):
        vsd_writer = VsdWriter()
        vsd_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(vsd_writer)

        existing_object_1 = MagicMock()
        existing_object_1.id = "existing1"
        existing_object_2 = MagicMock()
        existing_object_2.id = "existing2"
        existing_object_3 = MagicMock()
        existing_object_3.id = "existing3"

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = [existing_object_1,
                                         existing_object_2,
                                         existing_object_3]

        child_object = MagicMock()
        mock_object.return_value = child_object

        if validate_only is True:
            mock_session.root_object = MagicMock()
            mock_session.root_object.spec = vsd_writer.specs['me']

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"
        mock_object.validate.return_value = True
        mock_object.assign.return_value = True

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        values = {
            "name": "test_enterprise",
            "assign(domain)": ["noexist", "existing1", "existing3"]
        }

        new_context = vsd_writer.unset_values(context, **values)

        if validate_only is True:
            mock_object.assign.assert_not_called()
        else:
            mock_object.assign.assert_called_once_with([existing_object_2],
                                                       nurest_object_type=None)
            assert mock_object.current_child_name == "domains"

        assert new_context.parent_object is None
        assert new_context.current_object == mock_object
        assert new_context.object_exists is True

    @patch("nuage_metroae_config.vsd_writer.ConfigObject")
    @patch("nuage_metroae_config.vsd_writer.Fetcher")
    def test_unassign__bambou_error(self, mock_fetcher, mock_object):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        existing_object_1 = MagicMock()
        existing_object_1.id = "abcd-1234"

        mock_fetcher.return_value = mock_fetcher
        mock_fetcher.get.return_value = [existing_object_1]

        child_object = MagicMock()
        mock_object.return_value = child_object

        mock_object = MagicMock()
        mock_object.spec = vsd_writer.specs['enterprise']
        mock_object.__resource_name__ = "enterprises"
        mock_object.validate.return_value = True

        fake_exception = get_mock_bambou_error(404, "not found")
        mock_object.assign.side_effect = fake_exception

        context = Context()
        context.parent_object = None
        context.current_object = mock_object
        context.object_exists = True

        values = {
            "name": "test_enterprise",
            "assign(domain)": "abcd-1234"
        }

        with pytest.raises(VsdError) as e:
            vsd_writer.unset_values(context, **values)

        assert "404" in str(e)
        assert "not found" in str(e)

        assert "Unset" in e.value.get_display_string()
        assert "HTTP 404" in e.value.get_display_string()


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


class TestVsdWriterVersion(object):

    @patch("requests.get")
    def test_get_version_6__success(self, mock_request):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = json.loads(VERSION_OUTPUT_6)
        mock_request.return_value = mock_response

        vsd_writer = VsdWriter()
        vsd_writer.set_session_params("https://localhost:8443")
        version = vsd_writer.get_version()

        mock_request.assert_called_once_with(
            "https://localhost:8443/nuage",
            verify=False)

        assert version == {
            "software_type": "Nuage Networks VSD",
            "software_version": "6.0.1"}

    @patch("requests.get")
    def test_get_version_5__success(self, mock_request):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = json.loads(VERSION_OUTPUT_5)
        mock_response.text = VERSION_OUTPUT
        mock_request.return_value = mock_response

        vsd_writer = VsdWriter()
        vsd_writer.set_session_params("https://localhost:8443")
        version = vsd_writer.get_version()

        mock_request.assert_any_call(
            "https://localhost:8443/nuage",
            verify=False)

        mock_request.assert_any_call(
            "https://localhost:8443/architect/Resources/app-version.js",
            verify=False)

        assert version == {
            "software_type": "Nuage Networks VSD",
            "software_version": "5.3.3"}

    @patch("requests.get")
    def test_get_version__bad_response(self, mock_request):

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Not found"
        mock_request.return_value = mock_response

        vsd_writer = VsdWriter()
        vsd_writer.set_session_params("https://localhost:8443")
        version = vsd_writer.get_version()

        mock_request.assert_any_call(
            "https://localhost:8443/nuage",
            verify=False)

        mock_request.assert_any_call(
            "https://localhost:8443/architect/Resources/app-version.js",
            verify=False)

        assert version == {
            "software_type": None,
            "software_version": None}

    @patch("requests.get")
    def test_get_version__legacy_success(self, mock_request):

        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = json.loads(VERSION_OUTPUT_5)
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 404
        mock_response_2.text = "Not found"
        mock_response_3 = MagicMock()
        mock_response_3.status_code = 200
        mock_response_3.text = VERSION_OUTPUT
        mock_request.side_effect = [mock_response_1, mock_response_2,
                                    mock_response_3]

        vsd_writer = VsdWriter()
        vsd_writer.set_session_params("https://localhost:8443")
        version = vsd_writer.get_version()

        mock_request.assert_any_call(
            "https://localhost:8443/nuage",
            verify=False)

        mock_request.assert_any_call(
            "https://localhost:8443/architect/Resources/app-version.js",
            verify=False)

        mock_request.assert_any_call(
            "https://localhost:8443/Resources/app-version.js",
            verify=False)

        assert version == {
            "software_type": "Nuage Networks VSD",
            "software_version": "5.3.3"}

    @patch("requests.get")
    def test_get_version__legacy_failure(self, mock_request):

        mock_response_1 = MagicMock()
        mock_response_1.status_code = 404
        mock_response_1.text = "Not found"
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 404
        mock_response_2.text = "Not Found"
        mock_request.side_effect = [mock_response_1, mock_response_2]

        vsd_writer = VsdWriter()
        vsd_writer.set_session_params("https://localhost:8443")
        version = vsd_writer.get_version()

        mock_request.assert_any_call(
            "https://localhost:8443/nuage",
            verify=False)

        mock_request.assert_any_call(
            "https://localhost:8443/architect/Resources/app-version.js",
            verify=False)

        mock_request.assert_any_call(
            "https://localhost:8443/Resources/app-version.js",
            verify=False)

        assert version == {
            "software_type": None,
            "software_version": None}

    @patch("requests.get")
    def test_get_version__not_parsable(self, mock_request):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = json.loads(VERSION_OUTPUT_5)
        mock_response.text = "INVALID version"
        mock_request.return_value = mock_response

        vsd_writer = VsdWriter()
        vsd_writer.set_session_params("https://localhost:8443")
        version = vsd_writer.get_version()

        mock_request.assert_any_call(
            "https://localhost:8443/nuage",
            verify=False)

        mock_request.assert_any_call(
            "https://localhost:8443/architect/Resources/app-version.js",
            verify=False)

        assert version == {
            "software_type": None,
            "software_version": None}

    def test_set_software_version__success(self):

        vsd_writer = VsdWriter()

        vsd_writer.set_software_version("4.0.R11")
        assert vsd_writer.version == "5.0"

        vsd_writer.set_software_version("5.4.1")
        assert vsd_writer.version == "5.0"

        vsd_writer.set_software_version("6.0.3")
        assert vsd_writer.version == "6"

        vsd_writer.set_software_version("20.5.R1")
        assert vsd_writer.version == "6"


class TestVsdWriterQuery(object):

    def create_mock_query_object(self, attr_dict):
        mock_object = MagicMock()
        mock_object.id = str(uuid.uuid1())
        mock_object._attributes = attr_dict
        mock_object.unknown = None
        for attr_name, value in attr_dict.items():
            setattr(mock_object, attr_name, value)

        return mock_object

    def add_mock_objects_to_vsd_writer(self, vsd_writer, get_object_calls):
        mock_get_object_list = MagicMock()
        mock_get_object_list.side_effect = get_object_calls
        vsd_writer._get_object_list = mock_get_object_list
        return mock_get_object_list

    @patch("nuage_metroae_config.vsd_writer.Session")
    def test_connect__success(self, mock_patch):
        vsd_writer = VsdWriter()

        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        mock_session = MagicMock()
        mock_session.root_object = MagicMock()
        mock_patch.return_value = mock_session

        vsd_writer.connect(SESSION_PARAMS["url"],
                           SESSION_PARAMS["username"],
                           SESSION_PARAMS["password"],
                           SESSION_PARAMS["enterprise"])

        expected_params = dict(EXPECTED_SESSION_PARAMS)
        del expected_params["certificate"]

        mock_patch.assert_called_once_with(spec=vsd_writer.specs['me'],
                                           **expected_params)

        mock_session.start.assert_called_once()

        mock_session.set_enterprise_spec.assert_called_once_with(
            vsd_writer.specs['enterprise'])
        assert mock_session.root_object.spec == vsd_writer.specs['me']

        mock_session.start.assert_called_once()

        mock_session.set_enterprise_spec.assert_called_once_with(
            vsd_writer.specs['enterprise'])

    @patch("nuage_metroae_config.vsd_writer.Session")
    def test_connect_certificate__success(self, mock_patch):
        vsd_writer = VsdWriter()

        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        mock_session = MagicMock()
        mock_session.root_object = MagicMock()
        mock_patch.return_value = mock_session

        vsd_writer.connect(SESSION_PARAMS["url"],
                           SESSION_PARAMS["username"],
                           SESSION_PARAMS["password"],
                           SESSION_PARAMS["enterprise"],
                           SESSION_PARAMS["certificate"][0],
                           SESSION_PARAMS["certificate"][1])

        mock_patch.assert_called_once_with(spec=vsd_writer.specs['me'],
                                           **EXPECTED_SESSION_PARAMS)

        mock_session.start.assert_called_once()

        mock_session.set_enterprise_spec.assert_called_once_with(
            vsd_writer.specs['enterprise'])
        assert mock_session.root_object.spec == vsd_writer.specs['me']

        mock_session.start.assert_called_once()

    @patch("nuage_metroae_config.vsd_writer.Session")
    def test_connect_existing__success(self, mock_patch):
        vsd_writer = VsdWriter()

        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)
        vsd_writer.set_session_params(**SESSION_PARAMS)

        mock_session_old = MagicMock()
        mock_session_old.root_object = MagicMock()
        mock_patch.return_value = mock_session_old

        vsd_writer.start_session()

        mock_patch.assert_called_once_with(spec=vsd_writer.specs['me'],
                                           **EXPECTED_SESSION_PARAMS)

        mock_session = MagicMock()
        mock_session.root_object = MagicMock()
        mock_patch.return_value = mock_session

        vsd_writer.connect("https://newurl:8443", "newuser", "newpass",
                           "newent")

        mock_patch.assert_called_with(spec=vsd_writer.specs['me'],
                                      **{"api_url": "https://newurl:8443",
                                         "username": "newuser",
                                         "password": "newpass",
                                         "enterprise": "newent",
                                         "version": "6",
                                         "api_prefix": "nuage/api"})

        mock_session.start.assert_called_once()

        mock_session.set_enterprise_spec.assert_called_once_with(
            vsd_writer.specs['enterprise'])
        assert mock_session.root_object.spec == vsd_writer.specs['me']

        mock_session.start.assert_called_once()

        mock_session.set_enterprise_spec.assert_called_once_with(
            vsd_writer.specs['enterprise'])

    @patch("nuage_metroae_config.vsd_writer.Session")
    def test_connect_defaults__success(self, mock_patch):
        vsd_writer = VsdWriter()

        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        mock_session = MagicMock()
        mock_session.root_object = MagicMock()
        mock_patch.return_value = mock_session

        vsd_writer.connect(SESSION_PARAMS["url"])

        expected_params = dict(EXPECTED_SESSION_PARAMS)
        del expected_params["certificate"]
        expected_params["username"] = "csproot"
        expected_params["password"] = "csproot"
        expected_params["enterprise"] = "csp"

        mock_patch.assert_called_once_with(spec=vsd_writer.specs['me'],
                                           **expected_params)

        mock_session.start.assert_called_once()

        mock_session.set_enterprise_spec.assert_called_once_with(
            vsd_writer.specs['enterprise'])
        assert mock_session.root_object.spec == vsd_writer.specs['me']

        mock_session.start.assert_called_once()

        mock_session.set_enterprise_spec.assert_called_once_with(
            vsd_writer.specs['enterprise'])

    @patch("nuage_metroae_config.vsd_writer.Session")
    def test_connect__no_args(self, mock_patch):
        vsd_writer = VsdWriter()

        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        mock_session = MagicMock()
        mock_session.root_object = MagicMock()
        mock_patch.return_value = mock_session

        with pytest.raises(SessionError) as e:
            vsd_writer.connect()

        assert "parameter is required" in str(e)

        mock_patch.assert_not_called()
        mock_session.start.assert_not_called()

    @patch("nuage_metroae_config.vsd_writer.Session")
    def test_connect__missing_cert_key(self, mock_patch):
        vsd_writer = VsdWriter()

        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        mock_session = MagicMock()
        mock_session.root_object = MagicMock()
        mock_patch.return_value = mock_session

        with pytest.raises(SessionError) as e:
            vsd_writer.connect(SESSION_PARAMS["url"],
                               SESSION_PARAMS["username"],
                               SESSION_PARAMS["password"],
                               SESSION_PARAMS["enterprise"],
                               SESSION_PARAMS["certificate"][0])

        assert "key parameter is required" in str(e)

        mock_patch.assert_not_called()
        mock_session.start.assert_not_called()

    @patch("nuage_metroae_config.vsd_writer.Session")
    def test_connect__extra_args(self, mock_patch):
        vsd_writer = VsdWriter()

        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        mock_session = MagicMock()
        mock_session.root_object = MagicMock()
        mock_patch.return_value = mock_session

        with pytest.raises(SessionError) as e:
            vsd_writer.connect(SESSION_PARAMS["url"],
                               SESSION_PARAMS["username"],
                               SESSION_PARAMS["password"],
                               SESSION_PARAMS["enterprise"],
                               SESSION_PARAMS["certificate"][0],
                               SESSION_PARAMS["certificate"][1],
                               "too many")

        assert "Too many arguments" in str(e)

        mock_patch.assert_not_called()
        mock_session.start.assert_not_called()

    @patch("nuage_metroae_config.vsd_writer.Session")
    def test_connect__bambou_error(self, mock_patch):
        vsd_writer = VsdWriter()
        vsd_writer.set_session_params(**SESSION_PARAMS)
        vsd_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        mock_session = MagicMock()
        mock_patch.return_value = mock_session
        fake_exception = get_mock_bambou_error(403, 'forbidden')
        mock_session.start.side_effect = fake_exception

        with pytest.raises(VsdError) as e:
            vsd_writer.connect(SESSION_PARAMS["url"])

        assert "403" in str(e)
        assert "forbidden" in str(e)

        assert "Session start" in e.value.get_display_string()
        assert "HTTP 403" in e.value.get_display_string()

    def test_query__no_session(self):
        vsd_writer = VsdWriter()

        objects = [
            {"name": "Enterprise",
             "filter": None}
        ]

        attributes = "name"

        with pytest.raises(SessionNotStartedError) as e:
            vsd_writer.query(objects, attributes)

        assert "not started" in str(e)

    def test_attrs_single__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None}
        ]

        attributes = "Name"

        mock_ent = self.create_mock_query_object({"name": "enterprise_1",
                                                  "bgpenabled": True,
                                                  "dhcpleaseinterval": 600})

        calls = [
            [mock_ent]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == ["enterprise_1"]

        mock_get.assert_has_calls([call("Enterprise",
                                        mock_session.root_object)])

    def test_attrs_single__unknown(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None}
        ]

        attributes = "unknown"

        mock_ent = self.create_mock_query_object({"name": "enterprise_1",
                                                  "bgpenabled": True,
                                                  "dhcpleaseinterval": 600})

        calls = [
            [mock_ent]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == []

        mock_get.assert_has_calls([call("Enterprise",
                                        mock_session.root_object)])

    def test_attrs_multiple__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None}
        ]

        attributes = ["Name", "DHCPLeaseInterval"]

        mock_ent = self.create_mock_query_object({"name": "enterprise_1",
                                                  "bgpenabled": True,
                                                  "dhcpleaseinterval": 600})

        calls = [
            [mock_ent]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == [{"Name": "enterprise_1", "DHCPLeaseInterval": 600}]

        mock_get.assert_has_calls([call("Enterprise",
                                        mock_session.root_object)])

    def test_attrs_multiple__unknown(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None}
        ]

        attributes = ["Name", "DHCPLeaseInterval", "unknown"]

        mock_ent = self.create_mock_query_object({"name": "enterprise_1",
                                                  "bgpenabled": True,
                                                  "dhcpleaseinterval": 600})

        calls = [
            [mock_ent]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == [{"Name": "enterprise_1", "DHCPLeaseInterval": 600}]

        mock_get.assert_has_calls([call("Enterprise",
                                        mock_session.root_object)])

    def test_attrs_all__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None}
        ]

        attributes = ["*"]

        mock_ent = self.create_mock_query_object({"name": "enterprise_1",
                                                  "bgpenabled": True,
                                                  "dhcpleaseinterval": 600})

        calls = [
            [mock_ent]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == [{"name": "enterprise_1",
                            "bgpenabled": True,
                            "dhcpleaseinterval": 600}]

        mock_get.assert_has_calls([call("Enterprise",
                                        mock_session.root_object)])

    def test_object_single__none_found(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
        ]

        attributes = "Name"

        calls = [
            []
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == []

        mock_get.assert_has_calls([call("Enterprise",
                                        mock_session.root_object)])

    def test_object_single__bambou_error(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
        ]

        attributes = "Name"

        calls = [
            get_mock_bambou_error(403, "forbidden")
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        with pytest.raises(VsdError) as e:
            vsd_writer.query(objects, attributes)

        assert "403" in str(e)
        assert "forbidden" in str(e)

        assert "Query" in e.value.get_display_string()
        assert "HTTP 403" in e.value.get_display_string()

        mock_get.assert_has_calls([call("Enterprise",
                                        mock_session.root_object)])

    def test_object_multiple__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1"})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2"})
        mock_ent_3 = self.create_mock_query_object({"name": "enterprise_3"})

        calls = [
            [mock_ent_1, mock_ent_2, mock_ent_3]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == ["enterprise_1", "enterprise_2", "enterprise_3"]

        mock_get.assert_has_calls([call("Enterprise",
                                        mock_session.root_object)])

    def test_object_multiple_2__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
        ]

        attributes = ["Name", "DHCPLeaseInterval"]

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1",
                                                    "dhcpleaseinterval": 100})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2",
                                                    "dhcpleaseinterval": 200})
        mock_ent_3 = self.create_mock_query_object({"name": "enterprise_3",
                                                    "dhcpleaseinterval": 300})

        calls = [
            [mock_ent_1, mock_ent_2, mock_ent_3]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == [{"Name": "enterprise_1",
                            "DHCPLeaseInterval": 100},
                           {"Name": "enterprise_2",
                            "DHCPLeaseInterval": 200},
                           {"Name": "enterprise_3",
                            "DHCPLeaseInterval": 300}]

        mock_get.assert_has_calls([call("Enterprise",
                                        mock_session.root_object)])

    def test_nested_object_multiple__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
            {"name": "Domain",
             "filter": None},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1"})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2"})
        mock_dom_1 = self.create_mock_query_object({"name": "domain_1"})
        mock_dom_2 = self.create_mock_query_object({"name": "domain_2"})
        mock_dom_3 = self.create_mock_query_object({"name": "domain_3"})
        mock_dom_4 = self.create_mock_query_object({"name": "domain_4"})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]
        mock_ent_2.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1, mock_ent_2],
            [mock_dom_1, mock_dom_2],
            [mock_dom_3, mock_dom_4]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == ["domain_1", "domain_2", "domain_3", "domain_4"]

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_1),
            call("Domain", mock_ent_2),
        ])

    def test_cache_root__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": {"%sort": "dhcpleaseinterval"}},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1",
                                                    "dhcpleaseinterval": 20})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2",
                                                    "dhcpleaseinterval": 10})

        calls = [
            [mock_ent_1, mock_ent_2],
            get_mock_bambou_error(400, "Should have cached result")
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)
        assert results == ["enterprise_2", "enterprise_1"]

        objects = [
            {"name": "Enterprise",
             "filter": None},
        ]

        attributes = "DHCPLeaseInterval"

        results = vsd_writer.query(objects, attributes)
        assert results == [20, 10]

        mock_get.assert_called_once_with("Enterprise",
                                         mock_session.root_object)

        objects = [
            {"name": "Domain",
             "filter": None},
        ]

        with pytest.raises(VsdError) as e:
            vsd_writer.query(objects, attributes)

        assert "400" in str(e)
        assert "Should have cached result" in str(e)

    def test_cache_nested__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": {"%sort": "dhcpleaseinterval"}},
            {"name": "Domain",
             "filter": None},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1",
                                                    "dhcpleaseinterval": 20})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2",
                                                    "dhcpleaseinterval": 10})
        mock_dom_1 = self.create_mock_query_object({"name": "domain_1",
                                                    "bgpenabled": True})
        mock_dom_2 = self.create_mock_query_object({"name": "domain_2",
                                                    "bgpenabled": False})
        mock_dom_3 = self.create_mock_query_object({"name": "domain_3",
                                                    "bgpenabled": True})
        mock_dom_4 = self.create_mock_query_object({"name": "domain_4",
                                                    "bgpenabled": True})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]
        mock_ent_2.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1, mock_ent_2],
            [mock_dom_3, mock_dom_4],
            [mock_dom_1, mock_dom_2],
            get_mock_bambou_error(400, "Should have cached result")
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)
        assert results == ["domain_3", "domain_4", "domain_1", "domain_2"]

        objects = [
            {"name": "Enterprise",
             "filter": None},
            {"name": "Domain",
             "filter": None},
        ]

        attributes = "BGPEnabled"

        results = vsd_writer.query(objects, attributes)
        assert results == [True, False, True, True]

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_2),
            call("Domain", mock_ent_1),
        ])

        objects = [
            {"name": "Domain",
             "filter": None},
        ]

        with pytest.raises(VsdError) as e:
            vsd_writer.query(objects, attributes)

        assert "400" in str(e)
        assert "Should have cached result" in str(e)

    def test_group_parent__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": {"%group": "DHCPLeaseInterval"}},
            {"name": "Domain",
             "filter": None},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1",
                                                    "dhcpleaseinterval": 10})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2",
                                                    "dhcpleaseinterval": 20})
        mock_ent_3 = self.create_mock_query_object({"name": "enterprise_3",
                                                    "dhcpleaseinterval": 10})
        mock_ent_4 = self.create_mock_query_object({"name": "enterprise_4",
                                                    "dhcpleaseinterval": 30})
        mock_dom_1 = self.create_mock_query_object({"name": "domain_1",
                                                    "bgpenabled": True})
        mock_dom_2 = self.create_mock_query_object({"name": "domain_2",
                                                    "bgpenabled": False})
        mock_dom_3 = self.create_mock_query_object({"name": "domain_3",
                                                    "bgpenabled": True})
        mock_dom_4 = self.create_mock_query_object({"name": "domain_4",
                                                    "bgpenabled": True})
        mock_dom_5 = self.create_mock_query_object({"name": "domain_5",
                                                    "bgpenabled": True})
        mock_dom_6 = self.create_mock_query_object({"name": "domain_6",
                                                    "bgpenabled": True})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]
        mock_ent_2.spec = vsd_writer.specs["enterprise"]
        mock_ent_3.spec = vsd_writer.specs["enterprise"]
        mock_ent_4.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1, mock_ent_2, mock_ent_3, mock_ent_4],
            [mock_dom_1, mock_dom_2],
            [mock_dom_3, mock_dom_4],
            [],
            [mock_dom_5, mock_dom_6]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == [
            [10,
                ["domain_1", "domain_2", "domain_3", "domain_4"]],
            [20,
                []],
            [30,
                ["domain_5", "domain_6"]]
        ]

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_1),
            call("Domain", mock_ent_3),
            call("Domain", mock_ent_2),
            call("Domain", mock_ent_4),
        ])

    def test_group_child__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
            {"name": "Domain",
             "filter": {"%group": "BGPEnabled"}},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1",
                                                    "dhcpleaseinterval": 10})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2",
                                                    "dhcpleaseinterval": 20})
        mock_ent_3 = self.create_mock_query_object({"name": "enterprise_3",
                                                    "dhcpleaseinterval": 10})
        mock_ent_4 = self.create_mock_query_object({"name": "enterprise_4",
                                                    "dhcpleaseinterval": 30})
        mock_dom_1 = self.create_mock_query_object({"name": "domain_1",
                                                    "bgpenabled": True})
        mock_dom_2 = self.create_mock_query_object({"name": "domain_2",
                                                    "bgpenabled": False})
        mock_dom_3 = self.create_mock_query_object({"name": "domain_3",
                                                    "bgpenabled": True})
        mock_dom_4 = self.create_mock_query_object({"name": "domain_4",
                                                    "bgpenabled": True})
        mock_dom_5 = self.create_mock_query_object({"name": "domain_5",
                                                    "bgpenabled": True})
        mock_dom_6 = self.create_mock_query_object({"name": "domain_6",
                                                    "bgpenabled": True})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]
        mock_ent_2.spec = vsd_writer.specs["enterprise"]
        mock_ent_3.spec = vsd_writer.specs["enterprise"]
        mock_ent_4.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1, mock_ent_2, mock_ent_3, mock_ent_4],
            [mock_dom_1, mock_dom_2],
            [],
            [mock_dom_3, mock_dom_4],
            [mock_dom_5, mock_dom_6]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == [
            [True,
                ["domain_1", "domain_3", "domain_4", "domain_5", "domain_6"]],
            [False,
                ["domain_2"]]
        ]

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_1),
            call("Domain", mock_ent_2),
            call("Domain", mock_ent_3),
            call("Domain", mock_ent_4),
        ])

    def test_group_both__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": {"%group": "DHCPLeaseInterval"}},
            {"name": "Domain",
             "filter": {"%group": "BGPEnabled"}},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1",
                                                    "dhcpleaseinterval": 10})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2",
                                                    "dhcpleaseinterval": 20})
        mock_ent_3 = self.create_mock_query_object({"name": "enterprise_3",
                                                    "dhcpleaseinterval": 10})
        mock_ent_4 = self.create_mock_query_object({"name": "enterprise_4",
                                                    "dhcpleaseinterval": 30})
        mock_dom_1 = self.create_mock_query_object({"name": "domain_1",
                                                    "bgpenabled": True})
        mock_dom_2 = self.create_mock_query_object({"name": "domain_2",
                                                    "bgpenabled": False})
        mock_dom_3 = self.create_mock_query_object({"name": "domain_3",
                                                    "bgpenabled": True})
        mock_dom_4 = self.create_mock_query_object({"name": "domain_4",
                                                    "bgpenabled": True})
        mock_dom_5 = self.create_mock_query_object({"name": "domain_5",
                                                    "bgpenabled": True})
        mock_dom_6 = self.create_mock_query_object({"name": "domain_6",
                                                    "bgpenabled": True})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]
        mock_ent_2.spec = vsd_writer.specs["enterprise"]
        mock_ent_3.spec = vsd_writer.specs["enterprise"]
        mock_ent_4.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1, mock_ent_2, mock_ent_3, mock_ent_4],
            [mock_dom_1, mock_dom_2],
            [mock_dom_3, mock_dom_4],
            [],
            [mock_dom_5, mock_dom_6]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == [
            [10,
                [[True,
                    ["domain_1", "domain_3", "domain_4"]],
                 [False,
                    ["domain_2"]]]],
            [20,
                []],
            [30,
                [[True,
                    ["domain_5", "domain_6"]]]]
        ]

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_1),
            call("Domain", mock_ent_3),
            call("Domain", mock_ent_2),
            call("Domain", mock_ent_4),
        ])

    def test_group_both_filtered__success(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": {"%group": "DHCPLeaseInterval",
                        "DHCPLeaseInterval": [10, 20]}},
            {"name": "Domain",
             "filter": {"%group": "BGPEnabled",
                        "BGPEnabled": True}},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1",
                                                    "dhcpleaseinterval": 10})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2",
                                                    "dhcpleaseinterval": 20})
        mock_ent_3 = self.create_mock_query_object({"name": "enterprise_3",
                                                    "dhcpleaseinterval": 10})
        mock_ent_4 = self.create_mock_query_object({"name": "enterprise_4",
                                                    "dhcpleaseinterval": 30})
        mock_dom_1 = self.create_mock_query_object({"name": "domain_1",
                                                    "bgpenabled": True})
        mock_dom_2 = self.create_mock_query_object({"name": "domain_2",
                                                    "bgpenabled": False})
        mock_dom_3 = self.create_mock_query_object({"name": "domain_3",
                                                    "bgpenabled": True})
        mock_dom_4 = self.create_mock_query_object({"name": "domain_4",
                                                    "bgpenabled": True})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]
        mock_ent_2.spec = vsd_writer.specs["enterprise"]
        mock_ent_3.spec = vsd_writer.specs["enterprise"]
        mock_ent_4.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1, mock_ent_2, mock_ent_3, mock_ent_4],
            [mock_dom_1, mock_dom_2],
            [mock_dom_3, mock_dom_4],
            []
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == [
            [10,
                [[True,
                    ["domain_1", "domain_3", "domain_4"]]]],
            [20,
                [[True,
                    []]]]
        ]

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_1),
            call("Domain", mock_ent_3),
            call("Domain", mock_ent_2),
        ])

    def test_nested_object_multiple__empty_child(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
            {"name": "Domain",
             "filter": None},
        ]

        attributes = ["*"]

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1"})
        mock_ent_2 = self.create_mock_query_object({"name": "enterprise_2"})
        mock_dom_3 = self.create_mock_query_object({"name": "domain_3",
                                                    "bgpenabled": True})
        mock_dom_4 = self.create_mock_query_object({"name": "domain_4",
                                                    "bgpenabled": False})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]
        mock_ent_2.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1, mock_ent_2],
            [],
            [mock_dom_3, mock_dom_4]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == [{"name": "domain_3",
                            "bgpenabled": True},
                           {"name": "domain_4",
                            "bgpenabled": False}]

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_1),
            call("Domain", mock_ent_2),
        ])

    def test_nested_object_multiple__bad_child(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
            {"name": "NotChild",
             "filter": None},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1"})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1],
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        with pytest.raises(InvalidObjectError) as e:
            vsd_writer.query(objects, attributes)

        assert "No specification" in str(e)

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object)
        ])

    def test_nested_object__bambou_error(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
            {"name": "Domain",
             "filter": None},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1"})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1],
            get_mock_bambou_error(403, "forbidden")
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        with pytest.raises(VsdError) as e:
            vsd_writer.query(objects, attributes)

        assert "403" in str(e)
        assert "forbidden" in str(e)

        assert "Query" in e.value.get_display_string()
        assert "HTTP 403" in e.value.get_display_string()

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_1)
        ])

    @pytest.mark.parametrize("filter, expected", QUERY_RANGE_SORT_CASES)
    def test_range_sort__success(self, filter, expected):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": filter},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "a1"})
        mock_ent_3 = self.create_mock_query_object({"name": "a3"})
        mock_ent_5 = self.create_mock_query_object({"name": "a5"})
        mock_ent_2 = self.create_mock_query_object({"name": "a2"})
        mock_ent_4 = self.create_mock_query_object({"name": "a4"})

        calls = [
            [mock_ent_1, mock_ent_3, mock_ent_5, mock_ent_2, mock_ent_4]
        ]

        self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == expected

    @pytest.mark.parametrize("filter, expected", QUERY_RANGE_SORT_CASES)
    def test_range_sort_nested__success(self, filter, expected):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
            {"name": "Domain",
             "filter": filter},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "e1"})
        mock_ent_2 = self.create_mock_query_object({"name": "e2"})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]
        mock_ent_2.spec = vsd_writer.specs["enterprise"]

        mock_dom_1 = self.create_mock_query_object({"name": "a1"})
        mock_dom_3 = self.create_mock_query_object({"name": "a3"})
        mock_dom_5 = self.create_mock_query_object({"name": "a5"})
        mock_dom_2 = self.create_mock_query_object({"name": "a2"})
        mock_dom_4 = self.create_mock_query_object({"name": "a4"})

        calls = [
            [mock_ent_1, mock_ent_2],
            [mock_dom_1, mock_dom_3, mock_dom_5, mock_dom_2, mock_dom_4],
            [mock_dom_1, mock_dom_3, mock_dom_5, mock_dom_2, mock_dom_4],
        ]

        self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        combined = list()
        combined.extend(expected)
        combined.extend(expected)

        assert results == combined

    @pytest.mark.parametrize("filter, expected", QUERY_RANGE_SORT_CASES)
    def test_range_sort_nested_filtered__success(self, filter, expected):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": {"%start": 0, "%end": 2}},
            {"name": "Domain",
             "filter": filter},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "e1"})
        mock_ent_2 = self.create_mock_query_object({"name": "e2"})
        mock_ent_3 = self.create_mock_query_object({"name": "e3"})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]
        mock_ent_2.spec = vsd_writer.specs["enterprise"]

        mock_dom_1 = self.create_mock_query_object({"name": "a1"})
        mock_dom_3 = self.create_mock_query_object({"name": "a3"})
        mock_dom_5 = self.create_mock_query_object({"name": "a5"})
        mock_dom_2 = self.create_mock_query_object({"name": "a2"})
        mock_dom_4 = self.create_mock_query_object({"name": "a4"})

        calls = [
            [mock_ent_1, mock_ent_2, mock_ent_3],
            [mock_dom_1, mock_dom_3, mock_dom_5, mock_dom_2, mock_dom_4],
            [mock_dom_1, mock_dom_3, mock_dom_5, mock_dom_2, mock_dom_4],
        ]

        self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        combined = list()
        combined.extend(expected)
        combined.extend(expected)

        assert results == combined

    def test_sort__bad_field(self):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": {"%sort": "foobar"}},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "a1"})
        mock_ent_3 = self.create_mock_query_object({"name": "a3"})
        mock_ent_5 = self.create_mock_query_object({"name": "a5"})
        mock_ent_2 = self.create_mock_query_object({"name": "a2"})
        mock_ent_4 = self.create_mock_query_object({"name": "a4"})

        calls = [
            [mock_ent_1, mock_ent_3, mock_ent_5, mock_ent_2, mock_ent_4]
        ]

        self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert "a1" in results
        assert "a3" in results
        assert "a5" in results
        assert "a2" in results
        assert "a4" in results

    @pytest.mark.parametrize("filter, expected", QUERY_ATTR_FILTER_CASES)
    def test_attr_filter__success(self, filter, expected):
        vsd_writer = VsdWriter()
        setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": filter},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "a1",
                                                    "dhcpleaseinterval": 300,
                                                    "avatartype": "URL"})
        mock_ent_3 = self.create_mock_query_object({"name": "a3",
                                                    "dhcpleaseinterval": 400,
                                                    "avatartype": "URL"})
        mock_ent_5 = self.create_mock_query_object({"name": "a5",
                                                    "dhcpleaseinterval": 500,
                                                    "avatartype": "URL"})
        mock_ent_2 = self.create_mock_query_object({"name": "a2",
                                                    "dhcpleaseinterval": 100,
                                                    "avatartype": "BASE64"})
        mock_ent_4 = self.create_mock_query_object({"name": "a4",
                                                    "dhcpleaseinterval": 200,
                                                    "avatartype": "BASE64"})

        calls = [
            [mock_ent_1, mock_ent_3, mock_ent_5, mock_ent_2, mock_ent_4]
        ]

        self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        results = vsd_writer.query(objects, attributes)

        assert results == expected

    def test_filter__invalid_type(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
            {"name": "Domain",
             "filter": 1},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1"})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1],
            [mock_ent_1]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        with pytest.raises(DeviceWriterError) as e:
            vsd_writer.query(objects, attributes)

        assert "Invalid filter" in str(e)

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_1)
        ])

    def test_filter__invalid_special(self):
        vsd_writer = VsdWriter()
        mock_session = setup_standard_session(vsd_writer)

        objects = [
            {"name": "Enterprise",
             "filter": None},
            {"name": "Domain",
             "filter": {"%foobar": "not cool"}},
        ]

        attributes = "Name"

        mock_ent_1 = self.create_mock_query_object({"name": "enterprise_1"})

        mock_ent_1.spec = vsd_writer.specs["enterprise"]

        calls = [
            [mock_ent_1],
            [mock_ent_1]
        ]

        mock_get = self.add_mock_objects_to_vsd_writer(vsd_writer, calls)

        with pytest.raises(DeviceWriterError) as e:
            vsd_writer.query(objects, attributes)

        assert "Invalid filter %foobar" in str(e)

        mock_get.assert_has_calls([
            call("Enterprise", mock_session.root_object),
            call("Domain", mock_ent_1)
        ])

    def test_query_attribute__success(self):
        vsd_writer = VsdWriter()

        mock_object = type('', (object,), {"name": "object name"})

        value = vsd_writer.query_attribute(mock_object, "Name")
        assert value == "object name"

    def test_query_attribute__not_found(self):
        vsd_writer = VsdWriter()

        mock_object = type('', (object,), {"name": "object name"})

        value = vsd_writer.query_attribute(mock_object, "Foobar")
        assert value is None
