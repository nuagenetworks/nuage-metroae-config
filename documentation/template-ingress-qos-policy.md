## Feature Template: Ingress Qos Policy
#### Description
Define an NSG Network Port ingress QoS policy with the Ingress QoS Policy feature template.

#### Usage
In NSG deployment cases where QoS is applied the Ingress QoS Policy provides the ability for priority treatment on a per queue basis by assigning bandwidth to each queue. The treatment is effectively a set of traffic shapers on a per class (4) basis.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/ingress_qos_policy.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define an NSG Network Port ingress QoS policy with the Ingress QoS Policy feature template.
- template: Ingress Qos Policy
  values:
    - enterprise_name: ""                      # (opt reference) ingress QoS Policy can be configured in the Platform Configuration or within an Enterprise. Optional addition of the Enterprise Name to configure it within an Enterprise only.
      description: ""                          # (opt string) optional description of the Ingress QoS Policy.
      ingress_qos_policy_name: ""              # (reference) name of the Ingress QoS Policy.
      parent_rate_limiter_name: ""             # (reference) optional assigned name of a rate limiter for the port.
      priority_queue_1_classes: []             # (opt list of choice) list of the Forwarding Classes assigned to the Priority Queue.
      priority_queue_1_rate_limiter_name: ""   # (opt reference) rate limiter attached to priority queue.
      wrr_queue_2_classes: []                  # (opt list of choice) list of the Forwarding Classes assigned to the WRR Q2.
      wrr_queue_2_rate_limiter_name: ""        # (opt reference) rate limiter attached to WRR Q2.
      wrr_queue_3_classes: []                  # (opt list of choice) list of the Forwarding Classes assigned to the WRR Q3.
      wrr_queue_3_rate_limiter_name: ""        # (opt reference) rate limiter attached to WRR Q3.
      wrr_queue_4_classes: []                  # (opt list of choice) list of the Forwarding Classes assigned to the WRR Q4.
      wrr_queue_4_rate_limiter_name: ""        # (opt reference) rate limiter attached to WRR Q4.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | optional | reference | ingress QoS Policy can be configured in the Platform Configuration or within an Enterprise. Optional addition of the Enterprise Name to configure it within an Enterprise only.
description | optional | string | optional description of the Ingress QoS Policy.
ingress_qos_policy_name | required | reference | name of the Ingress QoS Policy.
parent_rate_limiter_name | required | reference | optional assigned name of a rate limiter for the port.
priority_queue_1_classes | optional | list | list of the Forwarding Classes assigned to the Priority Queue.
priority_queue_1_rate_limiter_name | optional | reference | rate limiter attached to priority queue.
wrr_queue_2_classes | optional | list | list of the Forwarding Classes assigned to the WRR Q2.
wrr_queue_2_rate_limiter_name | optional | reference | rate limiter attached to WRR Q2.
wrr_queue_3_classes | optional | list | list of the Forwarding Classes assigned to the WRR Q3.
wrr_queue_3_rate_limiter_name | optional | reference | rate limiter attached to WRR Q3.
wrr_queue_4_classes | optional | list | list of the Forwarding Classes assigned to the WRR Q4.
wrr_queue_4_rate_limiter_name | optional | reference | rate limiter attached to WRR Q4.


#### Restrictions
**create:**
* Ingress QoS Policy name must be unique.
* Rate Limiters attached to Parent and Queues must exist.
* Forwarding Classed can only be assigned to a single queue.

**revert:**
* Ingress QoS policy cannot reverted if it is attached a NSG port.

