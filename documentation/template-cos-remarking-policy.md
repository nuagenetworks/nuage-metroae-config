## Feature Template: Cos Remarking Policy
#### Description
Set 802.1P COS bits on outgoing ethernet frames on NSG Ports with the CoS Remarking Policy feature template.

#### Usage
Campus and Service Provider access networks will sometimes use 802.1P COS bits in the Ethernet VLAN header to indicate a target Class of Service for packet treatment across the network. The CoS Remarking Policy which is attached to an NSG Port VLAN provides the ability to set the 802.1P COS bits based on the Forwarding Class of each packet. The network in which the NSG is connected to for transport will use the 802.1P COS bits to determine what COS treatment each packet receives. For Network ports the treatment is typically part of the service contract with the service provider.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/cos_remarking_policy.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Set 802.1P COS bits on outgoing ethernet frames on NSG Ports with the CoS Remarking Policy feature template.
- template: Cos Remarking Policy
  values:
    - enterprise_name: ""                      # (opt reference) CoS Remarking Policy can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.
      description: ""                          # (opt string) optional description of the CoS Remarking Policy.
      cos_remarking_policy_name: ""            # (string) name of the CoS Remarking Policy.
      forwarding_classes: []                   # (opt list of choice) list of forwarding classes that will have COS Bits marked. Length of forwarding_classes must match length of remarking_cos_list.
      remarking_cos_list: []                   # (opt list of string) matching list of markings to be used per Forwarding Class. CoS is a 3 bit field and decimal values from 0 to 7 are valid.

```

#### Parameters
*enterprise_name:* CoS Remarking Policy can be configured in the Platform Configuration or within an Enterprise. Optional additional of the Enterprise Name to configure it within an Enterprise only.<br>
*description:* optional description of the CoS Remarking Policy.<br>
*cos_remarking_policy_name:* name of the CoS Remarking Policy.<br>
*forwarding_classes:* list of forwarding classes that will have COS Bits marked. Length of forwarding_classes must match length of remarking_cos_list.<br>
*remarking_cos_list:* matching list of markings to be used per Forwarding Class. CoS is a 3 bit field and decimal values from 0 to 7 are valid.<br>


#### Restrictions
**create:**
* Name of CoS Remarking Policy must be unique.
* Each forwarding class can only have a single entry.
* Forwarding Classes and Remarking COS List must have the same number of entries.
* CoS Remarking Policy can only be attached to Ports with non default VLAN. ie. not VLAN 0.

**revert:**
* Cannot revert a COS Remarking Policy that is attached to a QOS Egress Policy.

