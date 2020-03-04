## Feature Template: Network Performance Measurement
#### Examples

##### Creating a NPM template
This example creates a Network Performance Measurement template.nsg-network-performance-measurement.yaml
```
- template: Network Performance Measurement
  values:
    - enterprise_name: "DemoEnterprise"
      network_performance_measurement_name: "initiate-one-way-probe"
      performance_monitor_name: "one-way-probe"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select PerformanceMonitor (name of one-way-probe)]
            [store id to name performance_monitor_id]
        NetworkPerformanceMeasurement
            associatedPerformanceMonitorID = [retrieve performance_monitor_id (PerformanceMonitor:id)]
            name = 'initiate-one-way-probe'
            description = 'Network Performance Measurement initiate-one-way-probe'

```
