## Feature Template: Ingress Qos Policy
#### Examples

##### Create Ingress QoS Policy for Two Provider Networks
This example creates two Ingress QoS policies with BW rate limiters and classes based on a 6 QoS scheme.  nsg-qos-ingress-policy.yaml
```
- template: Ingress Qos Policy
  values:
    - ingress_qos_policy_name: MPLS-Provider-1-6QoS-1000M
      parent_rate_limiter_name: rate-1000M
      priority_queue_1_classes: ['A']
      priority_queue_1_rate_limiter_name: rate-100M
      wrr_queue_2_classes: ['B']
      wrr_queue_2_rate_limiter_name: rate-200M
      wrr_queue_3_classes: ['C', 'D', 'E']
      wrr_queue_3_rate_limiter_name: rate-500M-1000M
      wrr_queue_4_classes: ['F', 'G', 'H']
      wrr_queue_4_rate_limiter_name: rate-200M-1000M
    - ingress_qos_policy_name: MPLS-Provider-2-6QoS-1000M
      parent_rate_limiter_name: rate-1000M
      priority_queue_1_classes: ['A']
      priority_queue_1_rate_limiter_name: rate-100M
      wrr_queue_2_classes: ['B']
      wrr_queue_2_rate_limiter_name: rate-200M
      wrr_queue_3_classes: ['C', 'D', 'E']
      wrr_queue_3_rate_limiter_name: rate-500M-1000M
      wrr_queue_4_classes: ['F', 'G', 'H']
      wrr_queue_4_rate_limiter_name: rate-200M-1000M

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
    IngressQOSPolicy
        name = 'MPLS-Provider-1-6QoS-1000M'
        queue4AssociatedRateLimiterID = [retrieve wrr_queue_4_rate_limiter_id (RateLimiter:id)]
        queue1AssociatedRateLimiterID = [retrieve priority_queue_1_rate_limiter_id (RateLimiter:id)]
        queue2AssociatedRateLimiterID = [retrieve wrr_queue_2_rate_limiter_id (RateLimiter:id)]
        queue2ForwardingClasses = ['B']
        queue3ForwardingClasses = ['C', 'D', 'E']
        queue4ForwardingClasses = ['F', 'G', 'H']
        queue3AssociatedRateLimiterID = [retrieve wrr_queue_3_rate_limiter_id (RateLimiter:id)]
        parentQueueAssociatedRateLimiterID = [retrieve parent_rate_limiter_id (RateLimiter:id)]
        queue1ForwardingClasses = ['A']
        description = 'ingress QoS policy MPLS-Provider-1-6QoS-1000M'
    IngressQOSPolicy
        name = 'MPLS-Provider-2-6QoS-1000M'
        queue4AssociatedRateLimiterID = [retrieve wrr_queue_4_rate_limiter_id (RateLimiter:id)]
        queue1AssociatedRateLimiterID = [retrieve priority_queue_1_rate_limiter_id (RateLimiter:id)]
        queue2AssociatedRateLimiterID = [retrieve wrr_queue_2_rate_limiter_id (RateLimiter:id)]
        queue2ForwardingClasses = ['B']
        queue3ForwardingClasses = ['C', 'D', 'E']
        queue4ForwardingClasses = ['F', 'G', 'H']
        queue3AssociatedRateLimiterID = [retrieve wrr_queue_3_rate_limiter_id (RateLimiter:id)]
        parentQueueAssociatedRateLimiterID = [retrieve parent_rate_limiter_id (RateLimiter:id)]
        queue1ForwardingClasses = ['A']
        description = 'ingress QoS policy MPLS-Provider-2-6QoS-1000M'

```
