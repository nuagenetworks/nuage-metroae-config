import pytest
import requests
import requests_mock

from .bambou_adapter_test_params import (DOMAINTMPL_SPEC_TEST,
                                         ENTERPRISE_SPEC_TEST,
                                         ENTERPRISE_SPEC_VALIDATE,
                                         ENTERPRISENET_SPEC_TEST,
                                         NETMACGRP_SPEC_TEST,
                                         ROOT_SPEC_TEST,
                                         SESSION_CREDS_REAL,
                                         SESSION_CREDS_TEST)
from bambou.exceptions import BambouHTTPError
from nuage_metroae_config.bambou_adapter import (ConfigObject,
                                                 EnterpriseFetcher,
                                                 Fetcher,
                                                 Session)

CSP_ENTERPRISE_ID = "76046673-d0ea-4a67-b6af-2829952f0812"
CSP_ENTERPRISE_NAME = "CSP"

VALIDATION_ERROR_CASES = [
    ('name', None, "value is mandatory"),
    ('name', "", "value is mandatory"),
    ('name', "a" * 256, "maximum length"),
    ('enableapplicationperformancemanagement', "True", "type should be"),
    ('floatingipsquota', "0", "type should be"),
    ('floatingipsquota', -1, "minimum value"),
    ('floatingipsquota', 250001, "maximum value"),
    ('allowedforwardingclasses', "A", "type should be"),
    ('allowedforwardingclasses', ["A", "FOO"], "not a valid choice"),
    ('encryptionmanagementmode', True, "type should be"),
    ('encryptionmanagementmode', "FOO", "not a valid choice")]


def build_mock_url(base, api, version, path):
    return "%s/%s/v%s/%s" % (base, api, version.replace('.', '_'), path)


def build_standard_mock_url(path):
    return build_mock_url(SESSION_CREDS_TEST['api_url'],
                          SESSION_CREDS_TEST['api_prefix'],
                          SESSION_CREDS_TEST['version'],
                          path)


def start_session(mock):
    session = Session(**SESSION_CREDS_TEST)
    session.set_enterprise_spec(ENTERPRISE_SPEC_TEST)

    mock.get(build_standard_mock_url(ROOT_SPEC_TEST["model"]["rest_name"]))
    session.start()

    assert mock.call_count == 1

    last_request = mock.last_request
    assert (last_request.headers['X-Nuage-Organization'] ==
            SESSION_CREDS_TEST['enterprise'])
    assert session.root_object is not None
    assert (session.root_object.__rest_name__ ==
            ROOT_SPEC_TEST["model"]["rest_name"])

    return session


class RequestSpy(object):
    """
    This class is not a test or part of a test.  It can be used to "spy" on the
    real VSD.  Issuing spy() will print out the response from the real VSD so
    it can be used as a guide for mocking.

    Example:

        def update(self, session):
            obj = ConfigObject(ENTERPRISE_SPEC_TEST)
            obj.id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"
            obj.name = "new_name"
            obj.save()

        def test__spy(self):
            req_spy = RequestSpy()
            req_spy.spy("enterprises/741fc5d9-fce7-4f98-9172-e962be6ee3e2",
                        self.update)
            assert False

    """

    def spy(self, url_path, test_func):
        session = Session(**SESSION_CREDS_REAL)
        session.set_enterprise_spec(ENTERPRISE_SPEC_TEST)
        session.start()

        with requests_mock.mock() as mock:
            url = build_mock_url(SESSION_CREDS_REAL['api_url'],
                                 SESSION_CREDS_REAL['api_prefix'],
                                 SESSION_CREDS_REAL['version'],
                                 url_path)
            mock.put(url)
            test_func(session)
            last_request = mock.last_request
            print("- Request -----")
            print(str(last_request.url))
            print(str(last_request.headers))
            print(str(last_request.json()))

        response = requests.put(last_request.url,
                                headers=last_request.headers,
                                verify=False,
                                json=last_request.json())
        print("- Response -----")
        print(str(response.status_code))
        print(str(response.headers))
        print(str(response.text))


