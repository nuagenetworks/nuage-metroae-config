## Feature Template: Underlay
#### Description
Create Underlay tags for NGS disjoint underlays with the Underlay feature template.

#### Usage
When NSGs are deployed across multiple discrete transport networks that need to communicate with each other using an NSG UBR (Underlay Border Router) is used as a gateway between the networks. Each discrete network is allocated an "Underlay" tag which is added to any NSG Uplinks that are connected to that specific transport network.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/underlay.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create Underlay tags for NGS disjoint underlays with the Underlay feature template.
- template: Underlay
  values:
    - underlay_name: ""                        # (string) name of the network to be used as the underlay tag.
      description: ""                          # (opt string) optional description of the underlay network.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
underlay_name | required | string | name of the network to be used as the underlay tag.
description | optional | string | optional description of the underlay network.


#### Restrictions
**create:**
* Underlay tags must be unique.

**revert:**
* Cannot revert an underlay tag that is being used by a NSG.

