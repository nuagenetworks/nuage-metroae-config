# Levistate

Levistate configuration template engine.

Version 0.0.0

This tool reads JSON or Yaml files of templates and user-data to
write a configuration to a VSD or to revert (remove) said configuration.

## Overview

Levistate is a Python-based engine which can apply configuration to VSDs
via templates.  The templates provide an abstraction around the VSD
configuration model simplifying and validating the required data.  Data is
provided by the user in the form of Yaml or JSON files and is transformed and
applied to the VSD through the tool's templates.  The required data and proper
format for each template is defined by standardized JSON schema specifications.

## Installation of Levistate


The primary requirements for running Levistate are:
1. Installation of Python and the necessary packages.
2. Installation of the Levistate engine python libraries
3. Access to the Configuration templates
4. Access to the VSD API Specification

#### Installation of Python and required packages.

Most linux distributions come with python bundled into the operating system. To verify that python is available we can do the following:

*Ubuntu*

```
root@ubuntu:~# python --version
Python 2.7.6
```

*RHEL/Centos*

```
[root@rhel]# python --version
Python 2.7.5
```

To manage the python package installation we will use PIP. PIP can be installed Levistate

*Ubuntu*

```
root@ubuntu:~# apt-get install python-pip
...
```

*RHEL/Centos*

```
[root@rhel]# yum install python-pip
...
```

Most packages required by Levistate are available as part of the base python functionality. However we will need to install the following:

- Bambou
- Jinja2 (min version 2.10)
- PyYAML

Additional packages for unit-test

    mock
    pytest
    requests
    requests-mock

The following packages are installed via the same method on both Ubuntu and RHEL/Centos.

*Ubuntu and RHEL/Centos*

```
[root@rhel]# pip install Bambou
...
[root@rhel]# pip install Jinja2
...
[root@rhel]# pip install PyYAML
...
```

### Installation of Levistate engine

Currently Levistate is available on github and will be installed via git clone. Check the levistate home page for latest master branch location.

First we need to install git.

*Ubuntu*

```
root@ubuntu:~# apt-get install git
```

*RHEL/Centos*

```
[root@rhel]# yum install git
```

Depending on the authentication method with github, ie. SSH Key, or Username/Password the git clone command line may change.


For username/password authentication

*Ubuntu and RHEL/Centos*

```
[root@rhel]# export GIT_SSL_NO_VERIFY=false
[root@rhel]# git clone  https://github.mv.usa.alcatel.com/CASO/levistate.git
Cloning into 'levistate'...
Username for 'https://github.mv.usa.alcatel.com': sfiddian
Password for 'https://sfiddian@github.mv.usa.alcatel.com':
remote: Counting objects: 619, done.
remote: Compressing objects: 100% (9/9), done.
remote: Total 619 (delta 1), reused 0 (delta 0), pack-reused 610
Receiving objects: 100% (619/619), 178.01 KiB | 0 bytes/s, done.
Resolving deltas: 100% (398/398), done.
```


### Installation of the VSD API Specifications

Levistate requires a description of the VSD API to create, read, update and delete the template contents into the VSD. We do this via reading the published VSD API Specification. This specificaiton is opensourced and is available on the public Nuage Networks github repository.



*Ubuntu and RHEL/Centos*

```
[root@rhel]# git clone https://github.com/nuagenetworks/vsd-api-specifications.git
Cloning into 'vsd-api-specifications'...
remote: Counting objects: 23428, done.
remote: Total 23428 (delta 0), reused 0 (delta 0), pack-reused 23428
Receiving objects: 100% (23428/23428), 4.98 MiB | 1013.00 KiB/s, done.
Resolving deltas: 100% (18163/18163), done.
```


## Parameters

