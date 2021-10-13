# Nuage MetroAE Configuration

Nuage MetroAE configuration template engine.

Version 1.1.0

This tool reads Excel spreadsheet (.xlsx file) or Yaml files of templates and user-data to
write a configuration to a VSD or to revert (remove) said configuration.

## Overview

MetroAE config is a Python-based engine which can apply configuration to VSDs
via templates.  The templates provide an abstraction around the VSD
configuration model simplifying and validating the required data.  Data is
provided by the user in the form of Yaml or Excel spreadsheet (.xlsx file) files and is transformed and
applied to the VSD through the tool's templates.  The required data and proper
format for each template is defined by standardized JSON schema specifications.

## Installation

### Via Docker Container

There are several modes of operation for MetroAE config.  For most users, the
tool should be consumed via the MetroAE Docker container.  Using this method
ensures that all of the libraries are properly installed and the `metroae`
command-line tool can be utilized for config (as well as deploy).  Instructions
for the Docker container installation are available at:

https://github.com/nuagenetworks/nuage-metroae/blob/master/Documentation/DOCKER.md

If using the Docker container, all remaining installation instructions can be
skipped.

### As Python Library

The MetroAE config tool is completely implemented as a Python library.  As such,
the functionality of the tool can be integrated into other Python tools or
libraries through the use of the APIs.  To do this, the library can be installed
via Python pip package from pypi.org:

```
pip install nuage-metroae-config
```

The pip installation of the package will pull in all dependent libraries
automatically.  The following section of installing from Github can be skipped.
The use of the Library APIs is documented in the `Python Library API` section.

### From Github Python Source

Using the MetroAE config tool without the Docker container can be accomplished
by pulling the source from Github.  You may want to use this method if you are
comfortable working with Python environments and don't want the overhead of a
container.   The instructions for this case is described in the next section.
If using this method, you would be responsible for installing all of the
necessary prerequiste libraries and to obtain the VSD API specs and templates.

#### Installation of MetroAE Config from Github

This section describes how to install the MetroAE config tool from the Github
repo.  These steps will be necessary to use the metroae_config command-line
tool directly.  If using the MetroAE Docker container, this section should be
skipped.

The primary requirements for running MetroAE config are:
1. Installation of Python and the necessary packages.
2. Installation of the config engine python libraries
3. Access to the Configuration templates
4. Access to the VSD API Specification

#### Installation of Python and required packages.

Most linux distributions come with python bundled into the operating system.
Python 2.7 is required. Additionally, Python 3 is also supported.

To verify that python is available we can do the following:
(Note: All examples provided below are in Python 2.7 syntax)

*Ubuntu*

```
root@ubuntu:~# python --version
Python 2.7.5
```

*RHEL/Centos*

```
[root@rhel]# python --version
Python 2.7.5
```

To manage the python package installation we will use PIP. Install PIP via
apt-get or yum:

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

Most packages required by MetroAE config are available as part of the base
python functionality. However we will need to install the following:

- Bambou
- Jinja2 (min version 2.10)
- PyYAML
- lark-parser

Additional packages for unit-test

- mock
- pytest
- requests
- requests-mock
- lark_parser

The following packages are installed via the same method on both Ubuntu and RHEL/Centos.

*Ubuntu and RHEL/Centos*

```
[root@rhel]# pip install -r requirements.txt
...
```

#### Installation of configuration engine

Currently MetroAE config is available on github and will be installed via git
clone. Check the MetroAE home page for latest master branch location.

First we need to install git.

*Ubuntu*

```
root@ubuntu:~# apt-get install git
```

*RHEL/Centos*

```
[root@rhel]# yum install git
```

The repository is available via Github:

```
https://github.com/nuagenetworks/nuage-metroae-config
```

Depending on the authentication method with github, ie. SSH Key, or
Username/Password the git clone command line may change.


For username/password authentication

*Ubuntu and RHEL/Centos*

```
[root@rhel]# export GIT_SSL_NO_VERIFY=false
[root@rhel]# git clone https://github.com/nuagenetworks/nuage-metroae-config.git
Cloning into 'levistate'...
Username for 'https://github.com/nuagenetworks/nuage-metroae-config.git': sfiddian
Password for 'https://sfiddian@github.mv.usa.alcatel.com':
remote: Counting objects: 619, done.
remote: Compressing objects: 100% (9/9), done.
remote: Total 619 (delta 1), reused 0 (delta 0), pack-reused 610
Receiving objects: 100% (619/619), 178.01 KiB | 0 bytes/s, done.
Resolving deltas: 100% (398/398), done.
```


#### Installation of the VSD API Specifications

MetroAE Config requires a description of the VSD API to create, read, update and
delete the template contents into the VSD. We do this via reading the published
VSD API Specification. This specificaiton is opensourced and is available on
the public Nuage Networks github repository.



*Ubuntu and RHEL/Centos*

