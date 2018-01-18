import os

from levistate.user_data_parser import (UserDataParseError,
                                        UserDataParser)
from user_data_test_params import (EXPECTED_ACLS_DATA,
                                   EXPECTED_ACLS_GROUPS_DATA,
                                   EXPECTED_DOMAINS_DATA)

FIXTURE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'fixtures')
VALID_USER_DATA_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                         'valid_user_data')
INVALID_USER_DATA_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                           'invalid_user_data')


class TestUserDataParser(object):

    def validate_valid_user_data(self, data_pairs):
        expected = list()
        expected.extend(EXPECTED_ACLS_DATA)
        expected.extend(EXPECTED_DOMAINS_DATA)
        expected.extend(EXPECTED_ACLS_GROUPS_DATA)

        assert sorted(data_pairs) == sorted(expected)

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
                                      'acls_groups.yaml'))

        data_pairs = parser.get_template_name_data_pairs()

        self.validate_valid_user_data(data_pairs)
