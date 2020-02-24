## Feature Template: NSGateway
#### Description
Create an NSG Instance inside an enterprise based on a specific NSG Gateway template with The NSGateway feature template.

#### Usage
NSG Instances are used to create sites in a WAN based overlay network. The NSG instance is based on a template that includes default configuration required for the NSG operation. The templates take a two step process between creation of an instance and initializing the boot strapping process.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/nsgateway.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create an NSG Instance inside an enterprise based on a specific NSG Gateway template with The NSGateway feature template.
- template: NSGateway
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which nsg will be created.
      nsg_name: ""                             # (string) name of the nsg.
      nsg_template_name: ""                    # (reference) NSG Gateway Template to use for the instance.
      description: ""                          # (opt string) optional description of the NSG instance.
      upgrade_profile_name: ""                 # (opt reference) existing upgrade profile to be attached to nsg for upgrade.
      bootstrap_match_type: HOSTNAME           # (opt ['HOSTNAME', 'IP_ADDRESS', 'MAC_ADDRESS', 'NONE', 'NSGATEWAY_ID', 'SERIAL_NUMBER']) optional match field for identifying NSG when using ZFB.
      bootstrap_match_value: ""                # (opt string) optional match value of the field selected in bootstrap_match_type when using ZFB.
      ssh_service: DISABLED                    # (opt ['DISABLED', 'ENABLED', 'INHERITED']) optional local override of template SSH setting.
      control_traffic_cos_value: 0             # (opt integer) optional COS value to mark control traffic with, defaults to 7.
      control_traffic_dscp_value: 0            # (opt integer) optional DSCO value to mark control traffic with, defaults to 56.
      tcp_mss_enabled: False                   # (opt boolean)

```

#### Parameters
*enterprise_name:* name of the enterprise in which nsg will be created.<br>
*nsg_name:* name of the nsg.<br>
*nsg_template_name:* NSG Gateway Template to use for the instance.<br>
*description:* optional description of the NSG instance.<br>
*upgrade_profile_name:* existing upgrade profile to be attached to nsg for upgrade.<br>
*bootstrap_match_type:* optional match field for identifying NSG when using ZFB.<br>
*bootstrap_match_value:* optional match value of the field selected in bootstrap_match_type when using ZFB.<br>
*ssh_service:* optional local override of template SSH setting.<br>
*control_traffic_cos_value:* optional COS value to mark control traffic with, defaults to 7.<br>
*control_traffic_dscp_value:* optional DSCO value to mark control traffic with, defaults to 56.<br>
*tcp_mss_enabled:* <br>


#### Restrictions
**create:**
* NSG name must be unique within an enterprise.
* NSG template referred in nsg_template_name must exist.
* ZFB bootstrap parameters only valid on NSG Template that is defined to support ZFB.
* Upgrade profile must exist.

**revert:**
* Cannot revert a NSG that has active vports attached to a subnet.

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
