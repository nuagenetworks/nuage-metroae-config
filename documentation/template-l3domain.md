## Feature Template: L3 Domain
#### Description
Create an L3 Domain within the specified Enterprise with the Domain feature template.

#### Usage
Use an L3 Domain within VSD to define an overlay network with routing capabilities between the subnets that are defined within the domain.

When defining the L3 Domain within VSD you must create a VSD Domain template first. The VSD Domain template, not to be confused with this feature template, is used to define configuration that is common to all defined domains based on the template.

For the Domain feature a new VSD Domain template is created automatically for each L3 Domain defined; you do not need to define or interact with the VSD Domain template. Thus, the interaction between the VSD Domain template and the L3 Domain is fixed when creating an L3 Domain via the configuration engine. A future release of the Domain Feature template will allow you to link to an existing VSD Domain template.

The L3 Domain within VSD has a mix of attribute settings and features enabled via attached objects defined elsewhere. The Domain feature template provides a minimum definition of attributes; additional VSD features that may be required on the Domain are provided by standalone templates.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/l3_domain.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create an L3 Domain within the specified Enterprise with the Domain feature template.
- template: L3 Domain
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which to create the Domain.
      domain_name: ""                          # (string) name of the L3 domain being created.
      description: ""                          # (opt string) optional description of the Domain. Defaults to "Domain <domain_name>".
      underlay_enabled: enabled                # (opt ['enabled', 'disabled', 'inherited']) optional enablement of underlay access from the overlay. Defaults to disabled.
      flow_collection_enabled: enabled         # (opt ['enabled', 'disabled', 'inherited'])
      aggregate_flows_enabled: False           # (opt boolean)
      address_translation: enabled             # (opt ['enabled', 'disabled', 'inherited']) optional enablement of underlay NAT from the overlay. Defaults to disabled.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | name of the enterprise in which to create the Domain.
domain_name | required | string | name of the L3 domain being created.
description | optional | string | optional description of the Domain. Defaults to "Domain <domain_name>".
underlay_enabled | optional | choice | optional enablement of underlay access from the overlay. Defaults to disabled.
flow_collection_enabled | optional | choice | 
aggregate_flows_enabled | optional | boolean | 
address_translation | optional | choice | optional enablement of underlay NAT from the overlay. Defaults to disabled.


#### Restrictions
**create:**
* The Domain feature template is restricted to L3 Domains only (no L2).
* In order to create the Domain, the Enterprise in which the domain is being created must exist or be created within the same *create* function.
* Domains must have a unique name within the Enterprise.
* Only PAT to underlay is supported as a Domain option. Other Domain features use dedicated templates (Static Routes)

**revert:**
* If there are attached vPorts on a subnet within the domain, then the Domain cannot be reverted .

