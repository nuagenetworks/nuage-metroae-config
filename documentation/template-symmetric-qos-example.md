## Feature Template: Symmetric Qos Policy
#### Examples

##### Creating a Symmetric QoS Policy with all Classes Enabled
This example creates a global Symmetric QoS policy. From this we will see that the following is created.  nsg-qos-symmetric-policy.yaml  
- COS Remarking policy
- DSCP Remarking Policy
- Rate limiters for the Port (parent) and each queue.
- Ingress QoS policy
- Egress QoS policy
```
- template: Symmetric Qos Policy
  values:
    - symmetric_qos_policy_name: SQ-MPLS-Provider-1-6QoS-1000M
      parent_committed_information_rate: 1000
      parent_peak_information_rate: 1000
      parent_peak_burst_size: 250000
      parent_rate_limiter_name: rate-1000M
      priority_queue_1_committed_information_rate: 100
      priority_queue_1_peak_information_rate: 100
      priority_queue_1_peak_burst_size: 50000
      priority_queue_1_classes: ['A']
      wrr_queue_2_classes: ['B']
      wrr_queue_2_committed_information_rate: 200
      wrr_queue_2_peak_information_rate: 200
      wrr_queue_2_peak_burst_size: 50000
      wrr_queue_3_classes: ['C', 'D', 'E']
      wrr_queue_3_committed_information_rate: 500
      wrr_queue_3_peak_information_rate: 1000
      wrr_queue_3_peak_burst_size: 125000
      wrr_queue_4_classes: ['F', 'G', 'H']
      wrr_queue_4_committed_information_rate: 200
      wrr_queue_4_peak_information_rate: 1000
      wrr_queue_4_peak_burst_size: 50000
      default_service_class: H
      cos_remarking_classes: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
      cos_remarking_cos_list: ['5', '5', '3', '3', '3', '3', '0', '0']
      dscp_remarking_classes: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
      dscp_remarking_dscp_list: ['46', '34', '26', '18', '10', '0', '0', '0']

```
```
(example)$ metroae config create user-data.yml
    RateLimiter
        committedInformationRate = '1000'
        peakBurstSize = '250000'
        peakInformationRate = '1000'
        description = 'parent rate limiter SQ-MPLS-Provider-1-6QoS-1000M'
        name = 'parent_rate_limiter_SQ-MPLS-Provider-1-6QoS-1000M'
        [store id to name parent_rate_limiter_id]
    RateLimiter
        committedInformationRate = '100'
        peakBurstSize = '50000'
        peakInformationRate = '100'
        description = 'priority queue 1 rate limiter SQ-MPLS-Provider-1-6QoS-1000M'
        name = 'priority_queue_1_rate_limiter_SQ-MPLS-Provider-1-6QoS-1000M'
        [store id to name priority_queue_1_rate_limiter_id]
    RateLimiter
        committedInformationRate = '200'
        peakBurstSize = '50000'
        peakInformationRate = '200'
        description = 'weighted RR queue 2 rate limiter SQ-MPLS-Provider-1-6QoS-1000M'
        name = 'wrr_queue_2_rate_limiter_SQ-MPLS-Provider-1-6QoS-1000M'
        [store id to name wrr_queue_2_rate_limiter_id]
    RateLimiter
        committedInformationRate = '500'
        peakBurstSize = '125000'
        peakInformationRate = '1000'
        description = 'weighted RR queue 3 rate limiter SQ-MPLS-Provider-1-6QoS-1000M'
        name = 'wrr_queue_3_rate_limiter_SQ-MPLS-Provider-1-6QoS-1000M'
        [store id to name wrr_queue_3_rate_limiter_id]
    RateLimiter
        committedInformationRate = '200'
        peakBurstSize = '50000'
        peakInformationRate = '1000'
        description = 'weighted RR queue 4 rate limiter SQ-MPLS-Provider-1-6QoS-1000M'
        name = 'wrr_queue_4_rate_limiter_SQ-MPLS-Provider-1-6QoS-1000M'
        [store id to name wrr_queue_4_rate_limiter_id]
    COSRemarkingPolicyTable
        name = 'cos_SQ-MPLS-Provider-1-6QoS-1000M'
        description = 'CoS policy SQ-MPLS-Provider-1-6QoS-1000M'
        [store id to name remarking_cos_policy_id]
        COSRemarkingPolicy
            forwardingClass = 'A'
            DSCP = '5'
        COSRemarkingPolicy
            forwardingClass = 'B'
            DSCP = '5'
        COSRemarkingPolicy
            forwardingClass = 'C'
            DSCP = '3'
        COSRemarkingPolicy
            forwardingClass = 'D'
            DSCP = '3'
        COSRemarkingPolicy
            forwardingClass = 'E'
            DSCP = '3'
        COSRemarkingPolicy
            forwardingClass = 'F'
            DSCP = '3'
        COSRemarkingPolicy
            forwardingClass = 'G'
            DSCP = '0'
        COSRemarkingPolicy
            forwardingClass = 'H'
            DSCP = '0'
    DSCPRemarkingPolicyTable
        name = 'dscp_SQ-MPLS-Provider-1-6QoS-1000M'
        description = 'DSCP policy SQ-MPLS-Provider-1-6QoS-1000M'
        [store id to name remarking_dscp_policy_id]
        DSCPRemarkingPolicy
            forwardingClass = 'A'
            DSCP = '46'
        DSCPRemarkingPolicy
            forwardingClass = 'B'
            DSCP = '34'
        DSCPRemarkingPolicy
            forwardingClass = 'C'
            DSCP = '26'
        DSCPRemarkingPolicy
            forwardingClass = 'D'
            DSCP = '18'
        DSCPRemarkingPolicy
            forwardingClass = 'E'
            DSCP = '10'
        DSCPRemarkingPolicy
            forwardingClass = 'F'
            DSCP = '0'
        DSCPRemarkingPolicy
            forwardingClass = 'G'
            DSCP = '0'
        DSCPRemarkingPolicy
            forwardingClass = 'H'
            DSCP = '0'
    IngressQOSPolicy
        name = 'SQ-MPLS-Provider-1-6QoS-1000M'
        queue4AssociatedRateLimiterID = [retrieve wrr_queue_4_rate_limiter_id (RateLimiter:id)]
        queue1AssociatedRateLimiterID = [retrieve priority_queue_1_rate_limiter_id (RateLimiter:id)]
        queue2AssociatedRateLimiterID = [retrieve wrr_queue_2_rate_limiter_id (RateLimiter:id)]
        queue2ForwardingClasses = ['B']
        queue3ForwardingClasses = ['C', 'D', 'E']
        queue4ForwardingClasses = ['F', 'G', 'H']
        queue3AssociatedRateLimiterID = [retrieve wrr_queue_3_rate_limiter_id (RateLimiter:id)]
        parentQueueAssociatedRateLimiterID = [retrieve parent_rate_limiter_id (RateLimiter:id)]
        queue1ForwardingClasses = ['A']
        description = 'symmetric QoS policy SQ-MPLS-Provider-1-6QoS-1000M'
    EgressQOSPolicy
        associatedDSCPRemarkingPolicyTableID = [retrieve remarking_dscp_policy_id (DSCPRemarkingPolicyTable:id)]
        name = 'SQ-MPLS-Provider-1-6QoS-1000M'
        queue4AssociatedRateLimiterID = [retrieve wrr_queue_4_rate_limiter_id (RateLimiter:id)]
        description = 'symmetric QoS policy SQ-MPLS-Provider-1-6QoS-1000M'
        queue1AssociatedRateLimiterID = [retrieve priority_queue_1_rate_limiter_id (RateLimiter:id)]
        queue2AssociatedRateLimiterID = [retrieve wrr_queue_2_rate_limiter_id (RateLimiter:id)]
        queue2ForwardingClasses = ['B']
        queue3ForwardingClasses = ['C', 'D', 'E']
        queue4ForwardingClasses = ['F', 'G', 'H']
        queue3AssociatedRateLimiterID = [retrieve wrr_queue_3_rate_limiter_id (RateLimiter:id)]
        associatedCOSRemarkingPolicyTableID = [retrieve remarking_cos_policy_id (COSRemarkingPolicyTable:id)]
        parentQueueAssociatedRateLimiterID = [retrieve parent_rate_limiter_id (RateLimiter:id)]
        queue1ForwardingClasses = ['A']
        defaultServiceClass = 'H'

```
