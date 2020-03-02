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

