## Feature Template: Routing Policy
#### Examples

##### Creating a default Routing Policy that will reject all routes.
This example creates an Routing Policy that can be used for either blocking either the advertisment or reception of all routes. network-bgp-neighbor-ipv4-vmip.yaml
```
- template: Routing Policy
  values:
    - enterprise_name: "DemoEnterprise"
      routing_policy_name: "RejectAll"
      description: "Policy to not advertise or receive routes via BGP"
      default_action: reject

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        RoutingPolicy
            defaultAction = 'REJECT'
            contentType = 'DEFAULT'
            name = 'RejectAll'
            description = 'Policy to not advertise or receive routes via BGP'

```

##### Creating a routing policy to only advertise or receive a default route.
This example creates an Routing Policy that will reject all routes except a default route.  network-bgp-neighbor-ipv4-vportuuid.yaml
```
- template: Routing Policy
  values:
    - enterprise_name: "DemoEnterprise"
      routing_policy_name: "DefaultOnly"
      description: "Policy to only receive or send default route"
      default_action: reject
      policy_definition_xml: |
        <routing-policy xmlns="alu:nuage:bgp:routing:policy">
        <defined-sets>
        <prefix-sets>
        <prefix-set>
        <prefix-set-name>prefix_list_1</prefix-set-name>
        <prefix>
        <ip-prefix>0.0.0.0/0</ip-prefix>
        <masklength-range>exact</masklength-range>
        </prefix>
        </prefix-set>
        </prefix-sets>
        </defined-sets>
        <policy-definition>
        <statements>
        <statement>
        <name>entry_1</name>
        <conditions>
        <match-prefix-set>
        <prefix-set>prefix_list_1</prefix-set>
        </match-prefix-set>
        </conditions>
        <actions>
        <accept-route-set>
        <accept-route/>
        </accept-route-set>
        </actions>
        </statement>
        </statements>
        </policy-definition>
        </routing-policy>

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        RoutingPolicy
            defaultAction = 'REJECT'
            policyDefinition = '<routing-policy xmlns="alu:nuage:bgp:routing:policy">
<defined-sets>
<prefix-sets>
<prefix-set>
<prefix-set-name>prefix_list_1</prefix-set-name>
<prefix>
<ip-prefix>0.0.0.0/0</ip-prefix>
<masklength-range>exact</masklength-range>
</prefix>
</prefix-set>
</prefix-sets>
</defined-sets>
<policy-definition>
<statements>
<statement>
<name>entry_1</name>
<conditions>
<match-prefix-set>
<prefix-set>prefix_list_1</prefix-set>
</match-prefix-set>
</conditions>
<actions>
<accept-route-set>
<accept-route/>
</accept-route-set>
</actions>
</statement>
</statements>
</policy-definition>
</routing-policy>'
            contentType = 'DEFAULT'
            name = 'DefaultOnly'
            description = 'Policy to only receive or send default route'

```
