## Feature Template: Dscp Remarking Policy
#### Examples

##### Setting DSCP Bits Based on Service Provider 6 class QoS Model
This example sets the DSCP Bits based on two different service provider 6 class QoS models. One Service Provider is using a Diffserv based marking scheme while another is using a CS scheme. This example maps the 8 Forwarding Classes into the correct scheme.It sets the marking according to the Service Provider requirements.  nsg-qos-dhcp-remarking-policy.yaml
```
- template: Dscp Remarking Policy
  values:
    - dscp_remarking_policy_name: MPLS-Provider-1
      description: "DSCP Alignment for MPLS Provider 1 / DiffServ"
      forwarding_classes: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
      remarking_dscp_list: ['46', '34', '26', '18', '10', '0', '0', '0']
    - dscp_remarking_policy_name: MPLS-Provider-2
      description: "DSCP Alignment for MPLS Provider 2 / CS"
      forwarding_classes: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
      remarking_dscp_list: ['40', '32', '24', '16', '8', '0', '0', '0']

```
```
(example)$ metroae config create user-data.yml
    DSCPRemarkingPolicyTable
        name = 'MPLS-Provider-1'
        description = 'DSCP Alignment for MPLS Provider 1 / DiffServ'
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
    DSCPRemarkingPolicyTable
        name = 'MPLS-Provider-2'
        description = 'DSCP Alignment for MPLS Provider 2 / CS'
        DSCPRemarkingPolicy
            forwardingClass = 'A'
            DSCP = '40'
        DSCPRemarkingPolicy
            forwardingClass = 'B'
            DSCP = '32'
        DSCPRemarkingPolicy
            forwardingClass = 'C'
            DSCP = '24'
        DSCPRemarkingPolicy
            forwardingClass = 'D'
            DSCP = '16'
        DSCPRemarkingPolicy
            forwardingClass = 'E'
            DSCP = '8'
        DSCPRemarkingPolicy
            forwardingClass = 'F'
            DSCP = '0'
        DSCPRemarkingPolicy
            forwardingClass = 'G'
            DSCP = '0'
        DSCPRemarkingPolicy
            forwardingClass = 'H'
            DSCP = '0'

```
