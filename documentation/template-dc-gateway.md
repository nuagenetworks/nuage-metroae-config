## Feature Template: DC Gateway
#### Description
Create a Data Center Gateway with the Gateway template.

#### Usage
In an overlay network we often have to interconnect to devices or networks that are outside of the overlay. In this case we use a Data Center Gateway which can be physical (WBX, VSG) or virtual (VRS-G). When Gateways are created in VSD and not dynamically discovered a VSD Gateway Template is required. The Gateway feature automatically creates the required template along with the actual Gateway in one step.

The Gateway feature template provides the ability to create a Data Center Gateway.

Note: In many cases a Data Center Gateway may be discovered dynamically, such as when the Gateway is a hardware gateway (VSG, WBX) that is configured with the appropriate VSD configuration (xmpp-server). In cases where the Gateway was dynamically discovered and is either in Pending or Active state the Gateway feature template is unnecessary.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/dc_gateway.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create a Data Center Gateway with the Gateway template.
- template: DC Gateway
  values:
    - gateway_name: ""                         # (string) name of gateway to create.
      description: ""                          # (opt string) optional description of gateway. Defaults to "Gateway <gateway_name>".
      personality: dc7x50                      # (opt ['dc7x50', 'hardware_vtep', 'nuage_210_wbx_32', 'nuage_210_wbx_48_s', 'other', 'vrsb', 'vrsg', 'vsa', 'vsg']) type of gateway being created. Use other for 3rd party.
      system_id: ""                            # (string) system IP address of the gateway. This is the VTEP IP.
      gateway_enterprise_name: ""              # (opt reference) optional. Provides the ability to add Enterprise Permissions to the Gateway when it is created.
      permitted_action: all                    # (opt ['all', 'deploy', 'extend', 'instantiate', 'read', 'use']) enterprise Permissions authorization, defaults to "use".

```

#### Parameters
*gateway_name:* name of gateway to create.<br>
*description:* optional description of gateway. Defaults to "Gateway <gateway_name>".<br>
*personality:* type of gateway being created. Use other for 3rd party.<br>
*system_id:* system IP address of the gateway. This is the VTEP IP.<br>
*gateway_enterprise_name:* optional. Provides the ability to add Enterprise Permissions to the Gateway when it is created.<br>
*permitted_action:* enterprise Permissions authorization, defaults to "use".<br>


#### Restrictions
**create:**
* Can only create Gateways in csproot Platform configuration.
* Cannot create a gateway that already exists.

**revert:**
* Gateways cannot be reverted if it has VLANs from any ports attached to a subnet. ie. an active Bridge Port.