Levistate command-line tool usage:

    usage: levistate.py [-h] -tp TEMPLATE_PATH [-sp SPEC_PATH] [-dp DATA_PATH]
                        [-t TEMPLATE_NAME] [-d DATA] [-r] [-v VSD_URL]
                        [-u USERNAME] [-p PASSWORD] [-e ENTERPRISE] [-dr] [-lg]
                        [-l] [-s] [-x]

    This prototype is able to read JSON or Yaml files of templates and user-data
    to write a configuration to a VSD or to revert (remove) said configuration.

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
      -d DATA, --data DATA  Specify user data as key=value
      -r, --revert          Revert (delete) templates instead of applying
      -v VSD_URL, --vsd-url VSD_URL
                            URL to VSD REST API
      -u USERNAME, --username USERNAME
                            Username for VSD
      -p PASSWORD, --password PASSWORD
                            Password for VSD
      -e ENTERPRISE, --enterprise ENTERPRISE
                            Enterprise for VSD
      -dr, --dry-run        Perform validation only
      -lg, --logs           Show logs after run
      -l, --list            Lists loaded templates
      -s, --schema          Displays template schema
      -x, --example         Displays template user data example

## Example Usage

Apply enterprise, domain and ACLs to VSD.

    levistate$ python levistate.py -tp sample/templates -sp ~/vsd-api-specifications -dp sample/user_data/acls.yaml -v https://localhost:8443

    Configuration
        Enterprise
            name = 'test_enterprise'
            DomainTemplate
                name = 'template_public'
                [store id to name domain_template_id]
            Domain
                name = 'public'
                templateID = [retrieve domain_template_id (DomainTemplate:id)]
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

Revert (remove) objects configured during application, use -r option

    levistate$ python levistate.py -tp sample/templates -sp ~/vsd-api-specifications -dp sample/user_data/acls.yaml -r

## User Data

The templates within the Levistate tool are applied using data provided by the
user.  Each set of data values provided allows the creation of an instance of
configuration on the VSD.  The required format for the data of each template is
defined by a JSON schema describing the required fields, types and other
constraints on the data.

### File Format

The user data for Levistate can be in either Yaml or JSON format.  Each entry
in the file defines a template and the value sets to use against that template
to instantiate configuration.

    - template: Enterprise
      values:
        - enterprise_name: my_first_enterprise
          description: The first

        - enterprise_name: my_second_enterprise
          description: The second

In this example, two data sets are provided for the Enterprise template and the
result will be that the two enterprises will be created on the VSD.  Only the
enterprise_name is required, but description can be provided optionally.  The
JSON schema for the Enterprise template defines the data format.

### Children

Let's now add domains to the enterprise objects.  In the Domain template, note
that in addition to a domain_name, it also needs the enterprise_name to be
specified so that the domain can be associated with the correct enterprise.  We
could define our user data as follows:

    - template: Enterprise
      values:
        - enterprise_name: my_first_enterprise
          description: The first

        - enterprise_name: my_second_enterprise
          description: The second

    - template: Domain
      values:
        - enterprise_name: my_first_enterprise
          description: The first
          domain_name: my_first_domain

        - enterprise_name: my_second_enterprise
          description: The second
          domain_name: my_second_domain

This user data is fully valid and will create two enterprises each with one
domain.  However, we are duplicating the enterprise names and it would be
tedious and error prone if the names needed to change.  In order to simplify
nested data, children can be utilized as follows:

    - template: Enterprise
      values:
        - enterprise_name: my_first_enterprise
          description: The first
      children:
        - template: Domain
          values:
            - domain_name: my_first_domain

    - template: Enterprise
      values:
        - enterprise_name: my_second_enterprise
          description: The second
      children:
        - template: Domain
          values:
            - domain_name: my_second_domain
              description: Overriden description

In this case, each Domain is a child of a parent Enterprise.  As such, all of
the values from the parent are inherited in the children.  The children
domains automatically inherit the enterprise_name of the parent.  This also
applies for the description.

Note that values can be overriden if necessary as with the description of the second
domain.  The most specific value takes precendence.  To prevent ambiguity, any
template with child templates can only define one set of values.

### Groups

