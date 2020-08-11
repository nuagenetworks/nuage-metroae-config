## MetroAE Configuration - Usage

### General Command Structure
Configure VSD via CLI and a local command (metroae) that runs on the host where MetroAE is installed. All MetroAE Config commands are structured with the menu "metroae config"

```
metroae config <action> <input>
```

Entering "metroae config", "metroae config help" or "metroae config --help" we will see the valid actions.

```
[root@metroae-host-ebc config]# metroae config

Nuage Networks Metro Automation Engine (MetroAE) Version: v4.1.0

MetroAE config is a tool that you can use to apply and manage day-zero configurations
for a Nuage Networks VSD. MetroAE config is only available via the MetroAE container.
system inside the MetroAE container. To access metroae config help you can
execute 'metroae config -h'. This will list the positional arguments that are
supported by the tool. To get additional help for each positional argument,
execute 'metroae config <positional argument> -h', e.g.
'metroae config create -h'.

MetroAE config usage:

metroae config                                            Configure VSD
metroae config help                                       Displays the help text for MetroAE configuration
metroae config version                                    Displays the current configuration engine version
metroae config engine update                              Update configuration engine to the latest version
metroae config <positional args>                          Execute configuration engine inside the container

usage: metroae config [-h]

                      {create,revert,validate,update,templates,schema,example,document,version,help}
                      ...

Version 1.0 - This tool reads JSON or Yaml files of templates and user-data to
write a configuration to a VSD or to revert (remove) said configuration.

positional arguments:
  {create,revert,validate,update,templates,schema,example,document,version,help}

optional arguments:
  -h, --help            show this help message and exit
```

We can see from the above that the "metroae config" command is split between engine management commands and Configuration execution commands that interact with the VSD.

#### Engine management commands
These commands are used to interact with the container, check the version and force an update.


```
metroae config help                                       Displays the help text for levistate
metroae config version                                    Displays the current levistate version
metroae config engine update                              Update levistate to the latest version
```

#### Configuration execution commands
These commands are used to prepare, validate and execute configuration on the VSD.

```
metroae config <positional args>                          Execute configuration engine inside the container

usage: metroae config [-h]

                      {create,revert,validate,update,templates,schema,example,document,version,help}
                      ...

Version 1.0 - This tool reads JSON or Yaml files of templates and user-data to
write a configuration to a VSD or to revert (remove) said configuration.

positional arguments:
  {create,revert,validate,update,templates,schema,example,document,version,help}
```


For each of the execution commands, you can type `metroae config <action> --help` to obtain information on the action's input requirements. The required input varies depending on the action.  
example: `metroae config create --help`

```
[root@metroae-host-ebc config]# metroae config create --help
Nuage Networks Metro Automation Engine (MetroAE) Version: v4.1.0

MetroAE config is a tool that you can use to apply and manage day-zero configurations
for a Nuage Networks VSD. MetroAE config is only available via the MetroAE container.
system inside the MetroAE container. To access metroae config help you can
execute 'metroae config -h'. This will list the positional arguments that are
supported by the tool. To get additional help for each positional argument,
execute 'metroae config <positional argument> -h', e.g.
'metroae config create -h'.

MetroAE config usage:


usage: metroae config create [-h] [-tp TEMPLATE_PATH] [--version]
                             [-sv SOFTWARE_VERSION] [-sp SPEC_PATH]
                             [-dp DATA_PATH] [-d DATA] [-v VSD_URL]
                             [-u USERNAME] [-p PASSWORD] [-c CERTIFICATE]
                             [-ck CERTIFICATE_KEY] [-e ENTERPRISE] [--debug]
                             [-lf LOG_FILE] [-ll LOG_LEVEL]
                             [datafiles [datafiles ...]]

positional arguments:
  datafiles             Optional datafile

optional arguments:
  -h, --help            show this help message and exit
  -tp TEMPLATE_PATH, --template-path TEMPLATE_PATH
                        Path containing template files. Can also set using
                        environment variable TEMPLATE_PATH
  --version             Displays version information
  -sv SOFTWARE_VERSION, --software-version SOFTWARE_VERSION
                        Override software version for VSD. Can also set using
                        environment variable SOFTWARE_VERSION
  -sp SPEC_PATH, --spec-path SPEC_PATH
                        Path containing object specifications. Can also set
                        using environment variable VSD_SPECIFICATIONS_PATH
  -dp DATA_PATH, --data-path DATA_PATH
                        Path containing user data. Can also set using
                        environment variable USER_DATA_PATH
  -d DATA, --data DATA  Specify user data as key=value
  -v VSD_URL, --vsd-url VSD_URL
                        URL to VSD REST API. Can also set using environment
                        variable VSD_URL
  -u USERNAME, --username USERNAME
                        Username for VSD. Can also set using environment
                        variable VSD_USERNAME
  -p PASSWORD, --password PASSWORD
                        Password for VSD. Can also set using environment
                        variable VSD_PASSWORD
  -c CERTIFICATE, --certificate CERTIFICATE
                        Certificate used to authenticate with VSD. Can also
                        set using environment variable VSD_CERTIFICATE
  -ck CERTIFICATE_KEY, --certificate-key CERTIFICATE_KEY
                        Certificate Key used to authenticate with VSD. Can
                        also set using environment variable VSD_CERTIFICATE
  -e ENTERPRISE, --enterprise ENTERPRISE
                        Enterprise for VSD. Can also set using environment
                        variable VSD_ENTERPRISE
  --debug               Output in debug mode
  -lf LOG_FILE, --log-file LOG_FILE
                        Write logs to specified file. Can also set using
                        environment variable LOG_FILE
  -ll LOG_LEVEL, --log-level LOG_LEVEL
                        Specify log level (OUTPUT, ERROR, INFO, DEBUG, API)
                        Can also set using environment variable LOG_LEVEL
```


