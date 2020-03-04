## Feature Template: NSG ZFBInfo Download
#### Examples

##### Downloading ISO from enterprise
This example downloads ISO from an enterprise and saves it to current user path.nsg-iso-download.yaml
```
- template: NSG ZFBInfo Download
  values:
    - enterprise_name: DemoEnterprise
      nsg_template_name: West-NSG-Type-1
      download_file_path: "/tmp/demo-enterprise.iso"

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [select NSGatewayTemplate (name of West-NSG-Type-1)]
            [store id to name nsgateway_template_id]
        Job
            command = 'GET_ZFB_INFO'
            parameters = {'NSGType': 'ANY', 'mediaType': 'ISO', 'associatedEntityID': 'ValidatePlaceholder', 'associatedEntityType': 'nsgatewaytemplate'}
            parameters.associatedEntityID = [retrieve nsgateway_template_id (NSGatewayTemplate:id)]
            [save result to file /tmp/demo-enterprise.iso]

```
