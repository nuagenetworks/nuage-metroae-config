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
        self.references = list()

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

    def _read_data(self, filename):
        try:
            with open(filename, 'r') as file:
                return file.read()
        except Exception as e:
            raise UserDataParseError("Error reading user data: " + str(e))

    def _parse_data_string(self, user_data_string, filename="(internal)"):
        data_dict = self._decode_to_dict(user_data_string, filename)
        reader = Reader(self)
        reader.set_filename(filename)
        reader.read(data_dict)

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

    def _add_data(self, name, values_list):
        for entry in values_list:
            self.data.append((name, entry))

    def _add_group(self, name, values_dict):
        self.groups[name] = values_dict

    def _add_reference(self, name, values_dict):
        self.references.append(Reference(name, values_dict))

    def _resolve_groups(self):
        for reference in self.references:
            reference.resolve(self.groups)


#
# Private classes to do the work
#

class Reference(object):
    def __init__(self, name, target_dict):
        self.name = name
        self.target_dict = target_dict

    def resolve(self, groups):
        if self.name not in groups:
            raise UserDataParseError("Group %s not defined" % self.name)

        group_dict = groups[self.name]
        for key, value in group_dict.iteritems():
            if key not in self.target_dict:
                self.target_dict[key] = value


class Reader(object):

    def __init__(self, store, parent=None):
        self.store = store
        self.parent = parent
        self.values_list = []
        self.inherit_values = None
        self.filename = None

    def read(self, data):
        self.read_children(data)

    def new(self, data_dict):
        template = self.get_dict_field(data_dict, 'template')
        group = self.get_dict_field(data_dict, 'group')

        if template is not None:
            entry = TemplateReader(template, self.store, self)
        elif group is not None:
            entry = GroupReader(group, self.store, self)
        else:
            self.raise_error("Invalid entry: " + str(data_dict))

        entry.set_filename(self.filename)
        entry.read(data_dict)

        return entry

    def get_dict_field(self, data_dict, field):
        try:
            return get_dict_field_no_case(data_dict, field)
        except TypeError:
            self.raise_error("Invalid entry: " + str(data_dict))

    def set_filename(self, filename):
        self.filename = filename

    def raise_error(self, message):
        filename = ''
        if self.filename is not None:
            filename = self.filename + ": "

        raise UserDataParseError(filename + message)

    def read_values(self, data_dict):
        values = self.get_dict_field(data_dict, 'values')
        if values is None:
            self.raise_error("Missing required entry field 'values'")

        fields = self.get_dict_field(data_dict, 'fields')

        if fields is None:
            entry = ValuesReader(self.store, self.parent)
        else:
            entry = FieldValuesReader(fields, self.store, self.parent)

        entry.set_filename(self.filename)
        self.values_list = entry.read(data_dict)

    def read_children(self, data):
        if type(data) == list:
            for entry in data:
                self.new(entry)
        else:
            self.new(data)

    def fill_inherit_values(self):
        if len(self.values_list) == 1:
            self.inherit_values = self.values_list[0]
        else:
            self.raise_error(
                "Only entries with single value sets can be inherited")


class TemplateReader(Reader):

    def __init__(self, name, store, parent=None):
        super(TemplateReader, self).__init__(store, parent)
        self.name = name

    def read(self, data_dict):
        self.read_values(data_dict)

        self.store._add_data(self.name, self.values_list)

        children = self.get_dict_field(data_dict, 'children')
        if children is not None:
            self.fill_inherit_values()
            self.read_children(children)


class GroupReader(Reader):

    def __init__(self, name, store, parent=None):
        super(GroupReader, self).__init__(store, parent)
        self.name = name

    def read(self, data_dict):
        self.read_values(data_dict)

        # Groups must have exactly one set of values
        self.fill_inherit_values()

        self.store._add_group(self.name, self.inherit_values)

        children = self.get_dict_field(data_dict, 'children')
        if children is not None:
            self.read_children(children)


class ValuesReader(Reader):
    def __init__(self, store, parent=None):
        super(ValuesReader, self).__init__(store, parent)

    @staticmethod
    def combine_dicts(values_dict, parent_values):
        for key, value in parent_values.iteritems():
            if key not in values_dict:
                values_dict[key] = value

    def read(self, data_dict):
        values = self.get_values_field(data_dict)

        if type(values) == list:
            values_list = values
        else:
            values_list = [values]

        values_list = self.process_values_list(values_list)
        return values_list

    def get_values_field(self, data_dict):
        values = self.get_dict_field(data_dict, 'values')

        if values is None:
            self.raise_error("Missing required entry field 'values'")

        return values

    def process_values_list(self, values_list):
        if self.parent is None:
            parent_values = None
        else:
            parent_values = self.parent.inherit_values

        if parent_values is None:
            parent_values = dict()

        for values_dict in values_list:
            if type(values_dict) != dict:
                self.raise_error(
                    "Values without fields specified must be a dictionary: " +
                    str(values_dict))

            ValuesReader.combine_dicts(values_dict, parent_values)
            self.read_references(values_dict)

        return values_list

    def read_references(self, values_dict):
        for key, value in values_dict.iteritems():
            if key.lower().startswith('$group'):
                self.store._add_reference(value, values_dict)


class FieldValuesReader(ValuesReader):
    def __init__(self, fields, store, parent=None):
        super(FieldValuesReader, self).__init__(store, parent)
        self.fields = fields

    def read(self, data_dict):
        values = self.get_values_field(data_dict)
        values_list = self.read_fields_values(self.fields, values)
        values_list = self.process_values_list(values_list)

        return values_list

    def read_fields_values(self, fields, values):
        if type(fields) != list:
            self.raise_error("Fields must be a list: " + str(fields))

        if type(values) != list:
            self.raise_error(
                "Values must be a list when fields specified: " + str(values))

        values_list = list()

        if len(values) == 0 or type(values[0]) == list:
            for entry in values:
                values_list.append(
                    self.read_fields_values_entry(fields, entry))
        else:
            values_list.append(
                self.read_fields_values_entry(fields, values))

        return values_list

    def read_fields_values_entry(self, fields, values):
        if type(values) != list:
            self.raise_error(
                "Values must be a list when fields specified: " + str(values))

        if len(fields) != len(values):
            self.raise_error(
                "Values list does not match the number of fields specified: " +
                str(values))

        values_dict = dict()
        for i, key in enumerate(fields):
            values_dict[key] = values[i]

        return values_dict
