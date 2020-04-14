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
Name | Required | Type | Description
---- | -------- | ---- | -----------
nsg_name | required | string | name of the nsg device that needs to be activated.
enterprise_name | required | reference | name of the enterprise in which the nsg is part of.
installer_username | required | string | username of the installer.
bootstrap_match_type | required | choice | match field for identifying NSG.
shipping_address | optional | string | pyhsical address where nsg will be activated.
locality | optional | string | pyhsical address where nsg will be activated.
state | optional | string | pyhsical address where nsg will be activated.
country | optional | string | pyhsical address where nsg will be activted.
timezone | optional | string | timezone where nsg will be activated.
send_activation | optional | boolean | send activation email to the installer.


#### Restrictions
**create:**
* Installer should pre-exist in enterprise.
* NSG should pre-exist in enterprise.

**revert:**
* No restrictions.

