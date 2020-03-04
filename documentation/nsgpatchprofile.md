## Feature Template: NSG Patch Profile
#### Description
Create a Patch Profile to apply to a NSG.

#### Usage
(documentation missing)

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/nsgpatchprofile.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Create a Patch Profile to apply to a NSG.
- template: NSG Patch Profile
  values:
    - description: ""                          # (opt string) Optional description of the NSG Patch Profile.
      name: ""                                 # (string) Name of the Patch Profile to create
      patch_url: ""                            # (string) Full URL including rpm filename of the patch.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
description | optional | string | Optional description of the NSG Patch Profile.
name | required | string | Name of the Patch Profile to create
patch_url | required | string | Full URL including rpm filename of the patch.


#### Restrictions
**create:**
* NSG Patch Profile is only created globally, cannot be created within an Enterprise.
* NSG Patch Profile name must be unique.
* NSG Patch Profile URL must conform to patch name standard.