```
[root@rhel]# git clone https://github.com/nuagenetworks/vsd-api-specifications.git
Cloning into 'vsd-api-specifications'...
remote: Counting objects: 23428, done.
remote: Total 23428 (delta 0), reused 0 (delta 0), pack-reused 23428
Receiving objects: 100% (23428/23428), 4.98 MiB | 1013.00 KiB/s, done.
Resolving deltas: 100% (18163/18163), done.
```

## Command-line Tool

When using the MetroAE Docker container, all commands are accessed through the
`metroae` command-line tool as:

    metroae config ...

If you are using the Python source obtained through Github, then any reference
to `metroae config` should substitute the equivalent Python source tool:

    python metroae_config.py ...


## Parameters

MetroAE Config command-line tool usage:

    usage: metroae config [-h]
                          {create,revert,validate,list,schema,example,upgrade-templates,version,help}
                          ...

    Version 1.0 - This tool reads JSON or Yaml files of templates and user-data to
    write a configuration to a VSD or to revert (remove) said configuration. See
    README.md for more.

    positional arguments:
      {create,revert,validate,list,schema,example,upgrade-templates,version,help}

    optional arguments:
      -h, --help            show this help message and exit


    usage: metroae config create [-h] [-tp TEMPLATE_PATH] [--version]
                                 [-sp SPEC_PATH] [-dp DATA_PATH] [-d DATA]
                                 [-v VSD_URL] [-u USERNAME] [-p PASSWORD]
                                 [-e ENTERPRISE] [-lg]
                                 [datafiles [datafiles ...]]

    positional arguments:
      datafiles             Optional datafile

    optional arguments:
      -h, --help            show this help message and exit
      -tp TEMPLATE_PATH, --template_path TEMPLATE_PATH
                            Path containing template files. Can also set using
                            environment variable TEMPLATE_PATH
      --version             Displays version information
      -sp SPEC_PATH, --spec_path SPEC_PATH
                            Path containing object specifications. Can also set
                            using environment variable VSD_SPECIFICATIONS_PATH
      -dp DATA_PATH, --data_path DATA_PATH
                            Path containing user data. Can also set using
                            environment variable USER_DATA_PATH
      -d DATA, --data DATA  Specify user data as key=value
      -v VSD_URL, --vsd_url VSD_URL
                            URL to VSD REST API. Can also set using environment
                            variable VSD_URL
      -u USERNAME, --username USERNAME
                            Username for VSD. Can also set using environment
                            variable VSD_USERNAME
      -p PASSWORD, --password PASSWORD
                            Password for VSD. Can also set using environment
                            variable VSD_PASSWORD
      -e ENTERPRISE, --enterprise ENTERPRISE
                            Enterprise for VSD. Can also set using environment
                            variable VSD_ENTERPRISE
      -lg, --logs           Show logs after run


## Example Usage

Apply enterprise, domain and ACLs to VSD.

    $ metroae config create -tp sample/templates -sp ~/vsd-api-specifications -v https://localhost:8443 sample/user_data/acls.yaml

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

    $ metroae config revert -tp sample/templates -sp ~/vsd-api-specifications sample/user_data/acls.yaml

### Custom Templates
You can also use your own custom templates with MetroAE Config. You can put your custom templates in the same directory as our standard templates or you can put them in one or more custom directories.

Note: Your custom templates must have unique template names (not file names... The template name inside the template file...) to avoid name collisions with standard templates. If two templates have the same name, MetroAE Config will use the template and VSD versions to determine which template to apply when run. This may result in unexpected behavior when your template names are the same as standard template names. We recommend that you use a prefix for your template names to guarantee uniqueness. For example, if you create a custom template with the name "Enterprise" there will be a collision. But if you use the name "my_enterprise" there will not be a collision.

#### Example commands for specifying custom template directories

The following command tells MetroAE Config to look for templates in the custom location, `sample/custom-templates`:

    $ metroae config create -tp sample/custom-templates -sp ~/vsd-api-specifications -v https://localhost:8443 sample/user_data/acls.yaml

Note that you can specify more than one template path so that you can utilize templates in more than one directory, for example if your solution needs to use some standard templates and some custom templates. The -tp option can be used to pass multiple template path at the same time:

    $ metroae config create -tp standard-templates/templates -tp sample/custom-templates -sp ~/vsd-api-specifications -v https://localhost:8443 sample/user_data/acls.yaml

## User Data

The templates within the MetroAE config tool are applied using data provided by the
user.  Each set of data values provided allows the creation of an instance of
configuration on the VSD.  The required format for the data of each template is
defined by a JSON schema describing the required fields, types and other
constraints on the data.

### File Format

The user data for MetroAE config can be in either Yaml or JSON format.  Each entry
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

The templates that have been loaded into the MetroAE config tool can be listed
with the following:

    $ metroae config -tp sample/templates --list

    Domain
    Enterprise
    Subnet
    Zone

## Generating User Data Examples

