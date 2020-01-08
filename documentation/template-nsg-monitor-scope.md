## Feature Template: Monitorscope
#### Description
Monitor Scope Template is used to define the list of source NSGs and destination NSGs.

#### Usage
Monitoring overlay network health using probes requires to define the list of source NSGs and destination NSGs. Using Monitor Scope template, user can select inidividual NSGs or use regex filter to automatically populate the list of NSGs.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/monitorscope.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Monitor Scope Template is used to define the list of source NSGs and destination NSGs.
- template: Monitorscope
  values:
    - enterprise_name: ""                      # (reference) name of the enterpirse where Monitor Scope will be created.
      network_performance_measurement_name: "" # (reference) name of the NPM.
      monitorscope_name: ""                    # (string) name to identify monitor scope.
      destination_nsg_list: []                 # (opt list of string) list of nsgs where probe traffic terminates.
      allow_all_destination_nsgs: False        # (opt boolean) select all nsgs that exists in the enterprise for running probe traffic.
      source_nsg_list: []                      # (opt list of string) list of nsgs where probe traffic initiates.
      allow_all_source_nsgs: False             # (opt boolean) select all nsgs that exists in the enterprise for running  probe traffic.
      all_nsgs_filter_list: []                 # (opt list of string) specify a list of nsg names. this list is used against regex filters to select desired nsgs for running probe traffic.
      destination_nsg_regex_filter: ""         # (opt string) regex expression used for selecting destination nsgs from all_nsgs_filter_list.
      source_nsg_regex_filter: ""              # (opt string) regex expression used for selecting source nsgs from all_nsgs_filter_list.

```

#### Parameters
*enterprise_name:* name of the enterpirse where Monitor Scope will be created.<br>
*network_performance_measurement_name:* name of the NPM.<br>
*monitorscope_name:* name to identify monitor scope.<br>
*destination_nsg_list:* list of nsgs where probe traffic terminates.<br>
*allow_all_destination_nsgs:* select all nsgs that exists in the enterprise for running probe traffic.<br>
*source_nsg_list:* list of nsgs where probe traffic initiates.<br>
*allow_all_source_nsgs:* select all nsgs that exists in the enterprise for running  probe traffic.<br>
*all_nsgs_filter_list:* specify a list of nsg names. this list is used against regex filters to select desired nsgs for running probe traffic.<br>
*destination_nsg_regex_filter:* regex expression used for selecting destination nsgs from all_nsgs_filter_list.<br>
*source_nsg_regex_filter:* regex expression used for selecting source nsgs from all_nsgs_filter_list.<br>


#### Restrictions
**create:**
* Enterpirse should pre exist.
* Network Performance Measurement should pre exist.
* NSGs should pre exist.

**revert:**
* Cannot revert a Monitor scope when it is attached to a L3/L2 Domain.

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
[metroae-user@metroae-host]# metroae config create nsg-monitor-scope-minimal.yaml
# update later

```

##### update later

```

##### Creating a Monitor Scope template with specific source and destination nsgs
This example creates a Monitor Scope Template, with specific nsgs.nsg-monitor-scope-specific.yaml

```
```
- enterprise_name: "DemoEnterprise"
  network_performance_measurement_name: "initiate-one-way-probe"
  monitorscope_name: "one-way-probe-specific-nsgs"
  allow_all_destination_nsgs: False
  allow_all_source_nsgs: False
  destination_nsg_list: ["West-Branch-002", "West-Branch-003"]
  src_nsg_list: ["West-Branch-001"]

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
[metroae-user@metroae-host]# metroae config create nsg-monitor-scope-specific.yaml
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of West-Branch-002)]
            [store id to name dst_list_nsg_id_1]
        [select NSGateway (name of West-Branch-003)]
            [store id to name dst_list_nsg_id_2]
        [select NSGateway (name of West-Branch-001)]
            [store id to name src_list_nsg_id_1]
        [select NetworkPerformanceMeasurement (name of initiate-one-way-probe)]
            Monitorscope
                allowAllDestinationNSGs = False
                destinationNSGs = [retrieve dst_list_nsg_id_1 (NSGateway:id), retrieve dst_list_nsg_id_2 (NSGateway:id)]
                allowAllSourceNSGs = False
                name = 'one-way-probe-specific-nsgs'
                sourceNSGs = [retrieve src_list_nsg_id_1 (NSGateway:id)]

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
[metroae-user@metroae-host]# metroae config create nsg-monitor-scope-regex-filter.yaml
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of East-Branch-001)]
            [store id to name dst_filter_nsg_id_4]
        [select NSGateway (name of East-Branch-002)]
            [store id to name dst_filter_nsg_id_5]
        [select NSGateway (name of West-Branch-001)]
            [store id to name src_filter_nsg_id_1]
        [select NSGateway (name of West-Branch-002)]
            [store id to name src_filter_nsg_id_2]
        [select NSGateway (name of West-Branch-003)]
            [store id to name src_filter_nsg_id_3]
        [select NetworkPerformanceMeasurement (name of initiate-one-way-probe)]
            Monitorscope
                allowAllDestinationNSGs = False
                destinationNSGs = [retrieve dst_filter_nsg_id_4 (NSGateway:id), retrieve dst_filter_nsg_id_5 (NSGateway:id)]
- template: Monitorscope
                allowAllSourceNSGs = False
                name = 'one-way-probe-specific-nsgs'
                sourceNSGs = [retrieve src_filter_nsg_id_1 (NSGateway:id), retrieve src_filter_nsg_id_2 (NSGateway:id), retrieve src_filter_nsg_id_3 (NSGateway:id)]

```
