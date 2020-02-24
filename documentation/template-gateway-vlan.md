## Feature Template: Gateway Vlan
#### Description
Create VLANs on a Data Center Gateway (VSG, VRSG, WBX) on Access Ports with the Vlan feature template.

#### Usage
In an overlay network we often have to interconnect to devices or networks that are outside of the overlay. In this case we use a Gateway which can be physical (WBX, VSG) or virtual (VRSG). When using a gateway to breakout from the overlay network we add a gateway access port VLAN to the overlay network. In order to provide the VLAN resource to the overlay network we must first create the VLAN on the Gateway Access port.

The Vlan feature template provides the ability to create one or more VLANs on a Gateway Access Port.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/gateway_vlan.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create VLANs on a Data Center Gateway (VSG, VRSG, WBX) on Access Ports with the Vlan feature template.
- template: Gateway Vlan
  values:
    - gateway_name: ""                         # (reference) describe parameter_1 and its default value.
      port_name: ""                            # (reference) describe parameter_2 and its default value.
      access_vlan_numbers: ""                  # (string) comma separated list of VLANs to be created that can include discontiguous ranges. ie. 1,2,4-10,21-30.
      description: ""                          # (opt string) optional description for the VLAN or group of VLANs being created.
      vlan_enterprise_name: ""                 # (opt reference) optional. It provides the ability to add Enterprise Permissions to the VLAN when it is created.

```

#### Parameters
*gateway_name:* describe parameter_1 and its default value.<br>
*port_name:* describe parameter_2 and its default value.<br>
*access_vlan_numbers:* comma separated list of VLANs to be created that can include discontiguous ranges. ie. 1,2,4-10,21-30.<br>
*description:* optional description for the VLAN or group of VLANs being created.<br>
*vlan_enterprise_name:* optional. It provides the ability to add Enterprise Permissions to the VLAN when it is created.<br>


#### Restrictions
**create:**
* The Gateway and Port on which the VLAN is being created must exist.
* The range of VLANs must fall within the range specified on the Access Port.
* Enterprise Permissions rules follow the same restrictions as detailed in the Enterprise Permission feature template, ie. the Enterprise must exist, cannot add permissions to a VLAN when permissions exist on the Port or the Gateway.

**revert:**
* Vlans cannot be reverted if they are currently attached to a subnet.

#### Examples

##### Configuring a List of VLANs on a Single Port
This example creates a list of VLANs on a single port.  dcgateway-vlan-list-flat.yaml
```
- template: Gateway Vlan
  values:
    gateway_name: 10.0.1.20
    port_name: eth2
    access_vlan_numbers: "11,21,31,41,51"

```
```
(example)$ metroae config create user-data.yml
    [select Gateway (name of 10.0.1.20)]
        [select Port (name of eth2)]
            Vlan
                description = 'Vlan 11'
                value = 11
            Vlan
                description = 'Vlan 21'
                value = 21
            Vlan
                description = 'Vlan 31'
                value = 31
            Vlan
                description = 'Vlan 41'
                value = 41
            Vlan
                description = 'Vlan 51'
                value = 51

```

##### Configuring a Range of VLANs on a Single Port
This example creates multiple ranges of VLANs on a single port along with some non contiguous VLANs from outside the ranges.  dcgateway-vlan-range-flat.yaml
```
- template: Gateway Vlan
  values:
    gateway_name: 10.0.1.20
    port_name: eth2
    access_vlan_numbers: "1,11-15,21-25,31"

```
```
(example)$ metroae config create user-data.yml
    [select Gateway (name of 10.0.1.20)]
        [select Port (name of eth2)]
            Vlan
                description = 'Vlan 1'
                value = 1
            Vlan
                description = 'Vlan 11'
                value = 11
            Vlan
                description = 'Vlan 12'
                value = 12
            Vlan
                description = 'Vlan 13'
                value = 13
            Vlan
                description = 'Vlan 14'
                value = 14
            Vlan
                description = 'Vlan 15'
                value = 15
            Vlan
                description = 'Vlan 21'
                value = 21
            Vlan
                description = 'Vlan 22'
                value = 22
            Vlan
                description = 'Vlan 23'
                value = 23
            Vlan
                description = 'Vlan 24'
                value = 24
            Vlan
                description = 'Vlan 25'
                value = 25
            Vlan
                description = 'Vlan 31'
                value = 31

```

##### Creating VLANs on More Than One Port
This example configures different VLAN ranges on different ports, we are going to use a group data set to define the gateway.  dcgateway-vlan-range-groups.yaml
```
- group: gateway
  values:
    gateway_name: 10.0.1.20
  children:
    - template: Gateway Vlan
      values:
        - port_name: eth2
          access_vlan_numbers: "21-23"
        - port_name: eth3
          access_vlan_numbers: "31-33"

```
```
(example)$ metroae config create user-data.yml
    [select Gateway (name of 10.0.1.20)]
        [select Port (name of eth2)]
            Vlan
                description = 'Vlan 21'
                value = 21
            Vlan
                description = 'Vlan 22'
                value = 22
            Vlan
                description = 'Vlan 23'
                value = 23
        [select Port (name of eth3)]
            Vlan
                description = 'Vlan 31'
                value = 31
            Vlan
                description = 'Vlan 32'
                value = 32
            Vlan
                description = 'Vlan 33'
                value = 33

```

##### Creating VLANs with Enterprise Permissions
This example creates VLANs and assigns Enterprise Permissions at the same time. In the specific example its going to be the same Enterprise for each VLAN.  dcgateway-vlan-range-groups-enterprise-permissions-common.yaml
```
- group: gateway
  values:
    gateway_name: 10.0.1.20
    vlan_enterprise_name: DemoEnterprise
  children:
    - template: Gateway Vlan
      values:
        - port_name: eth2
          access_vlan_numbers: "21"
        - port_name: eth3
          access_vlan_numbers: "31"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [store id to name enterprise_id]
        [store id to name enterprise_id]
    [select Gateway (name of 10.0.1.20)]
        [select Port (name of eth2)]
            Vlan
                description = 'Vlan 21'
                value = 21
                EnterprisePermission
                    permittedEntityDescription = 'Enterprise permission '
                    permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                    name = 'DemoEnterprise'
                    permittedAction = 'USE'
                    permittedEntityName = 'DemoEnterprise'
        [select Port (name of eth3)]
            Vlan
                description = 'Vlan 31'
                value = 31
                EnterprisePermission
                    permittedEntityDescription = 'Enterprise permission '
                    permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                    name = 'DemoEnterprise'
                    permittedAction = 'USE'
                    permittedEntityName = 'DemoEnterprise'

```
