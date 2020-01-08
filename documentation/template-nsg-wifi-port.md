## Feature Template: Wifi Port
#### Description
Define a Wifi Port on an nsg instance within an enterprise

#### Usage
A service provider or enterprise can deploy WiFi-enabled NSGs in branch locations to provide Access Point (AP) capabilities. Wifi Port template lets you create the Wifi Port on the NSG

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/wifi_port.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define a Wifi Port on an nsg instance within an enterprise
- template: Wifi Port
  values:
    - nsg_name: ""                             # (reference) name of the nsg where wifi port will be created.
      enterprise_name: ""                      # (reference) name of the enterpise where nsg exists.
      wifi_port_name: ""                       # (string) name of the wifi port.
      description: ""                          # (opt string) optional description of the wifi port.
      wifi_band: 2.4GHz                        # (['2.4GHz', '5.0GHz']) frequency band for wifi port. defaults to 2.4GHz.
      country_code: AT                         # (opt ['AT', 'AU', 'BE', 'BR', 'CA', 'CH', 'CN', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GR', 'HK', 'HU', 'ID', 'IE', 'IL', 'IN', 'IT', 'JP', 'KR', 'LT', 'LU', 'LV', 'MY', 'NL', 'NO', 'NZ', 'PH', 'PL', 'PT', 'SE', 'SG', 'SI', 'SK', 'TH', 'TW', 'US', 'ZA']) country where wifi is operated. defaults to US.
      wifi_mode: a                             # (['a', 'a/ac', 'a/n', 'a/n/ac', 'b/g', 'b/g/n']) defaults to 'a'.
      frequency_channel: 0                     # (opt integer 0..14, 36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165) channel for wifi frequency. defaults to 36.
      generic_config: ""                       # (opt string) include those attributes that are not essential for beaconing as akey value pair.

```

#### Parameters
*nsg_name:* name of the nsg where wifi port will be created.<br>
*enterprise_name:* name of the enterpise where nsg exists.<br>
*wifi_port_name:* name of the wifi port.<br>
*description:* optional description of the wifi port.<br>
*wifi_band:* frequency band for wifi port. defaults to 2.4GHz.<br>
*country_code:* country where wifi is operated. defaults to US.<br>
*wifi_mode:* defaults to 'a'.<br>
*frequency_channel:* channel for wifi frequency. defaults to 36.<br>
*generic_config:* include those attributes that are not essential for beaconing as akey value pair.<br>


#### Restrictions
**create:**
* NSG must pre exist.
* Only one Wifi Port per NSG.

**revert:**
* Cannot revert a Wifi Port when it is attached as bridge port to a subnet in L3 Domain.

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
[metroae-user@metroae-host]# metroae config create nsg-wifi-port.yaml
Device: Nuage Networks VSD 5.4.1
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
    - template: Access Port
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
