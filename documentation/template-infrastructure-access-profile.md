## Feature Template: Infrastructure Access Profile
#### Description
Define SSH settings for remote access to bootstrapped NSGs with the Infrastructure Access Profile feature template.

#### Usage
In many cases console access to an NSG is not operationally feasible. The Infrastructure Access Profile is used to define SSH settings that will be pushed to the NSG as part of bootstrapping and configuration sync. The Infrastructure Access Profile is attached to an NSG Template, that itself is used to define an NSG to be deployed.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/infrastructure_access_profile.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define SSH settings for remote access to bootstrapped NSGs with the Infrastructure Access Profile feature template.
- template: Infrastructure Access Profile
  values:
    - infrastructure_access_profile_name: ""   # (string) name of the access profile. Must be unique.
      description: ""                          # (opt string) optional description of the profile.
      ssh_auth_mode: KEY_BASED                 # (['KEY_BASED', 'PASSWORD_AND_KEY_BASED', 'PASSWORD_BASED']) choice of authentication modes supported by the user account on the NSG. Defaults to SSH Key only (KEY_BASED).
      user_name: ""                            # (string) username of the user account to be configured on the NSG.
      password: ""                             # (string) regardless of the auth mode selected a password is required. It is the password that will be configured for the user account.
      source_ip_filters: []                    # (opt list of string) optional list of IP addresses that are used to whitelist the IP source of any SSH session requests.
      ssh_key_names: []                        # (opt list of string) If KEY_BASED or PASSWORD_AND_KEY_BASED is selected as the auth mode then an SSH key must be provided. The keys are created as a name/key-value pair. The is a list of Key Names. For each key name in the list an SSH key must be provided.
      ssh_keys: []                             # (opt list of string) If KEY_BASED or PASSWORD_AND_KEY_BASED is selected as the auth mode then an SSH key must be provided. The keys are created as a name/key-value pair. This is a list of SSH Keys. For each key in the list an SSH key name must be provided.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
infrastructure_access_profile_name | required | string | name of the access profile. Must be unique.
description | optional | string | optional description of the profile.
ssh_auth_mode | required | choice | choice of authentication modes supported by the user account on the NSG. Defaults to SSH Key only (KEY_BASED).
user_name | required | string | username of the user account to be configured on the NSG.
password | required | string | regardless of the auth mode selected a password is required. It is the password that will be configured for the user account.
source_ip_filters | optional | list | optional list of IP addresses that are used to whitelist the IP source of any SSH session requests.
ssh_key_names | optional | list | If KEY_BASED or PASSWORD_AND_KEY_BASED is selected as the auth mode then an SSH key must be provided. The keys are created as a name/key-value pair. The is a list of Key Names. For each key name in the list an SSH key must be provided.
ssh_keys | optional | list | If KEY_BASED or PASSWORD_AND_KEY_BASED is selected as the auth mode then an SSH key must be provided. The keys are created as a name/key-value pair. This is a list of SSH Keys. For each key in the list an SSH key name must be provided.


#### Restrictions
**create:**
* The profile name must be unique.
* If providing SSH Keys then both a Key Name and Key value must be provided.
* Username format must follow supported VSD conventions (ie. alphanumeric only).
* Password is required regardless of the auth method.

**revert:**
* Cannot revert a profile that is currently attached a NSG Template.

