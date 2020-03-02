## Feature Template: NSGateway
#### Examples

##### Creating An NSG Instance for Future Bootstrapping
This example creates an NSG Instance with minimal additional configuration in a specific enterprise that will be activated at a later date.  nsg-instance-minimal.yaml
```
- template: NSGateway
  values:
    - enterprise_name: "DemoEnterprise"
      nsg_name: "West-Branch-001"
      nsg_template_name: "West-NSG-Type-1"

```
```
(example)$ metroae config create user-data.yml
    [select NSGatewayTemplate (name of West-NSG-Type-1)]
        [store id to name nsgateway_template_id]
    [select Enterprise (name of DemoEnterprise)]
        NSGateway
            TCPMSSEnabled = False
            name = 'West-Branch-001'
            controlTrafficDSCPValue = 56
            controlTrafficCOSValue = 7
            templateID = [retrieve nsgateway_template_id (NSGatewayTemplate:id)]
            SSHService = 'INHERITED'
            description = 'NSGateway West-Branch-001'
            [select Bootstrap ($position of 0)]
                ZFBMatchValue = ''
                ZFBMatchAttribute = 'NONE'

```

##### Creating multiple NSG Instances for Future Bootstrapping using groups
This example creates multiple NSG Instances in a specific enterprise using groups for repeated user data.nsg-instance-multiple.yaml
```
- group: multiple_nsgs_in_demo_enterprise
  values:
    - enterprise_name: "DemoEnterprise"
      nsg_template_name: "West-NSG-Type-1"
      ssh_service: "INHERITED"
  children:
    - template: NSGateway
      values:
        - nsg_name: "West-Branch-001"
        - nsg_name: "West-Branch-002"
        - nsg_name: "West-Branch-003"
        - nsg_name: "East-Branch-001"
        - nsg_name: "East-Branch-002"
        - nsg_name: "East-Branch-003"

```
```
(example)$ metroae config create user-data.yml
    [select NSGatewayTemplate (name of West-NSG-Type-1)]
        [store id to name nsgateway_template_id]
        [store id to name nsgateway_template_id]
        [store id to name nsgateway_template_id]
        [store id to name nsgateway_template_id]
        [store id to name nsgateway_template_id]
        [store id to name nsgateway_template_id]
    [select Enterprise (name of DemoEnterprise)]
        NSGateway
            TCPMSSEnabled = False
            name = 'West-Branch-001'
            controlTrafficDSCPValue = 56
            controlTrafficCOSValue = 7
            templateID = [retrieve nsgateway_template_id (NSGatewayTemplate:id)]
            SSHService = 'INHERITED'
            description = 'NSGateway West-Branch-001'
            [select Bootstrap ($position of 0)]
                ZFBMatchValue = ''
                ZFBMatchAttribute = 'NONE'
        NSGateway
            TCPMSSEnabled = False
            name = 'West-Branch-002'
            controlTrafficDSCPValue = 56
            controlTrafficCOSValue = 7
            templateID = [retrieve nsgateway_template_id (NSGatewayTemplate:id)]
            SSHService = 'INHERITED'
            description = 'NSGateway West-Branch-002'
            [select Bootstrap ($position of 0)]
                ZFBMatchValue = ''
                ZFBMatchAttribute = 'NONE'
        NSGateway
            TCPMSSEnabled = False
            name = 'West-Branch-003'
            controlTrafficDSCPValue = 56
            controlTrafficCOSValue = 7
            templateID = [retrieve nsgateway_template_id (NSGatewayTemplate:id)]
            SSHService = 'INHERITED'
            description = 'NSGateway West-Branch-003'
            [select Bootstrap ($position of 0)]
                ZFBMatchValue = ''
                ZFBMatchAttribute = 'NONE'
        NSGateway
            TCPMSSEnabled = False
            name = 'East-Branch-001'
            controlTrafficDSCPValue = 56
            controlTrafficCOSValue = 7
            templateID = [retrieve nsgateway_template_id (NSGatewayTemplate:id)]
            SSHService = 'INHERITED'
            description = 'NSGateway East-Branch-001'
            [select Bootstrap ($position of 0)]
                ZFBMatchValue = ''
                ZFBMatchAttribute = 'NONE'
        NSGateway
            TCPMSSEnabled = False
            name = 'East-Branch-002'
            controlTrafficDSCPValue = 56
            controlTrafficCOSValue = 7
            templateID = [retrieve nsgateway_template_id (NSGatewayTemplate:id)]
            SSHService = 'INHERITED'
            description = 'NSGateway East-Branch-002'
            [select Bootstrap ($position of 0)]
                ZFBMatchValue = ''
                ZFBMatchAttribute = 'NONE'
        NSGateway
            TCPMSSEnabled = False
            name = 'East-Branch-003'
            controlTrafficDSCPValue = 56
            controlTrafficCOSValue = 7
            templateID = [retrieve nsgateway_template_id (NSGatewayTemplate:id)]
            SSHService = 'INHERITED'
            description = 'NSGateway East-Branch-003'
            [select Bootstrap ($position of 0)]
                ZFBMatchValue = ''
                ZFBMatchAttribute = 'NONE'

```

##### Creating an NSG Instance for ZFB Bootstrapping
This example creates an NSG instance within the enterprise with match criteria defined in the user data.  nsg-instance-zfb.yaml
```
- template: NSGateway
  values:
    - enterprise_name: "DemoEnterprise"
      nsg_name: "West-Branch-001"
      nsg_template_name: "West-NSG-Type-1"
      bootstrap_match_type: "SERIAL_NUMBER"
      bootstrap_match_value: "NS1550Q0448"

```
```
(example)$ metroae config create user-data.yml
    [select NSGatewayTemplate (name of West-NSG-Type-1)]
        [store id to name nsgateway_template_id]
    [select Enterprise (name of DemoEnterprise)]
        NSGateway
            TCPMSSEnabled = False
            name = 'West-Branch-001'
            controlTrafficDSCPValue = 56
            controlTrafficCOSValue = 7
            templateID = [retrieve nsgateway_template_id (NSGatewayTemplate:id)]
            SSHService = 'INHERITED'
            description = 'NSGateway West-Branch-001'
            [select Bootstrap ($position of 0)]
                ZFBMatchValue = 'NS1550Q0448'
                ZFBMatchAttribute = 'SERIAL_NUMBER'

```
