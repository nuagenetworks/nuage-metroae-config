## Feature Template: DHCP Option
#### Description
Add DHCP Options to VSD managed DHCP

#### Usage
DHCP Options can be added to Subnets within L3 Domains or L2 Domains where DHCP is provided by VSD. The options added will be included in the DHCP lease response from the client that requested DHCP lease from the VRS/NSG.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/dhcp_option.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Add DHCP Options to VSD managed DHCP
- template: DHCP Option
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which to create the DHCP Pool.
      domain_name: ""                          # (opt reference) If configuring on L3 Domain the name of the domain in which to add the DHCP Option.
      zone_name: ""                            # (opt reference) If configuring on L3 Domain the name of the zone in which to add the DHCP Option.
      subnet_name: ""                          # (opt reference) If configuring on L3 Domain the name of the subnet in which to add the DHCP Option.
      l2_domain_name: ""                       # (opt reference) If configuring on L2 Domain the name of the domain in which to add the DHCP Option.
      type: 0                                  # (integer) DHCP Option as defined by IANA https://www.iana.org/assignments/bootp-dhcp-parameters/bootp-dhcp-parameters.xhtml.
      values: []                               # (list of string) Value for DHCP Option, format is a list but defined by the Option type.

```

#### Parameters
*enterprise_name:* name of the enterprise in which to create the DHCP Pool.<br>
*domain_name:* If configuring on L3 Domain the name of the domain in which to add the DHCP Option.<br>
*zone_name:* If configuring on L3 Domain the name of the zone in which to add the DHCP Option.<br>
*subnet_name:* If configuring on L3 Domain the name of the subnet in which to add the DHCP Option.<br>
*l2_domain_name:* If configuring on L2 Domain the name of the domain in which to add the DHCP Option.<br>
*type:* DHCP Option as defined by IANA https://www.iana.org/assignments/bootp-dhcp-parameters/bootp-dhcp-parameters.xhtml.<br>
*values:* Value for DHCP Option, format is a list but defined by the Option type.<br>


#### Restrictions
**create:**
* Each DHCP Option can only be configured once per Subnet or L2 Domain.
* Must follow appropriate format for each DHCP Option.
* Must include either L2 Domain or L3 Domain name, zone and subnet.
* Only one option can be created per dataset.

**revert:**
* Revert is not supported for DHCP Options

#### Examples

##### Creating multiple static routes using DHCP Options on a L3 Domain subnet
In this example we are going to set DHCP Option 121 to return multiple classless static route to DHCP clients.  network-dhcp-option-routes.yaml
```
- template: DHCP Option
  values:
    - enterprise_name: DemoEnterprise
      domain_name: L3-Domain-US
      zone_name: West-Zone
      subnet_name: West-Subnet-001
      type: 121
      values: [
"10.0.0.0/16",
"100.1.1.1",
"11.0.0.0/16",
"100.1.1.1"
              ]

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-001)]
                    DHCPOption
                        actualType = 121
                        actualValues = ['10.0.0.0/16', '100.1.1.1', '11.0.0.0/16', '100.1.1.1']
                        type = '79'

```

##### Creating multiple DHCP Options on a L3 Domain subnet
In this example we are going to set a DNS Server, MTU for the Interface and a default GW as DHCP options to return to DHCP clients.  network-dhcp-option-groups.yaml
```
- group: DHCPOptions
  values:
    - enterprise_name: DemoEnterprise
      domain_name: L3-Domain-US
      zone_name: West-Zone
      subnet_name: West-Subnet-001
  children:
    - template: DHCP Option
      values:
        - type: 6
          values: ["172.16.20.1"]
        - type: 26
          values: ["1450"]
        - type: 33
          values: [
          "0.0.0.0",
          "100.1.1.254"
          ]

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-001)]
                    DHCPOption
                        actualType = 6
                        actualValues = ['172.16.20.1']
                        type = '06'
                    DHCPOption
                        actualType = 26
                        actualValues = ['1450']
                        type = '1a'
                    DHCPOption
                        actualType = 33
                        actualValues = ['0.0.0.0', '100.1.1.254']
                        type = '21'

```

##### Creating DHCP Options on a L2 Domain
In this example we will set DHCP Option for Default GW on a L2 Domain.  network-dhcp-option-l2domain.yaml
```
- template: DHCP Option
  values:
    - enterprise_name: DemoEnterprise
      l2_domain_name: L2-Domain-IPv4
      type: 33
      values: [
      "0.0.0.0",
      "1.1.1.254"
       ]

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select L2domain (name of L2-Domain-IPv4)]
            DHCPOption
                actualType = 33
                actualValues = ['0.0.0.0', '1.1.1.254']
                type = '21'

```