#### Authentication parameters
When interacting with VSD it is required to provide the authentication parameters for the VSD, this includes:  
* VSD URL (-v or --vsd-url)
* VSD Enterprise (-e or --enterprise)
* VSD Username (-u or --username)
* VSD Password (-p or --password)

It is also required that the engine is provided location of the data required to execute. This includes:
* User data location (-dp or --data-path)
* Feature Template location (-tp or --template-path)
* VSD API Specifications location (-sp or --spec-path)

These attributes can be provided as an environment RC file. See Using an [RC File](config-env-variables.md).    


### Config Actions
The supported actions are generally grouped to those that interact with VSD, maintain​ and explore supported feature templates, and validate the metroae version and local host settings.

**Service Configuration Summary**
* create - Creates a new VSD configuration based on the provided user data.
* revert - Reverts a previously created configuration based on the provided user data
* validate - Locally validates that the user data provided meets the feature template requirements
* update - Update configuration in VSD based on provided user data. The update feature is limited in the Features that can be updated and has strict data requirements for its usage. Its provided in this release as a sample of whats possible only.

**Template Summary**
* templates list - List all supported feature templates
* templates update - Pull latest feature templates from repository
* schema - Dump the feature template schema
* example - Dump the required user data for a feature template.
* document - render usage document of a feature template




### Service Configuration Action Details

In all examples unless otherwise specified an RC file is being used and sourced to provide input attributes required for the specified action.

#### create
##### Description
Use create to push a configuration that is based on the provided user data to a VSD. When creating a configuration you must provide the configuration engine with the user data file for configuration, or if a directory is specified then all user data templates in that directory will be used.
##### Usage
The create command is executed by providing a single user data template or a directory.

*metroae config create*  - creates all user-data templates in the default USER_DATA_PATH directory  
*metroae config create \<user-data.yml>* - creates the user-data template specified  
*metroae config create \<user-data.yml> --data-path /path-to/\<new-directory>* - creates the user data template specified that is located in the directory /path-to/\<new-directory>

##### Example
This example creates an enterprise using the user data "enterprise.yml". It calls a single template "Enterprise" and inputs minimal user data.

```
- template: Enterprise
  values:
    enterprise_name: SimpleEnterprise
```

When using the create action as previously outlined you need to provide VSD location and credentials. In the below case they are sourced to metroae command via user environment variables. To create the VSD Enterprise from our user data template list above we use the create action and pass in the name of the user data template ie. `admin-enterprise-default.yaml.`

```
[root@metroae-host-ebc metroae_data]# metroae config create admin-enterprise-default.yml

Device: Nuage Networks VSD 6.0.5
    EnterpriseProfile
        forwardingClass = [{'forwardingClass': 'A', 'loadBalancing': False}, {'forwardingClass': 'B', 'loadBalancing': False}, {'forwardingClass': 'C', 'loadBalancing': False}, {'forwardingClass': 'D', 'loadBalancing': False}, {'forwardingClass': 'E', 'loadBalancing': False}, {'forwardingClass': 'F', 'loadBalancing': False}, {'forwardingClass': 'G', 'loadBalancing': False}, {'forwardingClass': 'H', 'loadBalancing': False}]
        VNFManagementEnabled = False
        description = 'profile for SimpleEnterprise'
        enableApplicationPerformanceManagement = False
        name = 'profile_SimpleEnterprise'
        [store id to name enterprise_profile_id]
    Enterprise
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'SimpleEnterprise'
        description = 'enterprise SimpleEnterprise'
>>> All actions successfully applied
```
The output of the creation action lists attribute level creation, including the default values that will be used where the user-data template did not provide any values. The attributes listed in the output are the attribute names as they appear in VSD API. The enterprise will now be created in VSD.

It is important to note here that the config engine is determining what version of VSD is being configured, from time to time attributes across major versions may change in the API and the engine uses the VSD version to determine what feature template to use. For example if we create the same Enterprise in a 5.4.1 VSD (note that I am overriding the local environment variable and parsing in a different VSD URL in the command line).

```
[root@metroae-host-ebc config]# metroae config create admin-enterprise-default.yml --vsd-url https://20.100.1.103:8443

Device: Nuage Networks VSD 5.4.1
    EnterpriseProfile
        VNFManagementEnabled = False
        allowedForwardingClasses = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        description = 'profile for SimpleEnterprise'
        enableApplicationPerformanceManagement = False
        name = 'profile_SimpleEnterprise'
        [store id to name enterprise_profile_id]
    Enterprise
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'SimpleEnterprise'
        description = 'enterprise SimpleEnterprise'
>>> All actions successfully applied
```

