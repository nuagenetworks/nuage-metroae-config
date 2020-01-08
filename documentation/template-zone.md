## Feature Template: Zone
#### Description
Create a "zone" belonging to an L3 domain in VSD with the Zone feature template.

#### Usage
The Zone feature template creates a Zone within a specified Enterprise and Domain for either SD-DC or SD-WAN use cases. The Zone typically aggregates a number of subnets and is used as an abstraction point for applying security policies.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/zone.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create a "zone" belonging to an L3 domain in VSD with the Zone feature template.
- template: Zone
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which to create the Zone.
      domain_name: ""                          # (reference) name of the L3 domain in which to create the Zone.
      zone_name: ""                            # (string) name of the L3 Zone being created.
      description: ""                          # (opt string) optional description of the zone. Defaults to "Zone " + zone_name.

```

#### Parameters
*enterprise_name:* name of the enterprise in which to create the Zone.<br>
*domain_name:* name of the L3 domain in which to create the Zone.<br>
*zone_name:* name of the L3 Zone being created.<br>
*description:* optional description of the zone. Defaults to "Zone " + zone_name.<br>


#### Restrictions
**create:**
* The Zone feature template is only applicable to L3 domains (no L2).
* In order to create the Zone, the Enterprise and L3 Domain must exist or be created within the same *create* function.

**revert:**
* If vPorts are attached to a subnet, then a zone cannot be reverted.

#### Examples

##### Creating Subnets in an Existing Enterprise and Domain
This example creates two Zones, both in the same Enterprise and Domain. All parameters are listed for each Zone to be created.  network-zone-flat.yaml
```
- template: Zone
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    zone_name: West-Zone
- template: Zone
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    zone_name: East-Zone

```
```
[root@oc-ebc-config-1 feature-samples]# metroae config create network-zone-flat.yaml
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            Zone
                name = 'West-Zone'
                description = 'Zone West-Zone'
            Zone
                name = 'East-Zone'
                description = 'Zone East-Zone'

```

##### Creating Zones in an existing Enterprise and Domain Using Group Inheritance
The common attributes (Enterprise and Domain) are listed under group, and the Zones are created as children.  network-zone-groups.yaml
```
- group: DemoEnterprise
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
  children:
    - template: Zone
      values:
        - zone_name: West-Zone
        - zone_name: East-Zone

```
```
[root@oc-ebc-config-1 feature-samples]# metroae config create network-zone-groups.yaml
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            Zone
                name = 'West-Zone'
                description = 'Zone West-Zone'
            Zone
                name = 'East-Zone'
                description = 'Zone East-Zone'

```
