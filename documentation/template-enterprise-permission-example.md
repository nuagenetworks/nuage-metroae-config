## Feature Template: Enterprise Permission
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
(example)$ metroae config create user-data.yml
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
(example)$ metroae config create user-data.yml
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
(example)$ metroae config create user-data.yml
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
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [store id to name enterprise_id]
        [store id to name enterprise_id]
        [store id to name enterprise_id]
        [store id to name enterprise_id]
        [store id to name enterprise_id]
        [store id to name enterprise_id]
    [select Gateway (name of 10.0.1.20)]
        [select Port (name of eth2)]
            [select Vlan (value of 21)]
                EnterprisePermission
                    permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                    permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                    permittedAction = 'USE'
                    permittedEntityName = 'DemoEnterprise'
            [select Vlan (value of 22)]
                EnterprisePermission
                    permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                    permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                    permittedAction = 'USE'
                    permittedEntityName = 'DemoEnterprise'
            [select Vlan (value of 23)]
                EnterprisePermission
                    permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                    permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                    permittedAction = 'USE'
                    permittedEntityName = 'DemoEnterprise'
        [select Port (name of eth3)]
            [select Vlan (value of 31)]
                EnterprisePermission
                    permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                    permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                    permittedAction = 'USE'
                    permittedEntityName = 'DemoEnterprise'
            [select Vlan (value of 32)]
                EnterprisePermission
                    permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                    permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                    permittedAction = 'USE'
                    permittedEntityName = 'DemoEnterprise'
            [select Vlan (value of 33)]
                EnterprisePermission
                    permittedEntityDescription = 'EnterprisePermission DemoEnterprise'
                    permittedEntityID = [retrieve enterprise_id (Enterprise:id)]
                    permittedAction = 'USE'
                    permittedEntityName = 'DemoEnterprise'

```
