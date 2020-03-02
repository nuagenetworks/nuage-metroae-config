## Feature Template: Enterprise Permission
#### Description
Add required permissions to shared gateways to a specific enterprise with the Enterprise Permissions feature template.

#### Usage
Any time a gateway is added to VSD in order for an Enterprise to use the resources it provides, ie. ports and vlans, the enterprise first needs to be authorized to use the resource. This is done by adding Enterprise Permissions to the resource in question. This authorization can be at the Gateway level, the Port level or the VLAN level.

The Enterprise Permissions feature template provides the ability to add permissions at any level in this hierarchy by simply adding the necessary resources in the user data set.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/enterprise_permission.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Add required permissions to shared gateways to a specific enterprise with the Enterprise Permissions feature template.
- template: Enterprise Permission
  values:
    - permission_enterprise_name: ""           # (reference) name of the enterprise that is added to the gateway permissions.
      gateway_name: ""                         # (reference) Required. name of the gateway to add the permissions. If dynamically discovered gateway it is typically an IP address.
      port_name: ""                            # (opt reference) name of the port in which to add the permissions. If not included in the data set then the permissions are added at the gateway level.
      access_vlan_number: 0                    # (opt integer) VLAN number in which to add the permissions. If port_name is included but not access_vlan_number in the data set then the permissions are added to the port.
      permitted_action: all                    # (opt ['all', 'deploy', 'extend', 'instantiate', 'read', 'use']) specific authorization provided to the enterprise. Defaults to "use".
      description: ""                          # (opt string) optional description included on the permissions.

```

#### Parameters
*permission_enterprise_name:* name of the enterprise that is added to the gateway permissions.<br>
*gateway_name:* Required. name of the gateway to add the permissions. If dynamically discovered gateway it is typically an IP address.<br>
*port_name:* name of the port in which to add the permissions. If not included in the data set then the permissions are added at the gateway level.<br>
*access_vlan_number:* VLAN number in which to add the permissions. If port_name is included but not access_vlan_number in the data set then the permissions are added to the port.<br>
*permitted_action:* specific authorization provided to the enterprise. Defaults to "use".<br>
*description:* optional description included on the permissions.<br>


#### Restrictions
**create:**
* The gateway, port, VLAN and Enterprise must exist prior to adding the permissions.
* Permissions cannot be added at multiple levels of the gateway hierarchy. If permissions are added to the gateway then it cannot be added to any port. If added to the port then it cannot be added to a VLAN on that port.

**revert:**
* Revert is currently non-functional for Enterprise Permissions.

