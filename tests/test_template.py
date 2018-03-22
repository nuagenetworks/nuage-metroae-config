import json
import os
import pytest

from levistate.template import (MissingTemplateError,
                                TemplateParseError,
                                TemplateStore,
                                UndefinedVariableError,
                                VariableValueError)
from .template_test_params import (ACL_TEMPLATE_VARS,
                                   DOMAIN_TEMPLATE_VARS,
                                   ENTERPRISE_TEMPLATE_VARS,
                                   EXPECTED_ACL_TEMPLATE,
                                   EXPECTED_DOMAIN_TEMPLATE,
                                   EXPECTED_ENTERPRISE_TEMPLATE,
                                   EXPECTED_VERSION)

FIXTURE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'fixtures')

VALID_TEMPLATE_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                        'valid_templates')

INVALID_TEMPLATE_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                          'invalid_templates')

VALID_SCHEMA_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                      'valid_schemas')

PARSE_ERROR_CASES = [
    ('no_exist.json', 'not found'),
    ('not_json.json', 'name missing'),
    ('not_yaml.yaml', 'name missing'),
    ('missing_name.json', 'name missing'),
    ('missing_name.yaml', 'name missing'),
    ('missing_software_type.json', 'software-type missing'),
    ('missing_software_type.yaml', 'software-type missing'),
    ('missing_software_version.json', 'software-version missing'),
    ('missing_software_version.yaml', 'software-version missing'),
    ('missing_variables.json', 'variables missing'),
    ('missing_variables.yaml', 'variables missing'),
    ('missing_actions.json', 'actions missing'),
    ('missing_actions.yaml', 'actions missing'),
    ('invalid_json.json', 'Syntax error'),
    ('invalid_yaml.yaml', 'Syntax error'),
    ('invalid_jinja.json', 'Syntax error'),
    ('invalid_jinja.yaml', 'Syntax error'),
    ('missing_var_name.json', 'name missing'),
    ('missing_var_name.yaml', 'name missing'),
    ('missing_var_type.json', 'type missing'),
    ('missing_var_type.yaml', 'type missing'),
    ('unknown_var_type.json', 'Invalid type'),
    ('unknown_var_type.yaml', 'Invalid type'),
    ('missing_var_item_type.json', 'item-type missing'),
    ('missing_var_item_type.yaml', 'item-type missing'),
    ('missing_var_choices.json', 'choices missing'),
    ('missing_var_choices.yaml', 'choices missing'),
    ('invalid_var_choices.json', 'must be a list'),
    ('invalid_var_choices.yaml', 'must be a list')]

SUBSTITUTE_CASES = ['string', True, False, 0, 1.0, '0', 'true', 'false', 'yes',
                    'no', 'on', 'off', '*', None, 'null', 'with"dquote',
                    "with'squote", 'with\'"both', '> test', '| test',
                    '* test', 'test | test', 'test > test', 'test * test', ':']

INVALID_VALUES_CASES = [
    ({"name": 1}, "not a string"),
    ({"number": "1"}, "not an integer"),
    ({"true_or_false": "True"}, "not a boolean"),
    ({"fruit": "candy"}, "not a valid choice"),
    ({"string_list": "not a list"}, "not a list"),
    ({"string_list": ["string", 1]}, "not a string"),
    ({"int_list": [1, "2"]}, "not an integer"),
    ({"soda_list": ["coke", "coffee"]}, "not a valid choice")]


