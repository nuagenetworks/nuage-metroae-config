# Levistate
Levistate configuration template engine.

Work in progress.

This prototype is able to read JSON or Yaml files of templates and user-data to
write a configuration to a VSD or to revert (remove) said configuration.

## TODO

* Unit-test for Actions class
* Unit-test for UserDataParser class
* Action ordering
* Variable validation
* VSD validation
* Configuration update
* User data improvements (groups, list format)
* Better error handling and logging

## Requirements

Packages required for Levistate engine
* bambou
* collections
* jinja2
* json
* os
* yaml

Additional packages for Levistate command-line tool
* argparse

Additional packages for unit-test
* mock
* pytest
* requests
* requests_mock

## Usage

Levistate command-line tool usage:

    usage: levistate.py [-h] [-tp TEMPLATE_PATH] [-sp SPEC_PATH] [-dp DATA_PATH]
                        [-t TEMPLATE_NAME] [-d DATA] [-v VSD_URL] [-u USERNAME]
                        [-p PASSWORD] [-e ENTERPRISE] [-r]

    Command-line tool for running template commands

    optional arguments:
      -h, --help            show this help message and exit
      -tp TEMPLATE_PATH, --template-path TEMPLATE_PATH
                            Path containing template files
      -sp SPEC_PATH, --spec-path SPEC_PATH
                            Path containing object specifications
      -dp DATA_PATH, --data-path DATA_PATH
                            Path containing user data
      -t TEMPLATE_NAME, --template TEMPLATE_NAME
                            Template name
      -d DATA, --data DATA  Specify extra variable as key=value
      -v VSD_URL, --vsd-url VSD_URL
                            URL to VSD REST API
      -u USERNAME, --username USERNAME
                            Username for VSD
      -p PASSWORD, --password PASSWORD
                            Password for VSD
      -e ENTERPRISE, --enterprise ENTERPRISE
                            Enterprise for VSD
      -r, --revert          Revert (delete) templates instead of applying

## File Descriptions

