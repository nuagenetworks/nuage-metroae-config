## Feature Template: Enterprise
#### Description
Create "tenant" in VSD with the Enterprise feature template. An Enterprise is sometimes referred to as an Organization, or a Partition in the OpenStack use case.

#### Usage
Each Enterprise in VSD is defined with an attached Organization Profile which enables additional feature sets in an Enterprise. Typically you would create an Organization Profile, create an Enterprise, then attach the profile to the Enterprise.

The Enterprise feature template automatically creates an Organization Profile for each new Enterprise based on provided user data. Thus, defining Enterprise and enabling advanced features for that Enterprise are handled in one *create* step.

You can create an Enterprise with an existing Organization Profile simply by specifying which Organization Profile (enterprise_profile_name) to use.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/enterprise.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create "tenant" in VSD with the Enterprise feature template. An Enterprise is sometimes referred to as an Organization, or a Partition in the OpenStack use case.
- template: Enterprise
  values:
    - enterprise_name: ""                      # (string) name of the Enterprise being created.
      description: ""                          # (opt string) optional description of the enterprise. Defaults to "enterprise <enterprise_name>".
      enterprise_profile_name: ""              # (opt reference) optional for attaching an existing Organization Profile to the new Enterprise.
      forwarding_classes: []                   # (opt list of choice) optional list of enabled forwarding classes. Defaults to all classes.
      routing_protocols_enabled: False         # (opt boolean) optional enablement of Routing protocols in the Enterprise. Defaults to disabled.
      local_as: 0                              # (opt integer)
      dhcp_lease_interval: 0                   # (opt integer) optional lease time which is returned in DHCP Offers. Defaults to 24.
      vnf_management_enabled: False            # (opt boolean) optional enablement VNF hosting on VNS NSGs. Defaults to disabled.
      allow_advanced_qos_configuration: False  # (opt boolean) optional enablement of Advanced QoS features. Defaults to disabled.
      allow_gateway_management: False          # (opt boolean) optional enablement of gateway management within the Enterprise (not csproot). Defaults to disabled.
      allow_trusted_forwarding_classes: False  # (opt boolean) optional enablement of DSCP trust. Defaults to disabled.
      enable_application_performance_management: False # (opt boolean) optional enablement of the AAR feature suite. Defaults to disabled.
      encryption_management_mode: disabled     # (opt ['disabled', 'managed']) optional enablement of Encryption features within the Enterprise. Defaults to disabled.
      floating_ips_quota: 0                    # (opt integer) optional number of floating IPs that can be assigned within the Enterprise. Defaults to 0.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | string | name of the Enterprise being created.
description | optional | string | optional description of the enterprise. Defaults to "enterprise <enterprise_name>".
enterprise_profile_name | optional | reference | optional for attaching an existing Organization Profile to the new Enterprise.
forwarding_classes | optional | list | optional list of enabled forwarding classes. Defaults to all classes.
routing_protocols_enabled | optional | boolean | optional enablement of Routing protocols in the Enterprise. Defaults to disabled.
local_as | optional | integer | 
dhcp_lease_interval | optional | integer | optional lease time which is returned in DHCP Offers. Defaults to 24.
vnf_management_enabled | optional | boolean | optional enablement VNF hosting on VNS NSGs. Defaults to disabled.
allow_advanced_qos_configuration | optional | boolean | optional enablement of Advanced QoS features. Defaults to disabled.
allow_gateway_management | optional | boolean | optional enablement of gateway management within the Enterprise (not csproot). Defaults to disabled.
allow_trusted_forwarding_classes | optional | boolean | optional enablement of DSCP trust. Defaults to disabled.
enable_application_performance_management | optional | boolean | optional enablement of the AAR feature suite. Defaults to disabled.
encryption_management_mode | optional | choice | optional enablement of Encryption features within the Enterprise. Defaults to disabled.
floating_ips_quota | optional | integer | optional number of floating IPs that can be assigned within the Enterprise. Defaults to 0.


#### Restrictions
**create:**
* You must include a value for enterprise_name in the template.
* The enterprise_name must be unique to the VSD.
* If Routing Protocols are enabled, then a local_as must be included.
* Feature enablement must have entitlement license in place.

**revert:**
* You cannot revert an Enterprise which has domains.
* You cannot revert an Enterprise which has activated NSGs.

