# MetroAE Config - Inheritance

When creating configuration user data to pass into MetroAE config you can make use of inheritance to avoid having to specify common parameters multiple times.

User data files are able to specify groups that contain common values for parameters that will then be inherited (used) by subsequent feature configuration.

#### Using Groups
You create a group by giving it a name and specifying the parameter names and associated values you would like contained in that group. The parameter names and values will be inherited by any feature that references that group.

For example to create a group called StaticRoutes that specifies an Enterprise and L3 Domain to use you would include the following in your user data:

```
- group: StaticRoutes
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
```

You can then reference this group instead of repeating the same value when instantiating a feature template with your configuration values.

If feature configuration that references a group contains parameters that are also specified in that group then the values in the feature configuration will take precedence over (override) the values defined in the group.

MetroAE config supports two types of inheritance using groups:
* Parent/Child
* Substitution

#### Parent/Child inheritance
With Parent/Child inheritance you instantiate one or more feature templates as children of the group you have defined. All children inherit all properties (and their values) from their parent group.

For example to create three static routes, two of which are within the same L3 Domain, under the same Enterprise you could include the following in your user data:
network-static-route-groups-child2.yaml
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
        - address: 172.25.0.0
          netmask: 255.255.0.0
          next_hop: 200.1.1.20

- template: Static Route
  values:
  - enterprise_name: DemoEnterprise
    domain_name: L3-Domain-EMEA
    address: 172.17.0.0
    netmask: 255.255.0.0
    next_hop: 100.1.2.15
```
which would generate output similar to:
```
(example)# metroae config create network-static-route-groups-child2.yaml

Device: Nuage Networks VSD 6.0.1
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.1.10'
                address = '172.16.0.0'
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '200.1.1.20'
                address = '172.25.0.0'
        [select Domain (name of L3-Domain-EMEA)]
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.2.15'
                address = '172.17.0.0'
```
#### Inheritance by substitution
Inheritance by substitution allows you to insert the parameter values defined in a group into the configuration for a feature without having to specify the resulting configuration as children of the group. This provides more flexibility in how you can structure your user data.

For example to create the same three static routes, two of which are within the same L3 Domain, under the same Enterprise you could include the following in your user data:
network-static-route-groups-sub2.yaml

```
- group: L3-Domain-US
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US

- group: L3-Domain-EMEA
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-EMEA

- template: Static Route
  values:
    - $group_domain: L3-Domain-US
      address: 172.16.0.0
      netmask: 255.255.0.0
      next_hop: 100.1.1.10
    - $group_domain: L3-Domain-EMEA
      address: 172.17.0.0
      netmask: 255.255.0.0
      next_hop: 100.1.2.15
    - $group_domain: L3-Domain-US
      address: 172.25.0.0
      netmask: 255.255.0.0
      next_hop: 200.1.1.20
```
which would generate output similar to:
```
(example)# metroae config create network-static-route-groups-sub2.yaml

Device: Nuage Networks VSD 6.0.1
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.1.10'
                address = '172.16.0.0'
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '200.1.1.20'
                address = '172.25.0.0'
        [select Domain (name of L3-Domain-EMEA)]
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.2.15'
                address = '172.17.0.0'
```

#### Combining Parent/Child inheritance with substitution
It is possible to use Parent/Child inheritance as well as inheritance by substitution together in a single user data file and even together within the configuration of a single feature.

For example to create the same three static routes, with their netmask only specified once you could include the following in your user data:
network-static-route-groups-child-sub.yaml

```
- group: L3-Domain-US
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US

- group: L3-Domain-EMEA
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-EMEA

- group: StaticRoutes
  values:
    $group_domain: L3-Domain-US
    netmask: 255.255.0.0
  children:
    - template: Static Route
      values:
        - address: 172.16.0.0
          next_hop: 100.1.1.10
        - address: 172.25.0.0
          next_hop: 200.1.1.20
        - $group_domain: L3-Domain-EMEA
          address: 172.17.0.0
          next_hop: 100.1.2.15
```
which would generate output similar to:
```
(example)# metroae config create network-static-route-groups-child-sub.yaml

Device: Nuage Networks VSD 6.0.1
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.1.10'
                address = '172.16.0.0'
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '200.1.1.20'
                address = '172.25.0.0'
        [select Domain (name of L3-Domain-EMEA)]
            StaticRoute
                netmask = '255.255.0.0'
                nextHopIp = '100.1.2.15'
                address = '172.17.0.0'
```
