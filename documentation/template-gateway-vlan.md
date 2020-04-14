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
Name | Required | Type | Description
---- | -------- | ---- | -----------
gateway_name | required | reference | describe parameter_1 and its default value.
port_name | required | reference | describe parameter_2 and its default value.
access_vlan_numbers | required | string | comma separated list of VLANs to be created that can include discontiguous ranges. ie. 1,2,4-10,21-30.
description | optional | string | optional description for the VLAN or group of VLANs being created.
vlan_enterprise_name | optional | reference | optional. It provides the ability to add Enterprise Permissions to the VLAN when it is created.


#### Restrictions
**create:**
* The Gateway and Port on which the VLAN is being created must exist.
* The range of VLANs must fall within the range specified on the Access Port.
* Enterprise Permissions rules follow the same restrictions as detailed in the Enterprise Permission feature template, ie. the Enterprise must exist, cannot add permissions to a VLAN when permissions exist on the Port or the Gateway.

**revert:**
* Vlans cannot be reverted if they are currently attached to a subnet.

