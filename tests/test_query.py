import pytest

from mock_reader import MockReader
from nuage_metroae_config.errors import QueryExecutionError, QueryParseError
from nuage_metroae_config.query import Query

PARSE_ERROR_CASES = [
    ("Enterprise.name Enterprise.Domain.name", 17),
    ("test = ;", 8),
    ("test = enterprise;", 18),
    ("Enterprise[:].name", 13),
    ("Enterprise[field=].name", 18),
    ("Enterprise[field=test field2=other].name", 23),
    ("Enterprise.{}", 13),
    ("count()", 7),
    ("reverse()", 9),
]


class TestQuery(object):

    def run_execute_test(self, query_text, expected_actions, mock_results,
                         expected_results, override_vars={}):
        query = Query()
        reader = MockReader()
        for mock_result in mock_results:
            reader.add_mock_result(mock_result)

        query.set_reader(reader)

        results = query.execute(query_text, **override_vars)

        expected_actions_formatted = self.format_expected_actions(
            expected_actions)

        print "\nExpected actions:"
        print "\n".join(expected_actions_formatted)

        print "\nRecorded actions:"
        print "\n".join(reader.get_recorded_actions())

        assert reader.get_recorded_actions() == expected_actions_formatted
        assert results == expected_results

        return query

    def run_execute_with_exception(self, query_text, expected_actions,
                                   exception, on_action, mock_results,
                                   expected_results=None, expect_error=True,
                                   override_vars={}):
        query = Query()
        reader = MockReader()
        reader.raise_exception(exception, on_action)
        for mock_result in mock_results:
            reader.add_mock_result(mock_result)

        query.set_reader(reader)

        if expect_error:
            with pytest.raises(exception.__class__) as e:
                query.execute(query_text, **override_vars)
                results = None
        else:
            results = query.execute(query_text, **override_vars)

        expected_actions_formatted = self.format_expected_actions(
            expected_actions)

        print "\nExpected actions:"
        print "\n".join(expected_actions_formatted)

        print "\nRecorded actions:"
        print "\n".join(reader.get_recorded_actions())

        assert reader.get_recorded_actions() == expected_actions_formatted
        assert results == expected_results

        if expect_error:
            assert e.value == exception
            return e

    def format_expected_actions(self, expected_actions):
        return filter(None, [x.strip() for x in expected_actions.split("\n")])

    @pytest.mark.parametrize("query_text, col", PARSE_ERROR_CASES)
    def test__parse_errors(self, query_text, col):
        query = Query()
        with pytest.raises(QueryParseError) as e:
            query.execute(query_text)

        assert ("line 1 col " + str(col)) in str(e)

    def test_simple__success(self):

        query_text = "Enterprise.name"

        mock_results = [["value1", "value2"]]
        expected_results = mock_results

        expected_actions = """
            start-session
            query [Enterprise (None)] {name}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_single_line__success(self):

        query_text = "Enterprise.name; Enterprise.Domain.name"

        mock_results = [["value1", "value2"], ["value3", "value4"]]
        expected_results = mock_results

        expected_actions = """
            start-session
            query [Enterprise (None)] {name}
            query [Enterprise (None),Domain (None)] {name}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_multi_line__success(self):

        query_text = """
            # Comment should do nothing
            Enterprise.name
            Enterprise.Domain.name; # Inline comment
        """

        mock_results = [["value1", "value2"], ["value3", "value4"]]
        expected_results = mock_results

        expected_actions = """
            start-session
            query [Enterprise (None)] {name}
            query [Enterprise (None),Domain (None)] {name}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_assign__success(self):

        query_text = """
            enterprises = Enterprise.name
            integer = -20
            list = ["a", "b", "c"]
            string1 = '"str1'
            string2 = "'str2"
            string3 = '''
multiline
'str3'
'''
        """

        query_text += '''string4 = """
multiline
"str4"
"""
'''

        mock_results = [["value1", "value2"]]
        expected_results = [
            {"enterprises": ["value1", "value2"]},
            {"integer": -20},
            {"list": ["a", "b", "c"]},
            {"string1": '"str1'},
            {"string2": "'str2"},
            {"string3": '''
multiline
'str3'
'''},
            {"string4": """
