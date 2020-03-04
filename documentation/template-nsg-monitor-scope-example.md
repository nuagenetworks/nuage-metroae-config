## Feature Template: Monitorscope
#### Examples

##### Creating a Monitor Scope template with minimal data
This example creates a Monitor Scope Template, with minimal user data.nsg-monitor-scope-minimal.yaml
```
- template: Monitorscope
  values:
    - enterprise_name: "DemoEnterprise"
      network_performance_measurement_name: "initiate-one-way-probe"
      monitorscope_name: "one-way-probe"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NetworkPerformanceMeasurement (name of initiate-one-way-probe)]
            Monitorscope
                allowAllDestinationNSGs = True
                allowAllSourceNSGs = True
                name = 'one-way-probe'

```

##### Creating a Monitor Scope template with specific source and destination nsgs
This example creates a Monitor Scope Template, with specific nsgs.nsg-monitor-scope-specific.yaml
```
- template: Monitorscope
  values:
    - enterprise_name: "DemoEnterprise"
      network_performance_measurement_name: "initiate-one-way-probe"
      monitorscope_name: "one-way-probe-specific-nsgs"
      allow_all_destination_nsgs: False
      allow_all_source_nsgs: False
      destination_nsg_list: ["West-Branch-002", "West-Branch-003"]
      src_nsg_list: ["West-Branch-001"]

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of West-Branch-002)]
            [store id to name dst_list_nsg_id_1]
        [select NSGateway (name of West-Branch-003)]
            [store id to name dst_list_nsg_id_2]
        [select NetworkPerformanceMeasurement (name of initiate-one-way-probe)]
            Monitorscope
                allowAllDestinationNSGs = False
                destinationNSGs = [retrieve dst_list_nsg_id_1 (NSGateway:id), retrieve dst_list_nsg_id_2 (NSGateway:id)]
                allowAllSourceNSGs = False
                name = 'one-way-probe-specific-nsgs'

```

##### Creating a Monitor Scope template with regex filters
This example creates a Monitor Scope Template, with regex filter. NSGs that mataches this filter are selected for running probe traffic. The filter is applied on the user defined list of nsgs define by all_nsgs_filter_list.nsg-monitor-scope-regex-filter.yaml
```
- template: Monitorscope
  values:
    - enterprise_name: "DemoEnterprise"
      network_performance_measurement_name: "initiate-one-way-probe"
      monitorscope_name: "one-way-probe-specific-nsgs"
      allow_all_destination_nsgs: False
      allow_all_source_nsgs: False
      all_nsgs_filter_list: ["West-Branch-001", "West-Branch-002", "West-Branch-003", "East-Branch-001", "East-Branch-002" ]
      destination_nsg_regex_filter: "East-*"
      src_nsg_regex_filter: "West-*"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of East-Branch-001)]
            [store id to name dst_filter_nsg_id_4]
        [select NSGateway (name of East-Branch-002)]
            [store id to name dst_filter_nsg_id_5]
        [select NetworkPerformanceMeasurement (name of initiate-one-way-probe)]
            Monitorscope
                allowAllDestinationNSGs = False
                destinationNSGs = [retrieve dst_filter_nsg_id_4 (NSGateway:id), retrieve dst_filter_nsg_id_5 (NSGateway:id)]
                allowAllSourceNSGs = False
                name = 'one-way-probe-specific-nsgs'

```

##### Creating a Monitor Scope template with regex filters
This example creates a Monitor Scope Template, with regex filter. NSGs that mataches this filter are selected for running probe traffic. The filter is applied on the user defined list of nsgs define by all_nsgs_filter_list.nsg-monitor-scope-regex-filter.yaml
```
- template: Monitorscope
  values:
    - enterprise_name: "DemoEnterprise"
      network_performance_measurement_name: "initiate-one-way-probe"
      monitorscope_name: "one-way-probe-specific-nsgs"
      allow_all_destination_nsgs: False
      allow_all_source_nsgs: False
      all_nsgs_filter_list: ["West-Branch-001", "West-Branch-002", "West-Branch-003", "East-Branch-001", "East-Branch-002" ]
      destination_nsg_regex_filter: "East-*"
      src_nsg_regex_filter: "West-*"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of East-Branch-001)]
            [store id to name dst_filter_nsg_id_4]
        [select NSGateway (name of East-Branch-002)]
            [store id to name dst_filter_nsg_id_5]
        [select NetworkPerformanceMeasurement (name of initiate-one-way-probe)]
            Monitorscope
                allowAllDestinationNSGs = False
                destinationNSGs = [retrieve dst_filter_nsg_id_4 (NSGateway:id), retrieve dst_filter_nsg_id_5 (NSGateway:id)]
                allowAllSourceNSGs = False
                name = 'one-way-probe-specific-nsgs'

```
