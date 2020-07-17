import pytest

from nuage_metroae_config.errors import SessionError
from nuage_metroae_config.es_reader import (EsError,
                                            EsReader,
                                            MissingSessionParamsError)

TEST_HOST = "localhost"
TEST_PORT = 12345
TEST_INDEX = "nuage_sysmon"

QUERY_INDEX_RANGE_SORT_CASES = [
    ({}, ""),
    ({"%end": 3}, "from=0&size=3"),
    ({"%end": 99}, "from=0&size=99"),
    ({"%end": 0}, "from=0&size=0"),
    ({"%start": 0}, ""),
    ({"%start": 3}, "from=3&size=100"),
    ({"%start": 99}, "from=99&size=100"),
    ({"%start": 0, "%end": 5}, "from=0&size=5"),
    ({"%start": 1, "%end": 3}, "from=1&size=2"),
    ({"%start": 3, "%end": 99}, "from=3&size=96"),
    ({"%start": 3, "%end": 4}, "from=3&size=1"),
    ({"%start": 3, "%end": 3}, "from=3&size=0"),
    ({"%start": 4, "%end": 3}, "from=4&size=0"),

    ({"%sort": "name"}, "sort=name:asc&"),
    ({"%sort": "name", "%end": 3}, "sort=name:asc&from=0&size=3"),
    ({"%sort": "name", "%end": 99}, "sort=name:asc&from=0&size=99"),
    ({"%sort": "name", "%end": 0}, "sort=name:asc&from=0&size=0"),
    ({"%sort": "name", "%start": 0}, "sort=name:asc&"),
    ({"%sort": "name", "%start": 3}, "sort=name:asc&from=3&size=100"),
    ({"%sort": "name", "%start": 99}, "sort=name:asc&from=99&size=100"),
    ({"%sort": "name", "%start": 0, "%end": 5}, "sort=name:asc&from=0&size=5"),
    ({"%sort": "name", "%start": 1, "%end": 3}, "sort=name:asc&from=1&size=2"),
    ({"%sort": "name", "%start": 3, "%end": 99}, "sort=name:asc&from=3&size=96"),
    ({"%sort": "name", "%start": 3, "%end": 4}, "sort=name:asc&from=3&size=1"),
    ({"%sort": "name", "%start": 3, "%end": 3}, "sort=name:asc&from=3&size=0"),
    ({"%sort": "name", "%start": 4, "%end": 3}, "sort=name:asc&from=4&size=0"),

    ({"%sort_asc": "name"}, "sort=name:asc&"),
    ({"%sort_asc": "name", "%end": 3}, "sort=name:asc&from=0&size=3"),
    ({"%sort_asc": "name", "%end": 99}, "sort=name:asc&from=0&size=99"),
    ({"%sort_asc": "name", "%end": 0}, "sort=name:asc&from=0&size=0"),
    ({"%sort_asc": "name", "%start": 0}, "sort=name:asc&"),
    ({"%sort_asc": "name", "%start": 3}, "sort=name:asc&from=3&size=100"),
    ({"%sort_asc": "name", "%start": 99}, "sort=name:asc&from=99&size=100"),
    ({"%sort_asc": "name", "%start": 0, "%end": 5}, "sort=name:asc&from=0&size=5"),
    ({"%sort_asc": "name", "%start": 1, "%end": 3}, "sort=name:asc&from=1&size=2"),
    ({"%sort_asc": "name", "%start": 3, "%end": 99}, "sort=name:asc&from=3&size=96"),
    ({"%sort_asc": "name", "%start": 3, "%end": 4}, "sort=name:asc&from=3&size=1"),
    ({"%sort_asc": "name", "%start": 3, "%end": 3}, "sort=name:asc&from=3&size=0"),
    ({"%sort_asc": "name", "%start": 4, "%end": 3}, "sort=name:asc&from=4&size=0"),

    ({"%sort_desc": "name"}, "sort=name:desc&"),
    ({"%sort_desc": "name", "%end": 3}, "sort=name:desc&from=0&size=3"),
    ({"%sort_desc": "name", "%end": 99}, "sort=name:desc&from=0&size=99"),
    ({"%sort_desc": "name", "%end": 0}, "sort=name:desc&from=0&size=0"),
    ({"%sort_desc": "name", "%start": 0}, "sort=name:desc&"),
    ({"%sort_desc": "name", "%start": 3}, "sort=name:desc&from=3&size=100"),
    ({"%sort_desc": "name", "%start": 99}, "sort=name:desc&from=99&size=100"),
    ({"%sort_desc": "name", "%start": 0, "%end": 5}, "sort=name:desc&from=0&size=5"),
    ({"%sort_desc": "name", "%start": 1, "%end": 3}, "sort=name:desc&from=1&size=2"),
    ({"%sort_desc": "name", "%start": 3, "%end": 99}, "sort=name:desc&from=3&size=96"),
    ({"%sort_desc": "name", "%start": 3, "%end": 4}, "sort=name:desc&from=3&size=1"),
    ({"%sort_desc": "name", "%start": 3, "%end": 3}, "sort=name:desc&from=3&size=0"),
    ({"%sort_desc": "name", "%start": 4, "%end": 3}, "sort=name:desc&from=4&size=0"),

    ({"timestamp": 100, "%sort": "name"}, "q=timestamp:100&sort=name:asc&"),
    ({"timestamp": 100, "%sort": "name", "%end": 3}, "q=timestamp:100&sort=name:asc&from=0&size=3"),
    ({"timestamp": 100, "%sort": "name", "%end": 99}, "q=timestamp:100&sort=name:asc&from=0&size=99"),
    ({"timestamp": 100, "%sort": "name", "%end": 0}, "q=timestamp:100&sort=name:asc&from=0&size=0"),
    ({"timestamp": 100, "%sort": "name", "%start": 0}, "q=timestamp:100&sort=name:asc&"),
    ({"timestamp": 100, "%sort": "name", "%start": 3}, "q=timestamp:100&sort=name:asc&from=3&size=100"),
    ({"timestamp": 100, "%sort": "name", "%start": 99}, "q=timestamp:100&sort=name:asc&from=99&size=100"),
    ({"timestamp": 100, "%sort": "name", "%start": 0, "%end": 5}, "q=timestamp:100&sort=name:asc&from=0&size=5"),
    ({"timestamp": 100, "%sort": "name", "%start": 1, "%end": 3}, "q=timestamp:100&sort=name:asc&from=1&size=2"),
    ({"timestamp": 100, "%sort": "name", "%start": 3, "%end": 99}, "q=timestamp:100&sort=name:asc&from=3&size=96"),
    ({"timestamp": 100, "%sort": "name", "%start": 3, "%end": 4}, "q=timestamp:100&sort=name:asc&from=3&size=1"),
    ({"timestamp": 100, "%sort": "name", "%start": 3, "%end": 3}, "q=timestamp:100&sort=name:asc&from=3&size=0"),
    ({"timestamp": 100, "%sort": "name", "%start": 4, "%end": 3}, "q=timestamp:100&sort=name:asc&from=4&size=0"),

    ({"timestamp": 100, "name": "a1", "%sort": "name"}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%end": 3}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=0&size=3"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%end": 99}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=0&size=99"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%end": 0}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=0&size=0"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%start": 0}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%start": 3}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=3&size=100"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%start": 99}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=99&size=100"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%start": 0, "%end": 5}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=0&size=5"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%start": 1, "%end": 3}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=1&size=2"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%start": 3, "%end": 99}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=3&size=96"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%start": 3, "%end": 4}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=3&size=1"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%start": 3, "%end": 3}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=3&size=0"),
    ({"timestamp": 100, "name": "a1", "%sort": "name", "%start": 4, "%end": 3}, "sort=name:asc&q=timestamp:100%20AND%20name:a1&from=4&size=0"),
]