We can see that there are differences between the API attributes for Forwarding Classes.

In 5.4.1 it is specified as

```
        allowedForwardingClasses = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
```

In 6.0.5 it is specified as

```
        forwardingClass = [{'forwardingClass': 'A', 'loadBalancing': False}, {'forwardingClass': 'B', 'loadBalancing': False}, {'forwardingClass': 'C', 'loadBalancing': False}, {'forwardingClass': 'D', 'loadBalancing': False}, {'forwardingClass': 'E', 'loadBalancing': False}, {'forwardingClass': 'F', 'loadBalancing': False}, {'forwardingClass': 'G', 'loadBalancing': False}, {'forwardingClass': 'H', 'loadBalancing': False}]
```

The engine determined based on the VSD version and the feature template what attribute is required, while the user data used to create the Enterprise remains consistent.



#### revert
##### Description
The revert action deletes configuration from the VSD. It must not be mistaken for a catch all delete action as we must have all the user-data present in order to revert the configuration. The same user-data template that was used in the create action will be parsed and used when reverting.

Attempting to revert user data that is not present in VSD results in a silent pass.

##### Usage
The create command is executed by providing a single user data template or a directory.

*metroae config revert*  - validates all user data templates in the default USER_DATA_PATH directory  
*metroae config revert \<user-data.yml>* - validates the user data template specified  
*metraoe config revert \<user-data.yml> --data-path /path-to/\<new-directory>* - validates the user data template specified that is located in the directory /path-to/\<new-directory>

##### Example
Th​is example uses the same user-data from enterprise.yml in the create action but with deleting the DemoEnterprise we created in VSD in the previous example.

```
[root@metroae-host-ebc config]# metroae config revert admin-enterprise-default.yml

Device: Nuage Networks VSD 6.0.5
Revert Enterprise (template: Enterprise)
Revert EnterpriseProfile (template: Enterprise)
>>> All actions successfully applied
```

The output is less verbose as the create, the revert outputs template level actions. The DemoEnterprise will now be deleted in VSD. Note that if the DemoEnterprise had other objects configured within it during the create and revert actions above, and those object block a deletion then the revert would fail.

#### validate
##### Description
The validate action allows you to check the userdata against the feature template requirements and provides you with a list of other default attributes that will be configured.

##### Usage
The validate command is executed by providing a single user data template or a directory.

*metroae config validate*  - validates all user data templates in the default USER_DATA_PATH directory  
*metroae config validate <user-data.yml>* - validates the user data template specified  
*metroae config validate <user-data.yml> --data-path /path-to/\<new-directory>* - validates the user data template specified that is located in the directory /path-to/<new-directory>  

As the validate command only runs locally any VSD specific parameters are ignored.

##### Example
This example uses the `admin-enterprise-default.yaml` user data template from the previous create and revert examples.

With the validate command you can check that the user data in the template is sufficient for the requirements (this of course doesn't validate any conflicts in pre-existing VSD configuration) along with detailing the default values that will be configured that were not specified in the user-data.

```
[root@metroae-host-ebc config]# metroae config validate admin-enterprise-default.yml

Device: Nuage Networks VSD 6.0.5
Configuration
    EnterpriseProfile
        forwardingClass = [{'forwardingClass': 'A', 'loadBalancing': False}, {'forwardingClass': 'B', 'loadBalancing': False}, {'forwardingClass': 'C', 'loadBalancing': False}, {'forwardingClass': 'D', 'loadBalancing': False}, {'forwardingClass': 'E', 'loadBalancing': False}, {'forwardingClass': 'F', 'loadBalancing': False}, {'forwardingClass': 'G', 'loadBalancing': False}, {'forwardingClass': 'H', 'loadBalancing': False}]
        VNFManagementEnabled = False
        description = 'profile for SimpleEnterprise'
        enableApplicationPerformanceManagement = False
        name = 'profile_SimpleEnterprise'
        [store id to name enterprise_profile_id]
    Enterprise
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'SimpleEnterprise'
        description = 'enterprise SimpleEnterprise'

>>> All actions valid
```

In the above case the RC file specified a VSD that is currently running 6.0.5 and thus validation occurred against a version of the Enterprise template that supports 6.0.5. If we want to validate one time against a VSD that is running a different version, say for example our 5.4.1 VSD from earlier besides editing the environment variable we can:

1) Override the VSD URL from the RC file in the command line, here I know that the VSD at the specified URL is running 5.4.1

```
[root@metroae-host-ebc config]# metroae config validate admin-enterprise-default.yml --vsd-url https://20.100.1.103:8443

Device: Nuage Networks VSD 5.4.1
Configuration
    EnterpriseProfile
        VNFManagementEnabled = False
        allowedForwardingClasses = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        description = 'profile for SimpleEnterprise'
        enableApplicationPerformanceManagement = False
        name = 'profile_SimpleEnterprise'
        [store id to name enterprise_profile_id]
    Enterprise
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'SimpleEnterprise'
        description = 'enterprise SimpleEnterprise'

>>> All actions valid
```

