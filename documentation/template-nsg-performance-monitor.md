## Feature Template: Performance Monitor
#### Description
Performance Monitor template is used to initiate test traffic between NSGs.

#### Usage
Network performance between NSGs can be measured using Performance monitors. Performance monitor is used to design test traffic which can be run between NSG(s) to analyze overall network health. After creating performance monitor it should be attached to a NPM group.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/performance_monitor.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Performance Monitor template is used to initiate test traffic between NSGs.
- template: Performance Monitor
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which performance monitor is created.
      performance_monitor_name: ""             # (string) name of performance monitor.
      probe_type: HTTP                         # (opt ['HTTP', 'IPSEC_AND_VXLAN', 'ONEWAY']) type of test traffic.
      number_of_packets: 0                     # (opt integer) number of packets to send in a certain duration.
      duration: 0                              # (opt integer) number of packets to send in this duration in seconds.
      packet_size: 0                           # (opt integer) size of each probe packet in bytes.
      service_class: A                         # (opt ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']) service class.
      hold_down_timer: 0                       # (opt integer) defines timeout for http probe packet response to a url.
      description: ""                          # (opt string)
      tier_description: ""                     # (opt string)
      down_threshold_count: 0                  # (opt integer)
      packet_count: 0                          # (opt integer)
      probe_interval: 0                        # (opt integer)
      tier_type: TIER1                         # (opt ['TIER1', 'TIER2'])
      timeout: 0                               # (opt integer)
      destination_url_http_method: GET         # (opt ['GET', 'HEAD'])
      destination_url: ""                      # (opt string)
      destination_url_down_threshold_count: 0  # (opt integer)
      destination_url_packet_count: 0          # (opt integer)
      destination_url_percentage_weight: 0     # (opt integer)
      destination_url_probe_interval: 0        # (opt integer)
      destination_url_timeout: 0               # (opt integer)

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | name of the enterprise in which performance monitor is created.
performance_monitor_name | required | string | name of performance monitor.
probe_type | optional | choice | type of test traffic.
number_of_packets | optional | integer | number of packets to send in a certain duration.
duration | optional | integer | number of packets to send in this duration in seconds.
packet_size | optional | integer | size of each probe packet in bytes.
service_class | optional | choice | service class.
hold_down_timer | optional | integer | defines timeout for http probe packet response to a url.
description | optional | string | 
tier_description | optional | string | 
down_threshold_count | optional | integer | 
packet_count | optional | integer | 
probe_interval | optional | integer | 
tier_type | optional | choice | 
timeout | optional | integer | 
destination_url_http_method | optional | choice | 
destination_url | optional | string | 
destination_url_down_threshold_count | optional | integer | 
destination_url_packet_count | optional | integer | 
destination_url_percentage_weight | optional | integer | 
destination_url_probe_interval | optional | integer | 
destination_url_timeout | optional | integer | 


#### Restrictions
**create:**
* Enterpirse should pre-exist.

**revert:**
* Performance monitor cannot be deleted when attached to a NPM group (Network Performance Measurement).

