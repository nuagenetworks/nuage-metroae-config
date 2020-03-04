## Feature Template: Performance Monitor
#### Examples

##### Creating Performance Monitor with HTTP probe.
This example creates Performance Monitor template with HTTP probe.nsg-perfromance-monitor-http.yaml
```
- template: Performance Monitor
  values:
    - enterprise_name: "DemoEnterprise"
      performance_monitor_name: "http-probe"
      probe_type: "HTTP"
      tier_type: tier1
      hold_down_timer: 1000

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        PerformanceMonitor
            numberOfPackets = 1
            interval = 10
            name = 'http-probe'
            probeType = 'HTTP'
            serviceClass = 'H'
            payloadSize = 137
            holdDownTimer = 1000
            description = 'Performance Monitor http-probe'
            [select Tier (tierType of TIER1)]
                tierType = 'TIER1'
                description = 'Tier tier1'
                destinationurl
                    percentageWeight = 100

```

##### Creating Performance Monitor with One-Way probe.
This example creates Performance Monitor template with One-Way probe.nsg-perfromance-monitor-one-way.yaml
```
- template: Performance Monitor
  values:
    - enterprise_name: "DemoEnterprise"
      performance_monitor_name: "one-way-probe"
      probe_type: "ONEWAY"
      number_of_packets: 10
      duration: 10
      packet_size: 150
      service_class: H

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        PerformanceMonitor
            numberOfPackets = 10
            interval = 10
            name = 'one-way-probe'
            probeType = 'ONEWAY'
            serviceClass = 'H'
            payloadSize = 150
            holdDownTimer = 1000
            description = 'Performance Monitor one-way-probe'

```

##### Creating Performance Monitor with ipsec-vxlan probe.
This example creates Performance Monitor template with ipsec-vxlan probe.nsg-perfromance-monitor-ipsec-vxlan.yaml
```
- template: Performance Monitor
  values:
    - enterprise_name: "DemoEnterprise"
      performance_monitor_name: "ipsec-vxlan-probe"
      probe_type: "IPSEC_AND_VXLAN"
      number_of_packets: 10
      duration: 10
      packet_size: 150
      service_class: H

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        PerformanceMonitor
            numberOfPackets = 10
            interval = 10
            name = 'ipsec-vxlan-probe'
            probeType = 'IPSEC_AND_VXLAN'
            serviceClass = 'H'
            payloadSize = 150
            holdDownTimer = 1000
            description = 'Performance Monitor ipsec-vxlan-probe'

```
