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
*enterprise_name:* name of the enterprise in which to create the Domain.<br>
*domain_name:* name of the L3 domain being created.<br>
*description:* optional description of the Domain. Defaults to "Domain <domain_name>".<br>
*underlay_enabled:* optional enablement of underlay access from the overlay. Defaults to disabled.<br>
*flow_collection_enabled:* <br>
*aggregate_flows_enabled:* <br>
*address_translation:* optional enablement of underlay NAT from the overlay. Defaults to disabled.<br>


#### Restrictions
**create:**
* The Domain feature template is restricted to L3 Domains only (no L2).
* In order to create the Domain, the Enterprise in which the domain is being created must exist or be created within the same *create* function.
* Domains must have a unique name within the Enterprise.
* Only PAT to underlay is supported as a Domain option. Other Domain features use dedicated templates (Static Routes)

**revert:**
* If there are attached vPorts on a subnet within the domain, then the Domain cannot be reverted .

#### Examples

##### Creating a Domain with Minimal Data
In this example, the minimum required data is passed to create an L3 domain.  network-domain-default.yaml
```
- template: L3 Domain
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        DomainTemplate
            name = 'template_L3-Domain-US'
            [store id to name domain_template_id]
        Domain
            underlayEnabled = 'DISABLED'
            PATEnabled = 'DISABLED'
            aggregateFlowsEnabled = False
            name = 'L3-Domain-US'
            flowCollectionEnabled = 'DISABLED'
            templateID = [retrieve domain_template_id (DomainTemplate:id)]
            description = 'Domain L3-Domain-US'

```

##### Creating a Domain with PAT to Underlay Enabled
This example adds the parameters required to enable PAT to underlay on the domain.  network-domain-options.yaml
```
- template: L3 Domain
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    descrption: "Domain with PAT to Underlay"
    underlay_enabled: enabled
    address_translation: enabled

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        DomainTemplate
            name = 'template_L3-Domain-US'
            [store id to name domain_template_id]
        Domain
            underlayEnabled = 'ENABLED'
            PATEnabled = 'ENABLED'
            aggregateFlowsEnabled = False
            name = 'L3-Domain-US'
            flowCollectionEnabled = 'DISABLED'
            templateID = [retrieve domain_template_id (DomainTemplate:id)]
            description = 'Domain L3-Domain-US'

```
