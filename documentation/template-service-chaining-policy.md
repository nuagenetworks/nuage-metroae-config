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
*enterprise_name:* enterpise name where Redirection target will be created.<br>
*domain_name:* l3 Domain where Redirection target will be created.<br>
*chaining_policy_name:* name of the redirection target.<br>
*policy_priority:* priority of the policy in ascending order.<br>
*active:* enable or disable the Security Policy.<br>
*description:* optional description for redirection target.<br>
*endpoint_type:* endpoint for service redirection target. defaults to L3.<br>
*location_type:* origination grouping for traffic in the entry.<br>
*location_name:* name of the object for the source ie. Zone name, Subnet name.<br>
*zone_name:* needed when location_type or net_type is set to subnet.<br>
*network_type:* destination grouping for traffic in the entry.<br>
*network_name:* name of the object for the destination ie. Zone name, Subnet name.<br>
*entry_priority:* priority of the policy entry in ascending order.<br>
*protocol:* well-known Protocol number or name of the traffic for the entry.<br>
*source_port:* protocol Source port (required for all but applicable to TCP/UDP only).<br>
*destination_port:* protocol Destination port (required for all applicable to TCP/UDP only).<br>
*ether_type:* IPv4 (0x0800) or IPv6 (0x86DD), defaults to IPv4.<br>
*dscp:* optional DSCP value to match in the IP header to identify traffic matching the rule. Defaults to all DSCP value.<br>
*action:* action to take on any packets matching the rule being either to Allow (forward) or Deny (drop) matching traffic.<br>
*flow_logging_enabled:* enable syslog logging of packets match ACL entry.<br>
*stats_logging_enabled:* enable the collection of stats on ACL hits for this entry.<br>


#### Restrictions
**create:**
* Enterpise should pre exist.
* Domain should pre exist.
* Policy name should be unique.
* Two policy entries of the same priority cannot exist.
* Current release only supports ingress forwarding policies

**revert:**

#### Examples

##### Service chaining policy with minimum data.
This examples creates a redirection target and ingress forwarding policy and its entry. network-service-chaining-policy-minimal.yaml
```
- template: Service Chaining Policy
  values:
    enterprise_name: DemoEnterprise
    chaining_policy_name: Forward-Any-Traffic-To-West-Zone
    domain_name: L3-Domain-US
    policy_priority: 100
    active: False
    endpoint_type: l3
    location_type: any
    network_type: zone
    network_name: West-Zone
    entry_priority: 100
    protocol: '17'
    source_port: '*'
    destination_port: '1153'
    action: forward
    flow_logging_enabled: False
    stats_logging_enabled: True

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [store id to name network_id]
            RedirectionTarget
                endPointType = 'L3'
                description = 'RedirectionTarget target_Forward-Any-Traffic-To-West-Zone'
                name = 'target_Forward-Any-Traffic-To-West-Zone'
            IngressAdvFwdTemplate
                active = False
                priority = 100
                name = 'Forward-Any-Traffic-To-West-Zone'
                description = 'IngressAdvFwdTemplate Forward-Any-Traffic-To-West-Zone'
                IngressAdvFwdEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    protocol = '17'
                    description = 'IngressAdvFwdEntryTemplate Entry_Forward-Any-Traffic-To-West-Zone'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 100
                    action = 'FORWARD'
                    locationID = ''
                    destinationPort = '1153'
                    locationType = 'ANY'
                    sourcePort = '*'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False

```
