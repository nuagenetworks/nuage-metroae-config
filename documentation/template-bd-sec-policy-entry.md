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
*enterprise_name:* name of the enterprise where the Security Policy Entry will be added.<br>
*domain_name:* name of the domain where the Security Policy entry will be applied.<br>
*security_policy_name:* name of the Security Policy where the entry will be added.<br>
*acl_entry_name:* name of the Security Policy Entry.<br>
*description:* optional description for the Security Policy Entry.<br>
*location_type:* origination grouping for traffic in the entry.<br>
*location_name:* name of the object for the source ie. Zone name, Subnet name.<br>
*zone_name:* <br>
*network_type:* destination grouping for traffic in the entry.<br>
*network_name:* name of the object for the destination ie. Zone name, Subnet name.<br>
*domain_type:* <br>
*application_signature_name:* for VNS/WAN domains only where DPI is enabled. L7 Application Signature name for traffic match.<br>
*mirror_destination_name:* Name of the vport or mirror destination when mirroring is enabled.<br>
*entry_priority:* priority of the policy entry in ascending order.<br>
*protocol:* well-known Protocol number or name of the traffic for the entry.<br>
*source_port:* protocol Source port (applicable to TCP/UDP only).<br>
*destination_port:* protocol Destination port (applicable to TCP/UDP only).<br>
*ether_type:* IPv4 (0x0800) or IPv6 (0x86DD), defaults to IPv4.<br>
*dscp:* optional DSCP value to match in the IP header to identify traffic matching the rule. Defaults to all DSCP value.<br>
*action:* action to take on any packets matching the rule being either to Allow (forward) or Deny (drop) matching traffic.<br>
*stateful:* policies entries can either be stateful or non-stateful.<br>
*flow_logging_enabled:* enable syslog logging of packets match ACL entry.<br>
*stats_logging_enabled:* enable the collection of stats on ACL hits for this entry.<br>


#### Restrictions
**create:**
* The security policy must be defined before an entry can be added.
* Two policy entries of the same priority cannot exist.

#### Examples

##### Creating a Single Security Policy Entry
This example creates a single ingress/egress security policy entry in an existing Security Policy. security-bd-sec-policy-entry-flat.yaml
```
- template: Bidirectional Security Policy Entry
  values:
    enterprise_name: DemoEnterprise
    security_policy_name: Intrazone-West
    domain_type: l3domain
    domain_name: L3-Domain-US
    acl_entry_name: dns
    entry_priority: 100
    location_type: zone
    location_name: West-Zone
    network_type: zone
    network_name: West-Zone
    protocol: '17'
    source_port: '*'
    destination_port: '53'
    action: forward
    stateful: True
    flow_logging_enabled: False
    stats_logging_enabled: True

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [store id to name location_id]
                [store id to name network_id]
            [select IngressACLTemplate (name of Intrazone-West)]
                IngressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = True
                    protocol = '17'
                    description = 'dns'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 100
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '53'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False
            [select EgressACLTemplate (name of Intrazone-West)]
                EgressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = True
                    protocol = '17'
                    description = 'dns'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 100
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '53'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False

```