class TestTemplateParsing(object):

    def verify_valid_templates(self, store):
        assert set(store.get_template_names()) == set(["Enterprise", "Domain",
                                                       "Bidirectional ACL"])

        template = store.get_template("enterprise")
        assert template.get_name() == "Enterprise"
        assert template.get_template_version() == "1.0"
        assert template.get_software_version() == EXPECTED_VERSION
        body = template._parse_with_vars(**ENTERPRISE_TEMPLATE_VARS)
        assert body == EXPECTED_ENTERPRISE_TEMPLATE

        with open(os.path.join(VALID_SCHEMA_DIRECTORY,
                               "enterprise_schema.json"), 'r') as file:
            schema_string = file.read()

        expected_schema = json.loads(schema_string)
        actual_schema = json.loads(template.get_schema())
        assert actual_schema == expected_schema

        template = store.get_template("Domain")
        assert template.get_name() == "Domain"
        assert template.get_template_version() == "1.0"
        assert template.get_software_version() == EXPECTED_VERSION
        body = template._parse_with_vars(**DOMAIN_TEMPLATE_VARS)
        assert body == EXPECTED_DOMAIN_TEMPLATE

        with open(os.path.join(VALID_SCHEMA_DIRECTORY,
                               "domain_schema.json"), 'r') as file:
            schema_string = file.read()

        expected_schema = json.loads(schema_string)
        actual_schema = json.loads(template.get_schema())
        assert actual_schema == expected_schema

        template = store.get_template("bidirectional acl")
        assert template.get_name() == "Bidirectional ACL"
        assert template.get_template_version() == "1.0"
        assert template.get_software_version() == EXPECTED_VERSION
        body = template._parse_with_vars(**ACL_TEMPLATE_VARS)
        assert body == EXPECTED_ACL_TEMPLATE

        with open(os.path.join(VALID_SCHEMA_DIRECTORY,
                               "acl_schema.json"), 'r') as file:
            schema_string = file.read()

        expected_schema = json.loads(schema_string)
        actual_schema = json.loads(template.get_schema())
        assert actual_schema == expected_schema

    def test_read_dir__success(self):
        store = TemplateStore()
        store.read_templates(VALID_TEMPLATE_DIRECTORY)

        self.verify_valid_templates(store)

    def test_read_files__success(self):
        store = TemplateStore()
        store.read_templates(os.path.join(VALID_TEMPLATE_DIRECTORY,
                                          "enterprise_template.json"))
        store.read_templates(os.path.join(VALID_TEMPLATE_DIRECTORY,
                                          "domain_template.yml"))
        store.read_templates(os.path.join(VALID_TEMPLATE_DIRECTORY,
                                          "bidirectional_acl_template.yaml"))

        assert set(store.get_template_names()) == set(["Enterprise", "Domain",
                                                       "Bidirectional ACL"])

        self.verify_valid_templates(store)

    def test_add_by_string__success(self):
        store = TemplateStore()

        with open(os.path.join(VALID_TEMPLATE_DIRECTORY,
                               "enterprise_template.json"), 'r') as file:
            template_string = file.read()
            store.add_template(template_string)

        with open(os.path.join(VALID_TEMPLATE_DIRECTORY,
                               "domain_template.yml"), 'r') as file:
            template_string = file.read()
            store.add_template(template_string)

        with open(os.path.join(VALID_TEMPLATE_DIRECTORY,
                               "bidirectional_acl_template.yaml"),
                  'r') as file:
            template_string = file.read()
            store.add_template(template_string)

        assert set(store.get_template_names()) == set(["Enterprise", "Domain",
                                                       "Bidirectional ACL"])

        self.verify_valid_templates(store)

        store = TemplateStore()

    def test_get_template__missing(self):
        store = TemplateStore()

        with pytest.raises(MissingTemplateError) as e:
            store.get_template("Foobar")

        assert "No template" in str(e)
        assert "Foobar" in str(e)

    @pytest.mark.parametrize("filename, message", PARSE_ERROR_CASES)
    def test_read_files__invalid(self, filename, message):
        store = TemplateStore()

        with pytest.raises(TemplateParseError) as e:
            store.read_templates(os.path.join(INVALID_TEMPLATE_DIRECTORY,
                                              filename))

        assert message in str(e)
        assert filename in str(e)

    def test_schema__success(self):
        store = TemplateStore()
        store.read_templates(os.path.join(INVALID_TEMPLATE_DIRECTORY,
                                          "variables.yaml"))

        template = store.get_template("Variables Testing")

        with open(os.path.join(VALID_SCHEMA_DIRECTORY,
                               "variables_test_schema.json"), 'r') as file:
            schema_string = file.read()

        expected_schema = json.loads(schema_string)
        actual_schema = json.loads(template.get_schema())
        assert actual_schema == expected_schema

    def test_example__success(self):
        store = TemplateStore()
        store.read_templates(os.path.join(INVALID_TEMPLATE_DIRECTORY,
                                          "variables.yaml"))

        template = store.get_template("Variables Testing")

        with open(os.path.join(VALID_SCHEMA_DIRECTORY,
                               "variables_example.yaml"), 'r') as file:
            expected_example = file.read()

        assert template.get_example() == expected_example


