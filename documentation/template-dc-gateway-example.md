## Feature Template: DC Gateway
#### Examples

##### Creating a Physical Data Center Gateway
This example creates a WBX Gateway in VSD. dcgateway-wbx.yaml
```
- template: DC Gateway
  values:
    gateway_name: 10.0.1.21
    personality: nuage_210_wbx_48_s
    system_id: 10.0.1.21

```
```
(example)$ metroae config create user-data.yml
    GatewayTemplate
        personality = 'NUAGE_210_WBX_48_S'
        description = 'Gateway 10.0.1.21'
        name = '10.0.1.21'
        [store id to name gateway_template_id]
    Gateway
        templateID = [retrieve gateway_template_id (GatewayTemplate:id)]
        systemID = '10.0.1.21'
        name = '10.0.1.21'
        description = 'Gateway 10.0.1.21'

```

##### Creating a Virtual Data Center Gateway
This example creates a VRS-G. This virtual gateway is not dynamically discovered by VSD, thus it must always be created in VSD.  dcgateway-vrsg.yaml
```
- template: DC Gateway
  values:
    gateway_name: 10.0.1.20
    personality: vrsg
    system_id: 10.0.1.20

```
```
(example)$ metroae config create user-data.yml
    GatewayTemplate
        personality = 'VRSG'
        description = 'Gateway 10.0.1.20'
        name = '10.0.1.20'
        [store id to name gateway_template_id]
    Gateway
        templateID = [retrieve gateway_template_id (GatewayTemplate:id)]
        systemID = '10.0.1.20'
        name = '10.0.1.20'
        description = 'Gateway 10.0.1.20'

```
