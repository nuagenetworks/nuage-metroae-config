## Feature Template: L2 Domain
#### Description
Create an L2 Domain within a specific enterprise with the L2 Domain feature template.

#### Usage
Use an L2 Domain within VSD to define an overlay network with L2 switching capabilities within a single broadcast domain. The L2 Domain may or may not be aware of any managing DHCP within the L2 Domain.

A VSD L2 Domain template must be created before defining the L2 Domain with VSD. The VSD L2 Domain Template, not to be confused with this feature template defines configuration that is used by the L2 Domain instance, including IPv4 and IPv6 address details if DHCP management is selected.

The L2 Domain Feature allows a new VSD L2 Domain Template to be created automatically for each L2 Domain defined; you do not need to define or interact with the VSD L2 Domain Template. Thus, the interaction between the VSD L2 Domain template and the L2 Domain is fixed when creating an L2 Domain via the configuration engine.

The L2 Domain within VSD has a mix of features enabled, attribute settings and features enabled via attaching objects defined elsewhere. The Domain feature template provides a minimum definition of attributes, while additional VSD features that may be required on the Domain are provided by standalone templates.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/l2_domain.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create an L2 Domain within a specific enterprise with the L2 Domain feature template.
- template: L2 Domain
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which to create the L2 Domain.
      l2_domain_name: ""                       # (string) name of the L2 Domain being created.
      description: ""                          # (opt string) optional description of the L2 Domain. Defaults to "L2 Domain <domain_name>".
      managed_dhcp: False                      # (boolean) enablement of VSD Management DHCP. If set to true then network address information must be provided below.
      use_global_mac: enabled                  # (opt ['enabled', 'disabled']) optional enablement of using the globally-defined GW MAC address. Default to disabled.
      ip_address_type: ipv4                    # (opt ['ipv4', 'dualstack']) if DHCP is set to True, then type of network to create. This can be either IPv4 or Dualstack (IPv4 and IPv6).
      ipv4_network: ""                         # (opt string) IPv4 network to create in CIDR format. ie. 10.0.0.0/24. Must be included if managed_dhcp is set.
      ipv4_gateway: ""                         # (opt string) IPv4 default gateway, typically first valid address within the CIDR. ie. 10.0.0.1. Must be included if managed_dhcp is set.
      ipv6_network: ""                         # (opt string) IPv6 network to create in IPv6 CIDR format. ie. 10::0/64. Must be included if ip_address_type is set to Dualstack.
      ipv6_gateway: ""                         # (opt string) IPv6 default gateway ie. 10::1. Must be included if ip_address_type is set to Dualstack.
      route_target: ""                         # (opt string) optional explicit RT assignment in extended community format. ie. 65000:100. Typically only included in specific use cases (interconnection to DCGW etc).
      route_distinguisher: ""                  # (opt string) optional explicit RD assignment in extended community format. ie. 65000:101. Typically only included in specific use cases (interconnection to DCGW etc).
      vnid: ""                                 # (opt string) optional explicit VXLAN ID assignment.

```

#### Parameters
*enterprise_name:* name of the enterprise in which to create the L2 Domain.<br>
*l2_domain_name:* name of the L2 Domain being created.<br>
*description:* optional description of the L2 Domain. Defaults to "L2 Domain <domain_name>".<br>
*managed_dhcp:* enablement of VSD Management DHCP. If set to true then network address information must be provided below.<br>
*use_global_mac:* optional enablement of using the globally-defined GW MAC address. Default to disabled.<br>
*ip_address_type:* if DHCP is set to True, then type of network to create. This can be either IPv4 or Dualstack (IPv4 and IPv6).<br>
*ipv4_network:* IPv4 network to create in CIDR format. ie. 10.0.0.0/24. Must be included if managed_dhcp is set.<br>
*ipv4_gateway:* IPv4 default gateway, typically first valid address within the CIDR. ie. 10.0.0.1. Must be included if managed_dhcp is set.<br>
*ipv6_network:* IPv6 network to create in IPv6 CIDR format. ie. 10::0/64. Must be included if ip_address_type is set to Dualstack.<br>
*ipv6_gateway:* IPv6 default gateway ie. 10::1. Must be included if ip_address_type is set to Dualstack.<br>
*route_target:* optional explicit RT assignment in extended community format. ie. 65000:100. Typically only included in specific use cases (interconnection to DCGW etc).<br>
*route_distinguisher:* optional explicit RD assignment in extended community format. ie. 65000:101. Typically only included in specific use cases (interconnection to DCGW etc).<br>
*vnid:* optional explicit VXLAN ID assignment.<br>


#### Restrictions
**create:**
* An L2 Domain cannot be created from an existing L2 Domain Template. This is a 1:1 relationship.
* The Enterprise in which the domain is being created must exist or be created within the same create function in order to create the Domain.
* Domains must have a unique name within the Enterprise.
* If managed_dhcp is set to true then IPv4 address information must be included.
* If ip_address_type is set to dualstack then IPv6 address information must be included.

**revert:**
* Cannot revert an L2 Domain that has active vports attached to it.

