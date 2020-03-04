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

