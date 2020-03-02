## Feature Template: DC Gateway Port
#### Examples

##### Creating a Single Access Port on a Gateway
This example creates a single access port on a Gateway with a defined VLAN range.  dcgateway-port-flat.yaml
```
- template: DC Gateway Port
  values:
    gateway_name: 10.0.1.20
    vlan_range: 0-4094
    port_name: eth2
    physical_name: eth2

```
```
(example)$ metroae config create user-data.yml
    [select Gateway (name of 10.0.1.20)]
        Port
            portType = 'ACCESS'
            VLANRange = '0-4094'
            description = 'Port eth2'
            physicalName = 'eth2'
            name = 'eth2'
            [store id to name port_template_id]

```

##### Creating Multiple Access Ports on a Gateway all with the Same VLAN Range
This example creates multiple Access Ports each with the VLAN range of 0-4094.  dcgateway-port-groups.yaml
```
- group: Gateway
  values:
    gateway_name: 10.0.1.20
    vlan_range: 0-4094
  children:
    - template: DC Gateway Port
      values:
        - port_name: eth2
          physical_name: eth2
        - port_name: eth3
          physical_name: eth3
        - port_name: eth4
          physical_name: eth4
        - port_name: eth5
          physical_name: eth5

```
```
(example)$ metroae config create user-data.yml
    [select Gateway (name of 10.0.1.20)]
        Port
            portType = 'ACCESS'
            VLANRange = '0-4094'
            description = 'Port eth2'
            physicalName = 'eth2'
            name = 'eth2'
            [store id to name port_template_id]
        Port
            portType = 'ACCESS'
            VLANRange = '0-4094'
            description = 'Port eth3'
            physicalName = 'eth3'
            name = 'eth3'
            [store id to name port_template_id]
        Port
            portType = 'ACCESS'
            VLANRange = '0-4094'
            description = 'Port eth4'
            physicalName = 'eth4'
            name = 'eth4'
            [store id to name port_template_id]
        Port
            portType = 'ACCESS'
            VLANRange = '0-4094'
            description = 'Port eth5'
            physicalName = 'eth5'
            name = 'eth5'
            [store id to name port_template_id]

```

##### Creating Multiple Access Ports on a Gateway all with Different VLAN Ranges
This example creates multiple Access Ports each with its own VLAN range.  dcgateway-port-vlans-groups.yaml
```
- group: Gateway
  values:
    gateway_name: 10.0.1.20
  children:
    - template: DC Gateway Port
      values:
        - port_name: eth2
          physical_name: eth2
          vlan_range: 0,200-299,1000
        - port_name: eth3
          physical_name: eth3
          vlan_range: 0,300-399,1000
        - port_name: eth4
          physical_name: eth4
          vlan_range: 0,400-499,1000
        - port_name: eth5
          physical_name: eth5
          vlan_range: 0,500-599,1000

```
```
(example)$ metroae config create user-data.yml
    [select Gateway (name of 10.0.1.20)]
        Port
            portType = 'ACCESS'
            VLANRange = '0,200-299,1000'
            description = 'Port eth2'
            physicalName = 'eth2'
            name = 'eth2'
            [store id to name port_template_id]
        Port
            portType = 'ACCESS'
            VLANRange = '0,300-399,1000'
            description = 'Port eth3'
            physicalName = 'eth3'
            name = 'eth3'
            [store id to name port_template_id]
        Port
            portType = 'ACCESS'
            VLANRange = '0,400-499,1000'
            description = 'Port eth4'
            physicalName = 'eth4'
            name = 'eth4'
            [store id to name port_template_id]
        Port
            portType = 'ACCESS'
            VLANRange = '0,500-599,1000'
            description = 'Port eth5'
            physicalName = 'eth5'
            name = 'eth5'
            [store id to name port_template_id]

```

##### Creating Access Ports with Enterprise Permissions
This example creates Access Ports and assigns Enterprise Permissions at the same time. In the specific example its going to be the same Enterprise for each Port.  dcgateway-vlan-range-groups-enterprise-permissions-common.yaml
```
- group: Gateway
  values:
    gateway_name: 10.0.1.20
    vlan_range: 0-4094
    port_enterprise_name: DemoEnterprise
  children:
    - template: DC Gateway Port
      values:
        - port_name: eth2
          physical_name: eth2
        - port_name: eth3
          physical_name: eth3

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [store id to name enterprise_id]
        [store id to name enterprise_id]
    [select Gateway (name of 10.0.1.20)]
        Port
            portType = 'ACCESS'
            VLANRange = '0-4094'
            description = 'Port eth2'
            physicalName = 'eth2'
            name = 'eth2'
            [store id to name port_template_id]
            EnterprisePermission
                permittedEntityDescription = 'Enterprise permission '
                permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                name = 'DemoEnterprise'
                permittedAction = 'USE'
                permittedEntityName = 'DemoEnterprise'
        Port
            portType = 'ACCESS'
            VLANRange = '0-4094'
            description = 'Port eth3'
            physicalName = 'eth3'
            name = 'eth3'
            [store id to name port_template_id]
            EnterprisePermission
                permittedEntityDescription = 'Enterprise permission '
                permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                name = 'DemoEnterprise'
                permittedAction = 'USE'
                permittedEntityName = 'DemoEnterprise'

```
