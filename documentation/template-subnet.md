## Feature Template: Subnet
#### Description
Create a subnet belonging to an L3 Domain and Zone in VSD with the Subnet Feature Template.

#### Usage
The Subnet template creates a subnet within a specified Enterprise, Domain and Zone that can be used for either SD-DC or SD-WAN use cases. Depending on the usage the additional features and options on a subnet may change, thus the Subnet feature template provides a minimum definition of attributes, while additional VSD features that may be required on the subnet are provided by standalone templates.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/subnet.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create a subnet belonging to an L3 Domain and Zone in VSD with the Subnet Feature Template.
- template: Subnet
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which to create the subnet.
      domain_name: ""                          # (reference) name of the L3 domain in which to create the subnet.
      zone_name: ""                            # (reference) name of the L3 Zone in which to create the subnet.
      subnet_name: ""                          # (string) name of the subnet being created.
      description: ""                          # (opt string) optional description of the subnet. Defaults to "subnet " + subnet_name
      underlay_enabled: enabled                # (opt ['enabled', 'disabled', 'inherited']) optional enablement of underlay access from the overlay. Defaults to disabled if not provided.
      address_translation: enabled             # (opt ['enabled', 'disabled', 'inherited']) optional enablement of underlay NAT from the overlay. Defaults to disabled if not provided.
      use_global_mac: enabled                  # (opt ['enabled', 'disabled']) optional enablement of global mac. Defaults to disabled.
      ip_address_type: ipv4                    # (opt ['ipv4', 'dualstack']) Type of subnet to be created. ipv4 or dualstack for IPv4 and IPv6. Defaults to ipv4.
      ipv4_network: ""                         # (opt string) IPv4 network CIDR and prefix length of the subnet being created.
      ipv4_gateway: ""                         # (opt string) IPv4 gateway address.
      ipv6_network: ""                         # (opt string) IPv6 CIDR and netmask for the subnet. Only added if "dualstack" ip_address_type.
      ipv6_gateway: ""                         # (opt string) IPv6 gateway address for the subnet. Only added if "dualstack" ip_address_type.
      route_target: ""                         # (opt string) optional static assignment of the RT to be used for the subnet.
      route_distinguisher: ""                  # (opt string) optional static assignment of the RD to be used for the subnet.
      vnid: ""                                 # (opt string) optional static assignment of the VNID to be used for the subnet.

```

#### Parameters
*enterprise_name:* name of the enterprise in which to create the subnet.<br>
*domain_name:* name of the L3 domain in which to create the subnet.<br>
*zone_name:* name of the L3 Zone in which to create the subnet.<br>
*subnet_name:* name of the subnet being created.<br>
*description:* optional description of the subnet. Defaults to "subnet " + subnet_name<br>
*underlay_enabled:* optional enablement of underlay access from the overlay. Defaults to disabled if not provided.<br>
*address_translation:* optional enablement of underlay NAT from the overlay. Defaults to disabled if not provided.<br>
*use_global_mac:* optional enablement of global mac. Defaults to disabled.<br>
*ip_address_type:* Type of subnet to be created. ipv4 or dualstack for IPv4 and IPv6. Defaults to ipv4.<br>
*ipv4_network:* IPv4 network CIDR and prefix length of the subnet being created.<br>
*ipv4_gateway:* IPv4 gateway address.<br>
*ipv6_network:* IPv6 CIDR and netmask for the subnet. Only added if "dualstack" ip_address_type.<br>
*ipv6_gateway:* IPv6 gateway address for the subnet. Only added if "dualstack" ip_address_type.<br>
*route_target:* optional static assignment of the RT to be used for the subnet.<br>
*route_distinguisher:* optional static assignment of the RD to be used for the subnet.<br>
*vnid:* optional static assignment of the VNID to be used for the subnet.<br>


#### Restrictions
**create:**
* The Subnet template is applicable to L3 domains only.
* The Enterprise, L3 Domain and Zone must exist or be created within the same create function in order to create a subnet.
* Gateway IP of the Subnet defaults to x.x.x.1 and is not definable within the template.
* Gateway MAC of the Subnet is auto-generated and is not definable within the template.
* Subnets within a single domain must have a unique name and/or network CIDR.
* Only PAT to underlay is supported as a subnet option. Other subnet features will use dedicated templates (DHCP Address ranges).

**revert:**
* A subnet cannot be reverted if there are attached vPorts.

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

Device: Nuage Networks VSD 5.4.1
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
[root@oc-ebc-config-1 feature-samples]# metroae config create network-subnet-groups.yaml

Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                Subnet
                    underlayEnabled = 'DISABLED'
                    PATEnabled = 'DISABLED'
                    name = 'West-Subnet-001'
                    description = 'Subnet West-Subnet-01'
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
[root@oc-ebc-config-1 feature-samples]# metroae config create network-subnet-groups-zones.yaml

Device: Nuage Networks VSD 5.4.1
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
                    name = 'East-Subnet-011'
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
[root@oc-ebc-config-1 feature-samples]$ metroae config create network-subnet-dualstack.yaml

Device: Nuage Networks VSD 5.4.1
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