2) Specify the version to be used in the command line directly

```
[root@metroae-host-ebc config]# metroae config validate admin-enterprise-default.yml --software-version 5.4.1

Configuration
    EnterpriseProfile
        VNFManagementEnabled = False
        allowedForwardingClasses = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        description = 'profile for SimpleEnterprise'
        enableApplicationPerformanceManagement = False
        name = 'profile_SimpleEnterprise'
        [store id to name enterprise_profile_id]
    Enterprise
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'SimpleEnterprise'
        description = 'enterprise SimpleEnterprise'

>>> All actions valid
```

In the later case we can see that the engine did not determine the version of the VSD and thus the version output is silent, it used the input from the CLI. As shown above in the create example we can again see differences from the first validation using a 6.0.5 VSD vs the later using 5.4.1 we can see a key difference in the attributes that will be pushed to VSD.

5.4.1
```
        allowedForwardingClasses = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
```

6.0.5
```
        forwardingClass = [{'forwardingClass': 'A', 'loadBalancing': False}, {'forwardingClass': 'B', 'loadBalancing': False}, {'forwardingClass': 'C', 'loadBalancing': False}, {'forwardingClass': 'D', 'loadBalancing': False}, {'forwardingClass': 'E', 'loadBalancing': False}, {'forwardingClass': 'F', 'loadBalancing': False}, {'forwardingClass': 'G', 'loadBalancing': False}, {'forwardingClass': 'H', 'loadBalancing': False}]
```



### Template Commands Detail
#### templates list
##### Description
The templates list command provides a list of the standard feature templates that are available on the local host in the current template-path directory. The feature-templates are returned in Alphabetical order.

##### Usage
The templates list command requires only the location of the feature templates.

*metroae config templates list* - provides a list of feature templates available in the default TEMPLATE_PATH directory  
*metroae config templates list --template-path /path-to/\<template-directory>* - provides a list of feature templates available in the directory /path-to/<template-directory"  

##### Example
In this example we are reading in the supported feature templates from the default directory specified in the RC file.
```
[root@metroae-host-ebc config]# metroae config templates list

Application
Application Binding
Application Performance Management
Application Performance Management Binding
Bgp Neighbor
Bidirectional Security Policy
Bidirectional Security Policy Entry
Bridge Port
Captive Portal Profile
Cos Remarking Policy
DC Gateway
DC Gateway Port
DHCP Option
DHCP Pool
DHCPv6 Option
Destination Url
Dscp Remarking Policy
Egress Qos Policy
Enterprise
Enterprise Permission
Gateway Vlan
Infrastructure Access Profile
Infrastructure Gateway Profile
Infrastructure Vsc Profile
Ingress Qos Policy
L2 Domain
L3 Domain
Monitorscope
NSG Access Port
NSG Network Port
NSG Patch Profile
NSG ZFBInfo Download
NSGateway
NSGateway Activate
NSGateway Template
Network Performance Binding
Network Performance Measurement
Performance Monitor
Policy Group
Rate Limiter
Routing Policy
SSID Connection
Service Chaining Policy
Static Route
Subnet
Symmetric Qos Policy
Underlay
VSD User
Wifi Port
ZFB Auto Assignment
Zone
```
#### templates update
##### Description
The feature templates are frequently augmented. As new product features are released or new solutions developed and documented the list of supported and standard templates will not be static. A user must be able to update these templates on demand. To support this the template update command is provided to download the latest set of standard feature templates.

The feature templates and VSD API Specification will be installed in the data directory provided as the mount point for the container.

##### Usage
*metroae config templates update*  - download the latest templates and VSD API Specification

##### Example
```
[root@metroae-host-ebc metroae_data]# ls -la
<snip>
drwxr-xr-x.  5 root   root        72 May 13 15:29 standard-templates
drwxrwxr-x.  2 centos centos   12288 May 13 15:29 vsd-api-specifications
[root@oc-ebc-config-1 metroae]# metroae config templates update
Updating templates...

[root@metroae-host-ebc metroae_data]# ls -la
<snip>
drwxr-xr-x.  5 root   root        72 May 13 18:45 standard-templates
drwxrwxr-x.  2 centos centos   12288 May 13 18:45 vsd-api-specifications
```

#### schema
##### Description
Each supported feature template includes its own schema. The schema defines the required user data and format for the feature. The template schema command provides the ability to dump the feature template schema details without the user having to dig through files manually.

##### Usage
The template schema command requires the input of a single template. If there are a VSD version specific templates due to VSD API changes then we can optionality add the VSD version.

*metroae config schema \<template-name>* - Display the available user data input and requirements for the specified template.

