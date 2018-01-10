from mock import patch, MagicMock
import os
import pytest

from levistate.template import (MissingTemplateError,
                                Template,
                                TemplateParseError,
                                TemplateStore,
                                UndefinedVariableError)
from .template_test_params import (ACL_TEMPLATE_VARS,
                                   DOMAIN_TEMPLATE_VARS,
                                   ENTERPRISE_TEMPLATE_VARS,
                                   EXPECTED_ACL_SCHEMA,
                                   EXPECTED_ACL_TEMPLATE,
                                   EXPECTED_DOMAIN_SCHEMA,
                                   EXPECTED_DOMAIN_TEMPLATE,
                                   EXPECTED_ENTERPRISE_SCHEMA,
                                   EXPECTED_ENTERPRISE_TEMPLATE,
                                   EXPECTED_VERSION)

FIXTURE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'fixtures')
VALID_TEMPLATE_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                        'valid_templates')
INVALID_TEMPLATE_DIRECTORY = os.path.join(FIXTURE_DIRECTORY,
                                          'invalid_templates')
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
    ('invalid_jinja.yaml', 'Syntax error')]

SUBSTITUTE_CASES = ['string', True, False, 0, 1.0, '0', 'true', 'false', 'yes',
                    'no', 'on', 'off', '*', None, 'null', 'with"dquote',
                    "with'squote", 'with\'"both', '> test', '| test',
                    '* test', 'test | test', 'test > test', 'test * test', ':']


class TestTemplateParsing(object):

    def verify_valid_templates(self, store):
        assert set(store.get_template_names()) == set(["Enterprise", "Domain",
                                                       "Bidirectional ACL"])

        template = store.get_template("enterprise")
        assert template.get_name() == "Enterprise"
        assert template.get_template_version() == "1.0"
        assert template.get_software_version() == EXPECTED_VERSION
        assert template.get_schema() == EXPECTED_ENTERPRISE_SCHEMA
        body = template._parse_with_vars(**ENTERPRISE_TEMPLATE_VARS)
        assert body == EXPECTED_ENTERPRISE_TEMPLATE

        template = store.get_template("Domain")
        assert template.get_name() == "Domain"
        assert template.get_template_version() == "1.0"
        assert template.get_software_version() == EXPECTED_VERSION
        assert template.get_schema() == EXPECTED_DOMAIN_SCHEMA
        body = template._parse_with_vars(**DOMAIN_TEMPLATE_VARS)
        assert body == EXPECTED_DOMAIN_TEMPLATE

        template = store.get_template("bidirectional acl")
        assert template.get_name() == "Bidirectional ACL"
        assert template.get_template_version() == "1.0"
        assert template.get_software_version() == EXPECTED_VERSION
        assert template.get_schema() == EXPECTED_ACL_SCHEMA
        body = template._parse_with_vars(**ACL_TEMPLATE_VARS)
        assert body == EXPECTED_ACL_TEMPLATE

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


class TestTemplateSubstitution(object):

    def get_enterprise_value(self, processed_template):
        return (processed_template['actions'][0]['create-object']
                                  ['actions'][0]['set-values']['name'])

    def get_domain_value(self, processed_template):
        return (processed_template['actions'][0]['select-object']
                                  ['actions'][0]['create-object']
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
