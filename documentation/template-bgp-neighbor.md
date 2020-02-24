## Feature Template: Bgp Neighbor
#### Description
Add a PE-CE BGP Peer to either a VRS(or AVRS), WBX/VSG or NSG with the BGP Neighbor feature template.

#### Usage
BGP peering within the overlay network is used to advertise routes to or receive routes from either a VM or device within the access network (in case of a GW) that are not natively part of the overlay itself. Depending on the deployment type the attributes required to identify where to configure the peer change. In a Datacenter deployment (VM or VSG/WBX) the peer is configured on a vPort, whereas in a WAN deployment (NSG) the BGP peer is configuration on a subnet.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/bgp_neighbor.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Add a PE-CE BGP Peer to either a VRS(or AVRS), WBX/VSG or NSG with the BGP Neighbor feature template.
- template: Bgp Neighbor
  values:
    - enterprise_name: ""                      # (reference) name of the Enterprise where the BGP peer will be created.
      bgp_neighbor_name: ""                    # (string) name of the BGP peer to be created.
      description: ""                          # (opt string) optional description for the BGP peer.
      deployment_type: datacenter              # (['datacenter', 'wan', 'vsg']) type of deployment where the BGP peer will be added. Choices are datacenter, wan or vsg. When datacenter is chosen then VM attributes are required to identify the vport to configure.
      vport_uuid: ""                           # (opt string) optional vport identification for datacenter or VSG deployment.
      domain_name: ""                          # (opt reference) name of the domain in which the BGP peer will be created.
      zone_name: ""                            # (opt reference) name of the zone in which the BGP peer will be created.
      subnet_name: ""                          # (opt reference) name of the subnet in which the BGP peer will be created.
      gateway_name: ""                         # (opt reference) If WAN or VSG deployment type name of the Gateway (NSG or WBX/VSG) to create the BGP peer.
      port_name: ""                            # (opt reference) If WAN or VSG deployment type name of the Access Port to create the BGP peer.
      vlan_value: ""                           # (opt reference) If WAN or VSG deployment type the VLAN to create the BGP peer.
      match_ip_address: ""                     # (opt string) If datacenter deployment type IPv4 address of the VM to create the BGP peer. The VM IPv4 address or MAC or both can be provided for the match criteria.
      match_mac_address: ""                    # (opt string) If datacenter deployment type MAC address of the VM to create the BGP peer. The VM MAC address or IPv4 or both can be provided for the match criteria.
      peer_as: 0                               # (integer) AS number of the Peer.
      peer_address: ""                         # (string) Neighbor IPv4 or IPv6 address.
      bfd_enabled: False                       # (opt boolean) Optional enablement of BFD on the BGP peer. Default is disabled.
      dampening_enabled: False                 # (opt boolean) Optional enablement of session dampening on the BGP peer. Default is disabled.
      import_routing_policy_name: ""           # (opt reference) Optional attachment of an Import Routing Policy for the BGP session.
      export_routing_policy_name: ""           # (opt reference) Optional attachment of an Export Routing Policy for the BGP session.
      session_xml: ""                          # (opt string) XML blob for additional configuration to be added to the BGP neighbor configuration. For multiline page text a YAML multiline Block Style Indicator is required (pipe "|").

```

#### Parameters
*enterprise_name:* name of the Enterprise where the BGP peer will be created.<br>
*bgp_neighbor_name:* name of the BGP peer to be created.<br>
*description:* optional description for the BGP peer.<br>
*deployment_type:* type of deployment where the BGP peer will be added. Choices are datacenter, wan or vsg. When datacenter is chosen then VM attributes are required to identify the vport to configure.<br>
*vport_uuid:* optional vport identification for datacenter or VSG deployment.<br>
*domain_name:* name of the domain in which the BGP peer will be created.<br>
*zone_name:* name of the zone in which the BGP peer will be created.<br>
*subnet_name:* name of the subnet in which the BGP peer will be created.<br>
*gateway_name:* If WAN or VSG deployment type name of the Gateway (NSG or WBX/VSG) to create the BGP peer.<br>
*port_name:* If WAN or VSG deployment type name of the Access Port to create the BGP peer.<br>
*vlan_value:* If WAN or VSG deployment type the VLAN to create the BGP peer.<br>
*match_ip_address:* If datacenter deployment type IPv4 address of the VM to create the BGP peer. The VM IPv4 address or MAC or both can be provided for the match criteria.<br>
*match_mac_address:* If datacenter deployment type MAC address of the VM to create the BGP peer. The VM MAC address or IPv4 or both can be provided for the match criteria.<br>
*peer_as:* AS number of the Peer.<br>
*peer_address:* Neighbor IPv4 or IPv6 address.<br>
*bfd_enabled:* Optional enablement of BFD on the BGP peer. Default is disabled.<br>
*dampening_enabled:* Optional enablement of session dampening on the BGP peer. Default is disabled.<br>
*import_routing_policy_name:* Optional attachment of an Import Routing Policy for the BGP session.<br>
*export_routing_policy_name:* Optional attachment of an Export Routing Policy for the BGP session.<br>
*session_xml:* XML blob for additional configuration to be added to the BGP neighbor configuration. For multiline page text a YAML multiline Block Style Indicator is required (pipe "|").<br>


#### Restrictions
**create:**
* Can only be created on an L3 Domain.
* vPort or Subnet must exist for the BGP peer to be created.
* In the Datacenter deployment type the vport UUID OR the Domain/Zone/Subnet and either match_mac_address or match_ip_address must be provided to identify the vport to create the BGP peer.
* In the VSG deployment type the Domain/Zone/Subnet and Gateway Name/Port/VLAN ID must be provided to indentify the vport to create the BGP peer.
* In the WAN deployment type the Domain/Zone/Subnet must be provided to create the BGP Peer.
* BFD enabled is not supported when creating a WAN BGP peer.

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
