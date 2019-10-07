from mock import patch, MagicMock
import os
import pytest

from levistate.sros_writer import (InvalidAttributeError,
                                   InvalidObjectError,
                                   InvalidSpecification,
                                   InvalidValueError,
                                   MissingSessionParamsError,
                                   SessionError,
                                   SessionNotStartedError,
                                   SrosError,
                                   SROS_PROMPT,
                                   SrosWriter)

FIXTURE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'fixtures')
VALID_SPECS_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                     'valid_sros_specifications')
INVALID_SPECS_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                       'invalid_sros_specifications')

MOCK_VERSION_OUTPUT = """
TiMOS-DC-B-5.1.2-125 both/x86 NUAGE 210 Copyright (c) 2000-2018 Nokia.
All rights reserved. All use subject to applicable license agreements.
Built on Wed Jan 17 13:35:31 PST 2018 [0008c8] by builder in
/rel5.1-DC/release/panos/main
"""

VALIDATE_ONLY_CASES = [False, True]

SESSION_PARAMS = {
    "hostname": "localhost",
    "username": "testuser",
    "password": "testpass",
    "port": 123
}

EXPECTED_SESSION_PARAMS = {
    'device_type': 'alcatel_sros',
    'ssh_config_file': "/etc/ssh/ssh_config",
    'secret': '',
    'verbose': False,
    "ip": SESSION_PARAMS['hostname'],
    "username": SESSION_PARAMS['username'],
    "password": SESSION_PARAMS['password'],
    "port": SESSION_PARAMS['port']
}


PARSE_ERROR_CASES = [
    ('noexist.yml', 'not found'),
    ('notyaml.yml', 'Error parsing'),
    ('noname.yml', "'name' missing"),
    ('noattributes.yml', "'attributes' missing"),
    ('noparent.yml', "'parent' missing"),
    ('nosoftwaretype.yml', "'software-type' missing"),
    ('noconfig.yml', "'config' missing"),
]


@patch("levistate.sros_writer.netmiko")
def setup_standard_session(sros_writer, mock_patch):
    sros_writer.set_session_params(**SESSION_PARAMS)
    sros_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

    mock_session = MagicMock()
    mock_session.is_alive.return_value = True
    mock_patch.ConnectHandler.return_value = mock_session
    sros_writer.start_session()

    if sros_writer.validate_only is True:
        mock_patch.ConnectHandler.assert_not_called()
    else:
        mock_patch.ConnectHandler.assert_called_once_with(
            **EXPECTED_SESSION_PARAMS)

    return mock_session


recorded_commands = list()


def mock_send_command(command, strip_prompt, strip_command, expect_string):
    assert strip_prompt is False
    assert strip_command is False
    assert expect_string == SROS_PROMPT

    recorded_commands.append(command)

    return command


class TestSrosWriterSpecParsing(object):

    def validate_valid_specs(self, sros_writer):
        assert "port" in sros_writer.specs
        assert sros_writer.specs['port']['name'] == "Port"
        assert "ethernet" in sros_writer.specs
        assert sros_writer.specs['ethernet']['name'] == "Ethernet"
        assert "lag" in sros_writer.specs
        assert sros_writer.specs['lag']['name'] == "Lag"
        assert "router" in sros_writer.specs
        assert sros_writer.specs['router']['name'] == "Router"
        assert "routerinterface" in sros_writer.specs
        assert sros_writer.specs['routerinterface'][
            'name'] == "RouterInterface"

    def test_read_dir__success(self):
        sros_writer = SrosWriter()

        sros_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        self.validate_valid_specs(sros_writer)

    def test_read_files__success(self):
        sros_writer = SrosWriter()

        sros_writer.read_api_specifications(os.path.join(VALID_SPECS_DIRECTORY,
                                                         "port.yml"))
        sros_writer.read_api_specifications(os.path.join(VALID_SPECS_DIRECTORY,
                                                         "ethernet.yml"))
        sros_writer.read_api_specifications(os.path.join(VALID_SPECS_DIRECTORY,
                                                         "lag.yml"))
        sros_writer.read_api_specifications(os.path.join(VALID_SPECS_DIRECTORY,
                                                         "router.yml"))
        sros_writer.read_api_specifications(os.path.join(
            VALID_SPECS_DIRECTORY,
            "router_interface.yml"))

        self.validate_valid_specs(sros_writer)

    @pytest.mark.parametrize("filename, message", PARSE_ERROR_CASES)
    def test_read_files__invalid(self, filename, message):
        sros_writer = SrosWriter()

        with pytest.raises(InvalidSpecification) as e:
            sros_writer.read_api_specifications(os.path.join(
                INVALID_SPECS_DIRECTORY,
                filename))

        assert message in str(e)


