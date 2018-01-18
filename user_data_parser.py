import os
import yaml

from util import get_dict_field_no_case


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
        self.groups = dict()

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
        self._resolve_groups()
        return self.data

    #
    # Private functions to do the work
    #

    @staticmethod
    def _get_dict_field(data_dict, field):
        try:
            return get_dict_field_no_case(data_dict, field)
        except TypeError:
            raise UserDataParseError("Invalid user data entry: " +
                                     str(data_dict))

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
        group = UserDataParser._get_dict_field(data_dict, 'group')

        if template is not None:
            values_list = self._parse_entry_contents(data_dict,
                                                     parent_values)
            self._add_data(template, values_list)
        elif group is not None:
            values_list = self._parse_entry_contents(data_dict,
                                                     parent_values)
            self._add_group(group, values_list)
        else:
            raise UserDataParseError("Invalid user data entry: " +
                                     str(data_dict))

        self._parse_children(data_dict, values_list)

    def _parse_entry_contents(self, entry_dict, parent_values):
        values = UserDataParser._get_dict_field(entry_dict, 'values')
        if values is None:
            raise UserDataParseError(
                "Missing required entry field 'values'")

        fields = UserDataParser._get_dict_field(entry_dict, 'fields')

        if fields is None:
            values_list = self._parse_values_list(values)
        else:
            values_list = self._parse_fields(fields, values)

        self._combine_entries(values_list, parent_values)
        return values_list

    def _parse_children(self, entry_dict, values_list):
        children = UserDataParser._get_dict_field(entry_dict, 'children')
        if children is not None:
            if len(values_list) == 1:
                self._parse_data_entries(children, values_list[0])
            else:
                raise UserDataParseError(
                    "Only entries with single value sets may have children")

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

    def _parse_fields(self, fields, values_list):
        values = list()

        if type(fields) != list:
            raise UserDataParseError("Fields must be a list: " +
                                     str(fields))

        if type(values_list) != list:
            raise UserDataParseError(
                "Values must be a list when fields specified: " +
                str(values_list))

        if len(values_list) == 0:
            return values

        if type(values_list[0]) == list:
            for entry in values_list:
                values.append(self._parse_field_value_entry(fields, entry))
        else:
            values.append(self._parse_field_value_entry(fields, values_list))

        return values

    def _parse_field_value_entry(self, fields, values):
        if type(values) != list:
            raise UserDataParseError(
                "Values must be a list when fields specified: " +
                str(values))

        if len(fields) != len(values):
            raise UserDataParseError(
                "Values list does not match the number of fields specified: " +
                str(values))

        values_dict = dict()
        for i, key in enumerate(fields):
            values_dict[key] = values[i]

        return values_dict

    def _combine_entries(self, values_list, parent_values):
        for values_dict in values_list:
            for key, value in parent_values.iteritems():
                if key not in values_dict:
                    values_dict[key] = value

    def _add_data(self, name, values_list):
        for entry in values_list:
            self.data.append((name, entry))

    def _add_group(self, name, values_list):
        if len(values_list) != 1:
            raise UserDataParseError(
                "Group %s must have exactly one set of values" % name)
        self.groups[name] = values_list[0]

    def _resolve_groups(self):
        for entry_pair in self.data:
            value_dict = entry_pair[1]
            group_apply_dict = dict()
            for key, group_name in value_dict.iteritems():
                if key.lower().startswith('$group'):
                    if group_name not in self.groups:
                        raise UserDataParseError(
                            "Group %s not defined" % group_name)
                    self._combine_entries([group_apply_dict],
                                          self.groups[group_name])
            self._combine_entries([value_dict], group_apply_dict)
