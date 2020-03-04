## Feature Template: DHCP Option
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
