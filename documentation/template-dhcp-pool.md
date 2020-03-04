## Feature Template: DHCP Pool
#### Description
Define a range of IP addresses on a subnet with the DHCP Pool feature template. These IP addresses are used to respond to DHCP requests and dynamic IP assignments (non fixed IP).

#### Usage
The DHCP Pool feature is added to a defined subnet with a starting and ending address that is within the subnet network range.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/dhcp_pool.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define a range of IP addresses on a subnet with the DHCP Pool feature template. These IP addresses are used to respond to DHCP requests and dynamic IP assignments (non fixed IP).
- template: DHCP Pool
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which to create the DHCP Pool.
      domain_name: ""                          # (reference) name of the L3 domain in which to create the DHCP Pool.
      zone_name: ""                            # (reference) name of the L3 Zone in which to create the DHCP Pool.
      subnet_name: ""                          # (reference) name of the Subnet in which to create the DHCP Pool.
      min_address: ""                          # (string) first address of the IP range for the DHCP Pool.
      max_address: ""                          # (string) last address of the IP range for the DHCP Pool.
      dhcp_pool_type: bridge                   # (['bridge', 'host']) defines whether the Pool is to respond to multiple requests per port (Bridge) or a single request per port (Host)
      iptype: ipv4                             # (['ipv4', 'ipv6']) IP Address type for the pool. IPv4 or IPv6.

```

#### Parameters
*enterprise_name:* name of the enterprise in which to create the DHCP Pool.<br>
*domain_name:* name of the L3 domain in which to create the DHCP Pool.<br>
*zone_name:* name of the L3 Zone in which to create the DHCP Pool.<br>
*subnet_name:* name of the Subnet in which to create the DHCP Pool.<br>
*min_address:* first address of the IP range for the DHCP Pool.<br>
*max_address:* last address of the IP range for the DHCP Pool.<br>
*dhcp_pool_type:* defines whether the Pool is to respond to multiple requests per port (Bridge) or a single request per port (Host)<br>
*iptype:* IP Address type for the pool. IPv4 or IPv6.<br>


#### Restrictions
**create:**
* Address range must be from within the subnet it is being created on.
* Address ranges cannot overlap with one another.

