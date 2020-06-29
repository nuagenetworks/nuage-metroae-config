import pytest

from mock_reader import MockReader
from nuage_metroae_config.query import Query


class TestQueryExecute(object):

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
