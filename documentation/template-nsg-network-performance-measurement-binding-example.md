## Feature Template: Network Performance Binding
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
