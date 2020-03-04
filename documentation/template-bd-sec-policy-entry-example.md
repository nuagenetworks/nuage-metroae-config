## Feature Template: Bidirectional Security Policy Entry
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
