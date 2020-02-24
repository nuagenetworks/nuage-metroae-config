## Feature Template: Bidirectional Security Policy
#### Description
Create ingress and egress security policies on a specific domain with the Bidirectional Security Policy feature template. The feature template automatically creates both ingress and egress policies based on the data provided.

#### Usage
Security Policies are used in VSD to permit, deny and mirror traffic to/from overlay endpoints. Ingress Policies are in relation to traffic received from a VM/container or access network on a VRS host or NSG. Egress Policies are in relation to traffic transmitted to a VM/container or access network. In a typical workflow a user must configure both Ingress and Egress rules discretely, however Bidirectional Security Policy feature template creates both Policies automatically. The Security Policy is not the set of rules, those are configured via Security Policy Entries, however it is a collection of rules that are created based on similar requirements/desired behavior.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/bidirectional_security_policy.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create ingress and egress security policies on a specific domain with the Bidirectional Security Policy feature template. The feature template automatically creates both ingress and egress policies based on the data provided.
- template: Bidirectional Security Policy
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise where the Security Policy will be created.
      domain_name: ""                          # (reference) name of the domain where the Security Policy will be applied.
      security_policy_name: ""                 # (string) name of the Security Policy to be created.
      domain_type: l2domain                    # (['l2domain', 'l3domain'])
      description: ""                          # (opt string) optional description of the Security Policy.
      default_allow_ip: False                  # (boolean) enablement of allowing all IP traffic.
      default_allow_non_ip: False              # (boolean) enablement of allowing all non IP traffic.
      policy_priority: 0                       # (integer) priority of the policy in ascending order.
      allow_address_spoof: False               # (boolean) enablement of address spoofing for packets hitting the Ingress Security Policy.
      default_install_acl_implicit_rules: False # (boolean) add implicit denies to end of the Egress Security Policy.
      active: False                            # (opt boolean) enable or disable the Security Policy.

```

#### Parameters
*enterprise_name:* name of the enterprise where the Security Policy will be created.<br>
*domain_name:* name of the domain where the Security Policy will be applied.<br>
*security_policy_name:* name of the Security Policy to be created.<br>
*domain_type:* <br>
*description:* optional description of the Security Policy.<br>
*default_allow_ip:* enablement of allowing all IP traffic.<br>
*default_allow_non_ip:* enablement of allowing all non IP traffic.<br>
*policy_priority:* priority of the policy in ascending order.<br>
*allow_address_spoof:* enablement of address spoofing for packets hitting the Ingress Security Policy.<br>
*default_install_acl_implicit_rules:* add implicit denies to end of the Egress Security Policy.<br>
*active:* enable or disable the Security Policy.<br>


#### Restrictions
**create:**
* Security Policy Name must be unique within each domain.
* Policy priority value can only be used once within each domain.

#### Examples

##### Creating a Single Security Policy
This example creates a single security policy. security-bd-sec-policy-flat.yaml
```
- template: Bidirectional Security Policy
  values:
      enterprise_name: DemoEnterprise
      security_policy_name: Intrazone-West
      domain_type: l3domain
      domain_name: L3-Domain-US
      policy_priority: 1000
      default_allow_ip: False
      default_allow_non_ip: False
      allow_address_spoof: False
      default_install_acl_implicit_rules: True
      active: True

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            IngressACLTemplate
                description = 'Ingress ACL template Intrazone-West'
                priority = 1000
                defaultAllowNonIP = False
                defaultAllowIP = False
                active = True
                allowAddressSpoof = False
                name = 'Intrazone-West'
            EgressACLTemplate
                priority = 1000
                description = 'Egress ACL template Intrazone-West'
                defaultInstallACLImplicitRules = True
                defaultAllowNonIP = False
                defaultAllowIP = False
                active = True
                name = 'Intrazone-West'

```

##### Creating Multiple Security Policies Using Groups
This example creates a series of security policies, using groups for repeated configuration on each Security Policy.  security-bd-sec-policy-groups.yaml
```
- group: policy_options1
  values:
    enterprise_name: DemoEnterprise
    domain_type: l3domain
    default_allow_ip: False
    default_allow_non_ip: False
    allow_address_spoof: False
    default_install_acl_implicit_rules: True
    active: True
  children:
    - template: Bidirectional Security Policy
      values:
        - security_policy_name: Intrazone-West
          domain_name: L3-Domain-US
          policy_priority: 1000
        - security_policy_name: Intrazone-East
          domain_name: L3-Domain-US
          policy_priority: 2000
        - security_policy_name: Interzone-East-West
          domain_name: L3-Domain-US
          policy_priority: 3000

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            IngressACLTemplate
                description = 'Ingress ACL template Intrazone-West'
                priority = 1000
                defaultAllowNonIP = False
                defaultAllowIP = False
                active = True
                allowAddressSpoof = False
                name = 'Intrazone-West'
            EgressACLTemplate
                priority = 1000
                description = 'Egress ACL template Intrazone-West'
                defaultInstallACLImplicitRules = True
                defaultAllowNonIP = False
                defaultAllowIP = False
                active = True
                name = 'Intrazone-West'
            IngressACLTemplate
                description = 'Ingress ACL template Intrazone-East'
                priority = 2000
                defaultAllowNonIP = False
                defaultAllowIP = False
                active = True
                allowAddressSpoof = False
                name = 'Intrazone-East'
            EgressACLTemplate
                priority = 2000
                description = 'Egress ACL template Intrazone-East'
                defaultInstallACLImplicitRules = True
                defaultAllowNonIP = False
                defaultAllowIP = False
                active = True
                name = 'Intrazone-East'
            IngressACLTemplate
                description = 'Ingress ACL template Interzone-East-West'
                priority = 3000
                defaultAllowNonIP = False
                defaultAllowIP = False
                active = True
                allowAddressSpoof = False
                name = 'Interzone-East-West'
            EgressACLTemplate
                priority = 3000
                description = 'Egress ACL template Interzone-East-West'
                defaultInstallACLImplicitRules = True
                defaultAllowNonIP = False
                defaultAllowIP = False
                active = True
                name = 'Interzone-East-West'

```