QUERY_INDEX_PAGING_CASES = [
    ({}, ["from=0&size=100"], [50]),
    ({}, ["from=0&size=100", "from=100&size=100"], [100, 50]),
    ({}, ["from=0&size=100", "from=100&size=100", "from=200&size=100"], [100, 100, 0]),
    ({}, ["from=0&size=100", "from=100&size=100"], [100, 99]),
    ({"%start": 1}, ["from=1&size=100"], [50]),
    ({"%start": 1}, ["from=1&size=100", "from=101&size=100"], [100, 50]),
    ({"%start": 1}, ["from=1&size=100", "from=101&size=100", "from=201&size=100"], [100, 100, 0]),
    ({"%start": 1}, ["from=1&size=100", "from=101&size=100"], [100, 99]),
    ({"%end": 0}, [], [0]),
    ({"%end": 50}, ["from=0&size=50"], [50]),
    ({"%end": 100}, ["from=0&size=100"], [50]),
    ({"%end": 100}, ["from=0&size=100"], [100]),
    ({"%end": 101}, ["from=0&size=100"], [99]),
    ({"%end": 101}, ["from=0&size=100", "from=100&size=1"], [100, 0]),
    ({"%start": 1, "%end": 0}, [], [0]),
    ({"%start": 1, "%end": 2}, ["from=1&size=1"], [1]),
    ({"%start": 1, "%end": 100}, ["from=1&size=99"], [99]),
    ({"%start": 1, "%end": 101}, ["from=1&size=100"], [100]),
    ({"%start": 1, "%end": 102}, ["from=1&size=100", "from=101&size=1"], [100, 1]),
    ({"%start": 1, "%end": 202}, ["from=1&size=100", "from=101&size=100", "from=201&size=1"], [100, 100, 1]),
]

