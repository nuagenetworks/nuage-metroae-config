## Feature Template: NSG Access Port
#### Description
Define a port and VLAN on the NSG that connects to an overlay network with the Access Port feature template.

#### Usage
An NSG Template that creates NSG instances includes the definition of the network ports that will be configured on the NSG. These ports are split between Network (uplinks connecting to the transport network) and Access (ports that connect to the overlay network). The Access Port template is used to define access ports and VLANs that can be used to create bridge ports in the overlay network. The configuration includes the Port attributes (speed, negotiation), VLAN ID to be used and any QOS to be applied. In this version of the template the uplink settings are fixed to Dynamic (DHCP) addressing.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/nsg_access_port.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define a port and VLAN on the NSG that connects to an overlay network with the Access Port feature template.
- template: NSG Access Port
  values:
    - nsg_name: ""                             # (opt reference)
      nsg_template_name: ""                    # (opt reference) the NSG Template that the access port will be added to.
      access_port_name: ""                     # (string) name of the access port.
      description: ""                          # (opt string) optional description of the access port.
      enterprise_name: ""                      # (opt reference)
      physical_name: ""                        # (string) used to assign which physical (or vnic) port will be used on the NSG. ie. port3, port4.
      speed: AUTONEGOTIATE                     # (opt ['AUTONEGOTIATE', 'BASET10', 'BASET1000', 'BASETX100', 'BASEX10G']) optional speed setting for the port. Defaults to AUTONEGOTIATE.
      mtu: 0                                   # (opt integer) optional MTU size for the port. Defaults to 1500.
      vlan_range: ""                           # (opt string) optional supported range of VLAN values that can be configured on the port. Defaults to "0-4094"
      vlan_value_list: []                      # (opt list of integer) list of VLANs to be created that can include discontiguous ranges. ie. 101,102,103.
      egress_qos_policy_names: []              # (opt list of reference) optional attachment of a Egress QOS policy to be configured on the port.

```

#### Parameters
*nsg_name:* <br>
*nsg_template_name:* the NSG Template that the access port will be added to.<br>
*access_port_name:* name of the access port.<br>
*description:* optional description of the access port.<br>
*enterprise_name:* <br>
*physical_name:* used to assign which physical (or vnic) port will be used on the NSG. ie. port3, port4.<br>
*speed:* optional speed setting for the port. Defaults to AUTONEGOTIATE.<br>
*mtu:* optional MTU size for the port. Defaults to 1500.<br>
*vlan_range:* optional supported range of VLAN values that can be configured on the port. Defaults to "0-4094"<br>
*vlan_value_list:* list of VLANs to be created that can include discontiguous ranges. ie. 101,102,103.<br>
*egress_qos_policy_names:* optional attachment of a Egress QOS policy to be configured on the port.<br>


#### Restrictions
**create:**
* Access Port name must be unique for each NSG Template.

**revert:**
* Cannot revert a Access Port that is on a NSG Template in use.

#### Examples

##### Create a single Access Port on an NSG Template with Multiple VLANs
This example creates a single access port on an existing NSG Template.  nsg-access-port-flat.yaml
```
- template: NSG Access Port
  values:
    - nsg_template_name: West-NSG-Type-1
      access_port_name: West-NSG-Type1-Access-Port
      physical_name: port3
      vlan_value_list: [101, 102, 103]

```
```
[metroae-user@metroae-host]# metroae config create nsg-access-port-flat.yaml
Device: Nuage Networks VSD 5.4.1
    [select NSGatewayTemplate (name of West-NSG-Type-1)]
        NSPortTemplate
            description = 'Access Port West-NSG-Type1-Access-Port'
            physicalName = 'port3'
            mtu = 1500
            VLANRange = '0-4094'
            portType = 'ACCESS'
            speed = 'AUTONEGOTIATE'
            name = 'West-NSG-Type1-Access-Port'
            VlanTemplate
                description = 'Access Port West-NSG-Type1-Access-Port'
                value = 101
            VlanTemplate
                description = 'Access Port West-NSG-Type1-Access-Port'
                value = 102
            VlanTemplate
                description = 'Access Port West-NSG-Type1-Access-Port'
                value = 103

```

##### Create Multiple Access Ports on an NSG Template with Multiple VLANs each
This example creates two access ports on the NSG Template, each with multiple VLANs with the same QoS policy applied.  nsg-access-port-groups.yaml
```
- group: AccessPorts
  values:
    nsg_template_name: West-NSG-Type-1
    egress_qos_policy_name: West-NSG-Type-1-Access-QoS
  children:
    - template: NSG Access Port
      values:
        - access_port_name: West-NSG-Type1-Access-Port-1
          physical_name: port3
          vlan_value_list: [101, 102, 103]
        - access_port_name: West-NSG-Type1-Access-Port-2
          physical_name: port4
          vlan_value_list: [201, 202, 203]

```
```
[metroae-user@metroae-host]# metroae config create nsg-access-port-groups.yaml
Device: Nuage Networks VSD 5.4.1
    [select NSGatewayTemplate (name of West-NSG-Type-1)]
        NSPortTemplate
            description = 'Access Port West-NSG-Type1-Access-Port-1'
            physicalName = 'port3'
            mtu = 1500
            VLANRange = '0-4094'
            portType = 'ACCESS'
            speed = 'AUTONEGOTIATE'
            name = 'West-NSG-Type1-Access-Port-1'
            VlanTemplate
                description = 'Access Port West-NSG-Type1-Access-Port-1'
                value = 101
            VlanTemplate
                description = 'Access Port West-NSG-Type1-Access-Port-1'
                value = 102
            VlanTemplate
                description = 'Access Port West-NSG-Type1-Access-Port-1'
                value = 103
        NSPortTemplate
            description = 'Access Port West-NSG-Type1-Access-Port-2'
            physicalName = 'port4'
            mtu = 1500
            VLANRange = '0-4094'
            portType = 'ACCESS'
            speed = 'AUTONEGOTIATE'
            name = 'West-NSG-Type1-Access-Port-2'
            VlanTemplate
                description = 'Access Port West-NSG-Type1-Access-Port-2'
                value = 201
            VlanTemplate
                description = 'Access Port West-NSG-Type1-Access-Port-2'
                value = 202
            VlanTemplate
                description = 'Access Port West-NSG-Type1-Access-Port-2'
                value = 203

```