An example of user data for any template can be provided using the following:

    metroae config example -tp sample/templates Domain

    # First template set - Create a L3 Domain
    - template: Domain
      values:
        - enterprise_name: ""                      # (reference)
          domain_name: ""                          # (string)
          description: ""                          # (opt string)
          underlay_enabled: enabled                # (['enabled', 'disabled', 'inherited'])
          address_translation: enabled             # (['enabled', 'disabled', 'inherited'])

## Generating JSON Schemas

A JSON schema can be generated for the user data required for any template.
These schemas conform to the json-schema.org standard specification:

    metroae config schema -tp sample/templates Domain

    {
      "title": "Schema validator for Nuage Metro config template Domain",
      "$id": "urn:nuage-metro:config:template:domain",
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

## Query Tool

### Description

MetroAE config can be used as a generic data querying tool to extract
information from devices.  At the time of this writing VSD and ES are
supported.  The tool uses a simple language to describe the data that is to be
retrieved.  The data will be displayed to the screen in a YAML like format, but
it could (in addition) be written to a file.  The results are also returned as
a Python list when using query tool as a library.

### Usage

The query tool is used by specifying "query" as the action to `metroae_config`.
The parameters are mostly the same as other actions supported by
`metroae_config`.  The VSD specification path `-sp` is required if querying a
VSD.  The other VSD parameters (i.e. user, pass, URL, etc) also apply for
query in the same way as configuration creation actions.

The query tool also supports queries to ElasticSearch (ES).  In this case, a
new `-es` parameter has been added to specify the address of the ES to query.

The `query language` can be specified to the tool directly on the command-line
for easy manual use using the `-q` query parameter.  An example follows:

    metroae config query -v https://localhost:8443 -q 'enterprise.name'

    Device: Nuage Networks VSD 20.5.1
    - Shared Infrastructure
    - public
    - private
    >>> All actions successfully applied

Multiple queries can be specified on a single line using semicolon `;`:

    metroae config query -v https://localhost:8443 -q 'apps = SAASApplicationType.name; ents = enterprise.name'

    Device: Nuage Networks VSD 20.5.1
    apps:
    - Office365
    - SalesForce
    - WebEx
    ents:
    - Shared Infrastructure
    - public
    - private
    >>> All actions successfully applied

The language definition for query tool can also be specifed in a file to be
read.  One or more of these files (or a directory containing .query files) can
be specifed on the command-line for the tool to read and execute each file.
Newlines in files separate commands.  However, semicolons are still
supported in files as well.

    example.query:

    apps = SAASApplicationType.name
    ents = enterprise.name

    metroae config query -v https://localhost:8443 example.query

    Device: Nuage Networks VSD 20.5.1
    apps:
    - Office365
    - SalesForce
    - WebEx
    ents:
    - Shared Infrastructure
    - public
    - private
    >>> All actions successfully applied

### Language Definition

The query tool uses a `query language` to specify the data to be reteived from
devices.  This language is intended to be simple to read and use and is easily
extendable.

#### General Formatting

Each query to be performed is specified one per-line.  Alternatively and
equivalently, semicolons `;` can be used to separate multiple queries on a
single line.  Any query beginning with a hash `#` indicates a comment and will
be ignored.  Outside of strings, any whitespace is ignored.

#### Data Retrieval

Data retrieval commands are specified by providing nested object names
separated by dot `.` with the attribute as the last identifier.  A retrieval
traverses all instances of each level of the specified object tree and returns
the attribute value for every instance found.

The result is always a flat list of the attribute values.  Any heirarchy is
flattened.  If no results are found or there is an error (such as missing child
object) then an empty list is returned.  With this procedure, processing
results is consistent as there will always be a list.

For VSD:

    Enterprise.Domain.Zone.Subnet.name

The above (reading from right to left) returns a list of the names from all
subnets under all zones under all domains under all enterprises.  For VSD
queries, each object is a configuration object specified by entity name.  The
names here are case-insensitve although note that case may matter for other
devices (like ES).

For ElasticSearch:

    nuage_sysmon.disks.available

The above (reading from right to left) returns the available values for all
disks under the nuage_sysmon index.  For ES, the first object is the ES index
and then subsequent object names traverse the JSON objects stored in each ES
record.  Since ES encodes using JSON, the object names and attribures are all
case-sensitive as required by the format.

#### Attributes

The last identifier on a data retrieval is the attribute.  It determines which
value to extract from the objects traversed.  In previous examples, a single
value was extracted, however multiple attributes can be gathered by specifying
a comma-separated list in curly braces `{}`.  When retrieving multiple
attributes, the result becomes a list of dictionaries with key/value pairs
for each of the attributes.  A star `*` can be used to get all available
attributes.

Single attribute:

    Enterprise.name

    - Shared Infrastructure
    - public
    - private

Multiple attributes:

    Enterprise.{name,id}

    - name: Shared Infrastructure
      id: abcd-0001
    - name: public
      id: abcd-0002
    - name: private
      id: abcd-0003

All attributes:

    Enterprise.{*}

    - name: Shared Infrastructure
      id: abcd-0001
      bgpenabled: false
      dhcpleaseinterval: 24
      (Whole bunch of stuff omitted for brevity...)
    - name: public
      id: abcd-0002
      bgpenabled: false
      dhcpleaseinterval: 24
      (Whole bunch of stuff omitted for brevity...)
    - name: private
      id: abcd-0003
      bgpenabled: false
      dhcpleaseinterval: 24
      (Whole bunch of stuff omitted for brevity...)

#### Filters

Filters can be applied to each object of the data retrieval.  Filters are
enclosed by square brackets `[]` and are separated by and `&` characters.  The
choice of `&` as a separator enforces that filters are combined together as
logical AND operations.

The filter applies only to the level where it is specified.  The filters
manipulate the results from the level, usually by removing unwanted records.
Any subsequent object levels would operate on the filtered list.  For example:

    Enterprise[name=public].domain.name

The filter on enterprise will limit enterprise results to only a single
enterprise object (with name `public`).  However, let's say the `public`
enterprise had 10 domains.  Then the 10 name results for those domains would be
returned.

##### Range Filter

A range filter can be used to limit the start and max number of results at the
level.  The filter has a start index and an end index separated by colon `:`.
Indexes are 0-based positions of the list.  Thus 0 is the first and 4 would be
the 5th item in the list.  The items from the query are returned starting at
the start index and ending one before the end index.  Any range out of bounds
of the results are omitted.  Thus if the start index is after the end of the
results, an empty list is returned.

If the start index is omitted, a value of 0 is assumed (start at beginning).
If the end index is omitted, then the entire remainder of the list is returned.

A single index (without colon specified) can be used to return the single
item from the results at the specified index.  If this is out of bounds of the
results, an empty list is returned.

Negative indicies are allowed and count from the end of the list.  Thus -1 is
the last item and -5 is the 5th from last.

The behavior of the range filter is exactly the same as Python list slicing.

    Note that ES index queries do not support negative range indicies.  Use a
    reverse sort and positive indicies instead.

Examples using enterpises: `e1, e2, e3, e4, e5`

    enterprise[1:5].name
    - e2
    - e3
    - e4

    enterprise[1:99].name
    - e2
    - e3
    - e4
    - e5

    enterprise[:5].name
    - e1
    - e2
    - e3
    - e4

    enterprise[3:].name
    - e4
    - e5

    enterprise[99:].name
    []

    enterprise[3].name
    - e4

    enterprise[99].name
    []

    enterprise[-3:-1].name
    - e3
    - e4

##### Attribute Filter

Object results can be filtered by attribute values.  Only results where the
field value of the object matches the filter value will be returned.  The
format for these filters is the field name equal `=` value.  A list of values
can be provided enclosed in square brackets `[]` and separated by comma `,`.
This denotes that any result matching any of the list values will be returned.

Given these enterprises:

    - name: e1
      BGPEnabled: true
    - name: e2
      BGPEnabled: false
    - name: e3
      BGPEnabled: true

The following examples produce:

    enterprise[BGPEnabled=true].name
    - e1
    - e3

    enterprise[name=[e2, e3]].name
    - e2
    - e3

    enterprise[name=[e2, e3] & BGPEnabled=false].name
    - e2

    enterprise[name=[e1, e3] & BGPEnabled=false].name
    []

##### Sort Filter

The sort filter can be used to sort the results by an object field.  Note that
the sorting occurs only at the level where it is specified.  If there are
child objects under a sort fitler the children would not be sorted, but they
would be queried in the parent's sorted order.

Sorting is specified by the `%sort=` keyword followed by the field name of the
object to sort by.  There is also `%sort_desc=` to sort in descending order.

Given these enterprises:

    - name: e3
      dhcpleaseinterval: 1
    - name: e1
      dhcpleaseinterval: 2
    - name: e2
      dhcpleaseinterval: 3

The following examples produce:

    enterprise[%sort=name].name
    - e1
    - e2
    - e3

    enterprise[%sort=DHCPLeaseInterval].name
    - e3
    - e1
    - e2

    enterprise[%sort_desc=name].name
    - e3
    - e2
    - e1

##### Group Filter

A group filter can be specified to combine together results by the value of
another field.  This makes it easier to identify subsets of results given that
the query tool collapses them all into flat lists.

The group filter is specified by `%group=` followed by the field name to group
by.  When using groups, results are returned as a list of pairs.  The first
item of the pair is the group field value and the second is the list of results
matching the group field value.

For example, normally results are flattened and thus it is difficult to
determine which domain goes with which enterprise:

    enterprise.domain.name

    - domain1
    - domain2
    - domain3
    - domain4

However, using grouping the relationships can be determined:

    enterprise[%group=name].domain.name

    - - public
      - - domain1
        - domain2
        - domain3
    - - private
      - - domain4
    - - Shared Infrastructure
      - []

#### Variables

Results can be stored in variables for identification and use in later queries.
Variables are restricted to C-like names which cannot start with a number and
can contain capital letters, lower case letters, numbers or underscore `_`.

Variable assignments are performed by specifying the variable name then equal
`=` then the expression or data type to store in the variable.  The output of
assigments changes to a dictionary.

    enterprise_names = enterprise.name

    enterprise_names:
    - public
    - private
    - Shared Infrastructure

Variables are dynamically typed and can contain any data type.  More
information about data types will be provided in a later section.  Variables
can be dereferenced in later queries by specifying dollar `$` and the variable
name.  Variables that have been dereferenced but not yet defined will cause an
error.

Variables can be filtered:

    enterprises = enterprise.{name,id}

    enterprises:
    - name: public
      id: abcd-0001
    - name: private
      id: abcd-0002

    $enterprises[%sort=name]

    - name: private
      id: abcd-0002
    - name: public
      id: abcd-0001

    $enterprises[%sort=name].id

    - abcd-0002
    - abcd-0001

Variables can also be used as the values for filters:

    enterprises = enterprise.name

    enterprises:
    - e1
    - e2
    - e3
    - e4

    start = 2

    start: 2

    $enterprises[$start:]
    - e3
    - e4

    name = "e2"

    name: e2

    enterprise[name=$name].{name,id}
    - name: e2
      id: abcd-0002

Variable values can be specified on the command-line using the `-d` option.
The format is variable name `=` value. i.e. `-d name=enterprise1`.  When
variables are defined on the command-line, they override any assignment
within queries.  This allows defaults to be set inside query files and `-d` to
override with a specific value.

#### Data Types

The query language defines various data types to be specified.  Variables are
dynamically typed and can accept any of these types.

Strings are defined enclosed with single `'` or double `"` quotes.  Multi-line
blocks can be defined using triple single `'''` or double `"""` quotes.

    string = 'this is a string'
    string = "another has ' in it"
    multiline = """
    this has
    multiple lines
    """

Numbers can be specified as positive or negative integers.  Floating point
numbers are not supported.

    integer = 42
    negative = -4

For Booleans, `true` specifies true and `false` specifies false.

    is_true = true
    is_false = false

Lists can be formed using square brackets `[]` and separating items by comma
`,`.  Lists can contain any of the above data types even in combinations.
However, lists of lists are not supported.

    enterprise_names = ['e1', 'e2', 'e3']

#### Functions

There are a set of functions that can operate on expressions such as data
retrieval or variables.  These come in the form of function name followed by
the expression enclosed in parens `()`.

The `count` function returns the number of items in a list.  An error is
produced if the expression provided to count is not a list.

    names = enterprise.name

    names:
    - e1
    - e2
    - e3

    count($names)
    3

The `reverse` function returns the items of a list in backward order.  An error
is produced if the expression provided to reverse is not a list.

    reverse(enterprise.name)
    - e3
    - e2
    - e1

#### Combine

There is a `combine` operator which combines expressions together depending on
the data types.  The format is expression1 plus `+` expression2.  The
expressions can be variables, data type constants or data retrieval.

If both expressions are lists, then the combine operator will return a list
with all of the items of both.

    names = enterprise.name

    names:
    - e1
    - e2
    - e3

    $names + ["new1", "new2"]
    - e1
    - e2
    - e3
    - new1
    - new2

If both expressions are integers, then the combine operator will add the
values.

    count(enterprise.name) + 1
    4

If both expressions are strings, then the strings will be concatenated.

    filename = "output"
    filename: output

    path = "/tmp/" + $filename + ".txt"
    path: /tmp/output.txt

Any other combination of data types will result in an error from combine.

#### Actions

There are a set of actions that can change the state of later queries or
perform a task.  These come in the form of action name followed by a list of
comma-separated arguments enclosed in parens `()`.  Actions do not return any
value and they cannot be part of an assignment or expression.

The `connect` action sets up a new session with a device.  All subsequent
queries are directed to the new device.  The first argument to connect is the
device type, then the remaining parameters are specific to the device.  Using
connect allows data to be gathered from multiple sources in the same query
execution.

For VSD:

    connect("VSD", url, username, password, enterprise, cert_file, cert_key_file)

    Where:
        url (required)           : URL of VSD to connect to
        username (optional)      : Username to be used to connect (default "csproot")
        password (optional)      : Password to be used to connect (default "csproot")
        enterprise (optional)    : Enterprise to be used to connect (default "csp")
        cert_file (optional)     : Path to a certificate file (instead of password)
        cert_key_file (optional) : Path to a certificate key file (required if cert_file specified)

For ElasticSearch:

    connect("ES", address, port)

    Where:
        address (required) : Address of ElasticSearch to connect to
        port (optional)    : Port of ElasticSearch (default 9200)

The `redirect_to_file` action causes all subsequent queries to write results
to the specified file in addition to echoing to the screen.

    redirect_to_file("/tmp/output.txt")

The `echo` action turns on and off the printing of output of subsequent queries
to the screen.  This only affects the display of the queries and they still
operate normally in all other ways.  Variables would still be assigned and
output would still be written to file if redirected.  Echoing is on by default.
it can be turned off with the string `off` and turned back on with the string
`on`.  Disabling echoing is useful when huge amounts of data are expected to be
returned but it would clutter the screen.

    echo("off")

The `output` action turns on and off the writing of results to the screen,
redirect file and Python returned results.  Variables are still assigned when
output is off.  Turning off output is useful for gathering all intermediate
variables and then turning it on to write out a single final report.  Output is
on by default.  It can be turned off with the string `off` and turned back on
with the string `on`.

    output("off")

The `render_template` action outputs the text of a variable substituted
template.  The action takes a [Python Jinja](https://jinja.palletsprojects.com/en/2.11.x/)
template string as an argument.  Jinja templates contain tags enclosed by
double curly braces `{{` `}}` that reference variables to be substituted into
the text.  The variables assigned from queries are all available to be injected
into the text output.  Jinja templates support loops, conditionals, math and
other filters.  See the [Python Jinja](https://jinja.palletsprojects.com/en/2.11.x/)
documentation for more. Using Jinja templates, many file formats can be output
including nice text reports, HTML pages, CSV or JSON.

The `render_yaml_template` action is exactly the same as `render_template`
except that substituted variables are formatted properly for YAML/JSON output.
For example strings are quoted, booleans are converted to true/false, etc.

Example query file:

    output("off")

    connect("VSD", "https://localhost:8443")

    report_file = "report.txt"
    ent_names = enterprise.name
    ent_count = count($ent_names)
    licenses_expires = License.expirytimestamp

    template = """============== VSD Health Report ===========
    VSD:
        Enterprises: {{ ent_names | join(', ') }} ({{ ent_count }})
        License expiry: {{ ((licenses_expires[0] / 1000 - now) / (3600 * 24)) | int }} days
    ===========================================
    """

    redirect_to_file($report_file)
    output("on")
    render_template($template)

Resulting output to `report.txt`:

    ============== VSD Health Report ===========
    VSD:
        Enterprises: public, private, Shared Infrastructure (3)
        License expiry: 90 days
    ===========================================


## Python Library API

The MetroAE Config engine is written entirely using Python.  It can be integrated
into other Python-based tools using the library APIs via the pip package
`nuage-metroae-config`.  The following sections describe the use of the APIs.

### Template Store Class

The `TemplateStore` class is a repository for all of the templates loaded into
the engine.  It will be used by the `Configuration` class to apply template
actions to a device via a `DeviceWriterBase` class.

from nuage_metroae_config.template import TemplateStore

    Reads and parses configuration templates.

- read_templates(path_or_file_name)

        Reads and parses templates from either all templates in a
        directory path, or a single template specified by filename.
        Both yaml (.yml) and JSON (.json) files are supported.

- add_template(template_string, filename=None)

        Parses the specified string as a template in Yaml or JSON format.

- get_template_names(software_type=None, software_version=None)

        Returns a list of all template names currently loaded in store.
        If software_version and/or software_type is provided, names will
        be filtered by the specified version/type.

- get_template(name, software_type=None, software_version=None)

        Returns a Template object of the specified name.  If software_version
        and/or software_type is provided, template of specified version/type
        will be returned.

### Template Class

The `Template` class is a read-only class which provides information about a
template that was read in via the `TemplateStore`.

from nuage_metroae_config.template import Template

    Configuration template.  This class is read-only.

- get_name()

        Returns the name of this template.

- get_template_version()

        Returns the template version

- get_software_version()

        Returns a dictionary of {"software_version": "xxx", "software_type": "xxx"}

- get_schema()

        Returns the schema for the template variables in json-schema form.

- get_example()

        Returns example user-data for template variables in YAML format.

- get_documentation()

        Returns template documentation in MarkDown format.

- validate_template_data(template_data)

        Validates that the template_data provided matches the variables schema.
        Returns True if ok, otherwise an exception is raised.

### VSD Writer Class

The `VsdWriter` class is a derived class of the `DeviceWriterBase` that applies
configuration to a Nuage Networks VSD.  The writers are modular such that
new devices could be configured by defining derived device writer classes based
off of the common `DeviceWriterBase` base class.  The remainder of the engine
APIs use the generic base class.  This provides great extendability to
configure many different devices.  Note that the `VsdWriter` class also acts as
a reader for the `Query` class.

from nuage_metroae_config.vsd_writer import VsdWriter

    Writes configuration to a VSD.  This class is a derived class from
    the DeviceWriterBase Abstract Base Class.

- set_session_params(url, username="csproot", password=None, enterprise="csp", certificate=None)

        Sets the parameters necessary to connect to the VSD.  This must
        be called before writing or an exception will be raised.

- get_version():

        Returns the version running on the VSD in format:
            {"software_version": "xxx", "software_type": "xxx"}

- set_software_version(software_version):

        Sets the software version of the VSD.  This can be obtained via the
        get_version() method to get from the VSD itself or overwriten
        to a specific value.

- read_api_specifications(path_or_file_name):

        Reads the VSD configuration API specifications from JSON files
        in the specified path or file name.  This must be called before
        writing or an exception will be raised.

- set_logger(logger):

        Set a custom logger for actions taken.  This should be based on the
        logging Python library.  It will need to define an 'output' log level
        which is intended to print to stdout.

### User Data Parser Class

The `UserDataParser` class parses the YAML-based user-data format defined in
the `User Data` section of this document.  It is able to return the data in
template_name/data_dictionary pairs.  This data can be fed into the
`Configuration` class to render templates and apply configuration.

from nuage_metroae_config.user_data_parser import UserDataParser

    Parses Yaml or JSON files containing template user data

- read_data(path_or_file_name):

        Reads and parses user data from either all files in a
        directory path, or a single file specified by filename.
        Both yaml (.yml) and JSON (.json) files are supported.

- add_data(user_data_string):

        Parses the specified string as user data in Yaml or JSON format.

- get_template_name_data_pairs():

        Returns parsed data as a list of (template_name, data_dict) pairs.

### Configuration Class

The `Configuration` class puts all the above pieces together to configure a
device.  It requires a `TemplateStore` object with loaded templates.  User data
is applied to the `Configuration` object which can be taken directly from the
`UserDataParser` class or from pure Python data via another source.  Finally,
the configuration is applied, updated or reverted to a device using one of the
derived writer classes.

from nuage_metroae_config.configuration import Configuration

    Container for template instances.

- set_software_version(software_type=None, software_version=None)

        Sets the current software version of templates that is desired.
        If not called, the latest software version of templates will be
        used.

- add_template_data(template_name, template_data)

        Adds template data (user data) for the specified template name.
        Data is specified in a kwargs dictionary with keys as the
        attribute/variable name.  The data is validated against the
        corresponding template schema.  An id is returned for reference.

- apply(writer)

        Applies this configuration to the provided device
        writer.  Returns True if ok, otherwise an exception is
        raised.

- update(writer)

        Applies this configuration to the provided device
        writer as an update.  This means objects that exist will
        not be considered conflicts.  Returns True if ok, otherwise
        an exception is raised.

- revert(writer)

        Reverts (removes or undo) this configuration from the
        provided device writer.  Returns True if ok, otherwise
        an exception is raised.

- set_logger(logger):

        Set a custom logger for actions taken.  This should be based on the
        logging Python library.  It will need to define an 'output' log level
        which is intended to print to stdout.

### Query Class

The `Query` class allows information to be retrieved from a device through
device readers based on the `DeviceReaderBase`.  Note that the `VsdWriter`
class is also a reader derived off of this base and can be used for query.  The
information to be retrieved is defined by a "query language" which is described
in the `Language Definition` section of this document.  Results are returned
from the `execute()` of the query language text.  Also, any variables set during
the query can be retrieved with `get_variables()`.

from nuage_metroae_config.query import Query

    A class which can retrieve information from a device using a
    DeviceReaderBase reader object.  The information to be retrieved is defined
    by query language text.

- set_reader(reader)

        Set the primary reader object for performing queries on the device.
        The reader needs to be derived from the DeviceReaderBase class.

- get_variables()

        Returns a dictionary of all variables and values set during queries.

- register_reader(reader_type, reader)

        Register a reader object for each 'connect' type for performing queries
        on the device.  This allows devices to be switched within the query
        text.  The readers need to be derived from the DeviceReaderBase class.

- add_query_file(path_or_file_name)

        Reads and parses query sets from either all query files in a
        directory path, or a single query file specified by filename.
        Query files are expected to have .query extension

- execute(query_text=None, override_variables)

        Executes the query defined in query_text.  Variables in the query
        text can be overriden using the override_variables kwargs dict.  The
        results of the query are returned as a list with an entry for each
        query text line.  If query_text is None, then query text is pulled
        from query files defined by add_query_file.

- set_logger(logger)

        Set a custom logger for actions taken.  This should be based on the
        logging Python library.  It will need to define an 'output' log level
        which is intended to print to stdout.

### ES Reader Class

The `EsReader` class can be used as another reader with the `Query` class.  It
is derived from the `DeviceReaderBase` class and can retrieve information from
ElasticSearch.

from nuage_metroae_config.es_reader import EsReader

    Performs queries on ElasticSearch.  This class is a derived class from
    the DeviceReaderBase Abstract Base Class.

- set_session_params(address, port=None):

        Sets the parameters necessary to connect to the ES.  This must
        be called before reading or an exception will be raised.

## Library API Example - Config

    from nuage_metroae_config.configuration import Configuration
    from nuage_metroae_config.template import TemplateStore
    from nuage_metroae_config.user_data_parser import UserDataParser
    from nuage_metroae_config.vsd_writer import VsdWriter

    ENGINE_VERSION = "1.1.0"
    VSD_API_SPEC_PATH = "./vsd-api-specifications"
    TEMPLATE_PATH = "./templates"
    USER_DATA_PATH = "./user_data"
    VSD_URL = "https://10.0.0.1:8443"
    VSD_USERNAME = "username"
    VSD_PASSWORD = "password"
    VSD_ENTERPRISE = "csp"


    def setup_template_store(template_path):
        store = TemplateStore(ENGINE_VERSION)

        store.read_templates(template_path)

        return store


    def setup_vsd_writer(vsd_url):
        vsd_writer = VsdWriter()
        vsd_writer.add_api_specification_path(VSD_API_SPEC_PATH)

        vsd_writer.set_session_params(vsd_url,
                                      username=VSD_USERNAME,
                                      password=VSD_PASSWORD,
                                      enterprise=VSD_ENTERPRISE)

        device_version = vsd_writer.get_version()
        vsd_writer.set_software_version(device_version)

        return vsd_writer


    def setup_configuration(template_store, user_data_path):
        config = Configuration(template_store)

        parser = UserDataParser()
        template_data_pairs = parser.read_data(user_data_path)

        for data in template_data_pairs:
            template_name = data[0]
            template_data = data[1]
            config.add_template_data(template_name, **template_data)

        return config


    # Setup
    template_store = setup_template_store(TEMPLATE_PATH)
    vsd_writer = setup_vsd_writer(VSD_URL)
    config = setup_configuration(template_store, USER_DATA_PATH)

    # Apply the configuration from user data
    config.apply(vsd_writer)

    # Revert the configuration from user data
    config.revert(vsd_writer)


## Library API Example - Query

    from nuage_metroae_config.es_reader import EsReader
    from nuage_metroae_config.query import Query
    from nuage_metroae_config.vsd_writer import VsdWriter

    VSD_API_SPEC_PATH = "./vsd-api-specifications"
    VSD_URL = "https://10.0.0.1:8443"
    VSD_USERNAME = "username"
    VSD_PASSWORD = "password"
    VSD_ENTERPRISE = "csp"

    ES_ADDRESS = "10.0.0.2"
    ES_PORT = 9200


    def setup_vsd_query_tool(vsd_url):
        vsd_reader = VsdWriter()
        vsd_reader.add_api_specification_path(VSD_API_SPEC_PATH)

        vsd_reader.set_session_params(vsd_url,
                                      username=VSD_USERNAME,
                                      password=VSD_PASSWORD,
                                      enterprise=VSD_ENTERPRISE)

        device_version = vsd_writer.get_version()
        vsd_reader.set_software_version(device_version)

        vsd_query = Query()
        vsd_query.set_reader(vsd_reader)

        return vsd_query


    def setup_es_query_tool(es_address):
        es_reader = EsReader()
        es_reader.set_session_params(es_address, ES_PORT)

        es_query = Query()
        es_query.set_reader(es_reader)

        return es_query


    def get_subnetwork_usage(vsd_query):

        query_string = """
        subnets = Enterprise.Domain.Zone.Subnet.{name, netmask}
        zones = Enterprise.Domain.Zone[%group=name].Subnet.{name, netmask}
        d_count = count(Enterprise.Domain)
        s_count = count(Enterprise.Domain.Zone.Subnet)
        z_count = count(Enterprise.Domain.Zone)
        """
        vsd_query.execute(query_string)

        results = vsd_query.get_variables()

        domain_dict = dict()
        domain_dict_agg = dict()

        # [{"name": <subnet_name>, "netmask": <netmask>}, ...]
        domain_dict["subnets"] = results["subnets"]
        # [[<zone_name>, [{"name": <subnet_name>, "netmask": <netmask>}, ...]], ...]
        domain_dict["zones"] = results["zones"]
        domain_dict_agg["d_count"] = results["d_count"]
        domain_dict_agg["s_count"] = results["s_count"]
        domain_dict_agg["z_count"] = results["z_count"]

        return domain_dict, domain_dict_agg


    def get_enterprises_with_alarms(vsd_query):

        query_string = """
        Enterprise[%group=name].Alarm[severity="CRITICAL"].description
        """
        results = vsd_query.execute(query_string)

        # [[<enterprise_name>, [{"description": <alarm_descr>}, ...]], ...]

        enterprises_with_critical_alarms = dict()
        count = 0

        for result in results:
            ent_name = result[0]
            alarms = result[1]
            if len(alarms) > 0:
                enterprises_with_critical_alarms[ent_name] = alarms
                count += 1

        enterprises_with_critical_alarms['total_enterprises_with_alarms'] = count

        return enterprises_with_critical_alarms


    # Setup query
    vsd_query = setup_vsd_query_tool(VSD_URL)

    # Perform queries
    domain_dict, domain_dict_agg = get_subnetwork_usage(vsd_query)
    enterprises_with_critical_alarms = get_enterprises_with_alarms(vsd_query)

