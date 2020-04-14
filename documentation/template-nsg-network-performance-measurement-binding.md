## Feature Template: Network Performance Binding
#### Description
Network Performance Binding Template to define a single or list of L3/L2 domains whose overlay network health will be monitored.

#### Usage
NPM bindings are defined on a L3/L2 domains. NPM bindings attaches the test traffic and scope fo test traffic to monitor the overlay network health between NSGs.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/network_performance_binding.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Network Performance Binding Template to define a single or list of L3/L2 domains whose overlay network health will be monitored.
- template: Network Performance Binding
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise where  NPM binding will be created.
      domain_name: ""                          # (opt reference) name of the L3 or L2 domain where NPM binding will be created.
      domain_name_list: []                     # (opt list of string) list of L3 or L2 domains where NPM binding will be created.
      l2_domain_name: ""                       # (opt reference)
      l2_domain_name_list: []                  # (opt list of string)
      network_performance_measurement_name: "" # (reference) name of the NPM.
      priority: 0                              # (opt integer) An integer value identifying the priority if multiple NPM bindings exist.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | name of the enterprise where  NPM binding will be created.
domain_name | optional | reference | name of the L3 or L2 domain where NPM binding will be created.
domain_name_list | optional | list | list of L3 or L2 domains where NPM binding will be created.
l2_domain_name | optional | reference | 
l2_domain_name_list | optional | list | 
network_performance_measurement_name | required | reference | name of the NPM.
priority | optional | integer | An integer value identifying the priority if multiple NPM bindings exist.


#### Restrictions
**create:**
* Enterpirse should pre exist.
* Network Performance Measurement should pre exist.
* NSGs should pre exist and bootstrapped in the enterprise.
* L3 or L2 domain should pre-exist.

**revert:**
* No restrictions