class TestTemplateSubstitution(object):

    def get_enterprise_value(self, processed_template):
        return (processed_template['actions'][0]['create-object']
                                  ['actions'][0]['set-values']['name'])

    def get_domain_value(self, processed_template):
        return (processed_template['actions'][0]['select-object']
                                  ['actions'][1]['create-object']
                                  ['actions'][0]['set-values']['name'])

    @pytest.mark.parametrize("value", SUBSTITUTE_CASES)
    def test__valid(self, value):
        store = TemplateStore()
        store.read_templates(VALID_TEMPLATE_DIRECTORY)

        json_template = store.get_template('enterprise')
        processed_template = json_template._parse_with_vars(
            enterprise_name=value)
        processed_value = self.get_enterprise_value(processed_template)
        assert processed_value == value

        yaml_template = store.get_template('domain')
        processed_template = yaml_template._parse_with_vars(
            enterprise_name=value,
            domain_name=value)
        processed_value = self.get_domain_value(processed_template)
        assert processed_value == value

    def test__missing_var(self):
        store = TemplateStore()
        store.read_templates(VALID_TEMPLATE_DIRECTORY)

        json_template = store.get_template('enterprise')
        with pytest.raises(UndefinedVariableError) as e:
            json_template._parse_with_vars()

        assert "'enterprise_name' is undefined" in str(e)
        assert "Enterprise" in str(e)

        yaml_template = store.get_template('Domain')
        with pytest.raises(UndefinedVariableError) as e:
            yaml_template._parse_with_vars(enterprise_name="test_enterprise")

        assert "'domain_name' is undefined" in str(e)
        assert "Domain" in str(e)

    def test__conditionals(self):
        store = TemplateStore()
        store.read_templates(os.path.join(INVALID_TEMPLATE_DIRECTORY,
                                          "conditionals.json"))
        store.read_templates(os.path.join(INVALID_TEMPLATE_DIRECTORY,
                                          "conditionals.yaml"))

        json_template = store.get_template('Conditionals JSON')

        processed_template = json_template._parse_with_vars(var1='a', var2='x')
        assert 'var1_is_a' in processed_template['actions']
        assert processed_template['actions']['var1_is_a'] == 'a'
        assert 'var2' in processed_template['actions']
        assert processed_template['actions']['var2'] == 'false'
        assert 'and_check' not in processed_template['actions']
        assert 'nested_check' not in processed_template['actions']
        assert 'var1_is_empty' in processed_template['actions']
        assert processed_template['actions']['var1_is_empty'] is False

        processed_template = json_template._parse_with_vars(var1='', var2=True)
        assert 'var1_is_a' not in processed_template['actions']
        assert 'var2' in processed_template['actions']
        assert processed_template['actions']['var2'] is True
        assert 'and_check' not in processed_template['actions']
        assert 'nested_check' not in processed_template['actions']
        assert 'var1_is_empty' in processed_template['actions']
        assert processed_template['actions']['var1_is_empty'] is True

        processed_template = json_template._parse_with_vars(
            var1='peanut butter',
            var2='jelly')
        assert 'var1_is_a' not in processed_template['actions']
        assert 'var2' in processed_template['actions']
        assert processed_template['actions']['var2'] == 'false'
        assert 'and_check' not in processed_template['actions']
        assert 'nested_check' in processed_template['actions']
        assert (processed_template['actions']['nested_check'] ==
                'peanut butter and jelly')
        assert 'var1_is_empty' in processed_template['actions']
        assert processed_template['actions']['var1_is_empty'] is False

        processed_template = json_template._parse_with_vars(var1='b', var2=0)
        assert 'var1_is_a' not in processed_template['actions']
        assert 'var2' in processed_template['actions']
        assert processed_template['actions']['var2'] == 'false'
        assert 'and_check' in processed_template['actions']
        assert processed_template['actions']['and_check'] is True
        assert 'nested_check' not in processed_template['actions']
        assert 'var1_is_empty' in processed_template['actions']
        assert processed_template['actions']['var1_is_empty'] is False

        yaml_template = store.get_template('Conditionals Yaml')

        processed_template = yaml_template._parse_with_vars(var1='a', var2='x')
        assert 'var1_is_a' in processed_template['actions']
        assert processed_template['actions']['var1_is_a'] == 'a'
        assert 'var2' in processed_template['actions']
        assert processed_template['actions']['var2'] == 'false'
        assert 'and_check' not in processed_template['actions']
        assert 'nested_check' not in processed_template['actions']
        assert 'var1_is_empty' in processed_template['actions']
        assert processed_template['actions']['var1_is_empty'] is False

        processed_template = yaml_template._parse_with_vars(var1='', var2=True)
        assert 'var1_is_a' not in processed_template['actions']
        assert 'var2' in processed_template['actions']
        assert processed_template['actions']['var2'] is True
        assert 'and_check' not in processed_template['actions']
        assert 'nested_check' not in processed_template['actions']
        assert 'var1_is_empty' in processed_template['actions']
        assert processed_template['actions']['var1_is_empty'] is True

        processed_template = yaml_template._parse_with_vars(
            var1='peanut butter',
            var2='jelly')
        assert 'var1_is_a' not in processed_template['actions']
        assert 'var2' in processed_template['actions']
        assert processed_template['actions']['var2'] == 'false'
        assert 'and_check' not in processed_template['actions']
        assert 'nested_check' in processed_template['actions']
        assert (processed_template['actions']['nested_check'] ==
                'peanut butter and jelly')
        assert 'var1_is_empty' in processed_template['actions']
        assert processed_template['actions']['var1_is_empty'] is False

        processed_template = yaml_template._parse_with_vars(var1='b', var2=0)
        assert 'var1_is_a' not in processed_template['actions']
        assert 'var2' in processed_template['actions']
        assert processed_template['actions']['var2'] == 'false'
        assert 'and_check' in processed_template['actions']
        assert processed_template['actions']['and_check'] is True
        assert 'nested_check' not in processed_template['actions']
        assert 'var1_is_empty' in processed_template['actions']
        assert processed_template['actions']['var1_is_empty'] is False


