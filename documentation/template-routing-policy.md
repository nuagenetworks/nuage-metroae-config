## Feature Template: Routing Policy
#### Description
Create a Routing Policy that can be attached to a BGP Neighbor for route filtering and manipulation.

#### Usage
When using BGP Peering it is often necessary to filter or modify the attributes of routes received from and advertised to the peer. We do this by creating a routing policy and attaching that policy to the BGP Neighbor. The Routing Policy feature template provides the ability to create a re-usable Routing Policy in VSD.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/routing_policy.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create a Routing Policy that can be attached to a BGP Neighbor for route filtering and manipulation.
- template: Routing Policy
  values:
    - enterprise_name: ""                      # (reference) name of the Enterprise where the Routing Policy will be created.
      routing_policy_name: ""                  # (string) name of the Routing Policy to be created to be created.
      description: ""                          # (opt string) optional description for the Routing Policy.
      default_action: accept                   # (['accept', 'reject']) default action to take on Routes that do not have a specific match in the policy.
      policy_definition_xml: ""                # (opt string) XML blob for he policy optional vport identification for datacenter or VSG deployment. For multiline page text a YAML multiline Block Style Indicator is required (pipe "|").
      content_type: default                    # (opt ['default', 'netconf_7x50'])

```

#### Parameters
*enterprise_name:* name of the Enterprise where the Routing Policy will be created.<br>
*routing_policy_name:* name of the Routing Policy to be created to be created.<br>
*description:* optional description for the Routing Policy.<br>
*default_action:* default action to take on Routes that do not have a specific match in the policy.<br>
*policy_definition_xml:* XML blob for he policy optional vport identification for datacenter or VSG deployment. For multiline page text a YAML multiline Block Style Indicator is required (pipe "|").<br>
*content_type:* <br>


#### Restrictions
**create:**
* Policy name must be unique within each enterprise.

**revert:**
* Cannot revert a policy that is attached to a BGP Neighbor.

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
