## Feature Template: Bidirectional Security Policy
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