Another mechanism for reducing duplication in data is by using groups.  A group
entry is very similar to a template, except that no actual template is
instantiated.  Thus, the group defines a stand-alone data set.  Groups are
useful when common data sets need to be defined and referenced elsewhere.

    - group: first
      values:
        - enterprise_name: my_first_enterprise
          domain_name: my_first_domain

    - group: second
      values:
        - enterprise_name: my_second_enterprise
          domain_name: my_second_domain

    - group: ssh
      values:
        - protocol: tcp
          port: 22

    - group: html
      values:
        - protocol: tcp
          port: 80

    - template: Acl
      values:
        - acl_name: http_acl
          $group_domain: first
          $group_traffic: http
          action: permit

        - acl_name: ssh_acl
          $group_domain: second
          $group_traffic: ssh
          action: deny

In the above example, data sets for domains and traffic types are defined as
groups.  These are being applied to the http_acl and ssh_acl templates using
$group fields and referencing by group name.  The template will inherit all of
the values from any group that is referenced.  The result in this case is that
http_acl is created in the first domain and permits http traffic (tcp port 80)
and the ssh_acl is created in the second domain and denies ssh traffic (tcp
port 22).

Group definitions can be children or have children.  However, they should only
define one set of values.  The field name for group references must start with
the string "$group", but can have any suffix following it.  The purpose of the
suffix is to allow multiple group references without name collision.  Although
any suffix can be specified, it is recommended to choose one that is
descriptive of the reference meaning.

### Field and Value Lists

An alternative way of specifying values is by using a field list and set of value
lists.  This format is similar to Comma Separated Values (CSV) data and
can efficiently specify a large amount of data.

    - template: Acl
      fields: ['acl_name', '$group_domain', 'protocol', 'port', 'action']
      values:
          -   ['acl1',     'first',         'tcp',      22,     'deny']
          -   ['acl2',     'first',         'udp',      5000,   'permit']
          -   ['acl3',     'second',        'tcp',      80,     'deny']
          -   ['acl4',     'second',        'udp',      5002,   'permit']

A fields list must be specified to define the field name for each position of
the value lists.  The values data sets must be specified as lists with the same
length as the fields list.

## Listing Templates

The templates that have been loaded into the Levistate tool can be listed with the following:

    levistate$ python levistate.py -tp sample/templates --list

    Domain
    Enterprise
    Subnet
    Zone

## Generating User Data Examples

An example of user data for any template can be provided using the following:

    python levistate.py -tp sample/templates --example --template Domain

    # First template set - Create a L3 Domain
    - template: Domain
      values:
        - enterprise_name: ""                      # (reference)
          domain_name: ""                          # (string)
          description: ""                          # (opt string)
          underlay_enabled: enabled                # (['enabled', 'disabled', 'inherited'])
          address_translation: enabled             # (['enabled', 'disabled', 'inherited'])

## Generating JSON Schemas

A JSON schema can be generated for the user data required for any template.  These schemas conform to the json-schema.org standard specification:

    python levistate.py -tp sample/templates --schema --template Domain

    {
      "title": "Schema validator for Nuage Metro Levistate template Domain",
      "$id": "urn:nuage-metro:levistate:template:domain",
      "required": [
        "enterprise_name",
        "domain_name",
        "underlay_enabled",
        "address_translation"
      ],
      "$schema": "http://json-schema.org/draft-04/schema#",
      "type": "object",
      "properties": {
        "underlay_enabled": {
          "enum": [
            "enabled",
            "disabled",
            "inherited"
          ],
          "title": "Underlay enabled"
        },
        "address_translation": {
          "enum": [
            "enabled",
            "disabled",
            "inherited"
          ],
          "title": "Address translation"
        },
        "domain_name": {
          "type": "string",
          "title": "Domain name"
        },
        "enterprise_name": {
          "type": "string",
          "title": "Enterprise name"
        },
        "description": {
          "type": "string",
          "title": "Description"
        }
      }
    }
