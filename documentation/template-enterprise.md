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
*enterprise_name:* name of the Enterprise being created.<br>
*description:* optional description of the enterprise. Defaults to "enterprise <enterprise_name>".<br>
*enterprise_profile_name:* optional for attaching an existing Organization Profile to the new Enterprise.<br>
*forwarding_classes:* optional list of enabled forwarding classes. Defaults to all classes.<br>
*routing_protocols_enabled:* optional enablement of Routing protocols in the Enterprise. Defaults to disabled.<br>
*local_as:* <br>
*dhcp_lease_interval:* optional lease time which is returned in DHCP Offers. Defaults to 24.<br>
*vnf_management_enabled:* optional enablement VNF hosting on VNS NSGs. Defaults to disabled.<br>
*allow_advanced_qos_configuration:* optional enablement of Advanced QoS features. Defaults to disabled.<br>
*allow_gateway_management:* optional enablement of gateway management within the Enterprise (not csproot). Defaults to disabled.<br>
*allow_trusted_forwarding_classes:* optional enablement of DSCP trust. Defaults to disabled.<br>
*enable_application_performance_management:* optional enablement of the AAR feature suite. Defaults to disabled.<br>
*encryption_management_mode:* optional enablement of Encryption features within the Enterprise. Defaults to disabled.<br>
*floating_ips_quota:* optional number of floating IPs that can be assigned within the Enterprise. Defaults to 0.<br>


#### Restrictions
**create:**
* You must include a value for enterprise_name in the template.
* The enterprise_name must be unique to the VSD.
* If Routing Protocols are enabled, then a local_as must be included.
* Feature enablement must have entitlement license in place.

**revert:**
* You cannot revert an Enterprise which has domains.
* You cannot revert an Enterprise which has activated NSGs.

#### Examples

##### Creating an Enterprise with Minimal Data
In this example we will create a single Enterprise with default features enabled. enterprise-default.yaml
```
- template: Enterprise
  values:
    enterprise_name: SimpleEnterprise

```
```
[root@oc-ebc-config-1 feature-samples]# metroae config create enterprise-default.yaml
Device: Nuage Networks VSD 5.4.1
    EnterpriseProfile
        VNFManagementEnabled = False
        allowedForwardingClasses = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        description = 'profile for SimpleEnterprise'
        enableApplicationPerformanceManagement = False
        name = 'profile_SimpleEnterprise'
        [store id to name enterprise_profile_id]
    Enterprise
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'SimpleEnterprise'
        description = 'enterprise SimpleEnterprise'

```

##### Creating an Enterprise with an existing Organization Profile
In this example we will create an Enterprise and link it to an existing Organization Profile. enterprise-reuse-org-profile.yaml
```
- template: Enterprise
  values:
    enterprise_name: ReuseEnterprise
    enterprise_profile_name: "Existing Profile"

```
```
[root@oc-ebc-config-1 feature-samples]# metroae config create enterprise-reuse-org-profile.yaml
Device: Nuage Networks VSD 5.4.1
    [select EnterpriseProfile (name of Existing Profile)]
        [store id to name enterprise_profile_id]
    Enterprise
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'ReuseEnterprise'
        description = 'enterprise ReuseEnterprise'

```

##### Creating an Enterprise with optional features enabled
In this example we will create an enterprise enabling specific features. enterprise-options.yaml
```
- template: Enterprise
  values:
    enterprise_name: AdvancedEnterprise
    description: "All the good stuff enabled"
    local_as: 65000
    forwarding_classes: [A, B, C, D]
    bgp_enabled: True
    vnf_management_enabled: True
    allow_advanced_qos_configuration: True
    allow_gateway_management: True
    allow_trusted_forwarding_classes: True
    enable_application_performance_management: True
    encryption_management_mode: managed
    floating_ips_quota: 100

```
```
[root@oc-ebc-config-1 feature-samples]# metroae config create enterprise-options.yaml
Device: Nuage Networks VSD 5.4.1
    EnterpriseProfile
        allowedForwardingClasses = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        allowGatewayManagement = True
        description = 'All the good stuff enabled'
        enableApplicationPerformanceManagement = True
        floatingIPsQuota = 100
        encryptionManagementMode = 'MANAGED'
        allowAdvancedQOSConfiguration = True
        VNFManagementEnabled = True
        name = 'profile_AdvancedEnterprise'
        [store id to name enterprise_profile_id]
    Enterprise
        localAS = 65000
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'AdvancedEnterprise'
        description = 'All the good stuff enabled'

```

##### Creating an Enterprise with optional features enabled using groups
In this example we will create two enterprises with similar configurations using groups. enterprise-demo.yaml
```
- group: Enterprises
  values:
    forwarding_classes: [A, B, C, D, E, F, G, H]
    bgp_enabled: True
    vnf_management_enabled: True
    allow_advanced_qos_configuration: True
    allow_gateway_management: True
    allow_trusted_forwarding_classes: True
    enable_application_performance_management: True
    encryption_management_mode: managed
    floating_ips_quota: 100
  children:
    - template: Enterprise
      values:
        - enterprise_name: DemoEnterprise
          description: "1st Enterprise for demo"
          local_as: 65000
        - enterprise_name: SecondEnterprise
          description: "2nd Enterprise for demo"
          local_as: 65001

```
```
[root@oc-ebc-config-1 feature-samples]# metroae config create enterprise-demo.yaml
Device: Nuage Networks VSD 5.4.1
    EnterpriseProfile
        allowedForwardingClasses = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        allowGatewayManagement = True
        description = '1st Enterprise for demo'
        enableApplicationPerformanceManagement = True
        floatingIPsQuota = 100
        encryptionManagementMode = 'MANAGED'
        allowAdvancedQOSConfiguration = True
        VNFManagementEnabled = True
        name = 'profile_DemoEnterprise'
        [store id to name enterprise_profile_id]
    Enterprise
        localAS = 65000
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'DemoEnterprise'
        description = '1st Enterprise for demo'
    EnterpriseProfile
        allowedForwardingClasses = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        allowGatewayManagement = True
        description = '2nd Enterprise for demo'
        enableApplicationPerformanceManagement = True
        floatingIPsQuota = 100
        encryptionManagementMode = 'MANAGED'
        allowAdvancedQOSConfiguration = True
        VNFManagementEnabled = True
        name = 'profile_SecondEnterprise'
        [store id to name enterprise_profile_id]
    Enterprise
        localAS = 65001
        enterpriseProfileID = [retrieve enterprise_profile_id (EnterpriseProfile:id)]
        name = 'SecondEnterprise'
        description = '2nd Enterprise for demo'

```
