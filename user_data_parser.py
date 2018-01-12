import os
import yaml


class UserDataParseError(Exception):
    """
    Exception class for errors parsing user data files
    """
    pass


class UserDataParser(object):
    """
    Parses Yaml or JSON files containing template user data
    """
    def __init__(self):
        self.data = list()

    def read_data(self, path_or_file_name):
        """
        Reads and parses user data from either all files in a
        directory path, or a single file specified by filename.
        Both yaml (.yml) and JSON (.json) files are supported.
        """
        if (os.path.isdir(path_or_file_name)):
            for file_name in os.listdir(path_or_file_name):
                if (file_name.endswith(".yml") or
                        file_name.endswith(".yaml") or
                        file_name.endswith(".json")):
                    full_path = os.path.join(path_or_file_name, file_name)
                    user_data_string = self._read_data(full_path)
                    self._parse_data_string(user_data_string, full_path)
        elif os.path.isfile(path_or_file_name):
            user_data_string = self._read_data(path_or_file_name)
            self._parse_data_string(user_data_string, path_or_file_name)
        else:
            raise UserDataParseError("File or path not found: " +
                                     path_or_file_name)

    def add_data(self, user_data_string):
        """
        Parses the specified string as user data in Yaml or JSON format.
        """
        self._parse_data_string(user_data_string)

    def get_template_name_data_pairs(self):
        return self.data

    #
    # Private functions to do the work
    #

    @staticmethod
    def _get_dict_field(data_dict, field):
        if type(data_dict) != dict:
            raise UserDataParseError("Invalid user data entry: " +
                                     str(data_dict))

        for key, value in data_dict.iteritems():
            if str(key).lower() == field:
                return value

        return None

    def _read_data(self, filename):
        try:
            with open(filename, 'r') as file:
                return file.read()
        except Exception as e:
            raise UserDataParseError("Error reading user data: " + str(e))

    def _parse_data_string(self, user_data_string, filename="(internal)"):
        data_dict = self._decode_to_dict(user_data_string, filename)
        self._parse_data_entries(data_dict)

    def _decode_to_dict(self, user_data_string, filename):
        try:
            data_dict = yaml.safe_load(user_data_string)
        except yaml.YAMLError as e:
            if hasattr(e, 'problem_mark'):
                lineno = str(e.problem_mark.line)
            else:
                lineno = '?'
            raise UserDataParseError("Syntax error in %s:%s: %s" %
                                     (filename, lineno, str(e)))
        return data_dict

    def _parse_data_entries(self, data_dict, parent_values={}):
        if type(data_dict) == list:
            for template in data_dict:
                self._parse_data_entry(template, parent_values)
        else:
            self._parse_data_entry(data_dict, parent_values)

    def _parse_data_entry(self, data_dict, parent_values):
        template = UserDataParser._get_dict_field(data_dict, 'template')

        if len(data_dict.keys()) != 1 or template is None:
            raise UserDataParseError("Invalid user data entry: " +
                                     str(data_dict))

        self._parse_template_entry(template, parent_values)

    def _parse_template_entry(self, template_dict, parent_values):
        name = UserDataParser._get_dict_field(template_dict, 'name')
        if name is None:
            raise UserDataParseError("Missing required template field 'name'")

        values = UserDataParser._get_dict_field(template_dict, 'values')
        if values is None:
            raise UserDataParseError(
                "Missing required template field 'values'")

        values_list = self._parse_values_list(values)
        self._add_data_entries(name, values_list, parent_values)

        children = UserDataParser._get_dict_field(template_dict, 'children')
        if children is not None:
            if len(values_list) == 1:
                self._parse_data_entries(children, values_list[0])
            else:
                raise UserDataParseError(
                    "Only templates with single value sets may have children")

    def _parse_values_list(self, values_entry):
        values = list()
        if type(values_entry) == list:
            for entry in values_entry:
                values.append(self._parse_values(entry))
        else:
            values.append(self._parse_values(values_entry))

        return values

    def _parse_values(self, values_dict):
        if type(values_dict) != dict:
            raise UserDataParseError("Invalid values entry: " +
                                     str(values_dict))

        return values_dict

    def _add_data_entries(self, template_name, template_values_list,
                          parent_values):
        for values_dict in template_values_list:
            for key, value in parent_values.iteritems():
                if key not in values_dict:
                    values_dict[key] = value
            self.data.append((template_name, values_dict))