```
[root@metroae-host-ebc metroae_data]# metroae config schema --help
Nuage Networks Metro Automation Engine (MetroAE) Version: v4.1.0

MetroAE config is a tool that you can use to apply and manage day-zero configurations
for a Nuage Networks VSD. MetroAE config is only available via the MetroAE container.
system inside the MetroAE container. To access metroae config help you can
execute 'metroae config -h'. This will list the positional arguments that are
supported by the tool. To get additional help for each positional argument,
execute 'metroae config <positional argument> -h', e.g.
'metroae config create -h'.

MetroAE config usage:


usage: metroae config schema [-h] [-tp TEMPLATE_PATH] [--version]
                             [-sv SOFTWARE_VERSION]
                             [template_names [template_names ...]]

positional arguments:
  template_names        Template names

optional arguments:
  -h, --help            show this help message and exit
  -tp TEMPLATE_PATH, --template-path TEMPLATE_PATH
                        Path containing template files. Can also set using
                        environment variable TEMPLATE_PATH
  --version             Displays version information
  -sv SOFTWARE_VERSION, --software-version SOFTWARE_VERSION
                        Override software version for VSD. Can also set using
                        environment variable SOFTWARE_VERSION
```

##### Example
In the previous examples of Configuration actions we used the Enterprise feature template to create and revert an enterprise in VSD. The user data template that was required to support this is detailed within those examples. However we can use the "template schema" command to detail all the configuration options available to us.

```
[root@metroae-host-ebc metroae_data]# metroae config schema Enterprise

{
  "title": "Schema validator for Nuage Metro Config template Enterprise",
  "$id": "urn:nuage-metro:config:template:enterprise",
  "required": [
    "enterprise_name"
  ],
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "enable_application_performance_management": {
      "type": "boolean",
      "description": "optional enablement of the AAR feature suite. Defaults to disabled.",
      "title": "Enable application performance management"
    },
    "allow_gateway_management": {
      "type": "boolean",
      "description": "optional enablement of gateway management within the Enterprise (not csproot). Defaults to disabled.",
      "title": "Allow gateway management"
    },
    "vnf_management_enabled": {
      "type": "boolean",
      "description": "optional enablement VNF hosting on VNS NSGs. Defaults to disabled.",
      "title": "Vnf management enabled"
    },
    "description": {
      "type": "string",
      "description": "optional description of the enterprise. Defaults to \"enterprise <enterprise_name>\".",
      "title": "Description"
    },
    "enterprise_name": {
      "type": "string",
      "description": "name of the Enterprise being created.",
      "title": "Enterprise name"
    },
    "routing_protocols_enabled": {
      "type": "boolean",
      "description": "optional enablement of Routing protocols in the Enterprise. Defaults to disabled.",
      "title": "Routing protocols enabled"
    },
    "allow_advanced_qos_configuration": {
      "type": "boolean",
      "description": "optional enablement of Advanced QoS features. Defaults to disabled.",
      "title": "Allow advanced qos configuration"
    },
    "forwarding_classes": {
      "items": {
        "enum": [
          "A",
          "B",
          "C",
          "D",
          "E",
          "F",
          "G",
          "H"
        ]
      },
      "type": "array",
      "description": "optional list of enabled forwarding classes. Defaults to all classes.",
      "title": "Forwarding classes"
    },
    "local_as": {
      "type": "integer",
      "title": "Local as"
    },
    "enterprise_profile_name": {
      "type": "string",
      "description": "optional for attaching an existing Organization Profile to the new Enterprise.",
      "title": "Enterprise profile name"
    },
    "dhcp_lease_interval": {
      "type": "integer",
      "description": "optional lease time which is returned in DHCP Offers. Defaults to 24.",
      "title": "Dhcp lease interval"
    },
    "floating_ips_quota": {
      "type": "integer",
      "description": "optional number of floating IPs that can be assigned within the Enterprise. Defaults to 0.",
      "title": "Floating ips quota"
    },
    "encryption_management_mode": {
      "enum": [
        "disabled",
        "managed"
      ],
      "description": "optional enablement of Encryption features within the Enterprise. Defaults to disabled.",
      "title": "Encryption management mode"
    },
    "load_balancing_classes": {
      "items": {
        "enum": [
          "A",
          "B",
          "C",
          "D",
          "E",
          "F",
          "G",
          "H"
        ]
      },
      "type": "array",
      "description": "optional list of load balancing classes.",
      "title": "Load balancing classes"
    },
    "allow_trusted_forwarding_classes": {
      "type": "boolean",
      "description": "optional enablement of DSCP trust. Defaults to disabled.",
      "title": "Allow trusted forwarding classes"
    }
  }
}
```

Again to check the schema against a specific VSD API version add --software-version



#### example

##### Description
Each feature template requires a set of user data to execute a configuration action, the actual user data and format is specifi to the feature template in question. The "template example" command provides a formatted sample of the user data required for a specific feature template. It provides the configuration options, value types and will let you know whether the value is optional (if not optional, then it is mandatory).

##### Usage
The template example command requires the input of a single template. Again if there are VSD version dependencies the software version can be added.

*metroae config example \<template-name>* - Display a sample user-data template for the specified template.

