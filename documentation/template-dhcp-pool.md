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

#### Examples

##### Creating a Single DHCP Pool Range on One Subnet
This example configures a single range on a single subnet. All required parameters are listed within the user data DHCP Pool template definition.  network-dhcp-pool-flat.yaml
```
- template: DHCP Pool
  values:
    - enterprise_name: DemoEnterprise
      domain_name: L3-Domain-US
      zone_name: West-Zone
      subnet_name: West-Subnet-001
      min_address: 100.1.1.10
      max_address: 100.1.1.20
      dhcp_pool_type: bridge
      iptype: ipv4

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-001)]
                    AddressRange
                        maxAddress = '100.1.1.20'
                        DHCPPoolType = 'BRIDGE'
                        IPType = 'IPV4'
                        minAddress = '100.1.1.10'

```

##### Creating multiple DHCP Pool Ranges on Multiple Subnets Using Group Inheritance
This example defines multiple IP ranges per subnet. The required Enterprise, Domain and Zone are defined in a group rather than being repeated for each entry.  network-dhcp-pool-multi-subnet-groups.yaml
```
- group: DHCPList
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    zone_name: West-Zone
    dhcp_pool_type: bridge
    iptype: ipv4
  children:
    - template: DHCP Pool
      values:
        - subnet_name: West-Subnet-001
          min_address: 100.1.1.10
          max_address: 100.1.1.20
        - subnet_name: West-Subnet-001
          min_address: 100.1.1.40
          max_address: 100.1.1.50
        - subnet_name: West-Subnet-002
          min_address: 100.1.2.10
          max_address: 100.1.2.20
        - subnet_name: West-Subnet-002
          min_address: 100.1.2.40
          max_address: 100.1.2.50

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-001)]
                    AddressRange
                        maxAddress = '100.1.1.20'
                        DHCPPoolType = 'BRIDGE'
                        IPType = 'IPV4'
                        minAddress = '100.1.1.10'
                    AddressRange
                        maxAddress = '100.1.1.50'
                        DHCPPoolType = 'BRIDGE'
                        IPType = 'IPV4'
                        minAddress = '100.1.1.40'
                [select Subnet (name of West-Subnet-002)]
                    AddressRange
                        maxAddress = '100.1.2.20'
                        DHCPPoolType = 'BRIDGE'
                        IPType = 'IPV4'
                        minAddress = '100.1.2.10'
                    AddressRange
                        maxAddress = '100.1.2.50'
                        DHCPPoolType = 'BRIDGE'
                        IPType = 'IPV4'
                        minAddress = '100.1.2.40'

```

##### Creating DHCP Pool Ranges Across Multiple Zones and Subnets Using Group Substitution
This example creates a DHCP range per subnet. The subnets span more than a single zone. We define a group, then define that group within the user data of the DHCP Pool template. This is similar to the previous example but rather than inheriting the group values as a child we are doing a substitution.  network-dhcp-pool-multi-zone-groups.yaml
```
- group: DHCPList
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    dhcp_pool_type: bridge
    iptype: ipv4
- template: DHCP Pool
  values:
    - $group_list: DHCPList
      zone_name: West-Zone
      subnet_name: West-Subnet-001
      min_address: 100.1.1.10
      max_address: 100.1.1.20
    - $group_zone: DHCPList
      zone_name: West-Zone
      subnet_name: West-Subnet-002
      min_address: 100.1.2.10
      max_address: 100.1.2.20
    - $group_list: DHCPList
      zone_name: East-Zone
      subnet_name: East-Subnet-001
      min_address: 200.1.1.10
      max_address: 200.1.1.20

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-001)]
                    AddressRange
                        maxAddress = '100.1.1.20'
                        DHCPPoolType = 'BRIDGE'
                        IPType = 'IPV4'
                        minAddress = '100.1.1.10'
                [select Subnet (name of West-Subnet-002)]
                    AddressRange
                        maxAddress = '100.1.2.20'
                        DHCPPoolType = 'BRIDGE'
                        IPType = 'IPV4'
                        minAddress = '100.1.2.10'
            [select Zone (name of East-Zone)]
                [select Subnet (name of East-Subnet-001)]
                    AddressRange
                        maxAddress = '200.1.1.20'
                        DHCPPoolType = 'BRIDGE'
                        IPType = 'IPV4'
                        minAddress = '200.1.1.10'

```
