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
*enterprise_name:* name of the enterprise in which performance monitor is created.<br>
*performance_monitor_name:* name of performance monitor.<br>
*probe_type:* type of test traffic.<br>
*number_of_packets:* number of packets to send in a certain duration.<br>
*duration:* number of packets to send in this duration in seconds.<br>
*packet_size:* size of each probe packet in bytes.<br>
*service_class:* service class.<br>
*hold_down_timer:* defines timeout for http probe packet response to a url.<br>
*description:* <br>
*tier_description:* <br>
*down_threshold_count:* <br>
*packet_count:* <br>
*probe_interval:* <br>
*tier_type:* <br>
*timeout:* <br>
*destination_url_http_method:* <br>
*destination_url:* <br>
*destination_url_down_threshold_count:* <br>
*destination_url_packet_count:* <br>
*destination_url_percentage_weight:* <br>
*destination_url_probe_interval:* <br>
*destination_url_timeout:* <br>


#### Restrictions
**create:**
* Enterpirse should pre-exist.

**revert:**
* Performance monitor cannot be deleted when attached to a NPM group (Network Performance Measurement).

