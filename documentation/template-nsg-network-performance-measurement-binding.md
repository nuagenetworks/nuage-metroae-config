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
*enterprise_name:* name of the enterprise where  NPM binding will be created.<br>
*domain_name:* name of the L3 or L2 domain where NPM binding will be created.<br>
*domain_name_list:* list of L3 or L2 domains where NPM binding will be created.<br>
*l2_domain_name:* <br>
*l2_domain_name_list:* <br>
*network_performance_measurement_name:* name of the NPM.<br>
*priority:* An integer value identifying the priority if multiple NPM bindings exist.<br>


#### Restrictions
**create:**
* Enterpirse should pre exist.
* Network Performance Measurement should pre exist.
* NSGs should pre exist and bootstrapped in the enterprise.
* L3 or L2 domain should pre-exist.

**revert:**
* No restrictions

#### Examples

##### Creating a NPM binding template with minimal user data
This example creates a NPM Binding Template, with minimal user data.nsg-network-performance-binding-minimal.yaml
```
- template: Network Performance Binding
  values:
    - enterprise_name: "DemoEnterprise"
      network_performance_measurement_name: "initiate-one-way-probe"
      domain_name: "L3-Domain-US"
      l2_domain_name: "L2-Domain"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NetworkPerformanceMeasurement (name of initiate-one-way-probe)]
            [store id to name network_performance_measurement_id]
        [select Domain (name of L3-Domain-US)]
            NetworkPerformanceBinding
                priority = 10
                associatedNetworkMeasurementID = [retrieve network_performance_measurement_id (NetworkPerformanceMeasurement:id)]
        [select L2Domain (name of L2-Domain)]
            NetworkPerformanceBinding
                priority = 10
                associatedNetworkMeasurementID = [retrieve network_performance_measurement_id (NetworkPerformanceMeasurement:id)]

```

##### Creating NPM binding template with multiple domains
This example creates a NPM Binding Template, with multiple L3, L2 domains. nsg-network-performance-binding-multiple-domains.yaml
```
- template: Network Performance Binding
  values:
    - enterprise_name: "DemoEnterprise"
      network_performance_measurement_name: "initiate-one-way-probe"
      domain_name_list: ["L3-Domain-US", "L2-Doamin-NoIP", "L2-Domain-IPv4"]
      priority: 20
      l2_domain_name: "L2-Domain"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NetworkPerformanceMeasurement (name of initiate-one-way-probe)]
            [store id to name network_performance_measurement_id]
        [select Domain (name of L3-Domain-US)]
            NetworkPerformanceBinding
                priority = 20
                associatedNetworkMeasurementID = [retrieve network_performance_measurement_id (NetworkPerformanceMeasurement:id)]
        [select Domain (name of L2-Doamin-NoIP)]
            NetworkPerformanceBinding
                priority = 20
                associatedNetworkMeasurementID = [retrieve network_performance_measurement_id (NetworkPerformanceMeasurement:id)]
        [select Domain (name of L2-Domain-IPv4)]
            NetworkPerformanceBinding
                priority = 20
                associatedNetworkMeasurementID = [retrieve network_performance_measurement_id (NetworkPerformanceMeasurement:id)]
        [select L2Domain (name of L2-Domain)]
            NetworkPerformanceBinding
                priority = 20
                associatedNetworkMeasurementID = [retrieve network_performance_measurement_id (NetworkPerformanceMeasurement:id)]

```