multiline
"str4"
"""}
        ]

        expected_actions = """
            start-session
            query [Enterprise (None)] {name}
            stop-session
        """

        query = self.run_execute_test(query_text, expected_actions,
                                      mock_results, expected_results)

        variables = query.get_variables()
        assert variables["enterprises"] == expected_results[0]["enterprises"]
        assert variables["integer"] == expected_results[1]["integer"]
        assert variables["list"] == expected_results[2]["list"]
        assert variables["string1"] == expected_results[3]["string1"]
        assert variables["string2"] == expected_results[4]["string2"]
        assert variables["string3"] == expected_results[5]["string3"]
        assert variables["string4"] == expected_results[6]["string4"]

    def test_filter_range_1__success(self):

        query_text = "Enterprise[1:10].Domain[:5].Subnet[3].Zone.name"

        mock_results = [["value1", "value2"]]
        expected_results = mock_results

        expected_actions = """
            start-session
            query [Enterprise (%end=10,%start=1),Domain (%end=5),Subnet (%end=4,%start=3),Zone (None)] {name}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_filter_range_2__success(self):

        query_text = "Enterprise[:10].Domain[-2].Subnet[-3:-5].Zone.name"

        mock_results = [["value1", "value2"]]
        expected_results = mock_results

        expected_actions = """
            start-session
            query [Enterprise (%end=10),Domain (%end=-1,%start=-2),Subnet (%end=-5,%start=-3),Zone (None)] {name}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_filter_range_3__success(self):

        query_text = """
            end1 = 10
            index = -2
            start = -3
            end2 = -5
            Enterprise[:$end1].Domain[$index].Subnet[$start:$end2].Zone.name
        """

        mock_results = [["value1", "value2"]]
        expected_results = [
            {"end1": 10},
            {"index": -2},
            {"start": -3},
            {"end2": -5},
            ["value1", "value2"]
        ]

        expected_actions = """
            start-session
            query [Enterprise (%end=10),Domain (%end=-1,%start=-2),Subnet (%end=-5,%start=-3),Zone (None)] {name}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_attributes_1__success(self):

        query_text = """
            Enterprise.{name, desc}
        """

        mock_results = [[{"name": "value1", "desc": "desc1"},
                         {"name": "value2", "desc": "desc1"}]]
        expected_results = mock_results

        expected_actions = """
            start-session
            query [Enterprise (None)] {name,desc}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_filter_sort__success(self):

        query_text = """
            sort_field = "id"
            Enterprise[:10 & %sort=creationtime].Domain[%sort_desc=$sort_field].Subnet[%sort_asc="name" & 3].Zone.name
        """

        mock_results = [["value1", "value2"]]
        expected_results = [{"sort_field": "id"}, ["value1", "value2"]]

        expected_actions = """
            start-session
            query [Enterprise (%end=10,%sort=creationtime),Domain (%sort_desc=id),Subnet (%end=4,%sort_asc=name,%start=3),Zone (None)] {name}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_filter_attrs__success(self):

        query_text = """
            field_value = "value"
            Enterprise[:10 & %sort=creationtime & field1=test].Domain[%sort_desc=id & field1=$field_value & field2="test"].Subnet[field="name"].Zone.name
        """

        mock_results = [["value1", "value2"]]
        expected_results = [{"field_value": "value"}, ["value1", "value2"]]

        expected_actions = """
            start-session
            query [Enterprise (%end=10,%sort=creationtime,field1=test),Domain (%sort_desc=id,field1=value,field2=test),Subnet (field=name),Zone (None)] {name}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_attributes_2__success(self):

        query_text = """
            Enterprise.{*}
        """

        mock_results = [[{"name": "value1", "desc": "desc1"},
                         {"name": "value2", "desc": "desc2"}]]
        expected_results = mock_results

        expected_actions = """
            start-session
            query [Enterprise (None)] {*}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_variables__override(self):

        query_text = """
            given_var = "try override"
            normal_var = "should set"
            test1 = $given_var
            test2 = $normal_var
        """

        mock_results = []
        expected_results = [
            {"given_var": "cannot override"},
            {"normal_var": "should set"},
            {"test1": "cannot override"},
            {"test2": "should set"},
        ]

        expected_actions = """
            start-session
            stop-session
        """

        query = self.run_execute_test(query_text, expected_actions,
                                      mock_results,
                                      expected_results,
                                      {"given_var": "cannot override"})

        variables = query.get_variables()
        assert variables["given_var"] == expected_results[0]["given_var"]
        assert variables["normal_var"] == expected_results[1]["normal_var"]
        assert variables["test1"] == expected_results[2]["test1"]
        assert variables["test2"] == expected_results[3]["test2"]

    def test_variables__undefined(self):

        query_text = """
            test = $unset_variable
        """

        query = Query()
        with pytest.raises(QueryExecutionError) as e:
            query.execute(query_text)

        assert "Unassigned variable" in str(e.value)

    def test_count_1__success(self):

        query_text = """
            count(Enterprise.id)
        """

        mock_results = [[1, 2, 3, 4, 5]]
        expected_results = [5]

        expected_actions = """
            start-session
            query [Enterprise (None)] {id}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_count_2__success(self):

        query_text = """
            list = []
            count($list)
        """

        mock_results = [[]]
        expected_results = [{'list': []}, 0]

        expected_actions = """
            start-session
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_count__invalid_type(self):

        query_text = """
            list = "not a list"
            count($list)
        """

        query = Query()
        with pytest.raises(QueryExecutionError) as e:
            query.execute(query_text)

        assert "Invalid data type" in str(e.value)

    def test_reverse_1__success(self):

        query_text = """
            reverse(Enterprise.id)
        """

        mock_results = [[1, 2, 3, 4, 5]]
        expected_results = [[5, 4, 3, 2, 1]]

        expected_actions = """
            start-session
            query [Enterprise (None)] {id}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_reverse_2__success(self):

        query_text = """
            list = []
            reverse($list)
        """

        mock_results = [[]]
        expected_results = [{'list': []}, []]

        expected_actions = """
            start-session
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_reverse__invalid_type(self):

        query_text = """
            list = "not a list"
            reverse($list)
        """

        query = Query()
        with pytest.raises(QueryExecutionError) as e:
            query.execute(query_text)

        assert "Invalid data type" in str(e.value)

    def test_connect__success(self):

        query_text = """
            first_reader_object.name
            connect("VSD", "https://localhost:8443", "csproot", "csproot", "csp")
            vsd_reader_object.name
            connect("ES", "localhost")
            es_reader_object.name
        """

        expected_results = [
            ["first reader object"],
            ["vsd reader object"],
            ["es reader object"],
        ]

        first_expected_actions = self.format_expected_actions("""
            start-session
            query [first_reader_object (None)] {name}
            stop-session
        """)

        vsd_expected_actions = self.format_expected_actions("""
            connect [https://localhost:8443,csproot,csproot,csp]
            query [vsd_reader_object (None)] {name}
            stop-session
        """)

        es_expected_actions = self.format_expected_actions("""
            connect [localhost]
            query [es_reader_object (None)] {name}
            stop-session
        """)

        query = Query()
        first_reader = MockReader()
        first_reader.add_mock_result(["first reader object"])
        query.set_reader(first_reader)

        vsd_reader = MockReader()
        vsd_reader.add_mock_result(["vsd reader object"])
        query.register_reader("Vsd", vsd_reader)

        es_reader = MockReader()
        es_reader.add_mock_result(["es reader object"])
        query.register_reader("Es", es_reader)

        results = query.execute(query_text)

        assert results == expected_results

        assert first_reader.get_recorded_actions() == first_expected_actions
        assert vsd_reader.get_recorded_actions() == vsd_expected_actions
        assert es_reader.get_recorded_actions() == es_expected_actions

    def test_connect__no_reader(self):

        query_text = """
            reader_object.name
        """

        query = Query()
        with pytest.raises(QueryExecutionError) as e:
            query.execute(query_text)

        assert "No reader for query" in str(e.value)

    def test_connect__wrong_reader(self):

        query_text = """
            first_reader.name
            connect("invalid", "user", "pass")
        """

        query = Query()
        first_reader = MockReader()
        first_reader.add_mock_result(["first reader object"])

        query.set_reader(first_reader)

        with pytest.raises(QueryExecutionError) as e:
            query.execute(query_text)

        assert "Invalid type for connection" in str(e.value)
