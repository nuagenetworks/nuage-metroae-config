## Feature Template: Policy Group
#### Description
Create a policy group

#### Usage
(documentation missing)

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/policy_group.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create a policy group
- template: Policy Group
  values:
    - policy_group_name: ""                    # (string)
      policy_type: HARDWARE                    # (['HARDWARE', 'SOFTWARE'])
      enterprise_name: ""                      # (reference)
      domain_name: ""                          # (reference)

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
policy_group_name | required | string | 
policy_type | required | choice | 
enterprise_name | required | reference | 
domain_name | required | reference | 


#### Restrictions
