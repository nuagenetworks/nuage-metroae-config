## Feature Template: NSGateway Template
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
(example)$ metroae config create user-data.yml
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
