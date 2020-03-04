## Feature Template: Subnet
#### Examples

##### Creating Subnets in an Existing Enterprise, Domain and Zone(s)
This example creates two subnets, both in the same Enterprise, Domain and Zone. All parameters are listed for each Subnet to be created.  network-subnet-flat.yaml
```
- template: Subnet
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    zone_name: West-Zone
    subnet_name: West-Subnet-001
    ipv4_network: 100.1.1.0/24
    ipv4_gateway: 100.1.1.1
- template: Subnet
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    zone_name: West-Zone
    subnet_name: West-Subnet-002
    ipv4_network: 100.1.2.0/24
    ipv4_gateway: 100.1.2.1
    underlay_enabled: enabled
    address_translation: enabled

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                Subnet
                    underlayEnabled = 'DISABLED'
                    PATEnabled = 'DISABLED'
                    name = 'West-Subnet-001'
                    description = 'Subnet West-Subnet-001'
                    netmask = '255.255.255.0'
                    address = '100.1.1.0'
                    gateway = '100.1.1.1'
                    iptype = 'IPV4'
                Subnet
                    underlayEnabled = 'ENABLED'
                    PATEnabled = 'ENABLED'
                    name = 'West-Subnet-002'
                    description = 'Subnet West-Subnet-002'
                    netmask = '255.255.255.0'
                    address = '100.1.2.0'
                    gateway = '100.1.2.1'
                    iptype = 'IPV4'

```

##### Creating Subnets in an Existing Enterprise, Domain and Zone Using Group Inheritance
In this case the common attributes for where the subnet is created ie. the Enterprise, Domain and Zone is listed in the group and the subnets to be created are listed as children.  network-subnet-groups.yaml
```
- group: DemoEnterprise
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    zone_name: West-Zone
  children:
    - template: Subnet
      values:
        - subnet_name: West-Subnet-001
          ipv4_network: 100.1.1.0/24
          ipv4_gateway: 100.1.1.1
        - subnet_name: West-Subnet-002
          ipv4_network: 100.1.2.0/24
          ipv4_gateway: 100.1.2.1
          underlay_enabled: enabled
          address_translation: enabled

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                Subnet
                    underlayEnabled = 'DISABLED'
                    PATEnabled = 'DISABLED'
                    name = 'West-Subnet-001'
                    description = 'Subnet West-Subnet-001'
                    netmask = '255.255.255.0'
                    address = '100.1.1.0'
                    gateway = '100.1.1.1'
                    iptype = 'IPV4'
                Subnet
                    underlayEnabled = 'ENABLED'
                    PATEnabled = 'ENABLED'
                    name = 'West-Subnet-002'
                    description = 'Subnet West-Subnet-002'
                    netmask = '255.255.255.0'
                    address = '100.1.2.0'
                    gateway = '100.1.2.1'
                    iptype = 'IPV4'

```

##### Creating Subnets in an Existing Enterprise, Domain and Different Zones Using Inheritance
This example is similar to the last example, except in this case we are creating subnets in different zones, but with the same Enterprise and Domain. We move the zone_name parameter from the group into each child. ie. explicitly listed within the subnet.  network-subnet-groups-zones.yaml
```
- group: DemoEnterprise
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
  children:
    - template: Subnet
      values:
        - subnet_name: West-Subnet-001
          zone_name: West-Zone
          ipv4_network: 100.1.1.0/24
          ipv4_gateway: 100.1.1.1
        - subnet_name: West-Subnet-002
          zone_name: West-Zone
          ipv4_network: 100.1.2.0/24
          ipv4_gateway: 100.1.2.1
          underlay_enabled: enabled
          address_translation: enabled
        - subnet_name: East-Subnet-001
          zone_name: East-Zone
          ipv4_network: 200.1.1.0/24
          ipv4_gateway: 200.1.1.1

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                Subnet
                    underlayEnabled = 'DISABLED'
                    PATEnabled = 'DISABLED'
                    name = 'West-Subnet-001'
                    description = 'Subnet West-Subnet-001'
                    netmask = '255.255.255.0'
                    address = '100.1.1.0'
                    gateway = '100.1.1.1'
                    iptype = 'IPV4'
                Subnet
                    underlayEnabled = 'ENABLED'
                    PATEnabled = 'ENABLED'
                    name = 'West-Subnet-002'
                    description = 'Subnet West-Subnet-002'
                    netmask = '255.255.255.0'
                    address = '100.1.2.0'
                    gateway = '100.1.2.1'
                    iptype = 'IPV4'
            [select Zone (name of East-Zone)]
                Subnet
                    underlayEnabled = 'DISABLED'
                    PATEnabled = 'DISABLED'
                    name = 'East-Subnet-001'
                    description = 'Subnet East-Subnet-001'
                    netmask = '255.255.255.0'
                    address = '200.1.1.0'
                    gateway = '200.1.1.1'
                    iptype = 'IPV4'

```

##### Creating a Dual Stack Subnet in an Existing Enterprise, Domain and Zone(s)
This example creates a dualstack IPv4 and IPv6 subnet.  network-subnet-dualstack.yaml
```
- template: Subnet
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    zone_name: West-Zone
    subnet_name: West-Subnet-DualStack
    ip_address_type: dualstack
    ipv4_network: 110.1.1.0/24
    ipv4_gateway: 110.1.1.1
    ipv6_network: 1100:1:1::0/64
    ipv6_gateway: 1100:1:1::1

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                Subnet
                    underlayEnabled = 'DISABLED'
                    PATEnabled = 'DISABLED'
                    name = 'West-Subnet-DualStack'
                    ipv6address = '1100:1:1::0/64'
                    description = 'Subnet West-Subnet-DualStack'
                    netmask = '255.255.255.0'
                    address = '110.1.1.0'
                    ipv6gateway = '1100:1:1::1'
                    gateway = '110.1.1.1'
                    iptype = 'DUALSTACK'

```
