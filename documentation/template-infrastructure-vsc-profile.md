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
*infrastructure_vsc_profile_name:* name of the VSC Profile.<br>
*description:* optional description for the VSC Profile.<br>
*primary_controller_address:* IPv4 address of the primary controller.<br>
*secondary_controller_address:* optional IPv4 address of the secondary controller.<br>
*probe_interval_msec:* optional interval in ms of probes sent to VSC to verify OF connectivity.<br>


#### Restrictions
**create:**
* VSC Profile name must be unique.
* VSC Profiles are created in Platform Configuration only.
* VSC Address Family IPv4 only.

**revert:**
* Cannot revert a VSC Profile that is currently in use on a NSG Network Port.

#### Examples

##### Creating a VSC Profile with a Single VSC
This example creates a VSC Profile with a single VSC assigned and default values for optional parameters.  nsg-infrastructure-vsc-profile-sa.yaml
```
- template: Infrastructure Vsc Profile
  values:
    - infrastructure_vsc_profile_name: Provider-1-VSC-East
      primary_controller_address: 192.168.1.200

```
```
[metroae-user@metroae-host]# metroae config create nsg-vscprofile-sa.yml
    InfrastructureVscProfile
        description = 'Infrastructure VSC Profile Provider-1-VSC-East'
        name = 'Provider-1-VSC-East'
        firstController = '192.168.1.200'

```

##### Creating Multiple VSC Profiles with Redundant VSCs
This example creates multiple VSC Profiles supporting different transport network providers, each with redundant VSCs along with setting VSC probe interval.  nsg-infrastructure-vsc-profile-ha.yaml
```
- template: Infrastructure Vsc Profile
  values:
    - infrastructure_vsc_profile_name: Provider-1-VSC-East
      primary_controller_address: 192.168.10.200
      secondary_controller_address: 192.168.10.201

    - infrastructure_vsc_profile_name: Provider-2-VSC-East
      primary_controller_address: 172.16.10.200
      secondary_controller_address: 172.16.10.201
      probe_interval_msec: 15000

    - infrastructure_vsc_profile_name: Provider-1-VSC-West
      primary_controller_address: 192.168.11.200
      secondary_controller_address: 192.168.11.201

    - infrastructure_vsc_profile_name: Provider-2-VSC-West
      primary_controller_address: 172.16.11.200
      secondary_controller_address: 172.16.11.201
      probe_interval_msec: 15000

```
```
[metroae-user@metroae-host]# metroae config create nsg-vscprofile-ha.yml
InfrastructureVscProfile
    secondController = '192.168.10.201'
    description = 'Infrastructure VSC Profile Provider-1-VSC-East'
    name = 'Provider-1-VSC-East'
    firstController = '192.168.10.200'
InfrastructureVscProfile
    probeInterval = 15000
    secondController = '172.16.10.201'
    description = 'Infrastructure VSC Profile Provider-2-VSC-East'
    name = 'Provider-2-VSC-East'
    firstController = '172.16.10.200'
InfrastructureVscProfile
    secondController = '192.168.11.201'
    description = 'Infrastructure VSC Profile Provider-1-VSC-West'
    name = 'Provider-1-VSC-West'
    firstController = '192.168.11.200'
InfrastructureVscProfile
    probeInterval = 15000
    secondController = '172.16.11.201'
    description = 'Infrastructure VSC Profile Provider-2-VSC-West'
    name = 'Provider-2-VSC-West'
    firstController = '172.16.11.200'

```
