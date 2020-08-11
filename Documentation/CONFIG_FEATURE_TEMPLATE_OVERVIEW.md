## MetroAE Config Feature Template Overview



##### What is a Feature Template

Feature Templates are what is used to define the data required to create one or many objects in VSD. They are yaml files that include Jinja2 substitution to normalize the user data provided, and to allow for data defaults and abstraction and call specific metroae config functions that operate against the VSD API.

##### MetroAE Config functions

In order to support the creation and linking of configuration within VSD, MetroAE Config supports a series of key functions. These include - create, select, store and retrieve.

* create - used to define a new object in the VSD
* select - used to find or place the creation of an object within the correct hierarchy
* store and retrieve - used to "lookup" a UUID of an object that will later be used within the create function.

Each feature template calls each of these functions based on the requirements of the feature. For instance if we want to create a new subnet in a L3 Domain we would require the following.  

Enterprise --> Domain --> Zone --> Subnet

The subnet template would define the following

```
  select enterprise  
    select domain   
      select zone  
        create subnet
```

#### Interacting with Templates

As covered in the general overview section MetroAE Config provides methods for checking the supported Feature Templates, outputting sample data required for execution of a template, checking the schema and rendering the support documentation for the specific template.

As a user the sample data and documentation will inform you what is required to create VSD configuration based on the template. One of the first things we have to do when building networks with VSD is create an Enterprise. Lets take a specific look then at the Enterprise Feature Template.

We can dump out the possible configuration options of the template by asking for an example.

```
[caso@metroae-host metroae_data]$ metroae config example "Enterprise"

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

By running example against the feature template name, in this case "Enterprise" we are provided will all the attributes that can be used when creating an Enterprise. We can also see that only a single attribute is mandatory, that being the "enterprise_name". All other attributes are listed as "opt".

We can then define user data based on the example to create an Enterprise in VSD, in this case we will take all the default values and only specify the mandatory attributes.

```
- template: Enterprise
  values:
    enterprise_name: SimpleEnterprise
```

#### Creating VSD Configuration using a Feature Template

To this point we have decided on the object we need to create in the VSD, ie. an Enterprise, we have used MetroAE Config to tell us what parameters are required to create the object and we have defined a set of data based on that. Now we can create the Enterprise in the VSD.

Its important at this point to highlight when creating configuration with feature templates there is no need to tell MetroAE Config during execution what object its creating. We have already defined that when we created the user data above. Before executing lets take a closer look at what the data is actually specifying.

From above here is the data we are going to use:

```
- template: Enterprise
  values:
    enterprise_name: SimpleEnterprise
```

A simple set of 3 lines, but what is this telling the config engine?

```
- template: Enterprise
```

This first line is critical, this is the key that tells the engine to create this set of data based on the "Enterprise" template. The definition of the Enterprise template specifies the actions that need to be performed in the creation of the new object. Now lets take a look at the data we are specifying, this always belongs to "values:"

```
values:
  enterprise_name: SimpleEnterprise
```

In this case we are only specifying an Enterprise name which is "SimpleEnterprise". If we were to want to specify more options when creating the Enterprise they would also be included as part of the value set. For instance the below would define an Enterprise with many more features enabled.

```
- template: Enterprise
  values:
    enterprise_name: DemoEnterprise
    description: "All the good stuff enabled"
    local_as: 65000
    forwarding_classes: [A, B, C, D]
    bgp_enabled: True
    vnf_management_enabled: True
    allow_advanced_qos_configuration: True
    allow_gateway_management: True
    allow_trusted_forwarding_classes: True
    enable_application_performance_management: True
    encryption_management_mode: managed
    floating_ips_quota: 100
```

Now as the data set provided tells the config engine what template to use, and the template has the operations that are required in order to create the object the execution is then a generic "create". Thus when creating configuration in VSD the data always specifies the objects and the user does not need to know specific runtime syntax for the myriad of features that VSD supports.

So lets execute.


#### Where are the Feature Templates

Feature templates are downloaded and installed within your metroae_data directory when you setup MetroAE Config. Assuming things were left with defaults this would be "standard-templates/templates/".



#### Updating Feature Templates

Updating of feature templates is covered in the general config usage section. However it can be executed using "metroae config templates update".

Two items of note when Updating
- The existing standard-template directory will be overwritten when executing updates (see recommendations below on Modifying/Creating templates)
- Internet access will be required. There is nothing special here, we have tried to make the install and setup process as simple as possible. If offline access is necessary the templates can be updated on any  internet connected host and copy the "standard-templates" and "vsd-api-specifications" directories to your offline host.


#### Modifying and Creating Feature Templates

If you want to modify or create a new feature template, we recommend you copy the standard-template directory and modify within that directory. You can then either create and source another rc file that contains the "new" templates directory or pass in the new directory at run time with "-tp" or "--template-path" with the path of your new or modified templates.


#### More information on Feature Templates, Samples and how to use data wisely

##### Template List

Feature templates are expected to be delivered orthogonally to MetroAE releases. The list of templates will be expanding to coverage of more VSD features. The list of templates supported in your current MetroAE setup can be gathered via "metroae config templates list", which provides an alphabetical list of all Feature Templates.

##### Sample Data for Templates

We have provided sample data for each feature template. This sample yaml files are named with the template  category, feature template and any other possible options. In some cases multiple samples for the same template maybe provided.

##### How to Define user data

The MetroAE Config has some powerful features in terms of being able to reduce data required by the user by functions such as inheritance and substitution. The section on [Inheritance](config-inheritance.md) will attempt to describe those.
