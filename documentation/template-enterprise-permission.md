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

#### Examples

##### Adding Permissions at a Gateway Level
This example adds permissions to a gateway.  dcgateway-enterprise-permission.yaml
```
- template: Enterprise Permission
  values:
    - permission_enterprise_name: DemoEnterprise
      gateway_name: 10.0.1.20

```
```
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [store id to name enterprise_id]
    [select Gateway (name of 10.0.1.20)]
        EnterprisePermission
            permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
            permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
            permittedAction = 'USE'
            permittedEntityName = 'DemoEnterprise'

```

##### Adding Permissions at a Port Level
This example adds permissions to a single port on a gateway.  dcgateway-enterprise-permission-port.yaml
```
- template: Enterprise Permission
  values:
    - permission_enterprise_name: DemoEnterprise
      gateway_name: 10.0.1.20
      port_name: eth2

```
```
[root@oc-ebc-config-1 feature-samples]# metroae config create dcgateway-enterprise-permission-port.yaml
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [store id to name enterprise_id]
    [select Gateway (name of 10.0.1.20)]
        [select Port (name of eth2)]
            EnterprisePermission
                permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                permittedAction = 'USE'
                permittedEntityName = 'DemoEnterprise'

```

##### Adding Permissions to Multiple Ports
This example adds permissions to multiple ports on a gateway and limits the data set using a group to define the common parameters.  dcgateway-enterprise-permission-port-groups.yaml
```
- group: gwpermission
  values:
    permission_enterprise_name: DemoEnterprise
    gateway_name: 10.0.1.20
  children:
    - template: Enterprise Permission
      values:
        - port_name: eth2
        - port_name: eth3
        - port_name: eth4

```
```
[root@oc-ebc-config-1 feature-samples]# metroae config create dcgateway-enterprise-permission-port-groups.yaml
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [store id to name enterprise_id]
        [store id to name enterprise_id]
        [store id to name enterprise_id]
    [select Gateway (name of 10.0.1.20)]
        [select Port (name of eth2)]
            EnterprisePermission
                permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                permittedAction = 'USE'
                permittedEntityName = 'DemoEnterprise'
        [select Port (name of eth3)]
            EnterprisePermission
                permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                permittedAction = 'USE'
                permittedEntityName = 'DemoEnterprise'
        [select Port (name of eth4)]
            EnterprisePermission
                permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                permittedAction = 'USE'
                permittedEntityName = 'DemoEnterprise'

```

##### Adding Permissions to VLANs
This example adds permissions to multiple VLANs on multiple Ports.  dcgateway-enterprise-permission-multi-port-vlans-groups.yaml
```
- group: gwpermission
  values:
    permission_enterprise_name: DemoEnterprise
    gateway_name: 10.0.1.20
  children:
    - group: port2
      values:
        port_name: eth2
      children:
        - template: Enterprise Permission
          values:
            - access_vlan_number: 21
            - access_vlan_number: 22
            - access_vlan_number: 23
    - group: port3
      values:
        port_name: eth3
      children:
        - template: Enterprise Permission
          values:
            - access_vlan_number: 31
            - access_vlan_number: 32
            - access_vlan_number: 33

```
```

```
