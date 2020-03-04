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

