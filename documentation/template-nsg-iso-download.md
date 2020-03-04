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
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | name of the existing enterprise where nsg exists.
nsg_template_name | required | string | name of the nsg tempalte created in the csproot account.
download_file_path | required | string | file name for downloaded iso.
download_format | optional | choice | 


#### Restrictions
**create:**
* Enterprise should pre exist.
* NSG Template should pre exist

**revert:**
* Not Applicable.

