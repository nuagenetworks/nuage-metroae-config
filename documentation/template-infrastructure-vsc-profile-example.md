## Feature Template: Infrastructure Vsc Profile
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
(example)$ metroae config create user-data.yml
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
(example)$ metroae config create user-data.yml
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
