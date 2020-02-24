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
*enterprise_name:* A Rate Limiter can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.<br>
*rate_limiter_name:* name of the rate limiter.<br>
*description:* optional description of the Rate Limiter.<br>
*committed_information_rate:* guaranteed or Committed Information Rate for the rate limiter in Mbps. Traffic above this threshold subject to real time queue conditions and available bandwidth on the port. IF PIR=CIR then any traffic above this rate will be dropped.<br>
*peak_information_rate:* peak Information Rate for the rate limiter in Mbps. Any traffic above this rate with be dropped.<br>
*peak_burst_size:* burst size in Kb applied to the rate limiter token bucket.<br>


#### Restrictions
**create:**
* Rate Limiter name must be unique.
* CIR cannot exceed PIR.

**revert:**
* Cannot revert a Rate Limiter that is attached to a QoS policy.

#### Examples

##### Creating a Rate Limiter with Committed Bandwidth Only
This example creates three rate limiters where CIR=PIR, such that all 100Mbps, 200Mbps and 1000Mbps of bandwidth is committed.  nsg-qos-rate-limiter-cir-eq-pir.yaml
```
- template: Rate Limiter
  values:
    - rate_limiter_name: rate-100M
      committed_information_rate: 100
      peak_information_rate: 100
      peak_burst_size: 25000
- template: Rate Limiter
  values:
    - rate_limiter_name: rate-200M
      committed_information_rate: 100
      peak_information_rate: 100
      peak_burst_size: 25000   
- template: Rate Limiter
  values:
    - rate_limiter_name: rate-1000M
      committed_information_rate: 1000
      peak_information_rate: 1000
      peak_burst_size: 50000

```
```
(example)$ metroae config create user-data.yml
    RateLimiter
        committedInformationRate = '100'
        peakBurstSize = '25000'
        peakInformationRate = '100'
        description = 'rate limiter rate-100M'
        name = 'rate-100M'
    RateLimiter
        committedInformationRate = '100'
        peakBurstSize = '25000'
        peakInformationRate = '100'
        description = 'rate limiter rate-200M'
        name = 'rate-200M'
    RateLimiter
        committedInformationRate = '1000'
        peakBurstSize = '50000'
        peakInformationRate = '1000'
        description = 'rate limiter rate-1000M'
        name = 'rate-1000M'

```

##### Creating a Rate Limiter for Bursting
This example creates two rate limiters with PIR >> CIR, such that 200Mbps and 500Mbps of bandwidth is committed but bursting is allowed up to 1Gbps.  nsg-qos-rate-limiter-cir-lt-pir.yaml
```
- template: Rate Limiter
  values:
    - rate_limiter_name: rate-200M-1000M
      committed_information_rate: 200
      peak_information_rate: 1000
      peak_burst_size: 50000
- template: Rate Limiter
  values:
    - rate_limiter_name: rate-500M-1000M
      committed_information_rate: 500
      peak_information_rate: 1000
      peak_burst_size: 50000

```
```
(example)$ metroae config create user-data.yml
    RateLimiter
        committedInformationRate = '200'
        peakBurstSize = '50000'
        peakInformationRate = '1000'
        description = 'rate limiter rate-200M-1000M'
        name = 'rate-200M-1000M'
    RateLimiter
        committedInformationRate = '500'
        peakBurstSize = '50000'
        peakInformationRate = '1000'
        description = 'rate limiter rate-500M-1000M'
        name = 'rate-500M-1000M'

```

##### Creating a Rate Limiter for Best Effort
This example creates a rate limiter for best effort traffic only. No bandwidth is dedicated to CIR however bursting is permitted up to 1Gbps.  nsg-qos-rate-limiter-be.yaml
```
- template: Rate Limiter
  values:
    - rate_limiter_name: rate-0M-1000M
      committed_information_rate: 0
      peak_information_rate: 1000
      peak_burst_size: 250000

```
```
(example)$ metroae config create user-data.yml
    RateLimiter
        committedInformationRate = '0'
        peakBurstSize = '250000'
        peakInformationRate = '1000'
        description = 'rate limiter rate-0M-1000M'
        name = 'rate-0M-1000M'

```
