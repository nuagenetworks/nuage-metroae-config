## Feature Template: Egress Qos Policy
#### Description
Define an NSG Port egress QoS policy with the Egress QoS Policy feature template.

#### Usage
In NSG deployment cases where QoS is applied the Egress QoS Policy provides the ability for priority treatment on a per queue basis by assigning bandwidth to each queue. Queue bandwidth is assigned on a CIR and PIR basis with one Priority Queue and 3 Weighted Round Robin (WRR) queues. COS and DSCP VLAN and IP packet header marking are supported via the attachment of a remarking policy.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/egress_qos_policy.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define an NSG Port egress QoS policy with the Egress QoS Policy feature template.
- template: Egress Qos Policy
  values:
    - enterprise_name: ""                      # (opt reference) egress QoS Policy can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.
      description: ""                          # (opt string) optional description of the Egress QoS Policy.
      egress_qos_policy_name: ""               # (reference) name of the Egress QoS Policy.
      parent_rate_limiter_name: ""             # (reference) optional assigned of a rate limiter for the port.
      priority_queue_1_classes: []             # (opt list of choice) list of the Forwarding Classes assigned to the Priority Queue.
      priority_queue_1_rate_limiter_name: ""   # (opt reference) rate limiter attached to priority queue.
      wrr_queue_2_classes: []                  # (opt list of choice) list of the Forwarding Classes assigned to the WRR Q2.
      wrr_queue_2_rate_limiter_name: ""        # (opt reference) rate limiter attached to WRR Q2.
      wrr_queue_3_classes: []                  # (opt list of choice) list of the Forwarding Classes assigned to the WRR Q3.
      wrr_queue_3_rate_limiter_name: ""        # (opt reference) rate limiter attached to WRR Q3.
      wrr_queue_4_classes: []                  # (opt list of choice) list of the Forwarding Classes assigned to the WRR Q4.
      wrr_queue_4_rate_limiter_name: ""        # (opt reference) rate limiter attached to WRR Q4.
      default_service_class: A                 # (opt ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']) service class to use for unclassified traffic.
      cos_remarking_policy_name: ""            # (opt reference) optional attachment of a 802.1P COS Bit Remarking Policy.
      dscp_remarking_policy_name: ""           # (opt reference) optional attachment of a DSCP Bit Remarking Policy.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | optional | reference | egress QoS Policy can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.
description | optional | string | optional description of the Egress QoS Policy.
egress_qos_policy_name | required | reference | name of the Egress QoS Policy.
parent_rate_limiter_name | required | reference | optional assigned of a rate limiter for the port.
priority_queue_1_classes | optional | list | list of the Forwarding Classes assigned to the Priority Queue.
priority_queue_1_rate_limiter_name | optional | reference | rate limiter attached to priority queue.
wrr_queue_2_classes | optional | list | list of the Forwarding Classes assigned to the WRR Q2.
wrr_queue_2_rate_limiter_name | optional | reference | rate limiter attached to WRR Q2.
wrr_queue_3_classes | optional | list | list of the Forwarding Classes assigned to the WRR Q3.
wrr_queue_3_rate_limiter_name | optional | reference | rate limiter attached to WRR Q3.
wrr_queue_4_classes | optional | list | list of the Forwarding Classes assigned to the WRR Q4.
wrr_queue_4_rate_limiter_name | optional | reference | rate limiter attached to WRR Q4.
default_service_class | optional | choice | service class to use for unclassified traffic.
cos_remarking_policy_name | optional | reference | optional attachment of a 802.1P COS Bit Remarking Policy.
dscp_remarking_policy_name | optional | reference | optional attachment of a DSCP Bit Remarking Policy.


#### Restrictions
**create:**
* Egress QoS Policy name must be unique.
* Rate Limiters attached to Parent and Queues must exist.
* Forwarding Classes can only be assigned to a single queue.
* Sum of child rate limiters CIR cannot exceed the Parent CIR rate limiter.
* A child rate limiter PIR cannot exceed the Parent rate limiter.

**revert:**
* Egress QoS policy cannot revert if it is attached an NSG port.

