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
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | name of the enterpirse where Monitor Scope will be created.
network_performance_measurement_name | required | reference | name of the NPM.
monitorscope_name | required | string | name to identify monitor scope.
destination_nsg_list | optional | list | list of nsgs where probe traffic terminates.
allow_all_destination_nsgs | optional | boolean | select all nsgs that exists in the enterprise for running probe traffic.
source_nsg_list | optional | list | list of nsgs where probe traffic initiates.
allow_all_source_nsgs | optional | boolean | select all nsgs that exists in the enterprise for running  probe traffic.
all_nsgs_filter_list | optional | list | specify a list of nsg names. this list is used against regex filters to select desired nsgs for running probe traffic.
destination_nsg_regex_filter | optional | string | regex expression used for selecting destination nsgs from all_nsgs_filter_list.
source_nsg_regex_filter | optional | string | regex expression used for selecting source nsgs from all_nsgs_filter_list.


#### Restrictions
**create:**
* Enterpirse should pre exist.
* Network Performance Measurement should pre exist.
* NSGs should pre exist.

**revert:**
* Cannot revert a Monitor scope when it is attached to a L3/L2 Domain.