```
[root@metroae-host-ebc metroae_data]# metroae config example --help
Nuage Networks Metro Automation Engine (MetroAE) Version: v4.1.0

MetroAE config is a tool that you can use to apply and manage day-zero configurations
for a Nuage Networks VSD. MetroAE config is only available via the MetroAE container.
system inside the MetroAE container. To access metroae config help you can
execute 'metroae config -h'. This will list the positional arguments that are
supported by the tool. To get additional help for each positional argument,
execute 'metroae config <positional argument> -h', e.g.
'metroae config create -h'.

MetroAE config usage:


usage: metroae config example [-h] [-tp TEMPLATE_PATH] [--version]
                              [-sv SOFTWARE_VERSION]
                              [template_names [template_names ...]]

positional arguments:
  template_names        Template names

optional arguments:
  -h, --help            show this help message and exit
  -tp TEMPLATE_PATH, --template-path TEMPLATE_PATH
                        Path containing template files. Can also set using
                        environment variable TEMPLATE_PATH
  --version             Displays version information
  -sv SOFTWARE_VERSION, --software-version SOFTWARE_VERSION
                        Override software version for VSD. Can also set using
                        environment variable SOFTWARE_VERSION
```

##### Example
This example uses the Enterprise template.

```
[root@metroae-host-ebc metroae_data]# metroae config example Enterprise

# Create "tenant" in VSD with the Enterprise feature template. An Enterprise is sometimes referred to as an Organization, or a Partition in the OpenStack use case.
- template: Enterprise
  values:
    - enterprise_name: ""                      # (string) name of the Enterprise being created.
      description: ""                          # (opt string) optional description of the enterprise. Defaults to "enterprise <enterprise_name>".
      enterprise_profile_name: ""              # (opt reference) optional for attaching an existing Organization Profile to the new Enterprise.
      forwarding_classes: []                   # (opt list of choice) optional list of enabled forwarding classes. Defaults to all classes.
      load_balancing_classes: []               # (opt list of choice) optional list of load balancing classes.
      routing_protocols_enabled: False         # (opt boolean) optional enablement of Routing protocols in the Enterprise. Defaults to disabled.
      local_as: 0                              # (opt integer)
      dhcp_lease_interval: 0                   # (opt integer) optional lease time which is returned in DHCP Offers. Defaults to 24.
      vnf_management_enabled: False            # (opt boolean) optional enablement VNF hosting on VNS NSGs. Defaults to disabled.
      allow_advanced_qos_configuration: False  # (opt boolean) optional enablement of Advanced QoS features. Defaults to disabled.
      allow_gateway_management: False          # (opt boolean) optional enablement of gateway management within the Enterprise (not csproot). Defaults to disabled.
      allow_trusted_forwarding_classes: False  # (opt boolean) optional enablement of DSCP trust. Defaults to disabled.
      enable_application_performance_management: False # (opt boolean) optional enablement of the AAR feature suite. Defaults to disabled.
      encryption_management_mode: disabled     # (opt ['disabled', 'managed']) optional enablement of Encryption features within the Enterprise. Defaults to disabled.
      floating_ips_quota: 0                    # (opt integer) optional number of floating IPs that can be assigned within the Enterprise. Defaults to 0.
```

Per earlier examples, to check against a specific VSD API version add --software-version.

```
[root@metroae-host-ebc metroae_data]# metroae config example Enterprise --software_version 5.4.1

# Create "tenant" in VSD with the Enterprise feature template. An Enterprise is sometimes referred to as an Organization, or a Partition in the OpenStack use case.
- template: Enterprise
  values:
    - enterprise_name: ""                      # (string) name of the Enterprise being created.
      description: ""                          # (opt string) optional description of the enterprise. Defaults to "enterprise <enterprise_name>".
      enterprise_profile_name: ""              # (opt reference) optional for attaching an existing Organization Profile to the new Enterprise.
      forwarding_classes: []                   # (opt list of choice) optional list of enabled forwarding classes. Defaults to all classes.
      routing_protocols_enabled: False         # (opt boolean) optional enablement of Routing protocols in the Enterprise. Defaults to disabled.
      local_as: 0                              # (opt integer)
      dhcp_lease_interval: 0                   # (opt integer) optional lease time which is returned in DHCP Offers. Defaults to 24.
      vnf_management_enabled: False            # (opt boolean) optional enablement VNF hosting on VNS NSGs. Defaults to disabled.
      allow_advanced_qos_configuration: False  # (opt boolean) optional enablement of Advanced QoS features. Defaults to disabled.
      allow_gateway_management: False          # (opt boolean) optional enablement of gateway management within the Enterprise (not csproot). Defaults to disabled.
      allow_trusted_forwarding_classes: False  # (opt boolean) optional enablement of DSCP trust. Defaults to disabled.
      enable_application_performance_management: False # (opt boolean) optional enablement of the AAR feature suite. Defaults to disabled.
      encryption_management_mode: disabled     # (opt ['disabled', 'managed']) optional enablement of Encryption features within the Enterprise. Defaults to disabled.
      floating_ips_quota: 0                    # (opt integer) optional number of floating IPs that can be assigned within the Enterprise. Defaults to 0.
```

#### document

##### Description
Feature templates are provided with embedded documentation that describes the template, provides usage context, parameter/attribute descriptions, requirements and format along with any restrictions. The document command provides a direct way of extracting the documentation for a template. Documentation is provided in md format.

