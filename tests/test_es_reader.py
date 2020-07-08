from mock import call, patch, MagicMock
import pytest
# import requests_mock

from nuage_metroae_config.errors import (DeviceWriterError,
                                         SessionError)
from nuage_metroae_config.es_reader import (EsError,
                                            EsReader,
                                            MissingSessionParamsError)

TEST_HOST = "localhost"
TEST_PORT = 12345
TEST_INDEX = "nuage_sysmon"


class TestEsReaderSession(object):

    def test_start__success(self):

        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        es_reader.start_session()
        assert es_reader.session_params == {"address": TEST_HOST,
                                            "port": TEST_PORT}

    def test_start__no_params(self):

        es_reader = EsReader()

        with pytest.raises(MissingSessionParamsError) as e:
            es_reader.start_session()

        assert "without parameters" in str(e)

    def test_stop__success(self):

        es_reader = EsReader()

        es_reader.stop_session()

    def test_connect__success(self):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)
        es_reader.start_session()

        es_reader.connect("otherhost")

        assert es_reader.session_params == {"address": "otherhost",
                                            "port": 9200}

    def test_connect__other_port(self):
        es_reader = EsReader()

        es_reader.connect(TEST_HOST, TEST_PORT)

        assert es_reader.session_params == {"address": TEST_HOST,
                                            "port": TEST_PORT}

    def test_connect__no_params(self):
        es_reader = EsReader()

        with pytest.raises(SessionError) as e:
            es_reader.connect()

        assert "parameter is required" in str(e)

    def test_connect__too_many_params(self):
        es_reader = EsReader()

        with pytest.raises(SessionError) as e:
            es_reader.connect(TEST_HOST, TEST_PORT, "extra")

        assert "Too many arguments" in str(e)


class TestEsReaderQuery(object):

    def register_mock_get(self, mock, params, response, status_code=200):
        if "from=" not in params:
            params_end = params + "from=100&size=100"
            params = params + "from=0&size=100"

            end_url = self.get_mock_url(params_end)
            mock.get(end_url, status_code=status_code, json={"hits":
                                                             {"hits": []}})

        url = self.get_mock_url(params)
        response = [{"_source": x} for x in response]
        mock.get(url, status_code=status_code, json={"hits":
                                                     {"hits": response}})

    def get_mock_url(self, params):
        return "http://%s:%d/%s/_search?%s" % (TEST_HOST, TEST_PORT,
                                               TEST_INDEX, params)

    def test_query__no_session(self):
        es_reader = EsReader()

        objects = [
            {"name": TEST_INDEX,
             "filter": None}
        ]

        attributes = "timestamp"

        with pytest.raises(MissingSessionParamsError) as e:
            es_reader.query(objects, attributes)

        assert "without parameters" in str(e)

    def test_attrs_single__success(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None}
        ]

        attributes = "timestamp"

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": "10.1"
        }

        self.register_mock_get(requests_mock, "", [mock_entry_1])

        result = es_reader.query(objects, attributes)

        assert result == [100]

    def test_attrs_single__unknown(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None}
        ]

        attributes = ["timestamp", "memory"]

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": 10.1,
            "memory": 500.2
        }

        self.register_mock_get(requests_mock, "", [mock_entry_1])

        result = es_reader.query(objects, attributes)

        assert result == [{"timestamp": 100, "memory": 500.2}]

    def test_attrs_multiple__unknown(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None}
        ]

        attributes = ["timestamp", "memory", "unknown"]

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": 10.1,
            "memory": 500.2
        }

        self.register_mock_get(requests_mock, "", [mock_entry_1])

        result = es_reader.query(objects, attributes)

        assert result == [{"timestamp": 100, "memory": 500.2}]

    def test_attrs_all__success(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None}
        ]

        attributes = ["*"]

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": 10.1,
            "memory": 500.2
        }

        self.register_mock_get(requests_mock, "", [mock_entry_1])

        result = es_reader.query(objects, attributes)

        assert result == [mock_entry_1]

    def test_index_single__none_found(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None}
        ]

        attributes = "timestamp"

        self.register_mock_get(requests_mock, "", [])

        result = es_reader.query(objects, attributes)

        assert result == []

    def test_index_single__http_error(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None}
        ]

        attributes = "timestamp"

        self.register_mock_get(requests_mock, "", [], status_code=403)

        with pytest.raises(EsError) as e:
            es_reader.query(objects, attributes)

        assert "Status code 403" in str(e)

    def test_index_multiple__success(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None}
        ]

        attributes = "timestamp"

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": "10.1"
        }

        mock_entry_2 = {
            "timestamp": 200,
            "cpu": "20.2"
        }

        mock_entry_3 = {
            "timestamp": 300,
            "cpu": "30.3"
        }

        self.register_mock_get(requests_mock, "",
                               [mock_entry_1, mock_entry_2, mock_entry_3])

        result = es_reader.query(objects, attributes)

        assert result == [100, 200, 300]

    def test_index_multiple_2__success(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None}
        ]

        attributes = ["timestamp", "cpu"]

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": "10.1"
        }

        mock_entry_2 = {
            "timestamp": 200,
            "cpu": "20.2"
        }

        mock_entry_3 = {
            "timestamp": 300,
            "cpu": "30.3"
        }

        self.register_mock_get(requests_mock, "",
                               [mock_entry_1, mock_entry_2, mock_entry_3])

        result = es_reader.query(objects, attributes)

        assert result == [mock_entry_1, mock_entry_2, mock_entry_3]

    def test_nested_object_multiple__success(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "disks",
             "filter": None},
        ]

        attributes = "name"

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": "10.1",
            "disks": [{"name": "cf1:"}, {"name": "cf2:"}]
        }

        mock_entry_2 = {
            "timestamp": 200,
            "cpu": "20.2",
            "disks": [{"name": "cf3:"}, {"name": "cf4:"}]
        }

        self.register_mock_get(requests_mock, "",
                               [mock_entry_1, mock_entry_2])

        result = es_reader.query(objects, attributes)

        assert result == ["cf1:", "cf2:", "cf3:", "cf4:"]

    def test_nested_object_multiple__empty_child(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "disks",
             "filter": None},
        ]

        attributes = "name"

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": "10.1",
            "disks": []
        }

        mock_entry_2 = {
            "timestamp": 200,
            "cpu": "20.2",
            "disks": [{"name": "cf3:"}, {"name": "cf4:"}]
        }

        self.register_mock_get(requests_mock, "",
                               [mock_entry_1, mock_entry_2])

        result = es_reader.query(objects, attributes)

        assert result == ["cf3:", "cf4:"]

    def test_nested_object_multiple__no_child(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "disks",
             "filter": None},
        ]

        attributes = "name"

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": "10.1"
        }

        mock_entry_2 = {
            "timestamp": 200,
            "cpu": "20.2",
            "disks": [{"name": "cf3:"}, {"name": "cf4:"}]
        }

        self.register_mock_get(requests_mock, "",
                               [mock_entry_1, mock_entry_2])

        result = es_reader.query(objects, attributes)

        assert result == ["cf3:", "cf4:"]