QUERY_NESTED_RANGE_SORT_CASES = [
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

QUERY_NESTED_ATTR_FILTER_CASES = [
    ({}, ["a1", "a3", "a5", "a2", "a4"]),
    ({"avatartype": "URL"}, ["a1", "a3", "a5"]),
    ({"avatartype": "URL", "%sort_desc": "dhcpleaseinterval"}, ["a5", "a3", "a1"]),
    ({"avatartype": "URL", "%start": 1, "%end": 2}, ["a3"]),
    ({"avatartype": "BASE64"}, ["a2", "a4"]),
    ({"avatartype": "BASE64", "name": "a2"}, ["a2"]),
    ({"avatartype": "URL", "name": "a2"}, []),
    ({"name": ["a1", "a2", "a3"]}, ["a1", "a3", "a2"]),
    ({"avatartype": "BASE64", "name": ["a1", "a2", "a3"]}, ["a2"]),
]


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
            params = params + "from=0&size=100"

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

    def test_group_parent__success(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": {"%group": "dhcpleaseinterval"}},
            {"name": "domains",
             "filter": None},
        ]

        attributes = "name"

        mock_entry_1 = {
            "name": "enterprise_1",
            "dhcpleaseinterval": 10,
            "domains": [
                {"name": "domain_1",
                 "bgpenabled": True},
                {"name": "domain_2",
                 "bgpenabled": False}
            ]
        }

        mock_entry_2 = {
            "name": "enterprise_2",
            "dhcpleaseinterval": 20,
            "domains": []
        }

        mock_entry_3 = {
            "name": "enterprise_3",
            "dhcpleaseinterval": 10,
            "domains": [
                {"name": "domain_3",
                 "bgpenabled": True},
                {"name": "domain_4",
                 "bgpenabled": True}
            ]
        }

        mock_entry_4 = {
            "name": "enterprise_4",
            "dhcpleaseinterval": 30,
            "domains": [
                {"name": "domain_5",
                 "bgpenabled": True},
                {"name": "domain_6",
                 "bgpenabled": True}
            ]
        }

        self.register_mock_get(requests_mock, "",
                               [mock_entry_1, mock_entry_2, mock_entry_3,
                                mock_entry_4])

        results = es_reader.query(objects, attributes)

        assert results == [
            [10,
                ["domain_1", "domain_2", "domain_3", "domain_4"]],
            [20,
                []],
            [30,
                ["domain_5", "domain_6"]]
        ]

    def test_group_child__success(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "domains",
             "filter": {"%group": "bgpenabled"}},
        ]

        attributes = "name"

        mock_entry_1 = {
            "name": "enterprise_1",
            "dhcpleaseinterval": 10,
            "domains": [
                {"name": "domain_1",
                 "bgpenabled": True},
                {"name": "domain_2",
                 "bgpenabled": False}
            ]
        }

        mock_entry_2 = {
            "name": "enterprise_2",
            "dhcpleaseinterval": 20,
            "domains": []
        }

        mock_entry_3 = {
            "name": "enterprise_3",
            "dhcpleaseinterval": 10,
            "domains": [
                {"name": "domain_3",
                 "bgpenabled": True},
                {"name": "domain_4",
                 "bgpenabled": True}
            ]
        }

        mock_entry_4 = {
            "name": "enterprise_4",
            "dhcpleaseinterval": 30,
            "domains": [
                {"name": "domain_5",
                 "bgpenabled": True},
                {"name": "domain_6",
                 "bgpenabled": True}
            ]
        }

        self.register_mock_get(requests_mock, "",
                               [mock_entry_1, mock_entry_2, mock_entry_3,
                                mock_entry_4])

        results = es_reader.query(objects, attributes)

        assert results == [
            [True,
                ["domain_1", "domain_3", "domain_4", "domain_5", "domain_6"]],
            [False,
                ["domain_2"]]
        ]

    def test_group_both__success(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": {"%group": "dhcpleaseinterval"}},
            {"name": "domains",
             "filter": {"%group": "bgpenabled"}},
        ]

        attributes = "name"

        mock_entry_1 = {
            "name": "enterprise_1",
            "dhcpleaseinterval": 10,
            "domains": [
                {"name": "domain_1",
                 "bgpenabled": True},
                {"name": "domain_2",
                 "bgpenabled": False}
            ]
        }

        mock_entry_2 = {
            "name": "enterprise_2",
            "dhcpleaseinterval": 20,
            "domains": []
        }

        mock_entry_3 = {
            "name": "enterprise_3",
            "dhcpleaseinterval": 10,
            "domains": [
                {"name": "domain_3",
                 "bgpenabled": True},
                {"name": "domain_4",
                 "bgpenabled": True}
            ]
        }

        mock_entry_4 = {
            "name": "enterprise_4",
            "dhcpleaseinterval": 30,
            "domains": [
                {"name": "domain_5",
                 "bgpenabled": True},
                {"name": "domain_6",
                 "bgpenabled": True}
            ]
        }

        self.register_mock_get(requests_mock, "",
                               [mock_entry_1, mock_entry_2, mock_entry_3,
                                mock_entry_4])

        results = es_reader.query(objects, attributes)

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

    def test_group_both_filtered__success(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": {"%group": "dhcpleaseinterval"}},
            {"name": "domains",
             "filter": {"%group": "bgpenabled",
                        "bgpenabled": True}}
        ]

        attributes = "name"

        mock_entry_1 = {
            "name": "enterprise_1",
            "dhcpleaseinterval": 10,
            "domains": [
                {"name": "domain_1",
                 "bgpenabled": True},
                {"name": "domain_2",
                 "bgpenabled": False}
            ]
        }

        mock_entry_2 = {
            "name": "enterprise_2",
            "dhcpleaseinterval": 20,
            "domains": []
        }

        mock_entry_3 = {
            "name": "enterprise_3",
            "dhcpleaseinterval": 10,
            "domains": [
                {"name": "domain_3",
                 "bgpenabled": True},
                {"name": "domain_4",
                 "bgpenabled": True}
            ]
        }

        mock_entry_4 = {
            "name": "enterprise_4",
            "dhcpleaseinterval": 30,
            "domains": [
                {"name": "domain_5",
                 "bgpenabled": True},
                {"name": "domain_6",
                 "bgpenabled": True}
            ]
        }

        self.register_mock_get(requests_mock, "",
                               [mock_entry_1, mock_entry_2, mock_entry_3,
                                mock_entry_4])

        results = es_reader.query(objects, attributes)

        assert results == [
            [10,
                [[True,
                    ["domain_1", "domain_3", "domain_4"]]]],
            [20,
                [[True,
                    []]]],
            [30,
                [[True,
                    ["domain_5", "domain_6"]]]]
        ]

    @pytest.mark.parametrize("filter, params",
                             QUERY_INDEX_RANGE_SORT_CASES)
    def test_index_range_sort__success(self, filter, params, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": filter}
        ]

        attributes = "timestamp"

        mock_entry_1 = {"timestamp": 100}
        mock_entry_3 = {"timestamp": 300}
        mock_entry_5 = {"timestamp": 500}
        mock_entry_2 = {"timestamp": 200}
        mock_entry_4 = {"timestamp": 400}

        self.register_mock_get(requests_mock, params,
                               [mock_entry_1, mock_entry_3, mock_entry_5,
                                mock_entry_2, mock_entry_4])

        result = es_reader.query(objects, attributes)

        if params.endswith("size=0"):
            assert result == []
        else:
            assert result == [100, 300, 500, 200, 400]

    def test_index_range_sort__negative_start(self):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": {"%start": -1}}
        ]

        attributes = "timestamp"

        with pytest.raises(EsError) as e:
            es_reader.query(objects, attributes)

        assert "negative indicies" in str(e)

    def test_index_range_sort__negative_end(self):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": {"%end": -1}}
        ]

        attributes = "timestamp"

        with pytest.raises(EsError) as e:
            es_reader.query(objects, attributes)

        assert "negative indicies" in str(e)

    def test_index_range_sort__invalid_filter(self):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": {"%foobar": "not cool"}}
        ]

        attributes = "timestamp"

        with pytest.raises(EsError) as e:
            es_reader.query(objects, attributes)

        assert "Invalid filter" in str(e)

    def test_index_range_sort__attr_list(self):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": {"timestamp": [100, 200]}}
        ]

        attributes = "timestamp"

        with pytest.raises(EsError) as e:
            es_reader.query(objects, attributes)

        assert "does not support" in str(e)

    @pytest.mark.parametrize("filter, params_per_call, num_per_call",
                             QUERY_INDEX_PAGING_CASES)
    def test_index_paging__success(self, filter, params_per_call, num_per_call,
                                   requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": filter}
        ]

        attributes = "name"

        mock_entry = {"name": "test"}

        for params, num_items in zip(params_per_call, num_per_call):
            self.register_mock_get(requests_mock, params,
                                   [mock_entry] * num_items)

        results = es_reader.query(objects, attributes)

        assert len(results) == sum(num_per_call)
        if len(results) > 0:
            assert results[0] == "test"

    @pytest.mark.parametrize("filter, expected", QUERY_NESTED_RANGE_SORT_CASES)
    def test_nested_range_sort__success(self, filter, expected, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "name",
             "filter": filter}
        ]

        attributes = "name"

        mock_object_1 = {"name": "a1"}
        mock_object_3 = {"name": "a3"}
        mock_object_5 = {"name": "a5"}
        mock_object_2 = {"name": "a2"}
        mock_object_4 = {"name": "a4"}

        mock_entry = [mock_object_1, mock_object_3,
                      mock_object_5, mock_object_2,
                      mock_object_4]

        self.register_mock_get(requests_mock, "", [mock_entry])

        results = es_reader.query(objects, attributes)

        assert results == expected

    @pytest.mark.parametrize("filter, expected",
                             QUERY_NESTED_ATTR_FILTER_CASES)
    def test_nested_attr_filter__success(self, filter, expected,
                                         requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "objects",
             "filter": filter}
        ]

        attributes = "name"

        mock_object_1 = {"name": "a1",
                         "dhcpleaseinterval": 300,
                         "avatartype": "URL"}
        mock_object_3 = {"name": "a3",
                         "dhcpleaseinterval": 400,
                         "avatartype": "URL"}
        mock_object_5 = {"name": "a5",
                         "dhcpleaseinterval": 500,
                         "avatartype": "URL"}
        mock_object_2 = {"name": "a2",
                         "dhcpleaseinterval": 100,
                         "avatartype": "BASE64"}
        mock_object_4 = {"name": "a4",
                         "dhcpleaseinterval": 200,
                         "avatartype": "BASE64"}

        mock_entry = {"objects": [mock_object_1, mock_object_3,
                      mock_object_5, mock_object_2,
                      mock_object_4]}

        self.register_mock_get(requests_mock, "", [mock_entry])

        results = es_reader.query(objects, attributes)

        assert results == expected

    def test_nested__not_found(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "foobar",
             "filter": None}
        ]

        attributes = "name"

        mock_object_1 = {"name": "a1",
                         "dhcpleaseinterval": 300,
                         "avatartype": "URL"}

        mock_entry = {"objects": [mock_object_1]}

        self.register_mock_get(requests_mock, "", [mock_entry])

        results = es_reader.query(objects, attributes)

        assert results == []

    def test_nested__not_dict(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "not_a_dict",
             "filter": None}
        ]

        attributes = "name"

        mock_object_1 = "not_a_dict"

        mock_entry = {"objects": [mock_object_1]}

        self.register_mock_get(requests_mock, "", [mock_entry])

        results = es_reader.query(objects, attributes)

        assert results == []

    def test_nested__no_attr(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "objects",
             "filter": None}
        ]

        attributes = "foobar"

        mock_object_1 = {"name": "a1",
                         "dhcpleaseinterval": 300,
                         "avatartype": "URL"}

        mock_entry = {"objects": [mock_object_1]}

        self.register_mock_get(requests_mock, "", [mock_entry])

        results = es_reader.query(objects, attributes)

        assert results == []

    def test_nested__no_attr_multiple(self, requests_mock):
        es_reader = EsReader()
        es_reader.set_session_params(TEST_HOST, TEST_PORT)

        objects = [
            {"name": TEST_INDEX,
             "filter": None},
            {"name": "objects",
             "filter": None}
        ]

        attributes = ["name", "foobar"]

        mock_object_1 = {"name": "a1",
                         "dhcpleaseinterval": 300,
                         "avatartype": "URL"}

        mock_entry = {"objects": [mock_object_1]}

        self.register_mock_get(requests_mock, "", [mock_entry])

        results = es_reader.query(objects, attributes)

        assert results == [{"name": "a1"}]

    def test_query_attribute__success(self):
        es_reader = EsReader()

        mock_object = {"name": "object name"}

        value = es_reader.query_attribute(mock_object, "name")
        assert value == "object name"

    def test_query_attribute__not_found(self):
        es_reader = EsReader()

        mock_object = {"name": "object name"}

        value = es_reader.query_attribute(mock_object, "foobar")
        assert value is None

    def test_query_attribute__bad_type(self):
        es_reader = EsReader()

        mock_object = ["name", "object name"]

        value = es_reader.query_attribute(mock_object, "name")
        assert value is None