Note that at this point in time template specific documentation is only provided locally when you install and setup metroae config and run the document command.

##### Usage
The document command can be executed on a single template, in which case the rendered document is printed to the terminal, or can be executed against a directory. either via specifying the `template-path` in an RC file or overriding on the command line.

*metroae config document \<template>*  - outputs documentation for the feature template specified   
*metroae config document* - creates md files for all templates in the directory specified in the local environment variables  
*metroae config document --template-path /path-to/\<templates-dir>* - creates md files for all templates in the directory specified in the local environment variables  

##### Example
To generate the documentation for the Enterprise template

```
[root@metroae-host-ebc metroae_data]# metroae config document Enterprise

## Feature Template: Enterprise
#### Description
Create "tenant" in VSD with the Enterprise feature template. An Enterprise is sometimes referred to as an Organization, or a Partition in the OpenStack use case.

#### Usage
Each Enterprise in VSD is defined with an attached Organization Profile which enables additional feature sets in an Enterprise. Typically you would create an Organization Profile, create an Enterprise, then attach the profile to the Enterprise.

The Enterprise feature template automatically creates an Organization Profile for each new Enterprise based on provided user data. Thus, defining Enterprise and enabling advanced features for that Enterprise are handled in one *create* step.

You can create an Enterprise with an existing Organization Profile simply by specifying which Organization Profile (enterprise_profile_name) to use.

#### Template File Name
/metroae_data/standard-templates/templates/enterprise_v600.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.


# Create "tenant" in VSD with the Enterprise feature template. An Enterprise is sometimes referred to as an Organization, or a Partition in the OpenStack use case.
- template: Enterprise
  values:
    - enterprise_name: ""                      # (string) name of the Enterprise being created.
      description: ""                          # (opt string) optional description of the enterprise. Defaults to "enterprise <enterprise_name>".
      enterprise_profile_name: ""              # (opt reference) optional for attaching an existing Organization Profile to the new Enterprise.
      forwarding_classes: []                   # (opt list of choice) optional list of enabled forwarding classes. Defaults to all classes.
      load_balancing_classes: []               # (opt list of choice) optional list of load balancing classes.
      routing_protocols_enabled: False         # (opt boolean) optional enablement of Routing protocols in the Enterprise. Defaults to disabled.
      local_as: 0                              # (opt integer)
      dhcp_lease_interval: 0                   # (opt integer) optional lease time which is returned in DHCP Offers. Defaults to 24.
      vnf_management_enabled: False            # (opt boolean) optional enablement VNF hosting on VNS NSGs. Defaults to disabled.
      allow_advanced_qos_configuration: False  # (opt boolean) optional enablement of Advanced QoS features. Defaults to disabled.
      allow_gateway_management: False          # (opt boolean) optional enablement of gateway management within the Enterprise (not csproot). Defaults to disabled.
      allow_trusted_forwarding_classes: False  # (opt boolean) optional enablement of DSCP trust. Defaults to disabled.
      enable_application_performance_management: False # (opt boolean) optional enablement of the AAR feature suite. Defaults to disabled.
      encryption_management_mode: disabled     # (opt ['disabled', 'managed']) optional enablement of Encryption features within the Enterprise. Defaults to disabled.
      floating_ips_quota: 0                    # (opt integer) optional number of floating IPs that can be assigned within the Enterprise. Defaults to 0.



#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | string | name of the Enterprise being created.
description | optional | string | optional description of the enterprise. Defaults to "enterprise <enterprise_name>".
enterprise_profile_name | optional | reference | optional for attaching an existing Organization Profile to the new Enterprise.
forwarding_classes | optional | list | optional list of enabled forwarding classes. Defaults to all classes.
load_balancing_classes | optional | list | optional list of load balancing classes.
routing_protocols_enabled | optional | boolean | optional enablement of Routing protocols in the Enterprise. Defaults to disabled.
local_as | optional | integer |
dhcp_lease_interval | optional | integer | optional lease time which is returned in DHCP Offers. Defaults to 24.
vnf_management_enabled | optional | boolean | optional enablement VNF hosting on VNS NSGs. Defaults to disabled.
allow_advanced_qos_configuration | optional | boolean | optional enablement of Advanced QoS features. Defaults to disabled.
allow_gateway_management | optional | boolean | optional enablement of gateway management within the Enterprise (not csproot). Defaults to disabled.
allow_trusted_forwarding_classes | optional | boolean | optional enablement of DSCP trust. Defaults to disabled.
enable_application_performance_management | optional | boolean | optional enablement of the AAR feature suite. Defaults to disabled.
encryption_management_mode | optional | choice | optional enablement of Encryption features within the Enterprise. Defaults to disabled.
floating_ips_quota | optional | integer | optional number of floating IPs that can be assigned within the Enterprise. Defaults to 0.


#### Restrictions
**create:**
* You must include a value for enterprise_name in the template.
* The enterprise_name must be unique to the VSD.
* If Routing Protocols are enabled, then a local_as must be included.
* Feature enablement must have entitlement license in place.

**revert:**
* You cannot revert an Enterprise which has domains.
* You cannot revert an Enterprise which has activated NSGs.
```