class TestSrosWriterGetVersion(object):

    @patch("levistate.sros_writer.netmiko")
    def test__success(self, mock_patch):
        sros_writer = SrosWriter()
        sros_writer.set_session_params(**SESSION_PARAMS)

        mock_session = MagicMock()
        mock_patch.ConnectHandler.return_value = mock_session
        mock_session.send_command.return_value = MOCK_VERSION_OUTPUT

        version = sros_writer.get_version()

        mock_patch.ConnectHandler.assert_called_once_with(
            **EXPECTED_SESSION_PARAMS)
        mock_session.send_command.assert_called_once_with("show version")

        assert version == {
            "software_type": "Nuage Networks WBX",
            "software_version": "5.1.2"
        }

    @patch("levistate.sros_writer.netmiko")
    def test__no_device_str(self, mock_patch):
        sros_writer = SrosWriter()
        sros_writer.set_session_params(**SESSION_PARAMS)

        mock_session = MagicMock()
        mock_patch.ConnectHandler.return_value = mock_session
        mock_session.send_command.return_value = "Unknown version output"

        version = sros_writer.get_version()

        mock_patch.ConnectHandler.assert_called_once_with(
            **EXPECTED_SESSION_PARAMS)
        mock_session.send_command.assert_called_once_with("show version")

        assert version == {
            "software_type": None,
            "software_version": None
        }

    @patch("levistate.sros_writer.netmiko")
    def test__netmiko_error(self, mock_patch):
        sros_writer = SrosWriter()
        sros_writer.set_session_params(**SESSION_PARAMS)

        mock_session = MagicMock()
        mock_patch.ConnectHandler.return_value = mock_session
        mock_session.send_command.side_effect = Exception("Cannot connect")

        version = sros_writer.get_version()

        mock_patch.ConnectHandler.assert_called_once_with(
            **EXPECTED_SESSION_PARAMS)
        mock_session.send_command.assert_called_once_with("show version")

        assert version == {
            "software_type": None,
            "software_version": None
        }


class TestSrosWriterSession(object):

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_start__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(sros_writer)

        if validate_only is True:
            assert sros_writer.session is None
        else:
            assert sros_writer.session == mock_session

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_start__no_params(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)

        with pytest.raises(MissingSessionParamsError) as e:
            sros_writer.start_session()

        assert "session without parameters" in str(e)

    @patch("levistate.sros_writer.netmiko")
    def test_start__netmiko_error(self, mock_patch):
        sros_writer = SrosWriter()
        sros_writer.set_session_params(**SESSION_PARAMS)
        sros_writer.read_api_specifications(VALID_SPECS_DIRECTORY)

        mock_patch.ConnectHandler.side_effect = Exception("forbidden")

        with pytest.raises(SrosError) as e:
            sros_writer.start_session()

        assert "forbidden" in str(e.value)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_stop__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)

        mock_session = setup_standard_session(sros_writer)
        mock_session.is_alive.return_value = True

        sros_writer.stop_session()

        if validate_only is True:
            mock_session.disconnect.assert_not_called()
        else:
            mock_session.disconnect.assert_called_once()


