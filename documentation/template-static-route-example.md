## Feature Template: Static Route
#### Examples

##### Creating a Static Route in a Domain
This example configures a single static route within a domain. In this case all required parameters are listed within the user data Static Route template definition.  network-static-route-flat.yaml
```
- template: Static Route
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    address: 172.16.0.0
    netmask: 255.255.0.0
    next_hop: 100.1.1.10

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.1.10'
                address = '172.16.0.0'

```

##### Creating Static Routes Using Group Inheritance
This example defines multiple static routes within a domain, however we will define the required Enterprise and Domain in a group rather than repeating for each entry.  network-static-route-groups-child.yaml
```
- group: StaticRoutes
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
  children:
    - template: Static Route
      values:
        - address: 172.16.0.0
          netmask: 255.255.0.0
          next_hop: 100.1.1.10
        - address: 172.17.0.0
          netmask: 255.255.0.0
          next_hop: 100.1.2.15
        - address: 172.25.0.0
          netmask: 255.255.0.0
          next_hop: 200.1.1.20

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.1.10'
                address = '172.16.0.0'
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.2.15'
                address = '172.17.0.0'
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '200.1.1.20'
                address = '172.25.0.0'

```

##### Creating Static Routes Using Group Substitution
This example creates multiple static routes but rather than inheriting the group values as a child we are doing a substitution.  network-static-route-groups-sub.yaml
```
- group: StaticRoutes
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US

- template: Static Route
  values:
    - $group_domain: StaticRoutes
      address: 172.16.0.0
      netmask: 255.255.0.0
      next_hop: 100.1.1.10
    - $group_domain: StaticRoutes
      address: 172.17.0.0
      netmask: 255.255.0.0
      next_hop: 100.1.2.15
    - $group_domain: StaticRoutes
      address: 172.25.0.0
      netmask: 255.255.0.0
      next_hop: 200.1.1.20

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.1.10'
                address = '172.16.0.0'
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.2.15'
                address = '172.17.0.0'
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '200.1.1.20'
                address = '172.25.0.0'

```
