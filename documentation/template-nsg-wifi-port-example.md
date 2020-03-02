## Feature Template: Wifi Port
#### Examples

##### Create a single Wifi Port on a NSG
This example creates a single wifi  port on an existing NSG.  nsg-wifi-port.yaml
```
- template: Wifi Port
  values:
    - enterprise_name: DemoEnterprise
      nsg_name: West-Branch-001
      wifi_port_name: West-Branch-Building1-Wifi-Port
      wifi_band: 5.0GHz
      country_code: US
      wifi_mode: 'a'
      frequency_channel: 36

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of West-Branch-001)]
            WirelessPort
                frequencyChannel = 'CH_36'
                name = 'West-Branch-Building1-Wifi-Port'
                countryCode = 'US'
                physicalName = 'wlan0'
                wifiFrequencyBand = 'FREQ_5_0_GHZ'
                wifiMode = 'WIFI_A'
                portType = 'ACCESS'
                description = 'WIFI Port West-Branch-Building1-Wifi-Port'

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
