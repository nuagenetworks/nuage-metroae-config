## Feature Template: Symmetric Qos Policy
#### Description
Create a matching ingress and egress QoS policy along with all of the dependent objects with the Symmetric QoS Policy feature template.

#### Usage
In NSG deployment cases where QoS is applied the Egress and Ingress QoS Policy provides the ability for priority treatment on a per queue basis by assigning bandwidth to each queue. The treatment is effectively a set of traffic shapers on a per class (4) basis. The Symmetric QoS Policy template is an all-in-one QOS template that creates both Egress and Ingress QoS policies with all necessary child objects (ie. rate limiter, dscp remarking and cos remarking) automatically.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/symmetric_qos_policy.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create a matching ingress and egress QoS policy along with all of the dependent objects with the Symmetric QoS Policy feature template.
- template: Symmetric Qos Policy
  values:
    - enterprise_name: ""                      # (opt reference) QoS Policies can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.
      symmetric_qos_policy_name: ""            # (string) name to apply to Symmetric QoS Policy objects.
      description: ""                          # (opt string) optional description of the all QoS Policy objects.
      default_service_class: A                 # (opt ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']) service class to use for unclassified traffic.
      parent_committed_information_rate: 0     # (integer) CIR for the port in Mbps. Traffic above this threshold subject to real time queue conditions and available bandwidth on the port. IF PIR=CIR then any traffic above this rate will be dropped.
      parent_peak_information_rate: 0          # (integer) PIR for the port in Mbps. Any traffic above this rate with be dropped.
      parent_peak_burst_size: 0                # (integer) burst size in Kb applied to the rate limiter token bucket for the parent queue.
      priority_queue_1_classes: []             # (opt list of choice) list of the Forwarding Classes assigned to the Priority Queue.
      priority_queue_1_committed_information_rate: 0 # (opt integer) guaranteed or Committed Information Rate for the priority queue in Mbps.
      priority_queue_1_peak_information_rate: 0 # (opt integer) PIR for the priority queue in Mbps. Any traffic above this rate with be dropped.
      priority_queue_1_peak_burst_size: 0      # (opt integer) burst size in Kb applied to the rate limiter token bucket for the priority queue.
      wrr_queue_2_classes: []                  # (opt list of choice) list of the Forwarding Classes assigned to the WRR Q2.
      wrr_queue_2_committed_information_rate: 0 # (opt integer) guaranteed or Committed Information Rate for queue 2 in Mbps.
      wrr_queue_2_peak_information_rate: 0     # (opt integer) PIR for queue 2 in Mbps. Any traffic above this rate with be dropped.
      wrr_queue_2_peak_burst_size: 0           # (opt integer) burst size in Kb applied to the rate limiter token bucket for queue 2.
      wrr_queue_3_classes: []                  # (opt list of choice) list of the Forwarding Classes assigned to the WRR Q3.
      wrr_queue_3_committed_information_rate: 0 # (opt integer) guaranteed or Committed Information Rate for queue 3 in Mbps.
      wrr_queue_3_peak_information_rate: 0     # (opt integer) PIR for queue 3 in Mbps. Any traffic above this rate with be dropped.
      wrr_queue_3_peak_burst_size: 0           # (opt integer) burst size in Kb applied to the rate limiter token bucket for queue 2.
      wrr_queue_4_classes: []                  # (opt list of choice) list of the Forwarding Classes assigned to the WRR Q4.
      wrr_queue_4_committed_information_rate: 0 # (opt integer) guaranteed or Committed Information Rate for queue 4 in Mbps.
      wrr_queue_4_peak_information_rate: 0     # (opt integer) PIR for queue 4 in Mbps. Any traffic above this rate with be dropped.
      wrr_queue_4_peak_burst_size: 0           # (opt integer) burst size in Kb applied to the rate limiter token bucket for queue 2.
      cos_remarking_classes: []                # (opt list of choice) list of forwarding classes that will have COS Bits marked.
      cos_remarking_cos_list: []               # (opt list of string) matching list of markings to be used per Forwarding Class. CoS is a 3 bit field and decimal values
      dscp_remarking_classes: []               # (opt list of choice) list of forwarding classes that will have DSCP Bits marked.
      dscp_remarking_dscp_list: []             # (opt list of string) matching list of markings to be used per Forwarding Class. DSCP is a 6 bit field and decimal values from 0 to 63 are valid.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | optional | reference | QoS Policies can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.
