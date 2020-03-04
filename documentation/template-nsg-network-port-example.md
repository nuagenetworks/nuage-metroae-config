## Feature Template: NSG Network Port
#### Examples

##### Creatint a Network Port on a NSG Template
This example creates a single network port on an existing NSG Template.  nsg-network-port-flat.yaml
```
- template: NSG Network Port
  values:
    - nsg_template_name: West-NSG-Type-1
      network_port_name: MPLS-Provider-1-West
      physical_name: port1
      speed: BASET1000
      mtu: 1500
      vlan_range: 0-1024
      vlan_value: 0
      infrastructure_vsc_profile_name: Provider-1-VSC-West
      ingress_qos_policy_name: MPLS-Provider-1-6QoS-1000M
      egress_qos_policy_name: MPLS-Provider-1-6QoS-1000M
      uplink_role: primary
      underlay_name: Underlay-MPLS-1
      download_rate_limit: 10.00
      nat_enabled: False
      route_to_underlay: False

```
```
(example)$ metroae config create user-data.yml
    [select InfrastructureVscProfile (name of Provider-1-VSC-West)]
        [store id to name infrastructure_vsc_profile_id]
    [select Underlay (name of Underlay-MPLS-1)]
        [store id to name underlay_id]
    [select IngressQOSPolicy (name of MPLS-Provider-1-6QoS-1000M)]
        [store id to name ingress_qos_policy_id]
    [select EgressQOSPolicy (name of MPLS-Provider-1-6QoS-1000M)]
        [store id to name egress_qos_policy_id]
    [select NSGatewayTemplate (name of West-NSG-Type-1)]
        NSPortTemplate
            description = 'NSG Network Port MPLS-Provider-1-West'
            physicalName = 'port1'
            mtu = 1500
            VLANRange = '0-1024'
            portType = 'NETWORK'
            speed = 'BASET1000'
            name = 'MPLS-Provider-1-West'
            VlanTemplate
                associatedVSCProfileID = [retrieve infrastructure_vsc_profile_id (InfrastructureVscProfile:id)]
                description = 'NSG Network Port MPLS-Provider-1-West'
                associatedIngressQOSPolicyID = [retrieve ingress_qos_policy_id (IngressQOSPolicy:id)]
                isUplink = True
                value = 0
                associatedEgressQOSPolicyID = [retrieve egress_qos_policy_id (EgressQOSPolicy:id)]
                UplinkConnection
                    PATEnabled = False
                    underlayEnabled = False
                    assocUnderlayID = [retrieve underlay_id (Underlay:id)]
                    role = 'PRIMARY'
                    mode = 'Dynamic'
                    downloadRateLimit = 10.0

```

##### Creating a Primary and Seconday Network Port on an NSG Template
This example adds both a primary and secondary network port to an existing NSG Template.  nsg-network-port-groups.yaml
```
- group: NetworkPorts
  values:
    nsg_template_name: West-NSG-Type-1
    speed: BASET1000
    mtu: 1500
    vlan_range: 0-1024
    vlan_value: 0
    download_rate_limit: 10.00
    nat_enabled: False
    route_to_underlay: False
  children:
    - template: NSG Network Port
      values:
        - network_port_name: MPLS-Provider-1-West
          physical_name: port1
          infrastructure_vsc_profile_name: Provider-1-VSC-West
          ingress_qos_policy_name: MPLS-Provider-1-6QoS-1000M
          egress_qos_policy_name: MPLS-Provider-1-6QoS-1000M
          uplink_role: primary
          underlay_name: Underlay-MPLS-1
        - network_port_name: MPLS-Provider-2-West
          physical_name: port2
          infrastructure_vsc_profile_name: Provider-2-VSC-West
          ingress_qos_policy_name: MPLS-Provider-2-6QoS-1000M
          egress_qos_policy_name: MPLS-Provider-2-6QoS-1000M
          uplink_role: secondary
          underlay_name: Underlay-MPLS-2

```
```
(example)$ metroae config create user-data.yml
    [select InfrastructureVscProfile (name of Provider-1-VSC-West)]
        [store id to name infrastructure_vsc_profile_id]
    [select Underlay (name of Underlay-MPLS-1)]
        [store id to name underlay_id]
    [select IngressQOSPolicy (name of MPLS-Provider-1-6QoS-1000M)]
        [store id to name ingress_qos_policy_id]
    [select EgressQOSPolicy (name of MPLS-Provider-1-6QoS-1000M)]
        [store id to name egress_qos_policy_id]
    [select InfrastructureVscProfile (name of Provider-2-VSC-West)]
        [store id to name infrastructure_vsc_profile_id]
    [select EgressQOSPolicy (name of MPLS-Provider-2-6QoS-1000M)]
        [store id to name egress_qos_policy_id]
    [select Underlay (name of Underlay-MPLS-2)]
        [store id to name underlay_id]
    [select IngressQOSPolicy (name of MPLS-Provider-2-6QoS-1000M)]
        [store id to name ingress_qos_policy_id]
    [select NSGatewayTemplate (name of West-NSG-Type-1)]
        NSPortTemplate
            description = 'NSG Network Port MPLS-Provider-1-West'
            physicalName = 'port1'
            mtu = 1500
            VLANRange = '0-1024'
            portType = 'NETWORK'
            speed = 'BASET1000'
            name = 'MPLS-Provider-1-West'
            VlanTemplate
                associatedVSCProfileID = [retrieve infrastructure_vsc_profile_id (InfrastructureVscProfile:id)]
                description = 'NSG Network Port MPLS-Provider-1-West'
                associatedIngressQOSPolicyID = [retrieve ingress_qos_policy_id (IngressQOSPolicy:id)]
                isUplink = True
                value = 0
                associatedEgressQOSPolicyID = [retrieve egress_qos_policy_id (EgressQOSPolicy:id)]
                UplinkConnection
                    PATEnabled = False
                    underlayEnabled = False
                    assocUnderlayID = [retrieve underlay_id (Underlay:id)]
                    role = 'PRIMARY'
                    mode = 'Dynamic'
                    downloadRateLimit = 10.0
        NSPortTemplate
            description = 'NSG Network Port MPLS-Provider-2-West'
            physicalName = 'port2'
            mtu = 1500
            VLANRange = '0-1024'
            portType = 'NETWORK'
            speed = 'BASET1000'
            name = 'MPLS-Provider-2-West'
            VlanTemplate
                associatedVSCProfileID = [retrieve infrastructure_vsc_profile_id (InfrastructureVscProfile:id)]
                description = 'NSG Network Port MPLS-Provider-2-West'
                associatedIngressQOSPolicyID = [retrieve ingress_qos_policy_id (IngressQOSPolicy:id)]
                isUplink = True
                value = 0
                associatedEgressQOSPolicyID = [retrieve egress_qos_policy_id (EgressQOSPolicy:id)]
                UplinkConnection
                    PATEnabled = False
                    underlayEnabled = False
                    assocUnderlayID = [retrieve underlay_id (Underlay:id)]
                    role = 'SECONDARY'
                    mode = 'Dynamic'
                    downloadRateLimit = 10.0

```
