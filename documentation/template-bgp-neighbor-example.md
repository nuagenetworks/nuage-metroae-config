## Feature Template: Bgp Neighbor
#### Examples

##### Creating an IPv4 BGP Peer on a VM Using VM IP address to Identify Vport
This example creates an IPv4 BGP Peer on a VM vPort, providing the VM IP address as the means to identify the vPort to create the peer.  network-bgp-neighbor-ipv4-vmip.yaml
```
- template: Bgp Neighbor
  values:
    - enterprise_name: DemoEnterprise
      bgp_neighbor_name: "vm-bgp"
      deployment_type: datacenter
      domain_name: L3-Domain-US
      zone_name: West-Zone
      subnet_name: West-Subnet-001
      match_ip_address: 100.1.1.2
      peer_as: 65001
      peer_address: 100.1.1.2

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-001)]
                    [select VPort ($child of VMInterface)]
                        [select VMInterface (IPAddress of 100.1.1.2)]
                        BGPNeighbor
                            peerIP = '100.1.1.2'
                            IPType = 'IPV4'
                            peerAS = 65001
                            description = 'BGP Neighbor vm-bgp'
                            dampeningEnabled = False
                            BFDEnabled = False
                            name = 'vm-bgp'

```

##### Creating an IPv4 BGP Peer on a VM Using the VM VPort UUID to Identify the Vport
This example creates an IPv4 BGP peer on the same vPort as the previous example, but rather than providing the Domain/Zone/Subnet and VM IP address to indentify the vPort to create the peer we will provide the UUID of the vPort directly.  network-bgp-neighbor-ipv4-vportuuid.yaml
```
- template: Bgp Neighbor
  values:
    - enterprise_name: DemoEnterprise
      bgp_neighbor_name: "vm-bgp"
      deployment_type: datacenter
      vport_uuid: 78c607f5-42d0-44a7-903b-8d2ee0f1f539
      peer_as: 65001
      peer_address: 100.1.1.2

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain ($child of Zone)]
            [select Zone ($child of Subnet)]
                [select Subnet ($child of VPort)]
                    [select VPort (id of 78c607f5-42d0-44a7-903b-8d2ee0f1f539)]
                        BGPNeighbor
                            peerIP = '100.1.1.2'
                            IPType = 'IPV4'
                            peerAS = 65001
                            description = 'BGP Neighbor vm-bgp'
                            dampeningEnabled = False
                            BFDEnabled = False
                            name = 'vm-bgp'

```

