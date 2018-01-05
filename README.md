# Levistate
Levistate configuration template engine.

Work in progress.

For the initial prototype, templates are hard-coded in Python.  As this work
stands, it proves that the Bambou library can be used to configure a VSD.

## Requirements
Packages required for Levistate engine
* bambou
* json
* os

Additional packages for Levistate command-line tool
- argparse

Additional packages for unit-test
* pytest
* requests
* requests_mock

## Usage

Levistate command-line tool usage:

`
    usage: levistate.py [-h] [-tp TEMPLATE_PATH] [-sp SPEC_PATH] [-v VSD_URL]
                        [-u USERNAME] [-p PASSWORD] [-e ENTERPRISE] [-r]

    Command-line tool for running template commands

    optional arguments:
      -h, --help            show this help message and exit
      -tp TEMPLATE_PATH, --template-path TEMPLATE_PATH
                            Path containing template files
      -sp SPEC_PATH, --spec-path SPEC_PATH
                            Path containing object specifications
      -v VSD_URL, --vsd-url VSD_URL
                            URL to VSD REST API
      -u USERNAME, --username USERNAME
                            Username for VSD
      -p PASSWORD, --password PASSWORD
                            Password for VSD
      -e ENTERPRISE, --enterprise ENTERPRISE
                            Enterprise for VSD
      -r, --revert          Revert (delete) templates instead of applying
`

## File Descriptions
* levistate.py: Command-line tool for issuing template commands. (work in
progress)
* device_writer_base.py: Base class for all template writers.  Not to be used
on its own, use a derived class writer.
* vsd_writer.py: Writes templates to a VSD using common APIs from base class.
* bambou_adapter.py: A set of wrapper classes around the Bambou library to make
it work generically for any configuration object based on specifications.
* tests/test_bambou_adapter.py: Unit-tests for the Bambou adpater classes.

## Levistate Example

Apply enterprise, domain and ACLs to VSD (hard-coded).  Needs
vsd-api-specifications for operation

`
    levistate$ python ./levistate.py -sp ../vsd-api-specifications

    Applying enterprise template: {'description': 'Demo enterprise', 'enterprise_name': 'demo_ent'}
    Applying domain template: {'domain_name': 'demo_domain_1', 'enterprise_name': 'demo_ent', 'description': 'This is a demo domain'}
    Applying acl template: {'protocol': '6', 'description': 'This is a demo policy', 'enterprise_name': 'demo_ent', 'etherType': '*', 'domain_name': 'demo_domain_1', 'policy_name': 'demo_policy_1', 'action': 'FORWARD', 'destinationPort': '80', 'sourcePort': '*'}
`

Revert (delete) objects configured during application

`
    levistate$ python ./levistate.py -sp ../vsd-api-specifications -r

    Reverting subnet template: {'domain_name': 'demo_domain_1', 'enterprise_name': 'demo_ent', 'policy_name': 'demo_policy_1'}
    Reverting domain template: {'domain_name': 'demo_domain_1', 'enterprise_name': 'demo_ent'}
    Reverting enterprise template: {'enterprise_name': 'demo_ent'}
`
