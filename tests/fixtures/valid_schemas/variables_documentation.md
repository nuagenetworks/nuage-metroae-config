## Feature Template: Variables Testing
#### Description
For testing variable validation and schemas

#### Usage
Test usage

#### Template File Name
tests/fixtures/invalid_templates/variables.yaml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# For testing variable validation and schemas
- template: Variables Testing
  values:
    - name: ""                                 # (string) Name field description
      select_name: ""                          # (reference)
      int_as_string: ""                        # (string)
      number: 0                                # (integer)
      floating_point: 0.0                      # (float 0.0..1.0, 98.6)
      true_or_false: False                     # (boolean)
      ipv4_address: 0.0.0.0                    # (opt ipv4)
      ipv6_address: 0::0                       # (opt ipv6)
      any_ip_address: 0.0.0.0                  # (opt ipv4_or_6)
      fruit: APPLE                             # (['APPLE', 'Orange', 'banana'])
      string_list: []                          # (list of string)
      int_list: []                             # (list of integer)
      soda_list: []                            # (list of choice)

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
name | required | string | Name field description
select_name | required | reference | 
int_as_string | required | string | 
number | required | integer | 
floating_point | required | float | 
true_or_false | required | boolean | 
ipv4_address | optional | ipv4 | 
ipv6_address | optional | ipv6 | 
any_ip_address | optional | ipv4_or_6 | 
fruit | required | choice | 
string_list | required | list | 
int_list | required | list | 
soda_list | required | list | 


#### Restrictions
**create:**
* The Zone feature template is only applicable to L3 domains (no L2).
* In order to create the Zone, the Enterprise and L3 Domain must exist or be created within the same *create* function.

**revert:**
* If vPorts are attached to a subnet, then a zone cannot be reverted.

