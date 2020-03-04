## Feature Template: NSGateway Activate
#### Examples

##### Creating NSGateway Activate template.
This example creates NSGateway Activate template with minimal information.nsg-gateway-activate-default.yaml
```
- template: NSGateway Activate
  values:
    - nsg_name: "West-Branch-001"
      enterprise_name: "DemoEnterprise"
      installer_username: "admin"
      bootstrap_match_type: "SERIAL_NUMBER"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select User (userName of admin)]
            [store id to name installer_id]
        [select NSGateway (name of West-Branch-001)]
            [select Bootstrap ($position of 0)]
                installerID = [retrieve installer_id (User:id)]
            [select Location ($position of 0)]
                timeZoneID = 'UTC'
                country = ''
                state = ''
                locality = ''
                address = ''
            Job
                command = 'NOTIFY_NSG_REGISTRATION'

```
