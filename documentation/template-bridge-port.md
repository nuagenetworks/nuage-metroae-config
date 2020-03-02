## Feature Template: Bridge Port
#### Description
Add gateway access ports to existing Subnets or L2 Domains with the Bridge Port template. The same template is used regardless of Gateway type. ie. Software, Hardware DC Gateways or an NSG WAN gateway.

#### Usage
Bridge Ports are used to join external broadcast networks to an overlay. The bridge port itself is a representation of an access port on a gateway device (one that is terminating VXLAN) and is defined using the Gateway, Port and VLAN for the broadcast domain.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/bridge_port.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Add gateway access ports to existing Subnets or L2 Domains with the Bridge Port template. The same template is used regardless of Gateway type. ie. Software, Hardware DC Gateways or an NSG WAN gateway.
- template: Bridge Port
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise to create the bridge port.
      domain_name: ""                          # (reference) name of the L3 Domain to create the bridge port.
      zone_name: ""                            # (opt reference) name of the Zone to create the bridge port.
      subnet_name: ""                          # (opt reference) name of the Subnet to create the bridge port.
      vport_name: ""                           # (string) name of the bridge port being created.
      description: ""                          # (opt string) optional description of the Bridge Port.
      domain_type: l2domain                    # (['l2domain', 'l3domain'])
      gateway_type: gateway                    # (['gateway', 'nsgateway']) type of gateway being used for the Bridge Port, this could be 'gateway' for a DC gateway or 'nsgateway' for WAN.
      gateway_name: ""                         # (reference) name of the gateway being used for the Bridge Port.
      access_port_name: ""                     # (reference) name of the access port being used for the Bridge Port. This will change depending on DC (along with Hardware or Software gateway) or WAN type gateway.
      interface_type: wired                    # (opt ['wired', 'wireless']) when gateway_type is nsg, interface type can be wired or wireless.
      vlan: 0                                  # (opt integer) VLAN to be used for the Bridge Port. For untagged ports it will be 0.
      ssid_connection_name: ""                 # (opt string) name of the ssid connection when interface_type is wireless for nsg.
      dpi: disabled                            # (opt ['disabled', 'enabled', 'inherited']) optional override of Domain level setting for DPI, only applicable to WAN/NSG Bridge Ports.
      address_spoofing: disabled               # (opt ['disabled', 'enabled', 'inherited']) optional Override of security policy settings for address spoofing, only applicable to software gateway ports.

```

#### Parameters
*enterprise_name:* name of the enterprise to create the bridge port.<br>
*domain_name:* name of the L3 Domain to create the bridge port.<br>
*zone_name:* name of the Zone to create the bridge port.<br>
*subnet_name:* name of the Subnet to create the bridge port.<br>
*vport_name:* name of the bridge port being created.<br>
*description:* optional description of the Bridge Port.<br>
*domain_type:* <br>
*gateway_type:* type of gateway being used for the Bridge Port, this could be 'gateway' for a DC gateway or 'nsgateway' for WAN.<br>
*gateway_name:* name of the gateway being used for the Bridge Port.<br>
*access_port_name:* name of the access port being used for the Bridge Port. This will change depending on DC (along with Hardware or Software gateway) or WAN type gateway.<br>
*interface_type:* when gateway_type is nsg, interface type can be wired or wireless.<br>
*vlan:* VLAN to be used for the Bridge Port. For untagged ports it will be 0.<br>
*ssid_connection_name:* name of the ssid connection when interface_type is wireless for nsg.<br>
*dpi:* optional override of Domain level setting for DPI, only applicable to WAN/NSG Bridge Ports.<br>
*address_spoofing:* optional Override of security policy settings for address spoofing, only applicable to software gateway ports.<br>


#### Restrictions
**create:**
* Template only supports adding bridge ports to L3 domains.
* When creating a WAN/nsgateway bridge port only a single bridge port can be added to a L3 Domain subnet.
* Bridge Ports can only be created on Gateways that already exist with defined Access Ports and VLANs with correct enterprise permissions.

