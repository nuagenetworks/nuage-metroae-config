## Feature Template: Service Chaining Policy
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
