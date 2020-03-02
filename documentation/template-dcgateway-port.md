## Feature Template: DC Gateway Port
#### Description
Create Ports on a Data Center Gateway (VSG, VRSG, WBX) with The Port feature template.

#### Usage
In an overlay network we often have to interconnect to devices or networks that are outside of the overlay. In this case we use a Data Center Gateway which can be physical (WBX, VSG) or virtual (VRSG). When using a gateway to breakout from the overlay network we must have a Gateway Access Port to configure VLANs.

The Port feature template provides the ability to create one or more Access Ports on a Gateway.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/dc_gateway_port.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create Ports on a Data Center Gateway (VSG, VRSG, WBX) with The Port feature template.
- template: DC Gateway Port
  values:
    - gateway_name: ""                         # (reference) name of the gateway to add the port. If dynamically discovered gateway it is typically an IP address.
      port_name: ""                            # (string) name of the port to add to the Gateway. If VRS-G this would typically be the dev name (ie eth2 or ens5), if VSG/WBX then will follow the Slot/MDA/Port convention ie. 1/1/1.
      description: ""                          # (opt string) optional description of the port being created.
      vlan_range: ""                           # (string) range of allowable VLAN ID's that can be configured on the port. If this is a VSG/WBX then will match the VLAN range configured in the "dynamic-services port-profile vlan-range".
      physical_name: ""                        # (string) name of the port on the actual gateway. If VRSG this would typically be the dev name (ie eth2 or ens5), if VSG/WBX then will follow the Slot/MDA/Port convention ie. 1/1/1.
      port_enterprise_name: ""                 # (opt reference) optional. It provides the ability to add Enterprise Permissions to the Port when it is created.

```

#### Parameters
*gateway_name:* name of the gateway to add the port. If dynamically discovered gateway it is typically an IP address.<br>
*port_name:* name of the port to add to the Gateway. If VRS-G this would typically be the dev name (ie eth2 or ens5), if VSG/WBX then will follow the Slot/MDA/Port convention ie. 1/1/1.<br>
*description:* optional description of the port being created.<br>
*vlan_range:* range of allowable VLAN ID's that can be configured on the port. If this is a VSG/WBX then will match the VLAN range configured in the "dynamic-services port-profile vlan-range".<br>
*physical_name:* name of the port on the actual gateway. If VRSG this would typically be the dev name (ie eth2 or ens5), if VSG/WBX then will follow the Slot/MDA/Port convention ie. 1/1/1.<br>
*port_enterprise_name:* optional. It provides the ability to add Enterprise Permissions to the Port when it is created.<br>


#### Restrictions
**create:**
* Only applicable to Gateways in csproot.
* Currently only can be used to create Access Ports (not network or management).
* If the port already exists on the gateway the create will fail. It currently does not update port settings.
* Cannot add a port with the same name as what already exists.

**revert:**
* Ports cannot reverted if it has VLANs that are currently attached to a subnet ie. an active Bridge Port.