class TestSession(object):

    @requests_mock.mock(kw="mock")
    def test_start__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)

    @requests_mock.mock(kw="mock")
    def test_start__invalid_pass(self, **kwargs):
        mock = kwargs['mock']
        session = Session(**SESSION_CREDS_TEST)
        session.set_enterprise_spec(ENTERPRISE_SPEC_TEST)

        mock.get(build_standard_mock_url(ROOT_SPEC_TEST["model"]["rest_name"]),
                 status_code=401,
                 reason="This request requires HTTP authentication.")
        with pytest.raises(BambouHTTPError) as e:
            session.start()

        assert mock.call_count == 1
        assert '401' in str(e)
        assert 'authentication' in str(e)


class TestConfigObject(object):

    @requests_mock.mock(kw="mock")
    def test_new_object__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        obj = ConfigObject(ENTERPRISE_SPEC_TEST)

        assert obj.get_name() == "Enterprise"

    @requests_mock.mock(kw="mock")
    def test_create_parent__success(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        assert obj.get_name() == "Enterprise"

        obj.name = "test_enterprise"
        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.post(build_standard_mock_url(resource_name),
                  status_code=201,
                  json=[{"name": "test_enterprise",
                         "ID": test_id}])

        session.root_object.current_child_name = resource_name
        session.root_object.create_child(obj)

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] is None
        assert "name" in json_data
        assert json_data["name"] == "test_enterprise"

        assert obj.name == "test_enterprise"
        assert obj.id == test_id

    @requests_mock.mock(kw="mock")
    def test_create_parent__conflict(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        obj = ConfigObject(ENTERPRISE_SPEC_TEST)

        assert obj.get_name() == "Enterprise"

        obj.name = "test_enterprise"
        assert hasattr(obj, "name")

        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.post(build_standard_mock_url(resource_name),
                  status_code=409,
                  json={"errors": [
                      {"property": "name",
                       "descriptions": [
                           {"title": "Cannot create duplicate entity.",
                            "description": "Another Enterprise with the same"
                            " name = test_enterprise exists."}]}],
                      "internalErrorCode": 9501})

        session.root_object.current_child_name = resource_name
        with pytest.raises(BambouHTTPError) as e:
            session.root_object.create_child(obj)

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] is None
        assert "name" in json_data
        assert json_data["name"] == "test_enterprise"

        assert '409' in str(e)
        assert 'duplicate' in str(e)
        assert 'test_enterprise exists' in str(e)

    @requests_mock.mock(kw="mock")
    def test_assign__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        parent_id = "bff6a2a3-0ac2-4891-b4e5-099741e6826d"
        child_id = "0d4a68c5-b351-45a2-80e4-fdb880016ef5"

        resource_name = NETMACGRP_SPEC_TEST["model"]["resource_name"]
        child_resource_name = ENTERPRISENET_SPEC_TEST["model"]["resource_name"]

        mock.put(build_standard_mock_url(resource_name + "/" +
                                         parent_id + "/" +
                                         child_resource_name),
                 status_code=204)

        obj = ConfigObject(NETMACGRP_SPEC_TEST)
        obj.id = parent_id
        obj.current_child_name = child_resource_name

        child_obj = ConfigObject(ENTERPRISENET_SPEC_TEST)
        child_obj.id = child_id
        obj.assign([child_obj], nurest_object_type=None)

        last_request = mock.last_request
        json_data = last_request.json()
        assert json_data == [child_id]

    @requests_mock.mock(kw="mock")
    def test_assign__invalid_id(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        parent_id = "bff6a2a3-0ac2-4891-b4e5-099741e6826d"
        child_id = "foobar"

        resource_name = NETMACGRP_SPEC_TEST["model"]["resource_name"]
        child_resource_name = ENTERPRISENET_SPEC_TEST["model"]["resource_name"]

        mock.put(build_standard_mock_url(resource_name + "/" +
                                         parent_id + "/" +
                                         child_resource_name),
                 status_code=409,
                 json={"errors": [
                     {"property": "",
                      "descriptions": [
                          {"title": "Invalid id list for entity "
                                    "enterprisenetwork",
                           "description": "Invalid id list for entity "
                                          "enterprisenetwork , invalid ids "
                                          "[foobar]"}]}],
                     "internalErrorCode": 9450})

        obj = ConfigObject(NETMACGRP_SPEC_TEST)
        obj.id = parent_id
        obj.current_child_name = child_resource_name

        child_obj = ConfigObject(ENTERPRISENET_SPEC_TEST)
        child_obj.id = child_id

        with pytest.raises(BambouHTTPError) as e:
            obj.assign([child_obj], nurest_object_type=None)

        last_request = mock.last_request
        json_data = last_request.json()
        assert json_data == [child_id]

        assert 'HTTP 409' in str(e)
        assert 'invalid id' in str(e)
        assert child_id in str(e)

    @requests_mock.mock(kw="mock")
    def test_unassign__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        test_id = "bff6a2a3-0ac2-4891-b4e5-099741e6826d"

        resource_name = NETMACGRP_SPEC_TEST["model"]["resource_name"]
        child_resource_name = ENTERPRISENET_SPEC_TEST["model"]["resource_name"]

        mock.put(build_standard_mock_url(resource_name + "/" +
                                         test_id + "/" +
                                         child_resource_name),
                 status_code=204)

        obj = ConfigObject(NETMACGRP_SPEC_TEST)
        obj.id = test_id
        obj.current_child_name = child_resource_name
        obj.assign([], nurest_object_type=None)

        last_request = mock.last_request
        json_data = last_request.json()
        assert json_data == list()

    @requests_mock.mock(kw="mock")
    def test_save_parent__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        assert obj.get_name() == "Enterprise"

        obj.id = test_id
        assert hasattr(obj, 'id') is True
        obj.name = "new_name"
        assert hasattr(obj, "name") is True
        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.put(build_standard_mock_url(resource_name + "/" + test_id),
                 status_code=204)

        obj.save()

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] == test_id
        assert "name" in json_data
        assert json_data["name"] == "new_name"

    @requests_mock.mock(kw="mock")
    def test_save_parent__not_found(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        assert obj.get_name() == "Enterprise"

        obj.id = test_id
        assert hasattr(obj, 'id') is True
        obj.name = "new_name"
        assert hasattr(obj, "name") is True
        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.put(build_standard_mock_url(resource_name + "/" + test_id),
                 status_code=404,
                 json={"description": "Cannot find enterprise with ID "
                       "741fc5d9-fce7-4f98-9172-e962be6ee3e2",
                       "title": "enterprise not found",
                       "errors": [{
                           "property": "",
                           "descriptions": [{
                               "title": "enterprise not found",
                               "description": "Cannot find enterprise with ID "
                               "741fc5d9-fce7-4f98-9172-e962be6ee3e2"}]}]})

        with pytest.raises(BambouHTTPError) as e:
            obj.save()

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] == test_id
        assert "name" in json_data
        assert json_data["name"] == "new_name"

        assert '404' in str(e)
        assert 'not found' in str(e)
        assert test_id in str(e)

    @requests_mock.mock(kw="mock")
    def test_create_child__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        parent_obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        parent_test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"
        child_test_id = "e5b683ed-5c24-4d43-bac9-181b6d4eb63b"

        parent_obj.id = parent_test_id
        assert hasattr(parent_obj, 'id') is True

        child_obj = ConfigObject(DOMAINTMPL_SPEC_TEST)

        assert child_obj.get_name() == "DomainTemplate"

        child_obj.name = "test_domain_template"
        assert hasattr(child_obj, 'name') is True

        parent_resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]
        child_resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.post(build_standard_mock_url(parent_resource_name +
                                          "/" + parent_test_id + "/" +
                                          child_resource_name),
                  status_code=201,
                  json=[{"name": "test_domain_template",
                         "ID": child_test_id}])

        parent_obj.current_child_name = child_resource_name
        parent_obj.create_child(child_obj)

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] is None
        assert "name" in json_data
        assert json_data["name"] == "test_domain_template"

        assert child_obj.name == "test_domain_template"
        assert child_obj.id == child_test_id

    @requests_mock.mock(kw="mock")
    def test_create_child__conflict(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        parent_obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        parent_test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        parent_obj.id = parent_test_id
        assert hasattr(parent_obj, 'id') is True

        child_obj = ConfigObject(DOMAINTMPL_SPEC_TEST)

        assert child_obj.get_name() == "DomainTemplate"

        child_obj.name = "test_domain_template"
        assert hasattr(child_obj, 'name') is True

        parent_resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]
        child_resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.post(build_standard_mock_url(parent_resource_name +
                                          "/" + parent_test_id + "/" +
                                          child_resource_name),
                  status_code=409,
                  json={"errors": [{
                      "property": "name",
                      "descriptions": [{
                          "title": "Resource in use",
                          "description": "name(test_domain_template) is in "
                          "use. Please retry with a different value."}]}],
                        "internalErrorCode": 2510})

        parent_obj.current_child_name = child_resource_name
        with pytest.raises(BambouHTTPError) as e:
            parent_obj.create_child(child_obj)

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] is None
        assert "name" in json_data
        assert json_data["name"] == "test_domain_template"

        assert '409' in str(e)
        assert 'in use' in str(e)
        assert 'test_domain_template' in str(e)

    @requests_mock.mock(kw="mock")
    def test_save_child__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        obj = ConfigObject(DOMAINTMPL_SPEC_TEST)
        test_id = "e5b683ed-5c24-4d43-bac9-181b6d4eb63b"

        assert obj.get_name() == "DomainTemplate"

        obj.id = test_id
        assert hasattr(obj, 'id') is True
        obj.name = "new_name"
        assert hasattr(obj, 'name') is True
        resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.put(build_standard_mock_url(resource_name + "/" + test_id),
                 status_code=204)

        obj.save()

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] == test_id
        assert "name" in json_data
        assert json_data["name"] == "new_name"

    @requests_mock.mock(kw="mock")
    def test_save_child__not_found(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        obj = ConfigObject(DOMAINTMPL_SPEC_TEST)
        test_id = "e5b683ed-5c24-4d43-bac9-181b6d4eb63b"

        assert obj.get_name() == "DomainTemplate"

        obj.id = test_id
        assert hasattr(obj, 'id') is True
        obj.name = "new_name"
        assert hasattr(obj, 'name') is True
        resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.put(build_standard_mock_url(resource_name + "/" + test_id),
                 status_code=404,
                 json={"description": "Cannot find domaintemplate with ID "
                       "e5b683ed-5c24-4d43-bac9-181b6d4eb63b",
                       "title": "domaintemplate not found",
                       "errors": [{
                           "property": "",
                           "descriptions": [{
                               "title": "domaintemplate not found",
                               "description": "Cannot find domaintemplate with"
                               " ID e5b683ed-5c24-4d43-bac9-181b6d4eb63b"}]}]})

        with pytest.raises(BambouHTTPError) as e:
            obj.save()

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] == test_id
        assert "name" in json_data
        assert json_data["name"] == "new_name"

        assert '404' in str(e)
        assert 'not found' in str(e)
        assert test_id in str(e)

    @requests_mock.mock(kw="mock")
    def test_delete_parent__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        assert obj.get_name() == "Enterprise"

        obj.id = test_id
        assert hasattr(obj, 'id') is True
        obj.name = "test_enterprise"
        assert hasattr(obj, 'name') is True
        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.delete(build_standard_mock_url(resource_name + "/" + test_id +
                                            "?responseChoice=1"),
                    status_code=204)

        obj.delete()

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] == test_id
        assert "name" in json_data
        assert json_data["name"] == "test_enterprise"

    @requests_mock.mock(kw="mock")
    def test_delete_parent__not_found(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        assert obj.get_name() == "Enterprise"

        obj.id = test_id
        assert hasattr(obj, 'id') is True
        obj.name = "test_enterprise"
        assert hasattr(obj, 'name') is True
        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.delete(build_standard_mock_url(resource_name + "/" + test_id +
                                            "?responseChoice=1"),
                    status_code=404,
                    json={"description": "Cannot find enterprise with ID "
                          "741fc5d9-fce7-4f98-9172-e962be6ee3e2",
                          "title": "enterprise not found",
                          "errors": [{
                              "property": "",
                              "descriptions": [{
                                  "title": "enterprise not found",
                                  "description": "Cannot find enterprise "
                                  "with ID 741fc5d9-fce7-4f98-9172-"
                                  "e962be6ee3e2"}]}]})

        with pytest.raises(BambouHTTPError) as e:
            obj.delete()

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] == test_id
        assert "name" in json_data
        assert json_data["name"] == "test_enterprise"

        assert '404' in str(e)
        assert 'enterprise not found' in str(e)
        assert test_id in str(e)

    @requests_mock.mock(kw="mock")
    def test_delete_child__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        obj = ConfigObject(DOMAINTMPL_SPEC_TEST)
        test_id = "e5b683ed-5c24-4d43-bac9-181b6d4eb63b"

        assert obj.get_name() == "DomainTemplate"

        obj.id = test_id
        assert hasattr(obj, 'id') is True
        obj.name = "test_domain_template"
        assert hasattr(obj, 'name') is True
        resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.delete(build_standard_mock_url(resource_name + "/" + test_id +
                                            "?responseChoice=1"),
                    status_code=204)

        obj.delete()

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] == test_id
        assert "name" in json_data
        assert json_data["name"] == "test_domain_template"

    @requests_mock.mock(kw="mock")
    def test_delete_child__not_found(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        obj = ConfigObject(DOMAINTMPL_SPEC_TEST)
        test_id = "e5b683ed-5c24-4d43-bac9-181b6d4eb63b"

        assert obj.get_name() == "DomainTemplate"

        obj.id = test_id
        assert hasattr(obj, 'id') is True
        obj.name = "test_domain_template"
        assert hasattr(obj, 'name') is True
        resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.delete(build_standard_mock_url(resource_name + "/" + test_id +
                                            "?responseChoice=1"),
                    status_code=404,
                    json={"description": "Cannot find domaintemplate with ID "
                          "e5b683ed-5c24-4d43-bac9-181b6d4eb63b",
                          "title": "domaintemplate not found",
                          "errors": [{
                              "property": "",
                              "descriptions": [{
                                  "title": "domaintemplate not found",
                                  "description": "Cannot find domaintemplate "
                                  "with ID e5b683ed-5c24-4d43-bac9-"
                                  "181b6d4eb63b"}]}]})

        with pytest.raises(BambouHTTPError) as e:
            obj.delete()

        last_request = mock.last_request
        json_data = last_request.json()
        assert "ID" in json_data
        assert json_data["ID"] == test_id
        assert "name" in json_data
        assert json_data["name"] == "test_domain_template"

        assert '404' in str(e)
        assert 'domaintemplate not found' in str(e)
        assert test_id in str(e)


class TestFetcher(object):

    @requests_mock.mock(kw="mock")
    def test_find_parent__success(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        fetcher = Fetcher(session.root_object, ENTERPRISE_SPEC_TEST)

        test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(resource_name),
                 status_code=200,
                 json=[{"name": "test_enterprise",
                        "ID": test_id}])

        objects = fetcher.get(filter='name is "test_enterprise"')

        last_request = mock.last_request
        request_headers = last_request.headers
        assert "X-Nuage-Filter" in request_headers
        assert request_headers["X-Nuage-Filter"] == 'name is "test_enterprise"'

        assert len(objects) == 1
        obj = objects[0]
        assert obj.get_name() == "Enterprise"
        assert hasattr(obj, 'name') is True
        assert obj.name == "test_enterprise"
        assert hasattr(obj, 'id') is True
        assert obj.id == test_id

    @requests_mock.mock(kw="mock")
    def test_find_parent__not_found(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        fetcher = Fetcher(session.root_object, ENTERPRISE_SPEC_TEST)

        # test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(resource_name),
                 status_code=200)

        objects = fetcher.get(filter='name is "test_enterprise"')

        last_request = mock.last_request
        request_headers = last_request.headers
        assert "X-Nuage-Filter" in request_headers
        assert request_headers["X-Nuage-Filter"] == 'name is "test_enterprise"'

        assert len(objects) == 0

    @requests_mock.mock(kw="mock")
    def test_find_parent__multiple(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        fetcher = Fetcher(session.root_object, ENTERPRISE_SPEC_TEST)

        test_id_1 = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"
        test_id_2 = "741fc5d9-fce7-4f98-9172-e962be6ee3e3"

        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(resource_name),
                 status_code=200,
                 json=[{"name": "test_enterprise",
                        "ID": test_id_1},
                       {"name": "test_enterprise",
                        "ID": test_id_2}])

        objects = fetcher.get(filter='name is "test_enterprise"')

        last_request = mock.last_request
        request_headers = last_request.headers
        assert "X-Nuage-Filter" in request_headers
        assert request_headers["X-Nuage-Filter"] == 'name is "test_enterprise"'

        assert len(objects) == 2
        obj_1 = objects[0]
        obj_2 = objects[1]

        assert obj_1.get_name() == "Enterprise"
        assert hasattr(obj_1, 'name') is True
        assert obj_1.name == "test_enterprise"
        assert hasattr(obj_1, 'id') is True
        assert obj_1.id == test_id_1

        assert obj_2.get_name() == "Enterprise"
        assert hasattr(obj_2, 'name') is True
        assert obj_2.name == "test_enterprise"
        assert hasattr(obj_2, 'id') is True
        assert obj_2.id == test_id_2

    @requests_mock.mock(kw="mock")
    def test_find_child__success(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)

        parent_obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        parent_test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        parent_obj.id = parent_test_id
        assert hasattr(parent_obj, 'id') is True

        fetcher = Fetcher(parent_obj, DOMAINTMPL_SPEC_TEST)

        child_test_id = "e5b683ed-5c24-4d43-bac9-181b6d4eb63b"

        parent_resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]
        child_resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(parent_resource_name + '/' +
                                         parent_test_id + '/' +
                                         child_resource_name),
                 status_code=200,
                 json=[{"name": "test_domain_template",
                        "ID": child_test_id}])

        objects = fetcher.get(filter='name is "test_domain_template"')

        last_request = mock.last_request
        request_headers = last_request.headers
        assert "X-Nuage-Filter" in request_headers
        assert request_headers["X-Nuage-Filter"] == (
            'name is "test_domain_template"')

        assert len(objects) == 1
        obj = objects[0]
        assert obj.get_name() == "DomainTemplate"
        assert hasattr(obj, 'name') is True
        assert obj.name == "test_domain_template"
        assert hasattr(obj, 'id') is True
        assert obj.id == child_test_id

    @requests_mock.mock(kw="mock")
    def test_find_child__not_found(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        parent_obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        parent_test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        parent_obj.id = parent_test_id
        assert hasattr(parent_obj, 'id') is True

        fetcher = Fetcher(parent_obj, DOMAINTMPL_SPEC_TEST)

        parent_resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]
        child_resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(parent_resource_name + '/' +
                                         parent_test_id + '/' +
                                         child_resource_name),
                 status_code=200)

        objects = fetcher.get(filter='name is "test_domain_template"')

        last_request = mock.last_request
        request_headers = last_request.headers
        assert "X-Nuage-Filter" in request_headers
        assert request_headers["X-Nuage-Filter"] == (
            'name is "test_domain_template"')

        assert len(objects) == 0

    @requests_mock.mock(kw="mock")
    def test_find_child__multiple(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        parent_obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        parent_test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        parent_obj.id = parent_test_id
        assert hasattr(parent_obj, 'id') is True

        fetcher = Fetcher(parent_obj, DOMAINTMPL_SPEC_TEST)

        child_test_id_1 = "e5b683ed-5c24-4d43-bac9-181b6d4eb63b"
        child_test_id_2 = "e5b683ed-5c24-4d43-bac9-181b6d4eb63c"

        parent_resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]
        child_resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(parent_resource_name + '/' +
                                         parent_test_id + '/' +
                                         child_resource_name),
                 status_code=200,
                 json=[{"name": "test_domain_template",
                        "ID": child_test_id_1},
                       {"name": "test_domain_template",
                        "ID": child_test_id_2}])

        objects = fetcher.get(filter='name is "test_domain_template"')

        last_request = mock.last_request
        request_headers = last_request.headers
        assert "X-Nuage-Filter" in request_headers
        assert request_headers["X-Nuage-Filter"] == (
            'name is "test_domain_template"')

        assert len(objects) == 2
        obj_1 = objects[0]
        obj_2 = objects[1]

        assert obj_1.get_name() == "DomainTemplate"
        assert hasattr(obj_1, 'name') is True
        assert obj_1.name == "test_domain_template"
        assert hasattr(obj_1, 'id') is True
        assert obj_1.id == child_test_id_1

        assert obj_2.get_name() == "DomainTemplate"
        assert hasattr(obj_2, 'name') is True
        assert obj_2.name == "test_domain_template"
        assert hasattr(obj_2, 'id') is True
        assert obj_2.id == child_test_id_2

    @requests_mock.mock(kw="mock")
    def test_find_child__invalid_parent(self, **kwargs):
        mock = kwargs['mock']
        start_session(mock)
        parent_obj = ConfigObject(ENTERPRISE_SPEC_TEST)
        parent_test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        parent_obj.id = parent_test_id
        assert hasattr(parent_obj, 'id') is True

        fetcher = Fetcher(parent_obj, DOMAINTMPL_SPEC_TEST)

        parent_resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]
        child_resource_name = DOMAINTMPL_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(parent_resource_name + '/' +
                                         parent_test_id + '/' +
                                         child_resource_name),
                 status_code=404,
                 json={"description": "Cannot find enterprise with ID "
                       "741fc5d9-fce7-4f98-9172-e962be6ee3e2",
                       "title": "enterprise not found",
                       "errors": [{
                           "property": "",
                           "descriptions": [{
                               "title": "enterprise not found",
                               "description": "Cannot find enterprise with ID "
                               "741fc5d9-fce7-4f98-9172-e962be6ee3e2"}]}]})

        with pytest.raises(BambouHTTPError) as e:
            fetcher.get(filter='name is "test_domain_template"')

        last_request = mock.last_request
        request_headers = last_request.headers
        assert "X-Nuage-Filter" in request_headers
        assert request_headers["X-Nuage-Filter"] == (
            'name is "test_domain_template"')

        assert '404' in str(e)
        assert 'enterprise not found' in str(e)
        assert parent_test_id in str(e)


