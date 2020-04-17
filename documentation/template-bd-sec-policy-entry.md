## Feature Template: Bidirectional Security Policy Entry
#### Description
Create security entries in ingress and egress security policies on a specific domain with the Bidirectional Security Policy Entry feature template. This feature template automatically creates both ingress and egress rules based on provided data.

#### Usage
Security Policies are used in VSD to permit, deny and mirror traffic to/from overlay endpoints. Ingress Policies are in relation to traffic received from a VM/container or access network on a VRS host or NSG. Egress Policies are in relation to traffic transmitted to a VM/container or access network. Security Policy entries define the rules that are added to Security Policies to permit/deny traffic within the overlay network.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/bidirectional_security_policy_entry.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create security entries in ingress and egress security policies on a specific domain with the Bidirectional Security Policy Entry feature template. This feature template automatically creates both ingress and egress rules based on provided data.
- template: Bidirectional Security Policy Entry
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise where the Security Policy Entry will be added.
      domain_name: ""                          # (reference) name of the domain where the Security Policy entry will be applied.
      security_policy_name: ""                 # (reference) name of the Security Policy where the entry will be added.
      acl_entry_name: ""                       # (string) name of the Security Policy Entry.
      description: ""                          # (opt string) optional description for the Security Policy Entry.
      location_type: any                       # (['any', 'subnet', 'zone', 'policygroup', 'pgexpression']) origination grouping for traffic in the entry.
      location_name: ""                        # (opt reference) name of the object for the source ie. Zone name, Subnet name.
      zone_name: ""                            # (opt reference)
      network_type: any                        # (['any', 'subnet', 'zone', 'endpoint_domain', 'endpoint_zone', 'endpoint_subnet', 'enterprise_network', 'network_macro_group', 'policygroup', 'pgexpression', 'saas_application_group', 'underlay_internet_policygroup']) destination grouping for traffic in the entry.
      network_name: ""                         # (reference) name of the object for the destination ie. Zone name, Subnet name.
      domain_type: l2domain                    # (['l2domain', 'l3domain'])
      application_signature_name: ""           # (opt reference) for VNS/WAN domains only where DPI is enabled. L7 Application Signature name for traffic match.
      mirror_destination_name: ""              # (opt reference) Name of the vport or mirror destination when mirroring is enabled.
      entry_priority: 0                        # (integer) priority of the policy entry in ascending order.
      protocol: ""                             # (string) well-known Protocol number or name of the traffic for the entry.
      source_port: ""                          # (opt string) protocol Source port (applicable to TCP/UDP only).
      destination_port: ""                     # (opt string) protocol Destination port (applicable to TCP/UDP only).
      ether_type: ipv4                         # (opt ['ipv4', 'ipv6']) IPv4 (0x0800) or IPv6 (0x86DD), defaults to IPv4.
      dscp: ""                                 # (opt string) optional DSCP value to match in the IP header to identify traffic matching the rule. Defaults to all DSCP value.
      action: forward                          # (['forward', 'drop']) action to take on any packets matching the rule being either to Allow (forward) or Deny (drop) matching traffic.
      stateful: False                          # (boolean) policies entries can either be stateful or non-stateful.
      flow_logging_enabled: False              # (boolean) enable syslog logging of packets match ACL entry.
      stats_logging_enabled: False             # (boolean) enable the collection of stats on ACL hits for this entry.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | name of the enterprise where the Security Policy Entry will be added.
domain_name | required | reference | name of the domain where the Security Policy entry will be applied.
security_policy_name | required | reference | name of the Security Policy where the entry will be added.
acl_entry_name | required | string | name of the Security Policy Entry.
description | optional | string | optional description for the Security Policy Entry.
location_type | required | choice | origination grouping for traffic in the entry.
location_name | optional | reference | name of the object for the source ie. Zone name, Subnet name.
zone_name | optional | reference | 
network_type | required | choice | destination grouping for traffic in the entry.
network_name | required | reference | name of the object for the destination ie. Zone name, Subnet name.
domain_type | required | choice | 
application_signature_name | optional | reference | for VNS/WAN domains only where DPI is enabled. L7 Application Signature name for traffic match.
mirror_destination_name | optional | reference | Name of the vport or mirror destination when mirroring is enabled.
entry_priority | required | integer | priority of the policy entry in ascending order.
protocol | required | string | well-known Protocol number or name of the traffic for the entry.
source_port | optional | string | protocol Source port (applicable to TCP/UDP only).
destination_port | optional | string | protocol Destination port (applicable to TCP/UDP only).
ether_type | optional | choice | IPv4 (0x0800) or IPv6 (0x86DD), defaults to IPv4.
dscp | optional | string | optional DSCP value to match in the IP header to identify traffic matching the rule. Defaults to all DSCP value.
action | required | choice | action to take on any packets matching the rule being either to Allow (forward) or Deny (drop) matching traffic.
stateful | required | boolean | policies entries can either be stateful or non-stateful.
flow_logging_enabled | required | boolean | enable syslog logging of packets match ACL entry.
stats_logging_enabled | required | boolean | enable the collection of stats on ACL hits for this entry.


#### Restrictions
**create:**
* The security policy must be defined before an entry can be added.
* Two policy entries of the same priority cannot exist.