symmetric_qos_policy_name | required | string | name to apply to Symmetric QoS Policy objects.
description | optional | string | optional description of the all QoS Policy objects.
default_service_class | optional | choice | service class to use for unclassified traffic.
parent_committed_information_rate | required | integer | CIR for the port in Mbps. Traffic above this threshold subject to real time queue conditions and available bandwidth on the port. IF PIR=CIR then any traffic above this rate will be dropped.
parent_peak_information_rate | required | integer | PIR for the port in Mbps. Any traffic above this rate with be dropped.
parent_peak_burst_size | required | integer | burst size in Kb applied to the rate limiter token bucket for the parent queue.
priority_queue_1_classes | optional | list | list of the Forwarding Classes assigned to the Priority Queue.
priority_queue_1_committed_information_rate | optional | integer | guaranteed or Committed Information Rate for the priority queue in Mbps.
priority_queue_1_peak_information_rate | optional | integer | PIR for the priority queue in Mbps. Any traffic above this rate with be dropped.
priority_queue_1_peak_burst_size | optional | integer | burst size in Kb applied to the rate limiter token bucket for the priority queue.
wrr_queue_2_classes | optional | list | list of the Forwarding Classes assigned to the WRR Q2.
wrr_queue_2_committed_information_rate | optional | integer | guaranteed or Committed Information Rate for queue 2 in Mbps.
wrr_queue_2_peak_information_rate | optional | integer | PIR for queue 2 in Mbps. Any traffic above this rate with be dropped.
wrr_queue_2_peak_burst_size | optional | integer | burst size in Kb applied to the rate limiter token bucket for queue 2.
wrr_queue_3_classes | optional | list | list of the Forwarding Classes assigned to the WRR Q3.
wrr_queue_3_committed_information_rate | optional | integer | guaranteed or Committed Information Rate for queue 3 in Mbps.
wrr_queue_3_peak_information_rate | optional | integer | PIR for queue 3 in Mbps. Any traffic above this rate with be dropped.
wrr_queue_3_peak_burst_size | optional | integer | burst size in Kb applied to the rate limiter token bucket for queue 2.
wrr_queue_4_classes | optional | list | list of the Forwarding Classes assigned to the WRR Q4.
wrr_queue_4_committed_information_rate | optional | integer | guaranteed or Committed Information Rate for queue 4 in Mbps.
wrr_queue_4_peak_information_rate | optional | integer | PIR for queue 4 in Mbps. Any traffic above this rate with be dropped.
wrr_queue_4_peak_burst_size | optional | integer | burst size in Kb applied to the rate limiter token bucket for queue 2.
cos_remarking_classes | optional | list | list of forwarding classes that will have COS Bits marked.
cos_remarking_cos_list | optional | list | matching list of markings to be used per Forwarding Class. CoS is a 3 bit field and decimal values
dscp_remarking_classes | optional | list | list of forwarding classes that will have DSCP Bits marked.
dscp_remarking_dscp_list | optional | list | matching list of markings to be used per Forwarding Class. DSCP is a 6 bit field and decimal values from 0 to 63 are valid.


#### Restrictions
**create:**
* Symmetric QoS Policy name must be unique.
* Forwarding Classed can only be assigned to a single queue.
* Sum of queue rate limiters CIR cannot exceed the port CIR rate limiter.
* A child rate limiter PIR cannot exceed the Parent rate limiter.

**revert:**
* Symmetric QoS policy cannot reverted if it is attached a NSG port.