class TestSrosWriterCreateObject(object):

    def test__no_session(self):
        sros_writer = SrosWriter()

        with pytest.raises(SessionNotStartedError) as e:
            sros_writer.create_object("Port")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        new_context = sros_writer.create_object("Port")

        assert new_context.has_current_object() is True
        assert new_context.get_obj_name() == "Port"
        assert new_context.get_path_config() is None
        assert new_context.object_exists is False

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent__no_object(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        with pytest.raises(InvalidObjectError) as e:
            sros_writer.create_object("Ethernet")

        assert "not defined at root" in str(e.value)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        parent_context = sros_writer.create_object("Port")
        child_context = sros_writer.create_object("Ethernet", parent_context)

        assert child_context.has_current_object() is True
        assert child_context.get_obj_name() == "Ethernet"
        assert child_context.get_path_config() is None
        assert child_context.object_exists is False

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child__no_object(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        parent_context = sros_writer.create_object("Port")

        with pytest.raises(InvalidObjectError) as e:
            sros_writer.create_object("Port", parent_context)

        assert "not defined as a child of Port" in str(e.value)


class TestSrosWriterUpdateObject(object):

    def test__no_session(self):
        sros_writer = SrosWriter()

        with pytest.raises(SessionNotStartedError) as e:
            sros_writer.update_object("Port", "identifier", "1/1/1")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        new_context = sros_writer.update_object("Port", "identifier", "1/1/1")

        assert new_context.has_current_object() is True
        assert new_context.get_obj_name() == "Port"
        assert new_context.get_path_config() == "port 1/1/1"
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent__no_object(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        with pytest.raises(InvalidObjectError) as e:
            sros_writer.update_object("Ethernet", "$singleton", "")

        assert "not defined at root" in str(e.value)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        parent_context = sros_writer.update_object("Port", "identifier",
                                                   "1/1/1")
        child_context = sros_writer.update_object("Ethernet", "$singleton", "",
                                                  parent_context)

        assert child_context.has_current_object() is True
        assert child_context.get_obj_name() == "Ethernet"
        assert child_context.get_path_config() == "port 1/1/1 ethernet"
        assert child_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child__no_object(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        parent_context = sros_writer.update_object("Port", "identifier",
                                                   "1/1/1")

        with pytest.raises(InvalidObjectError) as e:
            sros_writer.update_object("Port", "identifier", "1/1/1",
                                      parent_context)

        assert "not defined as a child of Port" in str(e.value)


class TestSrosWriterSelectObject(object):

    def test__no_session(self):
        sros_writer = SrosWriter()

        with pytest.raises(SessionNotStartedError) as e:
            sros_writer.select_object("Port", "identifier", "1/1/1")

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        new_context = sros_writer.select_object("Port", "identifier", "1/1/1")

        assert new_context.has_current_object() is True
        assert new_context.get_obj_name() == "Port"
        assert new_context.get_path_config() == "port 1/1/1"
        assert new_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent__no_object(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        with pytest.raises(InvalidObjectError) as e:
            sros_writer.select_object("Ethernet", "$singleton", "")

        assert "not defined at root" in str(e.value)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        parent_context = sros_writer.select_object("Port", "identifier",
                                                   "1/1/1")
        child_context = sros_writer.select_object("Ethernet", "$singleton", "",
                                                  parent_context)

        assert child_context.has_current_object() is True
        assert child_context.get_obj_name() == "Ethernet"
        assert child_context.get_path_config() == "port 1/1/1 ethernet"
        assert child_context.object_exists is True

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child__no_object(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        parent_context = sros_writer.select_object("Port", "identifier",
                                                   "1/1/1")

        with pytest.raises(InvalidObjectError) as e:
            sros_writer.select_object("Port", "identifier", "1/1/1",
                                      parent_context)

        assert "not defined as a child of Port" in str(e.value)


class TestSrosWriterDeleteObject(object):

    def test__no_session(self):
        sros_writer = SrosWriter()

        with pytest.raises(SessionNotStartedError) as e:
            sros_writer.delete_object(None, dict())

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(sros_writer)
        mock_session.send_command = mock_send_command

        del recorded_commands[:]

        sel_context = sros_writer.select_object("Port", "identifier", "1/1/1")
        del_context = sros_writer.delete_object(sel_context,
                                                {"identifier": "1/1/1"})

        assert del_context.has_current_object() is False
        assert del_context.get_obj_name() is None
        assert del_context.get_path_config() is None
        assert del_context.object_exists is False

        if validate_only:
            assert recorded_commands == []
        else:
            assert recorded_commands == [
                "configure",
                "port 1/1/1",
                "shutdown",
                "exit all",
                "configure",
                "no port 1/1/1",
                "exit all",
            ]

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(sros_writer)
        mock_session.send_command = mock_send_command

        del recorded_commands[:]

        parent_context = sros_writer.select_object("Router", "$singleton", "")
        sel_context = sros_writer.select_object("RouterInterface", "name",
                                                "intf1", parent_context)
        del_context = sros_writer.delete_object(sel_context,
                                                {"name": "intf1"})

        assert del_context.has_current_object() is False
        assert del_context.get_obj_name() is None
        assert del_context.get_path_config() == "router"
        assert del_context.object_exists is False

        if validate_only:
            assert recorded_commands == []
        else:
            assert recorded_commands == [
                "configure",
                "router interface intf1",
                "shutdown",
                "exit all",
                "configure",
                "router no interface intf1",
                "exit all",
            ]

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_object(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        with pytest.raises(SessionError) as e:
            sros_writer.delete_object(None, {"identifier": "1/1/1"})

        assert "No object for deletion" in str(e.value)


class TestSrosWriterSetValues(object):

    def test__no_session(self):
        sros_writer = SrosWriter()

        with pytest.raises(SessionNotStartedError) as e:
            sros_writer.set_values(None, **{})

        assert "not started" in str(e)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_parent__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(sros_writer)
        mock_session.send_command = mock_send_command

        del recorded_commands[:]

        sel_context = sros_writer.create_object("Port")
        set_context = sros_writer.set_values(sel_context,
                                             **{"identifier": "1/1/1",
                                                "description": "test descr",
                                                "shutdown": False})

        assert set_context.has_current_object() is True
        assert set_context.get_obj_name() is "Port"
        assert set_context.get_path_config() == "port 1/1/1"
        assert set_context.object_exists is True

        if validate_only:
            assert recorded_commands == []
        else:
            assert recorded_commands == [
                "configure",
                "port 1/1/1",
                'description "test descr"',
                "no shutdown",
                "exit all",
            ]

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test_child__success(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        mock_session = setup_standard_session(sros_writer)
        mock_session.send_command = mock_send_command

        del recorded_commands[:]

        sel_context = sros_writer.select_object("Port", "identifier", "1/1/1")
        create_context = sros_writer.create_object("Ethernet", sel_context)
        set_context = sros_writer.set_values(create_context,
                                             **{"mtu": 1600,
                                                "speed": 1000})

        assert set_context.has_current_object() is True
        assert set_context.get_obj_name() is "Ethernet"
        assert set_context.get_path_config() == "port 1/1/1 ethernet"
        assert set_context.object_exists is True

        if validate_only:
            assert recorded_commands == []
        else:
            assert recorded_commands == [
                "configure",
                "port 1/1/1 ethernet",
                "speed 1000",
                "mtu 1600",
                "exit all",
            ]

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__no_object(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        with pytest.raises(SessionError) as e:
            sros_writer.set_values(None, **{})

        assert "No object for setting values" in str(e.value)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__invalid_choice(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        create_context = sros_writer.create_object("Lag")

        with pytest.raises(InvalidValueError) as e:
            sros_writer.set_values(create_context,
                                   **{"mode": "not valid"})

        assert "not a valid choice" in str(e.value)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__invalid_integer(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        sel_context = sros_writer.select_object("Port", "identifier", "1/1/1")
        create_context = sros_writer.create_object("Ethernet", sel_context)
        set_context = sros_writer.set_values(create_context,
                                             **{"mtu": 1600,
                                                "speed": 1000})

        with pytest.raises(InvalidValueError) as e:
            sros_writer.set_values(set_context,
                                   **{"mtu": "not integer"})

        assert "not an integer" in str(e.value)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__invalid_boolean(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        create_context = sros_writer.create_object("Port")

        with pytest.raises(InvalidValueError) as e:
            sros_writer.set_values(create_context,
                                   **{"shutdown": "not boolean"})

        assert "not a boolean" in str(e.value)

    @pytest.mark.parametrize("validate_only", VALIDATE_ONLY_CASES)
    def test__invalid_attribute(self, validate_only):
        sros_writer = SrosWriter()
        sros_writer.set_validate_only(validate_only)
        setup_standard_session(sros_writer)

        create_context = sros_writer.create_object("Port")

        with pytest.raises(InvalidAttributeError) as e:
            sros_writer.set_values(create_context,
                                   **{"foobar": "not attribute"})

        assert "does not define an attribute" in str(e.value)
