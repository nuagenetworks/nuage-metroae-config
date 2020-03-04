## Feature Template: Enterprise
#### Examples

##### Creating an Enterprise with Minimal Data
In this example we will create a single Enterprise with default features enabled. enterprise-default.yaml
```
- template: Enterprise
  values:
    enterprise_name: SimpleEnterprise

```
```
(example)$ metroae config create user-data.yml
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
(example)$ metroae config create user-data.yml
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
(example)$ metroae config create user-data.yml
    EnterpriseProfile
        allowedForwardingClasses = ['A', 'B', 'C', 'D']
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
(example)$ metroae config create user-data.yml
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
