import pytest

from nuage_metroae_config.variable_reader import VariableReader

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


class TestVariableReaderSession(object):

    def test_start__success(self):

        var_reader = VariableReader()

        var_reader.start_session()

    def test_stop__success(self):

        var_reader = VariableReader()

        var_reader.stop_session()

    def test_connect__not_supported(self):
        var_reader = VariableReader()

        with pytest.raises(NotImplementedError):
            var_reader.connect("host")


class TestVariableReaderQuery(object):

    def test_attrs_single__success(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
             "filter": None}
        ]

        attributes = "timestamp"

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": "10.1"
        }

        var_reader.set_data([mock_entry_1])

        result = var_reader.query(objects, attributes)

        assert result == [100]

    def test_attrs_single__unknown(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
             "filter": None}
        ]

        attributes = ["timestamp", "memory"]

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": 10.1,
            "memory": 500.2
        }

        var_reader.set_data([mock_entry_1])

        result = var_reader.query(objects, attributes)

        assert result == [{"timestamp": 100, "memory": 500.2}]

    def test_attrs_multiple__unknown(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
             "filter": None}
        ]

        attributes = ["timestamp", "memory", "unknown"]

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": 10.1,
            "memory": 500.2
        }

        var_reader.set_data([mock_entry_1])

        result = var_reader.query(objects, attributes)

        assert result == [{"timestamp": 100, "memory": 500.2}]

    def test_attrs_all__success(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
             "filter": None}
        ]

        attributes = ["*"]

        mock_entry_1 = {
            "timestamp": 100,
            "cpu": 10.1,
            "memory": 500.2
        }

        var_reader.set_data([mock_entry_1])

        result = var_reader.query(objects, attributes)

        assert result == [mock_entry_1]

    def test_single__none_found(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
             "filter": None}
        ]

        attributes = "timestamp"

        result = var_reader.query(objects, attributes)

        assert result == []

    def test_multiple__success(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry_1, mock_entry_2, mock_entry_3])

        result = var_reader.query(objects, attributes)

        assert result == [100, 200, 300]

    def test_multiple_2__success(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry_1, mock_entry_2, mock_entry_3])

        result = var_reader.query(objects, attributes)

        assert result == [mock_entry_1, mock_entry_2, mock_entry_3]

    def test_nested_object_multiple__success(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry_1, mock_entry_2])

        result = var_reader.query(objects, attributes)

        assert result == ["cf1:", "cf2:", "cf3:", "cf4:"]

    def test_nested_object_multiple__empty_child(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry_1, mock_entry_2])

        result = var_reader.query(objects, attributes)

        assert result == ["cf3:", "cf4:"]

    def test_nested_object_multiple__no_child(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry_1, mock_entry_2])

        result = var_reader.query(objects, attributes)

        assert result == ["cf3:", "cf4:"]

    def test_group_parent__success(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry_1, mock_entry_2, mock_entry_3,
                             mock_entry_4])

        results = var_reader.query(objects, attributes)

        assert results == [
            [10,
                ["domain_1", "domain_2", "domain_3", "domain_4"]],
            [20,
                []],
            [30,
                ["domain_5", "domain_6"]]
        ]

    def test_group_child__success(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry_1, mock_entry_2, mock_entry_3,
                             mock_entry_4])

        results = var_reader.query(objects, attributes)

        assert results == [
            [True,
                ["domain_1", "domain_3", "domain_4", "domain_5", "domain_6"]],
            [False,
                ["domain_2"]]
        ]

    def test_group_both__success(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry_1, mock_entry_2, mock_entry_3,
                             mock_entry_4])

        results = var_reader.query(objects, attributes)

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

    def test_group_both_filtered__success(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry_1, mock_entry_2, mock_entry_3,
                             mock_entry_4])

        results = var_reader.query(objects, attributes)

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

    @pytest.mark.parametrize("filter, expected", QUERY_NESTED_RANGE_SORT_CASES)
    def test_nested_range_sort__success(self, filter, expected):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry])

        results = var_reader.query(objects, attributes)

        assert results == expected

    @pytest.mark.parametrize("filter, expected",
                             QUERY_NESTED_ATTR_FILTER_CASES)
    def test_nested_attr_filter__success(self, filter, expected):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
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

        var_reader.set_data([mock_entry])

        results = var_reader.query(objects, attributes)

        assert results == expected

    def test_nested__not_found(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
             "filter": None},
            {"name": "foobar",
             "filter": None}
        ]

        attributes = "name"

        mock_object_1 = {"name": "a1",
                         "dhcpleaseinterval": 300,
                         "avatartype": "URL"}

        mock_entry = {"objects": [mock_object_1]}

        var_reader.set_data([mock_entry])

        results = var_reader.query(objects, attributes)

        assert results == []

    def test_nested__not_dict(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
             "filter": None},
            {"name": "not_a_dict",
             "filter": None}
        ]

        attributes = "name"

        mock_object_1 = "not_a_dict"

        mock_entry = {"objects": [mock_object_1]}

        var_reader.set_data([mock_entry])

        results = var_reader.query(objects, attributes)

        assert results == []

    def test_nested__no_attr(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
             "filter": None},
            {"name": "objects",
             "filter": None}
        ]

        attributes = "foobar"

        mock_object_1 = {"name": "a1",
                         "dhcpleaseinterval": 300,
                         "avatartype": "URL"}

        mock_entry = {"objects": [mock_object_1]}

        var_reader.set_data([mock_entry])

        results = var_reader.query(objects, attributes)

        assert results == []

    def test_nested__no_attr_multiple(self):
        var_reader = VariableReader()

        objects = [
            {"name": "v",
             "filter": None},
            {"name": "objects",
             "filter": None}
        ]

        attributes = ["name", "foobar"]

        mock_object_1 = {"name": "a1",
                         "dhcpleaseinterval": 300,
                         "avatartype": "URL"}

        mock_entry = {"objects": [mock_object_1]}

        var_reader.set_data([mock_entry])

        results = var_reader.query(objects, attributes)

        assert results == [{"name": "a1"}]

    def test_query_attribute__success(self):
        var_reader = VariableReader()

        mock_object = {"name": "object name"}

        value = var_reader.query_attribute(mock_object, "name")
        assert value == "object name"

    def test_query_attribute__not_found(self):
        var_reader = VariableReader()

        mock_object = {"name": "object name"}

        value = var_reader.query_attribute(mock_object, "foobar")
        assert value is None

    def test_query_attribute__bad_type(self):
        var_reader = VariableReader()

        mock_object = ["name", "object name"]

        value = var_reader.query_attribute(mock_object, "name")
        assert value is None
