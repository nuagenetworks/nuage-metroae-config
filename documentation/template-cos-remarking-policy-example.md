## Feature Template: Cos Remarking Policy
#### Examples

##### Setting 802.1P CoS Bits Based on Service Provider 3 Classes.
This example sets the COS Bits based on a service provider 3 class model. The provider has deemed COS 5 to be the highest class, COS 3 to be bulk class and COS 0 to be best effort.  nsg-qos-cos-remarking-profile.yaml
```
- template: Cos Remarking Policy
  values:
    - cos_remarking_policy_name: MPLS-Provider-1-COS
      forwarding_classes: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
      remarking_cos_list: ['5', '5', '3', '3', '3', '3', '0', '0']

```
```
(example)$ metroae config create user-data.yml
    COSRemarkingPolicyTable
        name = 'MPLS-Provider-1-COS'
        description = 'CoS remarking policy MPLS-Provider-1-COS'
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

```
