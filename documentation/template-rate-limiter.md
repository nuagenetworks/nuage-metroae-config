## Feature Template: Rate Limiter
#### Description
Create bandwidth allocations that are applied to Ingress and Egress QoS Policies with the Rate Limiter feature template.

#### Usage
When implementing a QoS scheme we typically allocate bandwidth to the Port and the queues. In the case of NSG Ports this is defined via Rate Limiters which are subsequently used to define bandwidth characteristics of Egress and Ingress queues.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/rate_limiter.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create bandwidth allocations that are applied to Ingress and Egress QoS Policies with the Rate Limiter feature template.
- template: Rate Limiter
  values:
    - enterprise_name: ""                      # (opt reference) A Rate Limiter can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.
      rate_limiter_name: ""                    # (string) name of the rate limiter.
      description: ""                          # (opt string) optional description of the Rate Limiter.
      committed_information_rate: 0            # (integer) guaranteed or Committed Information Rate for the rate limiter in Mbps. Traffic above this threshold subject to real time queue conditions and available bandwidth on the port. IF PIR=CIR then any traffic above this rate will be dropped.
      peak_information_rate: 0                 # (integer) peak Information Rate for the rate limiter in Mbps. Any traffic above this rate with be dropped.
      peak_burst_size: 0                       # (integer) burst size in Kb applied to the rate limiter token bucket.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | optional | reference | A Rate Limiter can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.
rate_limiter_name | required | string | name of the rate limiter.
description | optional | string | optional description of the Rate Limiter.
committed_information_rate | required | integer | guaranteed or Committed Information Rate for the rate limiter in Mbps. Traffic above this threshold subject to real time queue conditions and available bandwidth on the port. IF PIR=CIR then any traffic above this rate will be dropped.
peak_information_rate | required | integer | peak Information Rate for the rate limiter in Mbps. Any traffic above this rate with be dropped.
peak_burst_size | required | integer | burst size in Kb applied to the rate limiter token bucket.


#### Restrictions
**create:**
* Rate Limiter name must be unique.
* CIR cannot exceed PIR.

**revert:**
* Cannot revert a Rate Limiter that is attached to a QoS policy.

