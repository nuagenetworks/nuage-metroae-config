## Feature Template: Zone
#### Examples

##### Creating Subnets in an Existing Enterprise and Domain
This example creates two Zones, both in the same Enterprise and Domain. All parameters are listed for each Zone to be created.  network-zone-flat.yaml
```
- template: Zone
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    zone_name: West-Zone
- template: Zone
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    zone_name: East-Zone

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            Zone
                name = 'West-Zone'
                description = 'Zone West-Zone'
            Zone
                name = 'East-Zone'
                description = 'Zone East-Zone'

```

##### Creating Zones in an existing Enterprise and Domain Using Group Inheritance
The common attributes (Enterprise and Domain) are listed under group, and the Zones are created as children.  network-zone-groups.yaml
```
- group: DemoEnterprise
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
  children:
    - template: Zone
      values:
        - zone_name: West-Zone
        - zone_name: East-Zone

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            Zone
                name = 'West-Zone'
                description = 'Zone West-Zone'
            Zone
                name = 'East-Zone'
                description = 'Zone East-Zone'

```
