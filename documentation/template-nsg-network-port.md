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
*nsg_template_name:* NSG Template that the network port will be added to.<br>
*nsg_name:* <br>
*network_port_name:* name of the Network Port.<br>
*description:* optional description of the network port.<br>
*enterprise_name:* <br>
*physical_name:* assigns which physical (or vnic) port will be used on the NSG. ie. port1, port2.<br>
*speed:* optional speed setting for the port. Defaults to AUTONEGOTIATE.<br>
*mtu:* optional MTU size for the port. Defaults to 1500.<br>
*vlan_range:* optional supported range of VLAN values that can be configured on the port. Defaults to "0-4094"<br>
*vlan_value:* VLAN ID to be used on the uplink, is set to "0" for no VLAN tagging.<br>
*infrastructure_vsc_profile_name:* Each NSG uplink is assigned a pair of VSC's to use as its controller, an Infrastructure VSC Profile is attached to the VLAN.<br>
*ingress_qos_policy_name:* optional attachment of a Ingress QOS policy to be configured on the port.<br>
*egress_qos_policy_name:* optional attachment of a Egress QOS policy to be configured on the port.<br>
*underlay_name:* optional assignment of an underlay tag to use on the uplink. Used when NSG UBR is deployed to interconnect discrete underlay/transport networks.<br>
*uplink_role:* For NSGs with more than one uplink the priority of the uplink is assigned. Default is PRIMARY.<br>
*download_rate_limit:* optional rate limiter that is applied on the download of NSG software updates. Defaults to 8Mbps.<br>
*nat_enabled:* optional enablement of NAT on underlay traffic. Defaults to True.<br>
*route_to_underlay:* optional enablement of direct underlay access. Defaults to True.<br>


#### Restrictions
**create:**
* Supports IPv4 address family only at this time.
* Supports Dynamic/DHCP addressing on uplink only at this time.

**revert:**
* Cannot revert a Network Port that is on a NSG Template in use.

