## Feature Template: NSG Access Port
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
(example)$ metroae config create user-data.yml
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
(example)$ metroae config create user-data.yml
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