* *levistate.py*: Command-line tool for issuing template commands. (work in
progress)
* *device_writer_base.py*: Base class for all template writers.  Not to be used
on its own, use a derived class writer.
* *vsd_writer.py*: Writes templates to a VSD using common APIs from base class.
* *bambou_adapter.py*: A set of wrapper classes around the Bambou library to
make it work generically for any configuration object based on specifications.
* *template.py*: Reads Yaml or JSON template files and parses them.
* *configuration.py*: Gathers together template user-data and applies it to a
device using a writer.
* *actions.py*: Reads actions from parsed templates and executes them to the
specified writer.
* *tests/*: Unit-tests for Levistate classes.
* *sample/templates*: Some basic templates to use as examples.
* *sample/user_data*: Some basic user data to use as examples.

## Levistate Example

Apply enterprise, domain and ACLs to VSD (hard-coded).  Needs
vsd-api-specifications for operation

    levistate$ python levistate.py -tp sample/templates -sp ~/vsd-api-specifications -dp sample/user_data/acls.yaml

    Configuration
        Enterprise
            name = 'test_enterprise'
        [select Enterprise (name of test_enterprise)]
            DomainTemplate
                name = 'template_public'
                [store id to name domain_template_id]
            Domain
                name = 'public'
                templateID = [retrieve domain_template_id (DomainTemplate:id)]
        [select Enterprise (name of test_enterprise)]
            [select Domain (name of public)]
                IngressACLTemplate
                    priority = 100
                    defaultAllowNonIP = False
                    allowAddressSpoof = False
                    name = 'test_acl'
                    defaultAllowIP = True
                    IngressACLEntryTemplate
                        networkID = ''
                        stateful = True
                        protocol = 6
                        description = 'Test ACL'
                        etherType = '0x0800'
                        statsLoggingEnabled = True
                        DSCP = '*'
                        priority = 200
                        action = 'FORWARD'
                        locationID = ''
                        destinationPort = '*'
                        locationType = 'ANY'
                        sourcePort = 80
                        networkType = 'ANY'
                        flowLoggingEnabled = True
                EgressACLTemplate
                    priority = 100
                    defaultInstallACLImplicitRules = True
                    defaultAllowNonIP = False
                    name = 'test_acl'
                    defaultAllowIP = True
                    EgressACLEntryTemplate
                        networkID = ''
                        stateful = True
                        protocol = 6
                        description = 'Test ACL'
                        etherType = '0x0800'
                        statsLoggingEnabled = True
                        DSCP = '*'
                        priority = 200
                        action = 'FORWARD'
                        locationID = ''
                        destinationPort = '*'
                        locationType = 'ANY'
                        sourcePort = 80
                        networkType = 'ANY'
                        flowLoggingEnabled = True

Revert (delete) objects configured during application, use -r option

    levistate$ python levistate.py -tp sample/templates -sp ~/vsd-api-specifications -dp sample/user_data/acls.yaml -r

    Configuration
        Enterprise
            name = 'test_enterprise'
        [select Enterprise (name of test_enterprise)]
            DomainTemplate
                name = 'template_public'
                [store id to name domain_template_id]
            Domain
                name = 'public'
                templateID = [retrieve domain_template_id (DomainTemplate:id)]
        [select Enterprise (name of test_enterprise)]
            [select Domain (name of public)]
                IngressACLTemplate
                    priority = 100
                    defaultAllowNonIP = False
                    allowAddressSpoof = False
                    name = 'test_acl'
                    defaultAllowIP = True
                    IngressACLEntryTemplate
                        networkID = ''
                        stateful = True
                        protocol = 6
                        description = 'Test ACL'
                        etherType = '0x0800'
                        statsLoggingEnabled = True
                        DSCP = '*'
                        priority = 200
                        action = 'FORWARD'
                        locationID = ''
                        destinationPort = '*'
                        locationType = 'ANY'
                        sourcePort = 80
                        networkType = 'ANY'
                        flowLoggingEnabled = True
                EgressACLTemplate
                    priority = 100
                    defaultInstallACLImplicitRules = True
                    defaultAllowNonIP = False
                    name = 'test_acl'
                    defaultAllowIP = True
                    EgressACLEntryTemplate
                        networkID = ''
                        stateful = True
                        protocol = 6
                        description = 'Test ACL'
                        etherType = '0x0800'
                        statsLoggingEnabled = True
                        DSCP = '*'
                        priority = 200
                        action = 'FORWARD'
                        locationID = ''
                        destinationPort = '*'
                        locationType = 'ANY'
                        sourcePort = 80
                        networkType = 'ANY'
                        flowLoggingEnabled = True

## Unit-tests

Unit-tests can be run using 'pytest'.  Bambou adapter, VSD writer, Template
and Configuration tests are complete.  The Actions and UserDataParser tests are
in progress

    levistate$ pytest -v
    ============================================================================================== test session starts ===============================================================================================
    platform darwin -- Python 2.7.10, pytest-3.2.5, py-1.5.2, pluggy-0.4.0 -- /Users/mpiecuch/virtualenvs/metro/bin/python
    cachedir: .cache
    rootdir: /Users/mpiecuch/levistate, inifile:
    collected 125 items

    tests/test_bambou_adapter.py::TestSession::test_start__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestSession::test_start__invalid_pass <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_delete_child__not_found <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_save_parent__not_found <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_save_child__not_found <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_delete_parent__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_new_object__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_save_child__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_save_parent__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_create_child__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_create_parent__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_delete_child__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_create_child__conflict <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_delete_parent__not_found <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestConfigObject::test_create_parent__conflict <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestFetcher::test_find_child__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestFetcher::test_find_child__invalid_parent <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestFetcher::test_find_parent__multiple <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestFetcher::test_find_child__multiple <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestFetcher::test_find_child__not_found <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestFetcher::test_find_parent__not_found <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_bambou_adapter.py::TestFetcher::test_find_parent__success <- ../virtualenvs/metro/lib/python2.7/site-packages/requests_mock/mocker.py PASSED
    tests/test_configuration.py::TestConfigurationTemplates::test__success PASSED
    tests/test_configuration.py::TestConfigurationTemplates::test__missing PASSED
    tests/test_configuration.py::TestConfigurationData::test_add_get__success PASSED
    tests/test_configuration.py::TestConfigurationData::test_add__invalid PASSED
    tests/test_configuration.py::TestConfigurationData::test_get__invalid PASSED
    tests/test_configuration.py::TestConfigurationData::test_update__success PASSED
    tests/test_configuration.py::TestConfigurationData::test_update__invalid PASSED
    tests/test_configuration.py::TestConfigurationData::test_remove__success PASSED
    tests/test_configuration.py::TestConfigurationData::test_remove__invalid PASSED
    tests/test_configuration.py::TestConfigurationApplyRevert::test_apply__success PASSED
    tests/test_configuration.py::TestConfigurationApplyRevert::test_apply__action_error PASSED
    tests/test_configuration.py::TestConfigurationApplyRevert::test_revert__success PASSED
    tests/test_configuration.py::TestConfigurationApplyRevert::test_revert__action_error PASSED
    tests/test_template.py::TestTemplateParsing::test_read_dir__success PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__success PASSED
    tests/test_template.py::TestTemplateParsing::test_add_by_string__success PASSED
    tests/test_template.py::TestTemplateParsing::test_get_template__missing PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[no_exist.json-not found] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[not_json.json-name missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[not_yaml.yaml-name missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_name.json-name missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_name.yaml-name missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_software_type.json-software-type missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_software_type.yaml-software-type missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_software_version.json-software-version missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_software_version.yaml-software-version missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_variables.json-variables missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_variables.yaml-variables missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_actions.json-actions missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[missing_actions.yaml-actions missing] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[invalid_json.json-Syntax error] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[invalid_yaml.yaml-Syntax error] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[invalid_jinja.json-Syntax error] PASSED
    tests/test_template.py::TestTemplateParsing::test_read_files__invalid[invalid_jinja.yaml-Syntax error] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[string] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[True] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[False] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[00] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[1.0] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[01] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[true] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[false] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[yes] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[no] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[on] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[off] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[*] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[None] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[null] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[with"dquote] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[with'squote] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[with'"both] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[> test] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[| test] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[* test] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[test | test] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[test > test] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[test * test] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__valid[:] PASSED
    tests/test_template.py::TestTemplateSubstitution::test__missing_var PASSED
    tests/test_template.py::TestTemplateSubstitution::test__conditionals PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_dir__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_files__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_files__invalid[noexist.spec-not found] PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_files__invalid[notjson.spec-Error parsing] PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_files__invalid[nomodel.spec-'model' missing] PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_files__invalid[noattributes.spec-'attributes' missing] PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_files__invalid[nochildren.spec-'children' missing] PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_files__invalid[noentityname.spec-'entity_name' missing] PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_files__invalid[noresourcename.spec-'resource_name' missing] PASSED
    tests/test_vsd_writer.py::TestVsdWriterSpecParsing::test_read_files__invalid[norestname.spec-'rest_name' missing] PASSED
    tests/test_vsd_writer.py::TestVsdWriterSession::test_start__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterSession::test_start__no_params PASSED
    tests/test_vsd_writer.py::TestVsdWriterSession::test_start__no_root_spec PASSED
    tests/test_vsd_writer.py::TestVsdWriterSession::test_start__no_enterprise_spec PASSED
    tests/test_vsd_writer.py::TestVsdWriterSession::test_start__bambou_error PASSED
    tests/test_vsd_writer.py::TestVsdWriterSession::test_stop__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterCreateObject::test__no_session PASSED
    tests/test_vsd_writer.py::TestVsdWriterCreateObject::test_parent__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterCreateObject::test_child__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterCreateObject::test__bad_object PASSED
    tests/test_vsd_writer.py::TestVsdWriterSelectObject::test__no_session PASSED
    tests/test_vsd_writer.py::TestVsdWriterSelectObject::test_parent__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterSelectObject::test_child__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterSelectObject::test__bad_object PASSED
    tests/test_vsd_writer.py::TestVsdWriterSelectObject::test__bad_child PASSED
    tests/test_vsd_writer.py::TestVsdWriterSelectObject::test__not_found PASSED
    tests/test_vsd_writer.py::TestVsdWriterSelectObject::test__multiple_found PASSED
    tests/test_vsd_writer.py::TestVsdWriterDeleteObject::test__no_session PASSED
    tests/test_vsd_writer.py::TestVsdWriterDeleteObject::test__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterDeleteObject::test__no_object PASSED
    tests/test_vsd_writer.py::TestVsdWriterSetValues::test__no_session PASSED
    tests/test_vsd_writer.py::TestVsdWriterSetValues::test_parent_new__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterSetValues::test_parent_update__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterSetValues::test_child_new__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterSetValues::test_child_update__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterSetValues::test__no_object PASSED
    tests/test_vsd_writer.py::TestVsdWriterSetValues::test__invalid_attr PASSED
    tests/test_vsd_writer.py::TestVsdWriterSetValues::test__bad_child PASSED
    tests/test_vsd_writer.py::TestVsdWriterGetValue::test__no_session PASSED
    tests/test_vsd_writer.py::TestVsdWriterGetValue::test__success PASSED
    tests/test_vsd_writer.py::TestVsdWriterGetValue::test__no_object PASSED
    tests/test_vsd_writer.py::TestVsdWriterGetValue::test__invalid_attr PASSED

    =========================================================================================== 125 passed in 4.57 seconds ===========================================================================================