class TestEnterpriseFetcher(object):

    @requests_mock.mock(kw="mock")
    def test_find_normal__success(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        fetcher = EnterpriseFetcher(session.root_object, ENTERPRISE_SPEC_TEST)

        test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(resource_name),
                 status_code=200,
                 json=[{"name": "test_enterprise",
                        "ID": test_id}])

        objects = fetcher.get(filter='name is "test_enterprise"')

        last_request = mock.last_request
        request_headers = last_request.headers
        assert "X-Nuage-Filter" in request_headers
        assert request_headers["X-Nuage-Filter"] == 'name is "test_enterprise"'

        assert len(objects) == 1
        obj = objects[0]
        assert obj.get_name() == "Enterprise"
        assert hasattr(obj, 'name') is True
        assert obj.name == "test_enterprise"
        assert hasattr(obj, 'id') is True
        assert obj.id == test_id

    @requests_mock.mock(kw="mock")
    def test_find_csp__by_name(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        fetcher = EnterpriseFetcher(session.root_object, ENTERPRISE_SPEC_TEST)

        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(resource_name),
                 status_code=404,
                 json=[])

        objects = fetcher.get(filter='name is "%s"' % CSP_ENTERPRISE_NAME)

        assert len(objects) == 1
        obj = objects[0]
        assert obj.get_name() == "Enterprise"
        assert hasattr(obj, 'name') is True
        assert obj.name == CSP_ENTERPRISE_NAME
        assert hasattr(obj, 'id') is True
        assert obj.id == CSP_ENTERPRISE_ID

    @requests_mock.mock(kw="mock")
    def test_find_csp__by_id(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        fetcher = EnterpriseFetcher(session.root_object, ENTERPRISE_SPEC_TEST)

        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(resource_name),
                 status_code=404,
                 json=[])

        objects = fetcher.get(filter='id is "%s"' % CSP_ENTERPRISE_ID)

        assert len(objects) == 1
        obj = objects[0]
        assert obj.get_name() == "Enterprise"
        assert hasattr(obj, 'name') is True
        assert obj.name == CSP_ENTERPRISE_NAME
        assert hasattr(obj, 'id') is True
        assert obj.id == CSP_ENTERPRISE_ID

    @requests_mock.mock(kw="mock")
    def test_find_parent__not_found(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        fetcher = EnterpriseFetcher(session.root_object, ENTERPRISE_SPEC_TEST)

        # test_id = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"

        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(resource_name),
                 status_code=200)

        objects = fetcher.get(filter='name is "test_enterprise"')

        last_request = mock.last_request
        request_headers = last_request.headers
        assert "X-Nuage-Filter" in request_headers
        assert request_headers["X-Nuage-Filter"] == 'name is "test_enterprise"'

        assert len(objects) == 0

    @requests_mock.mock(kw="mock")
    def test_find__multiple(self, **kwargs):
        mock = kwargs['mock']
        session = start_session(mock)
        fetcher = EnterpriseFetcher(session.root_object, ENTERPRISE_SPEC_TEST)

        test_id_1 = "741fc5d9-fce7-4f98-9172-e962be6ee3e2"
        test_id_2 = "741fc5d9-fce7-4f98-9172-e962be6ee3e3"

        resource_name = ENTERPRISE_SPEC_TEST["model"]["resource_name"]

        mock.get(build_standard_mock_url(resource_name),
                 status_code=200,
                 json=[{"name": "test_enterprise",
                        "ID": test_id_1},
                       {"name": "test_enterprise",
                        "ID": test_id_2}])

        objects = fetcher.get()

        assert len(objects) == 3
        obj_1 = objects[0]
        obj_2 = objects[1]
        obj_3 = objects[2]

        assert obj_1.get_name() == "Enterprise"
        assert hasattr(obj_1, 'name') is True
        assert obj_1.name == "test_enterprise"
        assert hasattr(obj_1, 'id') is True
        assert obj_1.id == test_id_1

        assert obj_2.get_name() == "Enterprise"
        assert hasattr(obj_2, 'name') is True
        assert obj_2.name == "test_enterprise"
        assert hasattr(obj_2, 'id') is True
        assert obj_2.id == test_id_2

        assert obj_2.get_name() == "Enterprise"
        assert hasattr(obj_2, 'name') is True
        assert obj_2.name == "test_enterprise"
        assert hasattr(obj_2, 'id') is True
        assert obj_2.id == test_id_2

        assert obj_3.get_name() == "Enterprise"
        assert hasattr(obj_3, 'name') is True
        assert obj_3.name == CSP_ENTERPRISE_NAME
        assert hasattr(obj_3, 'id') is True
        assert obj_3.id == CSP_ENTERPRISE_ID