We can see that the above was for a VSD 6.0.0 version. If we wanted documentation for a 5.4.1 version we can add the `--software-version 5.4.1` to the command.


To generate md files for all templates we can run the document command with no additional output, it will process all templates provided in the template-path env variable.

```

[root@metroae-host-ebc metroae_data]# metroae config document

Generating documentation
Writing Application documentation to documentation/template-application.md
Writing Application Binding documentation to documentation/template-applicationbinding.md
Writing Application Performance Management documentation to documentation/template-applicationperformancemanagement.md
Writing Application Performance Management Binding documentation to documentation/template-applicationperformancemanagementbinding.md
Writing Bgp Neighbor documentation to documentation/template-bgp-neighbor.md
Writing Bidirectional Security Policy documentation to documentation/template-bd-sec-policy.md
Writing Bidirectional Security Policy Entry documentation to documentation/template-bd-sec-policy-entry.md
Writing Bridge Port documentation to documentation/template-bridge-port.md
Writing Captive Portal Profile documentation to documentation/template-nsg-wifi-captive-portal-profile.md
Writing Cos Remarking Policy documentation to documentation/template-cos-remarking-policy.md
Writing DC Gateway documentation to documentation/template-dc-gateway.md
Writing DC Gateway Port documentation to documentation/template-dcgateway-port.md
Writing DHCP Option documentation to documentation/template-dhcp-option.md
Writing DHCP Pool documentation to documentation/template-dhcp-pool.md
Writing DHCPv6 Option documentation to documentation/template-dhcpv6option.md
Writing Destination Url documentation to documentation/template-destination-url.md
Writing Dscp Remarking Policy documentation to documentation/template-dscp-remarking-policy.md
Writing Egress Qos Policy documentation to documentation/template-egress-qos-policy.md
Writing Enterprise documentation to documentation/template-enterprise.md
Writing Enterprise Permission documentation to documentation/template-enterprise-permission.md
Writing Gateway Vlan documentation to documentation/template-gateway-vlan.md
Writing Infrastructure Access Profile documentation to documentation/template-infrastructure-access-profile.md
Writing Infrastructure Gateway Profile documentation to documentation/template-infrastructure-gateway-profile.md
Writing Infrastructure Vsc Profile documentation to documentation/template-infrastructure-vsc-profile.md
Writing Ingress Qos Policy documentation to documentation/template-ingress-qos-policy.md
Writing L2 Domain documentation to documentation/template-l2domain.md
Writing L3 Domain documentation to documentation/template-l3domain.md
Writing Monitorscope documentation to documentation/template-nsg-monitor-scope.md
Writing NSG Access Port documentation to documentation/template-nsg-access-port.md
Writing NSG Network Port documentation to documentation/template-nsg-network-port.md
Writing NSG Patch Profile documentation to documentation/nsgpatchprofile.md
Writing NSG ZFBInfo Download documentation to documentation/template-nsg-iso-download.md
Writing NSGateway documentation to documentation/template-nsg-instance.md
Writing NSGateway Activate documentation to documentation/template-nsg-activate.md
Writing NSGateway Template documentation to documentation/template-nsg-template.md
Writing Network Performance Binding documentation to documentation/template-nsg-network-performance-measurement-binding.md
Writing Network Performance Measurement documentation to documentation/template-nsg-network-performance-measurement.md
Writing Performance Monitor documentation to documentation/template-nsg-performance-monitor.md
Writing Policy Group documentation to documentation/template-policy-group.md
Writing Rate Limiter documentation to documentation/template-rate-limiter.md
Writing Routing Policy documentation to documentation/template-routing-policy.md
Writing SSID Connection documentation to documentation/template-nsg-wifi-ssid.md
Writing Service Chaining Policy documentation to documentation/template-service-chaining-policy.md
Writing Static Route documentation to documentation/template-static-route.md
Writing Subnet documentation to documentation/template-subnet.md
Writing Symmetric Qos Policy documentation to documentation/template-symmetric-qos.md
Writing Underlay documentation to documentation/template-underlay.md
Writing VSD User documentation to documentation/template-vsd-user.md
Writing Wifi Port documentation to documentation/template-nsg-wifi-port.md
Writing ZFB Auto Assignment documentation to documentation/template-nsg-zfb.md
Writing Zone documentation to documentation/template-zone.md
```



### Reduce Command Requirements with an RC File
The configuration engine supports the use of local environment variable in the user shell. Assuming the VSD, templates and VSP API SPEC are not changing locally this reduces the command requirements to the action and a single data input. See the article [Exporting the environment variables using an RC File](config-env-variables.md) for details.

Without using an RC file

```
metroae config create admin-enterprise-default.yaml --template-path /metroae_data/standard-templates/matroae-templates/templates --spec-path /metroae_data/vsd-api-specifications/vsd-api-specifications --data-path /metroae_data/config/ --vsd-url https://20.100.1.103:8443 --username csproot --password csproot --enterprise csp
```

With the use of an RC file

```
metroae create admin-enterprise-default.yaml
```
