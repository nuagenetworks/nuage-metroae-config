## Feature Template: Infrastructure Vsc Profile
#### Description
Define the sets of VSCs that are used for NSG control in a WAN environment with the Infrastructure VSC Profile template.

#### Usage
As part of the definition of NSG infrastructure a set of VSCs must be assigned to each NSG. The VSCs are assigned on a HA Pair basis and are typically aligned to NSG uplinks (Network Ports).

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/infrastructure_vsc_profile.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define the sets of VSCs that are used for NSG control in a WAN environment with the Infrastructure VSC Profile template.
- template: Infrastructure Vsc Profile
  values:
    - infrastructure_vsc_profile_name: ""      # (string) name of the VSC Profile.
      description: ""                          # (opt string) optional description for the VSC Profile.
      primary_controller_address: ""           # (string) IPv4 address of the primary controller.
      secondary_controller_address: ""         # (opt string) optional IPv4 address of the secondary controller.
      probe_interval_msec: 0                   # (opt integer) optional interval in ms of probes sent to VSC to verify OF connectivity.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
infrastructure_vsc_profile_name | required | string | name of the VSC Profile.
description | optional | string | optional description for the VSC Profile.
primary_controller_address | required | string | IPv4 address of the primary controller.
secondary_controller_address | optional | string | optional IPv4 address of the secondary controller.
probe_interval_msec | optional | integer | optional interval in ms of probes sent to VSC to verify OF connectivity.


#### Restrictions
**create:**
* VSC Profile name must be unique.
* VSC Profiles are created in Platform Configuration only.
* VSC Address Family IPv4 only.

**revert:**
* Cannot revert a VSC Profile that is currently in use on a NSG Network Port.

