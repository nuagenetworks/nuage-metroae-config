## Feature Template: ZFB Auto Assignment
#### Description
ZFB Auto Assigment is pre-created matching criteria that allows CSPRoot to auto-assign incoming auto-bootstrapping requests of a NSG to an Enterprise should a match occur.

#### Usage
This function allows the CSPRoot to define match criteria to auto-assign requesting NSGs to an enterprise. NSGs that
get matched will be reflected in the CSPRoot Pending Requests list with an assigned status, and will also be placed in
the enterprise admininstrator's Pending Requests list for review

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/zfb_auto_assignment.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# ZFB Auto Assigment is pre-created matching criteria that allows CSPRoot to auto-assign incoming auto-bootstrapping requests of a NSG to an Enterprise should a match occur.
- template: ZFB Auto Assignment
  values:
    - zfb_auto_assignment_name: ""             # (string) name to identify zfb auto assignment.
      description: ""                          # (opt string) optional description of the zfb auto assignment.
      priority: 0                              # (integer) specifies an order in which multiple attributes must be matched.A lower value implies a higher preference.
      zfb_match_attribute: HOSTNAME            # (['HOSTNAME', 'IP_ADDRESS', 'MAC_ADDRESS', 'NSGATEWAY_ID', 'SERIAL_NUMBER', 'UUID']) match field for identifying NSG when using ZFB.
      zfb_match_attribute_values: []           # (opt list of string) match value of the field selected in zfb_match_attribute when using ZFB.
      enterprise_name: ""                      # (reference) name of the enterprise where incoming auto-bootstraping requests will be assigned.

```

#### Parameters
*zfb_auto_assignment_name:* name to identify zfb auto assignment.<br>
*description:* optional description of the zfb auto assignment.<br>
*priority:* specifies an order in which multiple attributes must be matched.A lower value implies a higher preference.<br>
*zfb_match_attribute:* match field for identifying NSG when using ZFB.<br>
*zfb_match_attribute_values:* match value of the field selected in zfb_match_attribute when using ZFB.<br>
*enterprise_name:* name of the enterprise where incoming auto-bootstraping requests will be assigned.<br>


#### Restrictions
**create:**
* ZFB auto assignment name should be unique.
* Priority number should be unique
* Enteprise should pre-exist.

**revert:**
* No restrictions.

#### Examples

##### Creating a ZFB Auto Assignment.
This example creates a ZFB Auto Assignment for auto-assigning incoming auto-bootstrapping requests to a pre existing Enterprise.nsg-zfb-auto-assignment.yaml
```
- template: ZFB Auto Assignment
  values:
    - enterprise_name: "DemoEnterprise"
      zfb_auto_assignment_name: "West-Branch-001"
      description: "Auto assign West-Branch-001 to DemoEnterprise"
      priority: 10
      zfb_match_attribute: "SERIAL_NUMBER"
      zfb_match_attribute_values: ["NS1550Q0448"]

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [store id to name enterprise_id]
    ZFBAutoAssignment
        name = 'West-Branch-001'
        ZFBMatchAttributeValues = ['NS1550Q0448']
        associatedEnterpriseName = 'DemoEnterprise'
        priority = 10
        associatedEnterpriseID = [retrieve enterprise_id (Enterprise:id)]
        ZFBMatchAttribute = 'SERIAL_NUMBER'
        description = 'Auto assign West-Branch-001 to DemoEnterprise'

```
