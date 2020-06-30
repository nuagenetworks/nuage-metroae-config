import pytest

from mock_reader import MockReader
from nuage_metroae_config.errors import QueryParseError
from nuage_metroae_config.query import Query


class TestQuery(object):

    def run_execute_test(self, query_text, expected_actions, mock_results,
                         expected_results, override_vars={}):
        query = Query()
        reader = MockReader()
        for mock_result in mock_results:
            reader.add_mock_result(mock_result)

        query.set_reader(reader)

        results = query.execute(query_text, **override_vars)

        expected_actions_formatted = filter(
            None, [x.strip() for x in expected_actions.split("\n")])

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

        expected_actions_formatted = filter(
            None, [x.strip() for x in expected_actions.split("\n")])

        print "\nExpected actions:"
        print "\n".join(expected_actions_formatted)

        print "\nRecorded actions:"
        print "\n".join(reader.get_recorded_actions())

        assert reader.get_recorded_actions() == expected_actions_formatted
        assert results == expected_results

        if expect_error:
            assert e.value == exception
            return e

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

    def test_missing_semi__parse_error(self):

        query_text = "Enterprise.name Enterprise.Domain.name"

        query = Query()
        with pytest.raises(QueryParseError) as e:
            query.execute(query_text)

        assert "line 1 col 17" in str(e)

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

    def test_invalid_range__parse_error(self):

        query_text = "Enterprise[:].name"

        query = Query()
        with pytest.raises(QueryParseError) as e:
            query.execute(query_text)

        assert "line 1 col 13" in str(e)

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

    def test_attributes_2__success(self):

        query_text = """
            Enterprise.{*}
        """

        mock_results = [[{"name": "value1", "desc": "desc1"},
                         {"name": "value2", "desc": "desc1"}]]
        expected_results = mock_results

        expected_actions = """
            start-session
            query [Enterprise (None)] {*}
            stop-session
        """

        self.run_execute_test(query_text, expected_actions, mock_results,
                              expected_results)

    def test_invalid_attributes__parse_error(self):

        query_text = "Enterprise.{}"

        query = Query()
        with pytest.raises(QueryParseError) as e:
            query.execute(query_text)

        assert "line 1 col 13" in str(e)
