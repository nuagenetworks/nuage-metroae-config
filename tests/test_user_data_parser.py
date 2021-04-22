import os
import pytest

from nuage_metroae_config.user_data_parser import (UserDataParseError,
                                                   UserDataParser)
from tests.user_data_test_params import (EXPECTED_ACLS_DATA,
                                         EXPECTED_ACLS_GROUPS_DATA,
                                         EXPECTED_DOMAINS_DATA)

FIXTURE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'fixtures')
VALID_USER_DATA_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                         'valid_user_data')
INVALID_USER_DATA_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                           'invalid_user_data')

PARSE_ERROR_CASES = [
    ('no_exist.json', 'not found'),
    ('invalid_json.json', 'Syntax error'),
    ('invalid_yaml.yaml', 'Syntax error'),
    ('missing_entry.json', 'Invalid entry'),
    ('missing_entry.yaml', 'Invalid entry'),
    ('missing_values.json', 'values'),
    ('missing_values.yaml', 'values'),
    ('invalid_values_1.json', 'must be a dictionary'),
    ('invalid_values_1.yaml', 'must be a dictionary'),
    ('invalid_values_2.json', 'must be a dictionary'),
    ('invalid_values_2.yaml', 'must be a dictionary'),
    ('invalid_fields_not_list_1.json', 'must be a list'),
    ('invalid_fields_not_list_1.yaml', 'must be a list'),
    ('invalid_fields_not_list_2.json', 'must be a list'),
    ('invalid_fields_not_list_2.yaml', 'must be a list'),
    ('invalid_fields_wrong_len.json', 'does not match'),
    ('invalid_fields_wrong_len.yaml', 'does not match'),
    ('invalid_child_missing_entry.json', 'Invalid entry'),
    ('invalid_child_missing_entry.yaml', 'Invalid entry'),
    ('invalid_child_multi_values.json', 'single value sets'),
    ('invalid_child_multi_values.yaml', 'single value sets'),
    ('invalid_group_multi_values.json', 'single value sets'),
    ('invalid_group_multi_values.yaml', 'single value sets')]


class TestUserDataParser(object):

    def validate_valid_user_data(self, data_pairs):
        expected = list()
        expected.extend(EXPECTED_ACLS_DATA)
        expected.extend(EXPECTED_DOMAINS_DATA)
        expected.extend(EXPECTED_ACLS_GROUPS_DATA)
        for i in data_pairs:
            assert i in expected
            expected.remove(i)
        assert len(expected) == 0

    def test_read_dir__success(self):
        parser = UserDataParser()
        parser.read_data(VALID_USER_DATA_DIRECTORY)

        data_pairs = parser.get_template_name_data_pairs()

        self.validate_valid_user_data(data_pairs)

    def test_read_files__success(self):
        parser = UserDataParser()
        parser.read_data(os.path.join(VALID_USER_DATA_DIRECTORY,
                                      'domains.json'))

        parser.read_data(os.path.join(VALID_USER_DATA_DIRECTORY,
                                      'acls.yaml'))

        parser.read_data(os.path.join(VALID_USER_DATA_DIRECTORY,
                                      'empty.yml'))

        parser.read_data(os.path.join(VALID_USER_DATA_DIRECTORY,
                                      'acls_groups.yaml'))

        data_pairs = parser.get_template_name_data_pairs()

        self.validate_valid_user_data(data_pairs)

    @pytest.mark.parametrize("filename, message", PARSE_ERROR_CASES)
    def test_read_files__invalid(self, filename, message):
        parser = UserDataParser()

        with pytest.raises(UserDataParseError) as e:
            parser.read_data(os.path.join(INVALID_USER_DATA_DIRECTORY,
                             filename))

        assert message in str(e.value)
        assert filename in str(e.value)

    def test_group__override(self):
        parser = UserDataParser()
        parser.read_data(os.path.join(INVALID_USER_DATA_DIRECTORY,
                                      'group_override.yaml'))

        expected_data = [
            ('Override', {'val1': 'override',
                          '$group_1': 'test_group',
                          'val2': 2,
                          'val3': 3}),
            ('Override', {'val1': 1,
                          '$group_1': 'test_group',
                          'val2': 2,
                          'val3': 3})]

        data_pairs = parser.get_template_name_data_pairs()

        assert data_pairs == expected_data

    def test_group__ordering(self):
        parser = UserDataParser()
        parser.read_data(os.path.join(INVALID_USER_DATA_DIRECTORY,
                                      'group_ordering.yaml'))

        expected_data = [
            ('Override', {'val1': 'override',
                          '$group_1': 'test_group',
                          'val2': 2,
                          'val3': 3}),
            ('Override', {'val1': 1,
                          '$group_1': 'test_group',
                          'val2': 2,
                          'val3': 3})]

        data_pairs = parser.get_template_name_data_pairs()

        assert data_pairs == expected_data

    def test_group__cross_file(self):
        parser = UserDataParser()
        parser.read_data(os.path.join(INVALID_USER_DATA_DIRECTORY,
                                      'group_cross_file.yaml'))
        parser.read_data(os.path.join(INVALID_USER_DATA_DIRECTORY,
                                      'group_defs.yaml'))

        expected_data = [
            ('Cross file', {'val1': 'override',
                            '$group_1': 'test_group_1',
                            '$group_2': 'test_group_2',
                            'val2': 2,
                            'val3': 3,
                            'val4': 4,
                            'val5': 5}),
            ('Cross file', {'val1': 1,
                            '$group_1': 'test_group_1',
                            '$group_2': 'test_group_2',
                            'val2': 2,
                            'val3': 3,
                            'val4': 4,
                            'val5': 5})]

        data_pairs = parser.get_template_name_data_pairs()

        assert data_pairs == expected_data

    def test_group__loop(self):
        parser = UserDataParser()
        parser.read_data(os.path.join(INVALID_USER_DATA_DIRECTORY,
                                      'group_loop.yaml'))

        expected_data = [
            ('Loop', {'val1': 'override',
                      '$group_1': 'test_group_1',
                      'val2': 2,
                      'val3': 3,
                      'val4': 4,
                      'val5': 5}),
            ('Loop', {'val1': 1,
                      '$group_1': 'test_group_2',
                      'val2': 2,
                      'val3': 3,
                      'val4': 4,
                      'val5': 5})]

        data_pairs = parser.get_template_name_data_pairs()

        assert data_pairs == expected_data

    def test_group__nested(self):
        parser = UserDataParser()
        parser.read_data(os.path.join(INVALID_USER_DATA_DIRECTORY,
                                      'group_nested.yaml'))

        expected_data = [
            ('Template', {'template_val': 'template',
                          '$group_1': 'child',
                          'parent_val': 'parent',
                          'child_val': 'child'})]

        data_pairs = parser.get_template_name_data_pairs()

        assert data_pairs == expected_data

    def test_group__missing(self):
        parser = UserDataParser()
        parser.read_data(os.path.join(INVALID_USER_DATA_DIRECTORY,
                                      'group_missing.yaml'))

        with pytest.raises(UserDataParseError) as e:
            parser.get_template_name_data_pairs()

        assert "Group not_a_group not defined" in str(e)