class TestValidate(object):

    def test__valid(self):
        obj = ConfigObject(ENTERPRISE_SPEC_VALIDATE)

        obj.name = 'a'
        assert hasattr(obj, 'name') is True
        assert obj.validate() is True

        obj.name = 'a' * 255
        assert hasattr(obj, 'name') is True
        assert obj.validate() is True

        obj.name = 'a'
        obj.enableapplicationperformancemanagement = False
        obj.floatingipsquota = 0
        obj.allowedforwardingclasses = []
        obj.encryptionmanagementmode = "DISABLED"
        assert obj.validate() is True

        obj.name = 'a' * 255
        obj.enableapplicationperformancemanagement = True
        obj.floatingipsquota = 250000
        obj.allowedforwardingclasses = ["A", "B"]
        obj.encryptionmanagementmode = "MANAGED"
        assert obj.validate() is True

    @pytest.mark.parametrize("attr, value, message", VALIDATION_ERROR_CASES)
    def test__invalid(self, attr, value, message):
        obj = ConfigObject(ENTERPRISE_SPEC_VALIDATE)

        # Name is required value, make sure it is set
        obj.name = 'a'

        setattr(obj, attr, value)

        assert obj.validate() is False
        attr_error = obj.errors[attr]
        assert message in attr_error['description']

    @pytest.mark.parametrize("attr, value, message", VALIDATION_ERROR_CASES)
    def test__invalid_without_required(self, attr, value, message):
        obj = ConfigObject(ENTERPRISE_SPEC_VALIDATE)

        # Name is required value, make sure it is set
        obj.name = 'a'

        setattr(obj, attr, value)

        if (message == "value is mandatory"):
            assert obj.validate(skip_required_check=True) is True
        else:
            assert obj.validate(skip_required_check=True) is False
            attr_error = obj.errors[attr]
            assert message in attr_error['description']
