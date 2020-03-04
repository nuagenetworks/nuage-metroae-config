## Feature Template: NSG Network Port
#### Description
Define an uplink that will be configured on an NSG Template with the Network Port template.

#### Usage
An NSG Template that will be used to create NSG instances includes the definition of the network ports that will be configured on the NSG. These ports are split between Network (uplinks connecting to the transport network) and Access (ports that connect to the overlay network). The Network Port template is used to define uplink port configuration, which includes the Port attributes (speed, negotiation), VLAN ID to be used and any QOS to be applied. In this version of the template the uplink settings are fixed to Dynamic (DHCP) addressing.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/nsg_network_port.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define an uplink that will be configured on an NSG Template with the Network Port template.
- template: NSG Network Port
  values:
    - nsg_template_name: ""                    # (opt reference) NSG Template that the network port will be added to.
      nsg_name: ""                             # (opt reference)
      network_port_name: ""                    # (string) name of the Network Port.
      description: ""                          # (opt string) optional description of the network port.
      enterprise_name: ""                      # (opt reference)
      physical_name: ""                        # (string) assigns which physical (or vnic) port will be used on the NSG. ie. port1, port2.
      speed: AUTONEGOTIATE                     # (opt ['AUTONEGOTIATE', 'BASET10', 'BASET1000', 'BASETX100', 'BASEX10G']) optional speed setting for the port. Defaults to AUTONEGOTIATE.
      mtu: 0                                   # (opt integer) optional MTU size for the port. Defaults to 1500.
      vlan_range: ""                           # (opt string) optional supported range of VLAN values that can be configured on the port. Defaults to "0-4094"
      vlan_value: 0                            # (integer) VLAN ID to be used on the uplink, is set to "0" for no VLAN tagging.
      infrastructure_vsc_profile_name: ""      # (reference) Each NSG uplink is assigned a pair of VSC's to use as its controller, an Infrastructure VSC Profile is attached to the VLAN.
      ingress_qos_policy_name: ""              # (opt reference) optional attachment of a Ingress QOS policy to be configured on the port.
      egress_qos_policy_name: ""               # (opt reference) optional attachment of a Egress QOS policy to be configured on the port.
      underlay_name: ""                        # (opt reference) optional assignment of an underlay tag to use on the uplink. Used when NSG UBR is deployed to interconnect discrete underlay/transport networks.
      uplink_role: NONE                        # (opt ['NONE', 'PRIMARY', 'SECONDARY', 'TERTIARY', 'UNKNOWN']) For NSGs with more than one uplink the priority of the uplink is assigned. Default is PRIMARY.
      download_rate_limit: 0.0                 # (opt float) optional rate limiter that is applied on the download of NSG software updates. Defaults to 8Mbps.
      nat_enabled: False                       # (opt boolean) optional enablement of NAT on underlay traffic. Defaults to True.
      route_to_underlay: False                 # (opt boolean) optional enablement of direct underlay access. Defaults to True.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
nsg_template_name | optional | reference | NSG Template that the network port will be added to.
nsg_name | optional | reference | 
network_port_name | required | string | name of the Network Port.
description | optional | string | optional description of the network port.
enterprise_name | optional | reference | 
physical_name | required | string | assigns which physical (or vnic) port will be used on the NSG. ie. port1, port2.
speed | optional | choice | optional speed setting for the port. Defaults to AUTONEGOTIATE.
mtu | optional | integer | optional MTU size for the port. Defaults to 1500.
vlan_range | optional | string | optional supported range of VLAN values that can be configured on the port. Defaults to "0-4094"
vlan_value | required | integer | VLAN ID to be used on the uplink, is set to "0" for no VLAN tagging.
infrastructure_vsc_profile_name | required | reference | Each NSG uplink is assigned a pair of VSC's to use as its controller, an Infrastructure VSC Profile is attached to the VLAN.
ingress_qos_policy_name | optional | reference | optional attachment of a Ingress QOS policy to be configured on the port.
egress_qos_policy_name | optional | reference | optional attachment of a Egress QOS policy to be configured on the port.
underlay_name | optional | reference | optional assignment of an underlay tag to use on the uplink. Used when NSG UBR is deployed to interconnect discrete underlay/transport networks.
uplink_role | optional | choice | For NSGs with more than one uplink the priority of the uplink is assigned. Default is PRIMARY.
download_rate_limit | optional | float | optional rate limiter that is applied on the download of NSG software updates. Defaults to 8Mbps.
nat_enabled | optional | boolean | optional enablement of NAT on underlay traffic. Defaults to True.
route_to_underlay | optional | boolean | optional enablement of direct underlay access. Defaults to True.


#### Restrictions
**create:**
* Supports IPv4 address family only at this time.
* Supports Dynamic/DHCP addressing on uplink only at this time.

**revert:**
* Cannot revert a Network Port that is on a NSG Template in use.

