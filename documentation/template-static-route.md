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

