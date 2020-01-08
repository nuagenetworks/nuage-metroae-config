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
*underlay_name:* name of the network to be used as the underlay tag.<br>
*description:* optional description of the underlay network.<br>


#### Restrictions
**create:**
* Underlay tags must be unique.

**revert:**
* Cannot revert an underlay tag that is being used by a NSG.

#### Examples

##### Creating a Single Underlay
This example configures a single underlay tag. nsg-infrastructure-single-underlay.yaml
```
- template: Underlay
  values:
    - underlay_name: Underlay-MPLS-1
      description: Underlay Tag for MPLS Provider 1

```
```
[metroae-user@metroae-host]# metroae config create nsg-infrastructure-single-underlay.yaml
Device: Nuage Networks VSD 5.4.1
    Underlay
        name = 'Underlay-MPLS-1'
        description = 'Underlay Tag for MPLS Provider 1'

```

##### Creating Multiple Underlays with a Single Template
This example configures three underlays with a single user data template.  nsg-infrastructure-multiple-underlay.yaml
```
- template: Underlay
  values:
    - underlay_name: Underlay-MPLS-1
      description: Underlay Tag for MPLS Provider 1
    - underlay_name: Underlay-MPLS-2
      description: Underlay Tag for MPLS Provider 2
    - underlay_name: Underlay-Internet-1
      decription: Underlay Tag for Internet Provider 1

```
```
[metroae-user@metroae-host]# metroae config create nsg-infrastructure-multiple-underlay.yaml
Device: Nuage Networks VSD 5.4.1
    Underlay
        name = 'Underlay-MPLS-1'
        description = 'Underlay Tag for MPLS Provider 1'
    Underlay
        name = 'Underlay-MPLS-2'
        description = 'Underlay Tag for MPLS Provider 2'
    Underlay
        name = 'Underlay-Internet-1'
        description = 'Underlay Underlay-Internet-1'

```
