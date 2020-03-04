## Feature Template: Bridge Port
#### Examples

##### Creating a Bridge Port on a DC gateway
This example adds a bridge port from a VRS-G to a DC subnet.  network-bridge-port-dcgateway.yaml
```
- template: Bridge Port
  values:
    - enterprise_name: "DemoEnterprise"
      domain_type: l3domain
      domain_name: "L3-Domain-US"
      zone_name: "West-Zone"
      subnet_name: "West-Subnet-001"
      vport_name: GW1-West-E2-V21
      gateway_type: gateway
      gateway_name: 10.0.1.20
      access_port_name: eth2
      vlan: 21

```
```
(example)$ metroae config create user-data.yml
    [select Gateway (name of 10.0.1.20)]
        [store id to name gateway_id]
        [select Port (name of eth2)]
            [select Vlan (value of 21)]
                [store id to name vlan_id]
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-001)]
                    Vport
                        associatedGatewayID = [retrieve gateway_id (Gateway:id)]
                        associatedGatewayType = 'GATEWAY'
                        name = 'GW1-West-E2-V21'
                        addressSpoofing = 'ENABLED'
                        VLANID = [retrieve vlan_id (Vlan:id)]
                        type = 'BRIDGE'
                        DPI = 'INHERITED'
                        description = 'Vport GW1-West-E2-V21'
                        BridgeInterface
                            name = 'interface-GW1-West-E2-V21'

```

##### Creating a Bridge Port on an NSG
This example adds a bridge port from an NSG to a WAN subnet for a LAN connection.  network-bridge-port-nsg-wired.yaml
```

- template: Bridge Port
  values:
    - enterprise_name: "DemoEnterprise"
      domain_type: l3domain
      domain_name: "L3-Domain-US"
      zone_name: "West-Zone"
      subnet_name: "West-Subnet-001"
      vport_name: "NSG-West-Branch-001-P3-V101"
      gateway_type: "nsgateway"
      gateway_name: "West-Branch-001"
      access_port_name: "West-NSG-Type1-Access-Port"
      interface_type: "wired"
      vlan: 101

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of West-Branch-001)]
            [store id to name gateway_id]
            [select NSPort (name of West-NSG-Type1-Access-Port)]
                [select Vlan (value of 101)]
                    [store id to name vlan_id]
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-001)]
                    Vport
                        associatedGatewayID = [retrieve gateway_id (NSGateway:id)]
                        associatedGatewayType = 'NSGATEWAY'
                        name = 'NSG-West-Branch-001-P3-V101'
                        addressSpoofing = 'ENABLED'
                        VLANID = [retrieve vlan_id (Vlan:id)]
                        type = 'BRIDGE'
                        DPI = 'INHERITED'
                        description = 'Vport NSG-West-Branch-001-P3-V101'
                        BridgeInterface
                            name = 'interface-NSG-West-Branch-001-P3-V101'

```

##### Creating a Bridge Port on an NSG
This example adds a bridge port from an NSG to a WAN subnet for a wireless connection.  network-bridge-port-nsg-wireless.yaml
```
- template: Bridge Port
  values:
    - enterprise_name: "DemoEnterprise"
      domain_type: l3domain
      domain_name: "L3-Domain-US"
      zone_name: "West-Zone"
      subnet_name: "West-Subnet-001"
      vport_name: "NSG-West-Branch-001-Wifi"
      gateway_type: "nsgateway"
      gateway_name: "West-Branch-001"
      access_port_name: "West-Branch-Building1-Wifi-Port"
      interface_type: "wireless"
      ssid_connection_name: "Nuage-Secure"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of West-Branch-001)]
            [store id to name gateway_id]
            [select WirelessPort (name of West-Branch-Building1-Wifi-Port)]
                [select SSIDConnection (name of Nuage-Secure)]
                    [store id to name ssid_connection_id]
    [select Enterprise (name of DemoEnterprise)]
        [select Domain (name of L3-Domain-US)]
            [select Zone (name of West-Zone)]
                [select Subnet (name of West-Subnet-001)]
                    Vport
                        associatedGatewayID = [retrieve gateway_id (NSGateway:id)]
                        associatedGatewayType = 'NSGATEWAY'
                        name = 'NSG-West-Branch-001-Wifi'
                        associatedSSID = [retrieve ssid_connection_id (SSIDConnection:id)]
                        addressSpoofing = 'ENABLED'
                        type = 'BRIDGE'
                        DPI = 'INHERITED'
                        description = 'Vport NSG-West-Branch-001-Wifi'
                        BridgeInterface
                            name = 'interface-NSG-West-Branch-001-Wifi'

```
