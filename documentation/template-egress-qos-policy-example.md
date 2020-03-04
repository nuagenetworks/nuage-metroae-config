## Feature Template: Egress Qos Policy
#### Examples

##### Creating Egress QoS Policy for Two Provider Networks
This example creates two Egress QoS policies with BW rate limiters for a 1Gbps service along with classes based on a 6 QoS scheme. In this case both providers are supporting 6 QoS, the FC mapping to provider classes is the same. However, different remarking policies will be applied based on provider support.  nsg-qos-egress-policy.yaml
```
- template: Egress Qos Policy
  values:
    - egress_qos_policy_name: MPLS-Provider-1-6QoS-1000M
      parent_rate_limiter_name: rate-1000M
      priority_queue_1_classes: ['A']
      priority_queue_1_rate_limiter_name: rate-100M
      wrr_queue_2_classes: ['B']
      wrr_queue_2_rate_limiter_name: rate-200M
      wrr_queue_3_classes: ['C', 'D', 'E']
      wrr_queue_3_rate_limiter_name: rate-500M-1000M
      wrr_queue_4_classes: ['F', 'G', 'H']
      wrr_queue_4_rate_limiter_name: rate-200M-1000M
      default_service_class: H
      cos_remarking_policy_name: MPLS-Provider-1-COS
      dscp_remarking_policy_name: MPLS-Provider-1
    - egress_qos_policy_name: MPLS-Provider-2-6QoS-1000M
      parent_rate_limiter_name: rate-1000M
      priority_queue_1_classes: ['A']
      priority_queue_1_rate_limiter_name: rate-100M
      wrr_queue_2_classes: ['B']
      wrr_queue_2_rate_limiter_name: rate-200M
      wrr_queue_3_classes: ['C', 'D', 'E']
      wrr_queue_3_rate_limiter_name: rate-500M-1000M
      wrr_queue_4_classes: ['F', 'G', 'H']
      wrr_queue_4_rate_limiter_name: rate-200M-1000M
      default_service_class: H
      dscp_remarking_policy_name: MPLS-Provider-2

```
```
(example)$ metroae config create user-data.yml
    [select RateLimiter (name of rate-1000M)]
        [store id to name parent_rate_limiter_id]
        [store id to name parent_rate_limiter_id]
    [select RateLimiter (name of rate-100M)]
        [store id to name priority_queue_1_rate_limiter_id]
        [store id to name priority_queue_1_rate_limiter_id]
    [select RateLimiter (name of rate-200M)]
        [store id to name wrr_queue_2_rate_limiter_id]
        [store id to name wrr_queue_2_rate_limiter_id]
    [select RateLimiter (name of rate-500M-1000M)]
        [store id to name wrr_queue_3_rate_limiter_id]
        [store id to name wrr_queue_3_rate_limiter_id]
    [select RateLimiter (name of rate-200M-1000M)]
        [store id to name wrr_queue_4_rate_limiter_id]
        [store id to name wrr_queue_4_rate_limiter_id]
    [select COSRemarkingPolicyTable (name of MPLS-Provider-1-COS)]
        [store id to name remarking_cos_policy_id]
    [select DSCPRemarkingPolicyTable (name of MPLS-Provider-1)]
        [store id to name remarking_dscp_policy_id]
    EgressQOSPolicy
        associatedDSCPRemarkingPolicyTableID = [retrieve remarking_dscp_policy_id (DSCPRemarkingPolicyTable:id)]
        name = 'MPLS-Provider-1-6QoS-1000M'
        queue4AssociatedRateLimiterID = [retrieve wrr_queue_4_rate_limiter_id (RateLimiter:id)]
        description = 'egress QoS policy MPLS-Provider-1-6QoS-1000M'
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
    [select DSCPRemarkingPolicyTable (name of MPLS-Provider-2)]
        [store id to name remarking_dscp_policy_id]
    EgressQOSPolicy
        associatedDSCPRemarkingPolicyTableID = [retrieve remarking_dscp_policy_id (DSCPRemarkingPolicyTable:id)]
        name = 'MPLS-Provider-2-6QoS-1000M'
        queue4AssociatedRateLimiterID = [retrieve wrr_queue_4_rate_limiter_id (RateLimiter:id)]
        description = 'egress QoS policy MPLS-Provider-2-6QoS-1000M'
        queue1AssociatedRateLimiterID = [retrieve priority_queue_1_rate_limiter_id (RateLimiter:id)]
        queue2AssociatedRateLimiterID = [retrieve wrr_queue_2_rate_limiter_id (RateLimiter:id)]
        queue2ForwardingClasses = ['B']
        queue3ForwardingClasses = ['C', 'D', 'E']
        queue4ForwardingClasses = ['F', 'G', 'H']
        queue3AssociatedRateLimiterID = [retrieve wrr_queue_3_rate_limiter_id (RateLimiter:id)]
        parentQueueAssociatedRateLimiterID = [retrieve parent_rate_limiter_id (RateLimiter:id)]
        queue1ForwardingClasses = ['A']
        defaultServiceClass = 'H'

```
