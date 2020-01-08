## Feature Template: NSGateway Template
#### Description
Define the common form factor (ports) and configuration settings for a set of NSGs with the NSGateway feature template.

#### Usage
Deploying an NSG in the overlay network requires a configuration to be applied to the hardware or virtual NSG. This is achieved by defining the configuration as a Template that can be applied to any number of NSGs that will be deployed to the overlay network. The configuration includes items such as the Ports (Network and Access) that will be enabled on the NSG, how the NSG is accessed, what infrastructure (VSC, Proxy/VSD) the NSG talks to for bootstrapping, control and configuration along with other items. The initial requirement is the definition of the NSG Template which this feature template accomplishes. Once defined then Network and Access Ports can be added to the NSG Template.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/nsgateway_template.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define the common form factor (ports) and configuration settings for a set of NSGs with the NSGateway feature template.
- template: NSGateway Template
  values:
    - nsg_template_name: ""                    # (string) unique name of the NSG Template.
      infrastructure_gateway_profile_name: ""  # (reference) attached Infrastructure Gateway Profile that will be used by the NSG Template.
      description: ""                          # (opt string) optional description for the NSG Template.
      infrastructure_access_profile_name: ""   # (opt reference) attached Infrastructure Access Profile that will be used by the NSG Template.
      ssh_service: DISABLED                    # (opt ['DISABLED', 'ENABLED']) optional enablement of SSH access to the NSG as defined by the Access Profile. Defaults to ENABLED.
      instance_ssh_override: ALLOWED           # (opt ['ALLOWED', 'DISALLOWED']) optional enablement of the NSG instance to override the Template SSH settings. Defaults to DISALLOWED.

```

#### Parameters
*nsg_template_name:* unique name of the NSG Template.<br>
*infrastructure_gateway_profile_name:* attached Infrastructure Gateway Profile that will be used by the NSG Template.<br>
*description:* optional description for the NSG Template.<br>
*infrastructure_access_profile_name:* attached Infrastructure Access Profile that will be used by the NSG Template.<br>
*ssh_service:* optional enablement of SSH access to the NSG as defined by the Access Profile. Defaults to ENABLED.<br>
*instance_ssh_override:* optional enablement of the NSG instance to override the Template SSH settings. Defaults to DISALLOWED.<br>


#### Restrictions
**create:**
* Template name must be unique.
* Attached profiles must exist (infrastructure_gateway_profile_name, infrastructure_access_profile_name).

**revert:**
* Cannot revert a NSG Template that is in use.

#### Examples

##### Creating an NSG Template
This example creates an NSG Template, and attaches the Infrastructure Gateway and Access profiles created in other examples from those feature templates. SSH and SSH Override will both use default values.  nsg-template.yaml
```
- template: NSGateway Template
  values:
    - nsg_template_name: "West-NSG-Type-1"
      infrastructure_gateway_profile_name: "West-NSG-profile-default"
      description: "NSG Templates for West network"
      infrastructure_access_profile_name: "access-key"

```
```
[metroae-user@metroae-host]# metroae config create nsg-template.yaml
Device: Nuage Networks VSD 5.4.1
    [select InfrastructureGatewayProfile (name of West-NSG-profile-default)]
        [store id to name infrastructure_gateway_profile_id]
    [select InfrastructureAccessProfile (name of access-key)]
        [store id to name infrastructure_access_profile_id]
    NSGatewayTemplate
        infrastructureProfileID = [retrieve infrastructure_gateway_profile_id (InfrastructureGatewayProfile:id)]
        instanceSSHOverride = 'DISALLOWED'
        name = 'West-NSG-Type-1'
        infrastructureAccessProfileID = [retrieve infrastructure_access_profile_id (InfrastructureAccessProfile:id)]
        SSHService = 'ENABLED'
        description = 'NSG Templates for West network'

```