class TestTemplateVariableValidation(object):

    def get_variables_template(self):
        store = TemplateStore()
        store.read_templates(os.path.join(INVALID_TEMPLATE_DIRECTORY,
                                          "variables.yaml"))

        return store.get_template("Variables Testing")

    def test_all_vars__success(self):
        template = self.get_variables_template()

        all_vars = {"name": "test_name",
                    "select_name": "test_select",
                    "number": 10,
                    "true_or_false": True,
                    "ipv4_address": "192.168.0.1",
                    "ipv6_address": "8000::0001",
                    "any_ip_address": "10.0.0.0",
                    "fruit": "apple",
                    "string_list": ["a", "b", "c"],
                    "int_list": [1, 2],
                    "soda_list": ["coke", "pepsi", "sprite"]}

        assert template.validate_template_data(**all_vars) is True

    @pytest.mark.parametrize("data, message", INVALID_VALUES_CASES)
    def test__invalid(self, data, message):
        template = self.get_variables_template()

        with pytest.raises(VariableValueError) as e:
            template.validate_template_data(**data)

        assert "Variables Testing" in str(e)
        assert data.keys()[0] in str(e)
        assert message in str(e)

    def test_required_vars__success(self):
        template = self.get_variables_template()

        min_vars = {"name": "another_name",
                    "select_name": "another_select",
                    "number": 100000,
                    "true_or_false": False,
                    "fruit": "orange",
                    "string_list": ["a", "b", "c"],
                    "int_list": [],
                    "soda_list": ["sprite"]}

        assert template.validate_template_data(**min_vars) is True

    def test_required_vars__missing_just_name(self):
        template = self.get_variables_template()

        missing_vars = {"select_name": "another_select",
                        "number": 100000,
                        "true_or_false": False,
                        "fruit": "orange",
                        "string_list": ["a", "b", "c"],
                        "int_list": [],
                        "soda_list": ["sprite"]}

        with pytest.raises(UndefinedVariableError) as e:
            template.validate_template_data(**missing_vars)

        assert "name" in str(e)

    def test_required_vars__missing_all(self):
        template = self.get_variables_template()

        missing_vars = {}

        with pytest.raises(UndefinedVariableError) as e:
            template.validate_template_data(**missing_vars)

        assert "name" in str(e)
        assert "select_name" in str(e)
        assert "number" in str(e)
        assert "true_or_false" in str(e)
        assert "fruit" in str(e)
        assert "string_list" in str(e)
        assert "int_list" in str(e)
        assert "soda_list" in str(e)

    def test_required_vars__missing_without_optional(self):
        template = self.get_variables_template()

        missing_vars = {"number": 100000,
                        "true_or_false": False,
                        "string_list": ["a", "b", "c"]}

        with pytest.raises(UndefinedVariableError) as e:
            template.validate_template_data(**missing_vars)

        assert "name" in str(e)
        assert "select_name" in str(e)
        assert "fruit" in str(e)
        assert "int_list" in str(e)
        assert "soda_list" in str(e)

    def test_required_vars__missing_optional_false(self):
        template = self.get_variables_template()

        missing_vars = {"name": "another_name",
                        "select_name": "another_select",
                        "number": 100000,
                        "fruit": "orange",
                        "int_list": [],
                        "soda_list": ["sprite"]}

        with pytest.raises(UndefinedVariableError) as e:
            template.validate_template_data(**missing_vars)

        assert "true_or_false" in str(e)
        assert "string_list" in str(e)
