## Feature Template: VSD User
#### Description
Define a VSD user account that is part of an enterprise. This user can also be used an installer that bootstraps NSG device.

#### Usage
VSD User can be part of enterprise. This user can be granted admin or root privilages from the VSD UI. This User can also be used as installer for NSG bootstrapping porcess. During the NSG bootstrapping process a user is notified with credentials required to bootstrap a NSG. The notification and process depends on the type of bootstrapping for the site. To enable a user to be notified of a site bootstrapping request an installer user account must be created.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/vsd_user.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define a VSD user account that is part of an enterprise. This user can also be used an installer that bootstraps NSG device.
- template: VSD User
  values:
    - enterprise_name: ""                      # (opt reference) name of the enterprise in which user will be created.
      username: ""                             # (string) username of the user.
      password: ""                             # (string) password for the user.
      first_name: ""                           # (string) first name of the user.
      last_name: ""                            # (string) last name of the user.
      email: ""                                # (string) email address of the user. This email is also used to receive nsg activation link as part of bootstrap process.
      mobile_number: ""                        # (opt string) optional mobile number of the user to receive sms.

```

#### Parameters
*enterprise_name:* name of the enterprise in which user will be created.<br>
*username:* username of the user.<br>
*password:* password for the user.<br>
*first_name:* first name of the user.<br>
*last_name:* last name of the user.<br>
*email:* email address of the user. This email is also used to receive nsg activation link as part of bootstrap process.<br>
*mobile_number:* optional mobile number of the user to receive sms.<br>


#### Restrictions
**create:**
* Username name must be unique.

**revert:**
* no restrictions

#### Examples
