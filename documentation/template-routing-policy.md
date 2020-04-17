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
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | name of the Enterprise where the Routing Policy will be created.
routing_policy_name | required | string | name of the Routing Policy to be created to be created.
description | optional | string | optional description for the Routing Policy.
default_action | required | choice | default action to take on Routes that do not have a specific match in the policy.
policy_definition_xml | optional | string | XML blob for he policy optional vport identification for datacenter or VSG deployment. For multiline page text a YAML multiline Block Style Indicator is required (pipe "|").
content_type | optional | choice | 


#### Restrictions
**create:**
* Policy name must be unique within each enterprise.

**revert:**
* Cannot revert a policy that is attached to a BGP Neighbor.

