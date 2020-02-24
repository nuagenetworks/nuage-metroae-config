## Feature Template: NSG ZFBInfo Download
#### Description
Download the ISO for Zero Factor Bootstrapping of NSG Gateway in an enterprise.

#### Usage
Zero Factor Bootstrapping allows NSG Gateway to be activated without user interventio. To acheive this, NSG has to be create in the enterprise and download the ISO. This ISO is later attached to a physical NSG through USB or through mount for virtual NSG in case of vmWare, kvm, openstack environments.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/nsg_zfbinfo_download.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Download the ISO for Zero Factor Bootstrapping of NSG Gateway in an enterprise.
- template: NSG ZFBInfo Download
  values:
    - enterprise_name: ""                      # (reference) name of the existing enterprise where nsg exists.
      nsg_template_name: ""                    # (string) name of the nsg tempalte created in the csproot account.
      download_file_path: ""                   # (string) file name for downloaded iso.
      download_format: iso                     # (opt ['iso', 'yaml'])

```

#### Parameters
*enterprise_name:* name of the existing enterprise where nsg exists.<br>
*nsg_template_name:* name of the nsg tempalte created in the csproot account.<br>
*download_file_path:* file name for downloaded iso.<br>
*download_format:* <br>


#### Restrictions
**create:**
* Enterprise should pre exist.
* NSG Template should pre exist

**revert:**
* Not Applicable.

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
