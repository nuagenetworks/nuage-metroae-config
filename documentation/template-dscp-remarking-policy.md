## Feature Template: Dscp Remarking Policy
#### Description
Set DSCP bits on outgoing IP packets on NSG Ports with the DSCP Remarking Policy feature template.

#### Usage
Campus and Service Provider access networks often use DSCP bits in the IP header to indicate a target Quality of Service for packet treatment across the network. The DSCP Remarking Policy which is attached to a NSG Port VLAN provides the ability to set the DSCP bits based on the Forwarding Class of each packet. The network in which the NSG is connected to for transport uses the DSCP bits to determine what Diffserv or QoS treatment each packet receives. For Network ports the treatment is typically part of the service contract with the service provider.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/dscp_remarking_policy.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Set DSCP bits on outgoing IP packets on NSG Ports with the DSCP Remarking Policy feature template.
- template: Dscp Remarking Policy
  values:
    - enterprise_name: ""                      # (opt reference) DSCP Remarking Policy can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.
      description: ""                          # (opt string) optional description of the DSCP Remarking Policy.
      dscp_remarking_policy_name: ""           # (string) name of the DSCP Remarking Policy.
      forwarding_classes: []                   # (opt list of choice) list of forwarding classes that will have DSCP Bits marked. Length of forwarding_classes must match dscp_list.
      dscp_list: []                            # (opt list of string) matching list of markings to be used per Forwarding Class. DSCP is a 6 bit field and decimal values from 0 to 63 are valid.

```

#### Parameters
*enterprise_name:* DSCP Remarking Policy can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.<br>
*description:* optional description of the DSCP Remarking Policy.<br>
*dscp_remarking_policy_name:* name of the DSCP Remarking Policy.<br>
*forwarding_classes:* list of forwarding classes that will have DSCP Bits marked. Length of forwarding_classes must match dscp_list.<br>
*dscp_list:* matching list of markings to be used per Forwarding Class. DSCP is a 6 bit field and decimal values from 0 to 63 are valid.<br>


#### Restrictions
**create:**
* Name of DSCP Remarking Policy must be unique.
* Each forwarding class can only have a single entry.
* Forwarding Classes and Remarking DSCP List must have the same number of entries.

**revert:**
* Cannot revert a COS Remarking Policy that is attached to a QOS Egress Policy.

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
