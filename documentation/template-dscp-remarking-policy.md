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
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | optional | reference | DSCP Remarking Policy can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.
description | optional | string | optional description of the DSCP Remarking Policy.
dscp_remarking_policy_name | required | string | name of the DSCP Remarking Policy.
forwarding_classes | optional | list | list of forwarding classes that will have DSCP Bits marked. Length of forwarding_classes must match dscp_list.
dscp_list | optional | list | matching list of markings to be used per Forwarding Class. DSCP is a 6 bit field and decimal values from 0 to 63 are valid.


#### Restrictions
**create:**
* Name of DSCP Remarking Policy must be unique.
* Each forwarding class can only have a single entry.
* Forwarding Classes and Remarking DSCP List must have the same number of entries.

**revert:**
* Cannot revert a COS Remarking Policy that is attached to a QOS Egress Policy.

