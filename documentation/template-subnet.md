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
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | name of the enterprise in which to create the subnet.
domain_name | required | reference | name of the L3 domain in which to create the subnet.
zone_name | required | reference | name of the L3 Zone in which to create the subnet.
subnet_name | required | string | name of the subnet being created.
description | optional | string | optional description of the subnet. Defaults to "subnet " + subnet_name
underlay_enabled | optional | choice | optional enablement of underlay access from the overlay. Defaults to disabled if not provided.
address_translation | optional | choice | optional enablement of underlay NAT from the overlay. Defaults to disabled if not provided.
use_global_mac | optional | choice | optional enablement of global mac. Defaults to disabled.
ip_address_type | optional | choice | Type of subnet to be created. ipv4 or dualstack for IPv4 and IPv6. Defaults to ipv4.
ipv4_network | optional | string | IPv4 network CIDR and prefix length of the subnet being created.
ipv4_gateway | optional | string | IPv4 gateway address.
ipv6_network | optional | string | IPv6 CIDR and netmask for the subnet. Only added if "dualstack" ip_address_type.
ipv6_gateway | optional | string | IPv6 gateway address for the subnet. Only added if "dualstack" ip_address_type.
route_target | optional | string | optional static assignment of the RT to be used for the subnet.
route_distinguisher | optional | string | optional static assignment of the RD to be used for the subnet.
vnid | optional | string | optional static assignment of the VNID to be used for the subnet.


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

