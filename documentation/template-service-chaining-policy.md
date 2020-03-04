## Feature Template: Service Chaining Policy
#### Description
Define redirection targets and the forwarding policies using Service Chaining Policy template.

#### Usage
Service providers need to be able to steer traffic to a number of service functions such as firewalls, load balancers, NAT, and IPS/IDS systems within their datacenter or service provider PoP networks. Organizations want the ability to specify Virtual Network Functions (VNFs) or Physical Network Functions (PNFs) and their sequence, so service functions can be added or removed seamlessly without requiring changes to the
underlying network infrastructure. This network sequencing of service functions is known as service chaining. It is accomplished using Policy-Based Routing. Using Service Chaining Policy template, users can define policies and entries associated to these policies to steer the traffic to a specific target.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/service_chaining.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define redirection targets and the forwarding policies using Service Chaining Policy template.
- template: Service Chaining Policy
  values:
    - enterprise_name: ""                      # (reference) enterpise name where Redirection target will be created.
      domain_name: ""                          # (reference) l3 Domain where Redirection target will be created.
      chaining_policy_name: ""                 # (string) name of the redirection target.
      policy_priority: 0                       # (integer) priority of the policy in ascending order.
      active: False                            # (boolean) enable or disable the Security Policy.
      description: ""                          # (opt string) optional description for redirection target.
      endpoint_type: l3                        # (['l3', 'none', 'nsg_vnf', 'virtual_wire']) endpoint for service redirection target. defaults to L3.
      location_type: any                       # (['any', 'subnet', 'zone']) origination grouping for traffic in the entry.
      location_name: ""                        # (opt reference) name of the object for the source ie. Zone name, Subnet name.
      zone_name: ""                            # (opt reference) needed when location_type or net_type is set to subnet.
      network_type: any                        # (['any', 'subnet', 'zone']) destination grouping for traffic in the entry.
      network_name: ""                         # (reference) name of the object for the destination ie. Zone name, Subnet name.
      entry_priority: 0                        # (integer) priority of the policy entry in ascending order.
      protocol: ""                             # (string) well-known Protocol number or name of the traffic for the entry.
      source_port: ""                          # (string) protocol Source port (required for all but applicable to TCP/UDP only).
      destination_port: ""                     # (string) protocol Destination port (required for all applicable to TCP/UDP only).
      ether_type: ipv4                         # (opt ['ipv4', 'ipv6']) IPv4 (0x0800) or IPv6 (0x86DD), defaults to IPv4.
      dscp: ""                                 # (opt string) optional DSCP value to match in the IP header to identify traffic matching the rule. Defaults to all DSCP value.
      action: forward                          # (['forward', 'drop']) action to take on any packets matching the rule being either to Allow (forward) or Deny (drop) matching traffic.
      flow_logging_enabled: False              # (boolean) enable syslog logging of packets match ACL entry.
      stats_logging_enabled: False             # (boolean) enable the collection of stats on ACL hits for this entry.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | enterpise name where Redirection target will be created.
domain_name | required | reference | l3 Domain where Redirection target will be created.
chaining_policy_name | required | string | name of the redirection target.
policy_priority | required | integer | priority of the policy in ascending order.
active | required | boolean | enable or disable the Security Policy.
description | optional | string | optional description for redirection target.
endpoint_type | required | choice | endpoint for service redirection target. defaults to L3.
location_type | required | choice | origination grouping for traffic in the entry.
location_name | optional | reference | name of the object for the source ie. Zone name, Subnet name.
zone_name | optional | reference | needed when location_type or net_type is set to subnet.
network_type | required | choice | destination grouping for traffic in the entry.
network_name | required | reference | name of the object for the destination ie. Zone name, Subnet name.
entry_priority | required | integer | priority of the policy entry in ascending order.
protocol | required | string | well-known Protocol number or name of the traffic for the entry.
source_port | required | string | protocol Source port (required for all but applicable to TCP/UDP only).
destination_port | required | string | protocol Destination port (required for all applicable to TCP/UDP only).
ether_type | optional | choice | IPv4 (0x0800) or IPv6 (0x86DD), defaults to IPv4.
dscp | optional | string | optional DSCP value to match in the IP header to identify traffic matching the rule. Defaults to all DSCP value.
action | required | choice | action to take on any packets matching the rule being either to Allow (forward) or Deny (drop) matching traffic.
flow_logging_enabled | required | boolean | enable syslog logging of packets match ACL entry.
stats_logging_enabled | required | boolean | enable the collection of stats on ACL hits for this entry.


#### Restrictions
**create:**
* Enterpise should pre exist.
* Domain should pre exist.
* Policy name should be unique.
* Two policy entries of the same priority cannot exist.
* Current release only supports ingress forwarding policies

**revert:**

