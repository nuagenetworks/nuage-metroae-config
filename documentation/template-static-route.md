## Feature Template: Static Route
#### Description
Inject static routing entries within the overlay L3 Domain with the Static Route feature template.

#### Usage
Static Routes are often required within an L3 Domain when reaching networks that are not controlled by VSD. These networks may be accessible via gateways (WBX, NSG etc) or within the overlay (a VM loopback address) and are typically required when dynamic routing (BGP or OSPF) is not possible.

Static Routes are applied on an L3 Domain and support Overlay Routes only in the current version of the template.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/static_route.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Inject static routing entries within the overlay L3 Domain with the Static Route feature template.
- template: Static Route
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which to create the Static Routes.
      domain_name: ""                          # (reference) name of the L3 domain in which to create the Static Routes.
      address: ""                              # (string) network address of the static route being added.
      netmask: ""                              # (string) netmask of the static route being added.
      next_hop: ""                             # (string) IP address of the next hop for the static route.

```

#### Parameters
*enterprise_name:* name of the enterprise in which to create the Static Routes.<br>
*domain_name:* name of the L3 domain in which to create the Static Routes.<br>
*address:* network address of the static route being added.<br>
*netmask:* netmask of the static route being added.<br>
*next_hop:* IP address of the next hop for the static route.<br>


#### Restrictions
**create:**
* The Enterprise and Domain on which the static route is being added must exist.
* The next hop detailed list in the static route entry must be a valid

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
[root@oc-ebc-config-1 feature-samples]# metroae config create network-static-route-flat.yaml
Device: Nuage Networks VSD 5.4.1
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
[root@oc-ebc-config-1 feature-samples]# metroae config create network-static-route-groups-child.yaml
Device: Nuage Networks VSD 5.4.1
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
[root@oc-ebc-config-1 feature-samples]# metroae config create network-static-route-groups-sub.yaml
Device: Nuage Networks VSD 5.4.1
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
