## Feature Template: L2 Domain
#### Examples

##### Creating an IPv4 L2 Domain
This example creates an L2 Domain with DHCP enabled using IPv4 addressing only.  network-l2domain-ipv4.yaml
```
- template: L2 Domain
  values:
    - enterprise_name: "DemoEnterprise"
      l2_domain_name: L2-Domain-IPv4
      managed_dhcp: True
      ip_address_type: ipv4
      ipv4_network: "1.1.1.0/24"
      ipv4_gateway: "1.1.1.1"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        L2DomainTemplate
            name = 'template_L2-Domain-IPv4'
            dhcpmanaged = True
            description = 'L2 Domain Template L2-Domain-IPv4'
            netmask = '255.255.255.0'
            address = '1.1.1.0'
            gateway = '1.1.1.1'
            iptype = 'IPV4'
            [store id to name l2domain_template_id]
        L2Domain
            templateID = [retrieve l2domain_template_id (L2DomainTemplate:id)]
            name = 'L2-Domain-IPv4'
            description = 'L2Domain L2-Domain-IPv4'

```

##### Creating a Dualstack L2 Domain
This example creates an L2 Domain with DHCP enabled using both IPv4 and IPv6 addressing.  network-l2domain-dualstack.yaml
```
- template: L2 Domain
  values:
    - enterprise_name: DemoEnterprise
      l2_domain_name: L2-Domain-DualStack
      managed_dhcp: True
      ip_address_type: DualStack
      ipv4_network: 1.1.1.0/24
      ipv4_gateway: 1.1.1.1
      ipv6_network: 1::0/64
      ipv6_gateway: 1::1

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        L2DomainTemplate
            name = 'template_L2-Domain-DualStack'
            ipv6address = '1::0/64'
            dhcpmanaged = True
            description = 'L2 Domain Template L2-Domain-DualStack'
            netmask = '255.255.255.0'
            address = '1.1.1.0'
            ipv6gateway = '1::1'
            gateway = '1.1.1.1'
            iptype = 'DUALSTACK'
            [store id to name l2domain_template_id]
        L2Domain
            templateID = [retrieve l2domain_template_id (L2DomainTemplate:id)]
            name = 'L2-Domain-DualStack'
            description = 'L2Domain L2-Domain-DualStack'

```

##### Creating an Unmanaged L2 Domain
This example creates an L2 Domain with no DHCP or network allocated.  network-l2domain-noip.yaml
```
- template: L2 Domain
  values:
    - enterprise_name: "DemoEnterprise"
      l2_domain_name: L2-Domain-NoIP
      managed_dhcp: False

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        L2DomainTemplate
            dhcpmanaged = False
            description = 'L2 Domain Template L2-Domain-NoIP'
            iptype = 'IPV4'
            name = 'template_L2-Domain-NoIP'
            [store id to name l2domain_template_id]
        L2Domain
            templateID = [retrieve l2domain_template_id (L2DomainTemplate:id)]
            name = 'L2-Domain-NoIP'
            description = 'L2Domain L2-Domain-NoIP'

```
