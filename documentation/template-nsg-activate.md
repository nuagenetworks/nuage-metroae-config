## Feature Template: NSGateway Activate
#### Description
NSGateay Activate template is used to notify an installer with the registered information for activating a NSG

#### Usage
When creating a NSG in enterprise, we would attach an installer. This installer is a VSD user that can recieve registration information through a registered email. NSGateay Activate would trigger the email, that consists the identifier for the gateway appliance to ensure that the intended gateway is activated from the site.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/nsgateway_activate.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# NSGateay Activate template is used to notify an installer with the registered information for activating a NSG
- template: NSGateway Activate
  values:
    - nsg_name: ""                             # (string) name of the nsg device that needs to be activated.
      enterprise_name: ""                      # (reference) name of the enterprise in which the nsg is part of.
      installer_username: ""                   # (string) username of the installer.
      bootstrap_match_type: HOSTNAME           # (['HOSTNAME', 'IP_ADDRESS', 'MAC_ADDRESS', 'NONE', 'NSGATEWAY_ID', 'SERIAL_NUMBER']) match field for identifying NSG.
      shipping_address: ""                     # (opt string) pyhsical address where nsg will be activated.
      locality: ""                             # (opt string) pyhsical address where nsg will be activated.
      state: ""                                # (opt string) pyhsical address where nsg will be activated.
      country: ""                              # (opt string) pyhsical address where nsg will be activted.
      timezone: ""                             # (opt string) timezone where nsg will be activated.
      send_activation: False                   # (opt boolean) send activation email to the installer.

```

#### Parameters
*nsg_name:* name of the nsg device that needs to be activated.<br>
*enterprise_name:* name of the enterprise in which the nsg is part of.<br>
*installer_username:* username of the installer.<br>
*bootstrap_match_type:* match field for identifying NSG.<br>
*shipping_address:* pyhsical address where nsg will be activated.<br>
*locality:* pyhsical address where nsg will be activated.<br>
*state:* pyhsical address where nsg will be activated.<br>
*country:* pyhsical address where nsg will be activted.<br>
*timezone:* timezone where nsg will be activated.<br>
*send_activation:* send activation email to the installer.<br>


#### Restrictions
**create:**
* Installer should pre-exist in enterprise.
* NSG should pre-exist in enterprise.

**revert:**
* No restrictions.

