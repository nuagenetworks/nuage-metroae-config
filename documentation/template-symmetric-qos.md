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
*enterprise_name:* QoS Policies can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.<br>
*symmetric_qos_policy_name:* name to apply to Symmetric QoS Policy objects.<br>
*description:* optional description of the all QoS Policy objects.<br>
*default_service_class:* service class to use for unclassified traffic.<br>
*parent_committed_information_rate:* CIR for the port in Mbps. Traffic above this threshold subject to real time queue conditions and available bandwidth on the port. IF PIR=CIR then any traffic above this rate will be dropped.<br>
*parent_peak_information_rate:* PIR for the port in Mbps. Any traffic above this rate with be dropped.<br>
*parent_peak_burst_size:* burst size in Kb applied to the rate limiter token bucket for the parent queue.<br>
*priority_queue_1_classes:* list of the Forwarding Classes assigned to the Priority Queue.<br>
*priority_queue_1_committed_information_rate:* guaranteed or Committed Information Rate for the priority queue in Mbps.<br>
*priority_queue_1_peak_information_rate:* PIR for the priority queue in Mbps. Any traffic above this rate with be dropped.<br>
*priority_queue_1_peak_burst_size:* burst size in Kb applied to the rate limiter token bucket for the priority queue.<br>
*wrr_queue_2_classes:* list of the Forwarding Classes assigned to the WRR Q2.<br>
*wrr_queue_2_committed_information_rate:* guaranteed or Committed Information Rate for queue 2 in Mbps.<br>
*wrr_queue_2_peak_information_rate:* PIR for queue 2 in Mbps. Any traffic above this rate with be dropped.<br>
*wrr_queue_2_peak_burst_size:* burst size in Kb applied to the rate limiter token bucket for queue 2.<br>
*wrr_queue_3_classes:* list of the Forwarding Classes assigned to the WRR Q3.<br>
*wrr_queue_3_committed_information_rate:* guaranteed or Committed Information Rate for queue 3 in Mbps.<br>
*wrr_queue_3_peak_information_rate:* PIR for queue 3 in Mbps. Any traffic above this rate with be dropped.<br>
*wrr_queue_3_peak_burst_size:* burst size in Kb applied to the rate limiter token bucket for queue 2.<br>
*wrr_queue_4_classes:* list of the Forwarding Classes assigned to the WRR Q4.<br>
*wrr_queue_4_committed_information_rate:* guaranteed or Committed Information Rate for queue 4 in Mbps.<br>
*wrr_queue_4_peak_information_rate:* PIR for queue 4 in Mbps. Any traffic above this rate with be dropped.<br>
*wrr_queue_4_peak_burst_size:* burst size in Kb applied to the rate limiter token bucket for queue 2.<br>
*cos_remarking_classes:* list of forwarding classes that will have COS Bits marked.<br>
*cos_remarking_cos_list:* matching list of markings to be used per Forwarding Class. CoS is a 3 bit field and decimal values<br>
*dscp_remarking_classes:* list of forwarding classes that will have DSCP Bits marked.<br>
*dscp_remarking_dscp_list:* matching list of markings to be used per Forwarding Class. DSCP is a 6 bit field and decimal values from 0 to 63 are valid.<br>


#### Restrictions
**create:**
* Symmetric QoS Policy name must be unique.
* Forwarding Classed can only be assigned to a single queue.
* Sum of queue rate limiters CIR cannot exceed the port CIR rate limiter.
* A child rate limiter PIR cannot exceed the Parent rate limiter.

**revert:**
* Symmetric QoS policy cannot reverted if it is attached a NSG port.

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
[root@oc-ebc-config-1 feature-samples]# metroae config create nsg-qos-symmetric-policy.yaml
Device: Nuage Networks VSD 5.4.1
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