##### Creating Multiple Security Policy Entries Using Groups
This example creates multiple security policy entries in a single security policy using groups to define repeated user data across the discrete entries. Groups are used to define policy entry options, the traffic path and the actual traffic. security-bd-sec-policy-entry-groups.yaml
```
- group: traffic_dns
  values:
    protocol: '17'
    source_port: '*'
    destination_port: '53'

- group: traffic_ssh
  values:
    protocol: '6'
    source_port: '*'
    destination_port: '22'

- group: traffic_http
  values:
    protocol: '6'
    source_port: '*'
    destination_port: '80'

- group: traffic_https
  values:
    protocol: '6'
    source_port: '*'
    destination_port: '443'

- group: traffic_icmp
  values:
    protocol: '1'

- group: traffic_mysql
  values:
    protocol: '6'
    source_port: '*'
    destination_port: '3306'

- group: path_z1
  values:
    location_type: zone
    location_name: West-Zone
    network_type: zone
    network_name: West-Zone

- group: path_z1_any
  values:
    location_type: zone
    location_name: West-Zone
    network_type: any
    network_name: ''

- group: entry_options1
  values:
    stateful: True
    flow_logging_enabled: False
    stats_logging_enabled: True
    dscp: '*'

- group: entry_options2
  values:
    stateful: False
    flow_logging_enabled: False
    stats_logging_enabled: True
    dscp: '*'

- group: policy_entries1
  values:
    enterprise_name: DemoEnterprise
    security_policy_name: Intrazone-West
    domain_type: l3domain
    domain_name: L3-Domain-US
    security_policy_name: Intrazone-West
  children:
    - template: Bidirectional Security Policy Entry
      values:
       -  acl_entry_name: dns
          entry_priority: 100
          $group_traffic: traffic_dns
          $group_path: path_z1_any
          $group_options: entry_options1
          action: forward
       -  acl_entry_name: ssh
          entry_priority: 200
          $group_traffic: traffic_ssh
          $group_path: path_z1
          $group_options: entry_options1
          action: forward
       -  acl_entry_name: http
          entry_priority: 300
          $group_traffic: traffic_http
          $group_path: path_z1
          $group_options: entry_options1
          action: forward
       -  acl_entry_name: https
          entry_priority: 400
          $group_traffic: traffic_https
          $group_path: path_z1
          $group_options: entry_options1
          action: forward
       -  acl_entry_name: icmp
          entry_priority: 1000
          $group_traffic: traffic_icmp
          $group_path: path_z1
          $group_options: entry_options2
          action: forward

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [store id to name location_id]
                [store id to name location_id]
                [store id to name network_id]
                [store id to name location_id]
                [store id to name network_id]
                [store id to name location_id]
                [store id to name network_id]
                [store id to name location_id]
                [store id to name network_id]
            [select IngressACLTemplate (name of Intrazone-West)]
                IngressACLEntryTemplate
                    networkID = ''
                    stateful = True
                    protocol = '17'
                    description = 'dns'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 100
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '53'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ANY'
                    flowLoggingEnabled = False
                IngressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = True
                    protocol = '6'
                    description = 'ssh'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 200
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '22'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False
                IngressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = True
                    protocol = '6'
                    description = 'http'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 300
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '80'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False
                IngressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = True
                    protocol = '6'
                    description = 'https'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 400
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '443'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False
                IngressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = False
                    protocol = '1'
                    description = 'icmp'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 1000
                    locationID = [retrieve location_id (Zone:id)]
                    locationType = 'ZONE'
                    action = 'FORWARD'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False
            [select EgressACLTemplate (name of Intrazone-West)]
                EgressACLEntryTemplate
                    networkID = ''
                    stateful = True
                    protocol = '17'
                    description = 'dns'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 100
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '53'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ANY'
                    flowLoggingEnabled = False
                EgressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = True
                    protocol = '6'
                    description = 'ssh'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 200
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '22'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False
                EgressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = True
                    protocol = '6'
                    description = 'http'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 300
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '80'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False
                EgressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = True
                    protocol = '6'
                    description = 'https'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 400
                    action = 'FORWARD'
                    locationID = [retrieve location_id (Zone:id)]
                    destinationPort = '443'
                    locationType = 'ZONE'
                    sourcePort = '*'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False
                EgressACLEntryTemplate
                    networkID = [retrieve network_id (Zone:id)]
                    stateful = False
                    protocol = '1'
                    description = 'icmp'
                    etherType = '0x0800'
                    statsLoggingEnabled = True
                    DSCP = '*'
                    priority = 1000
                    locationID = [retrieve location_id (Zone:id)]
                    locationType = 'ZONE'
                    action = 'FORWARD'
                    networkType = 'ZONE'
                    flowLoggingEnabled = False

```