##### Creating an IPv6 BGP Peer on a Bridge vPort on a WBX using the GW Port Details to Identify the Vport
This example creates an IPv6 BGP Peer on a WBX bridge Vport. We do not need to specify that IPv6 is being used explicitly, this is determined based on the format of the peer_address provided. In this example we also specify a XML session blob to be configured on the neighbor. The format of the XML blob is the same as what is used in the VSD UI, however in the template we must use the block classifier pipe ("I") to indicate a multi-line YAML input.  network-bgp-neighbor-ipv6-vmip-blob.yaml
```
- template: Bgp Neighbor
  values:
    - enterprise_name: DemoEnterprise
      bgp_neighbor_name: "gw-bgp"
      deployment_type: vsg
      domain_name: L3-Domain-US
      zone_name: West-Zone
      subnet_name: West-Subnet-DualStack
      peer_as: 65001
      peer_address: "100:1:3::10"
      gateway_name: "10.0.1.20"
      port_name: "eth2"
      vlan_value: "22"
      bfd_enabled: True
      dampening_enabled: True
      import_routing_policy_name: "Import-RP"
      export_routing_policy_name: "Export-RP"
      session_xml: |
        <neighbor xmlns="alu:nuage:bgp:neighbor">
          <config>
            <description>vsrA External-1</description>
            <advertise-inactive>false</advertise-inactive>
            <disable-4byte-asn>false</disable-4byte-asn>
            <disable-capability-negotiation>false</disable-capability-negotiation>
            <local-preference>0</local-preference>
            <next-hop-self>true</next-hop-self>
            <remove-private-as>false</remove-private-as>
            <set-med-out>0</set-med-out>
            <split-horizon>true</split-horizon>
            <local-as>65101</local-as>
            <no-prepend-global-as>true</no-prepend-global-as>
          </config>
          <timers>
            <connect-retry>5</connect-retry>
            <hold-time>15</hold-time>
            <keepalive>5</keepalive>
            <minimum-advertisement-interval>1</minimum-advertisement-interval>
          </timers>
          <transport>
            <mtu-discovery>false</mtu-discovery>
            <passive-mode>false</passive-mode>
          </transport>
          <error-handling>
            <treat-as-withdraw>false</treat-as-withdraw>
          </error-handling>
        </neighbor>

```
```
(example)$ metroae config create user-data.yml
    [select Gateway (name of 10.0.1.20)]
        [select Port (name of eth2)]
            [select Vlan (value of 22)]
                [store vportID to name vport_id]
    [select Enterprise (name of DemoEnterprise)]
        [select RoutingPolicy (name of Import-RP)]
            [store id to name import_routing_policy_id]
        [select RoutingPolicy (name of Export-RP)]
            [store id to name export_routing_policy_id]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-DualStack)]
                    [select VPort ($retrieve-value of id)]
                        id = [retrieve vport_id (Vlan:vportID)]
                        BGPNeighbor
                            associatedExportRoutingPolicyID = [retrieve export_routing_policy_id (RoutingPolicy:id)]
                            IPType = 'IPV6'
                            IPv6Address = '100:1:3::10'
                            peerAS = 65001
                            description = 'BGP Neighbor gw-bgp'
                            associatedImportRoutingPolicyID = [retrieve import_routing_policy_id (RoutingPolicy:id)]
                            session = '<neighbor xmlns="alu:nuage:bgp:neighbor">
  <config>
    <description>vsrA External-1</description>
    <advertise-inactive>false</advertise-inactive>
    <disable-4byte-asn>false</disable-4byte-asn>
    <disable-capability-negotiation>false</disable-capability-negotiation>
    <local-preference>0</local-preference>
    <next-hop-self>true</next-hop-self>
    <remove-private-as>false</remove-private-as>
    <set-med-out>0</set-med-out>
    <split-horizon>true</split-horizon>
    <local-as>65101</local-as>
    <no-prepend-global-as>true</no-prepend-global-as>
  </config>
  <timers>
    <connect-retry>5</connect-retry>
    <hold-time>15</hold-time>
    <keepalive>5</keepalive>
    <minimum-advertisement-interval>1</minimum-advertisement-interval>
  </timers>
  <transport>
    <mtu-discovery>false</mtu-discovery>
    <passive-mode>false</passive-mode>
  </transport>
  <error-handling>
    <treat-as-withdraw>false</treat-as-withdraw>
  </error-handling>
</neighbor>'
                            dampeningEnabled = True
                            BFDEnabled = True
                            name = 'gw-bgp'

```

##### Creating BGP Peer on NSG Access Port
This example creates a BGP peer for a WAN deployment on a NSG associated Subnet.  network-bgp-neighbor-ipv4-nsg-access-port.yaml
```
- template: Bgp Neighbor
  values:
    - enterprise_name: DemoEnterprise
      bgp_neighbor_name: "nsg-bgp"
      deployment_type: wan
      domain_name: L3-Domain-US
      zone_name: West-Zone
      subnet_name: West-Subnet-002
      peer_as: 65001
      peer_address: "100.1.2.10"
      dampening_enabled: True

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-002)]
                    BGPNeighbor
                        peerIP = '100.1.2.10'
                        IPType = 'IPV4'
                        peerAS = 65001
                        description = 'BGP Neighbor nsg-bgp'
                        dampeningEnabled = True
                        BFDEnabled = False
                        name = 'nsg-bgp'

```
