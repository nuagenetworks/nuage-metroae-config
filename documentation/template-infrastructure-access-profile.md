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
*infrastructure_access_profile_name:* name of the access profile. Must be unique.<br>
*description:* optional description of the profile.<br>
*ssh_auth_mode:* choice of authentication modes supported by the user account on the NSG. Defaults to SSH Key only (KEY_BASED).<br>
*user_name:* username of the user account to be configured on the NSG.<br>
*password:* regardless of the auth mode selected a password is required. It is the password that will be configured for the user account.<br>
*source_ip_filters:* optional list of IP addresses that are used to whitelist the IP source of any SSH session requests.<br>
*ssh_key_names:* If KEY_BASED or PASSWORD_AND_KEY_BASED is selected as the auth mode then an SSH key must be provided. The keys are created as a name/key-value pair. The is a list of Key Names. For each key name in the list an SSH key must be provided.<br>
*ssh_keys:* If KEY_BASED or PASSWORD_AND_KEY_BASED is selected as the auth mode then an SSH key must be provided. The keys are created as a name/key-value pair. This is a list of SSH Keys. For each key in the list an SSH key name must be provided.<br>


#### Restrictions
**create:**
* The profile name must be unique.
* If providing SSH Keys then both a Key Name and Key value must be provided.
* Username format must follow supported VSD conventions (ie. alphanumeric only).
* Password is required regardless of the auth method.

**revert:**
* Cannot revert a profile that is currently attached a NSG Template.

#### Examples

##### Creating an Access Profile with Password only
This example creates a simple SSH profile using password authentication only.  nsg-infrastructure-access-profile-password.yaml
```
- template: Infrastructure Access Profile
  values:
    - infrastructure_access_profile_name: access-password
      ssh_auth_mode: password_based
      user_name: opsadmin
      password: nsgpassword

```
```
(example)$ metroae config create user-data.yml
    InfrastructureAccessProfile
        userName = 'opsadmin'
        name = 'access-password'
        SSHAuthMode = 'PASSWORD_BASED'
        sourceIPFilter = 'DISABLED'
        password = 'nsgpassword'
        description = 'Infrastructure Access Profile access-password'

```

##### Creating an Access Profile with SSH Key Authentication Only
This example creates an SSH profile using RSA keys as the authentication method. Two keys will be provided in the user data. These are listed separately in this example but can also be input via a list.  nsg-infrastructure-access-profile-sshkey.yaml
```
- template: Infrastructure Access Profile
  values:
    - infrastructure_access_profile_name: access-key
      ssh_auth_mode: key_based
      user_name: opsadminkey
      password: notarealpassword
      ssh_key_names:
        - east
        - west
      ssh_keys:
        - AAAAB3NzaC1yc2EAAAADAQABAAABAQC6om+jJ5CZJDNj10sdlM6kzJerCgr19hXx+bWBRRaWXeqz2zshR/MAzoVpAB5m9/NE+j7R9tHsuSMqGSZ8x6QTpbqgovgH3nUQURQiKpbxlY92QvE+I7Ari0n52qdRJkPC7Uw3nCxP2T7GtWslyw5OOhYZbxlNe+09rz27EiCAqoqAHttafvT+QfVBI+I5Zkbnzu3MY2p0m6MiwbR0gWYgyRETpLmVKz1rNeOpEQ2asI8i1ufVmYwHXwwxhXK8Ql/v5STnyAze7KM+/65mmppJK6mZigPD75327JACWGxJp8Z39UpSVaZb2nduhBh2qshATqFfmOCvGgqoZ5+i6O2R
        - AAAAB3NzaC1yc2EAAAADAQABAAABAQDMfGiqdgyagyiwTnqoWu3kiWCOEelFtkN3dRkWG+Vn/S4dQpROKyRntyuz2G0CsyldNJigNCqg2HO+rABW9q2i7niOq0PQsFB4QxTB4yzGh3ipdmoB0TAKjtsWJYQoEDB8MtLCTShjxRszKaKMY4Ijjq3Ah74MP4/q0ZBeRw+6mdAawsM6TPX90vaTZiknGaNJNOXYh7EbZnGOlPVRDdRk8GkVvZ7qQRW//JbNeI1eijAfUoLTaDHLbRuVMnukurd4Yp+KDjZ+49Vlv8voiNec/F7Zl1AjrB4n/hNrh3/EyovGs6ydBll9TbuDsyafn/9y+8Mjt6cCPr6QID4Lzvj5

```
```
(example)$ metroae config create user-data.yml
    InfrastructureAccessProfile
        userName = 'opsadminkey'
        name = 'access-key'
        SSHAuthMode = 'KEY_BASED'
        sourceIPFilter = 'DISABLED'
        password = 'notarealpassword'
        description = 'Infrastructure Access Profile access-key'
        SSHKey
            publicKey = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQC6om+jJ5CZJDNj10sdlM6kzJerCgr19hXx+bWBRRaWXeqz2zshR/MAzoVpAB5m9/NE+j7R9tHsuSMqGSZ8x6QTpbqgovgH3nUQURQiKpbxlY92QvE+I7Ari0n52qdRJkPC7Uw3nCxP2T7GtWslyw5OOhYZbxlNe+09rz27EiCAqoqAHttafvT+QfVBI+I5Zkbnzu3MY2p0m6MiwbR0gWYgyRETpLmVKz1rNeOpEQ2asI8i1ufVmYwHXwwxhXK8Ql/v5STnyAze7KM+/65mmppJK6mZigPD75327JACWGxJp8Z39UpSVaZb2nduhBh2qshATqFfmOCvGgqoZ5+i6O2R'
            name = 'east'
        SSHKey
            publicKey = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQDMfGiqdgyagyiwTnqoWu3kiWCOEelFtkN3dRkWG+Vn/S4dQpROKyRntyuz2G0CsyldNJigNCqg2HO+rABW9q2i7niOq0PQsFB4QxTB4yzGh3ipdmoB0TAKjtsWJYQoEDB8MtLCTShjxRszKaKMY4Ijjq3Ah74MP4/q0ZBeRw+6mdAawsM6TPX90vaTZiknGaNJNOXYh7EbZnGOlPVRDdRk8GkVvZ7qQRW//JbNeI1eijAfUoLTaDHLbRuVMnukurd4Yp+KDjZ+49Vlv8voiNec/F7Zl1AjrB4n/hNrh3/EyovGs6ydBll9TbuDsyafn/9y+8Mjt6cCPr6QID4Lzvj5'
            name = 'west'

```

##### Creating an Access Profile with Password and SSH Authentication Along with Source IP Filter
This example creates an SSH profile that enables password and key authentication but will also enforces a source IP filter for incoming SSH sessions.  nsg-infrastructure-access-profile-password-and-sshkey.yaml
```
- template: Infrastructure Access Profile
  values:
    - infrastructure_access_profile_name: access-both
      ssh_auth_mode: password_and_key_based
      user_name: opsadmin
      password: opspassword
      source_ip_filters: [1.1.1.1,2.2.2.2,3.3.3.3]
      ssh_key_names:
        - east
        - west
      ssh_keys:
        - AAAAB3NzaC1yc2EAAAADAQABAAABAQC6om+jJ5CZJDNj10sdlM6kzJerCgr19hXx+bWBRRaWXeqz2zshR/MAzoVpAB5m9/NE+j7R9tHsuSMqGSZ8x6QTpbqgovgH3nUQURQiKpbxlY92QvE+I7Ari0n52qdRJkPC7Uw3nCxP2T7GtWslyw5OOhYZbxlNe+09rz27EiCAqoqAHttafvT+QfVBI+I5Zkbnzu3MY2p0m6MiwbR0gWYgyRETpLmVKz1rNeOpEQ2asI8i1ufVmYwHXwwxhXK8Ql/v5STnyAze7KM+/65mmppJK6mZigPD75327JACWGxJp8Z39UpSVaZb2nduhBh2qshATqFfmOCvGgqoZ5+i6O2R
        - AAAAB3NzaC1yc2EAAAADAQABAAABAQDMfGiqdgyagyiwTnqoWu3kiWCOEelFtkN3dRkWG+Vn/S4dQpROKyRntyuz2G0CsyldNJigNCqg2HO+rABW9q2i7niOq0PQsFB4QxTB4yzGh3ipdmoB0TAKjtsWJYQoEDB8MtLCTShjxRszKaKMY4Ijjq3Ah74MP4/q0ZBeRw+6mdAawsM6TPX90vaTZiknGaNJNOXYh7EbZnGOlPVRDdRk8GkVvZ7qQRW//JbNeI1eijAfUoLTaDHLbRuVMnukurd4Yp+KDjZ+49Vlv8voiNec/F7Zl1AjrB4n/hNrh3/EyovGs6ydBll9TbuDsyafn/9y+8Mjt6cCPr6QID4Lzvj5

```
```
(example)$ metroae config create user-data.yml
    InfrastructureAccessProfile
        userName = 'opsadmin'
        name = 'access-both'
        SSHAuthMode = 'PASSWORD_AND_KEY_BASED'
        sourceIPFilter = 'ENABLED'
        password = 'opspassword'
        description = 'Infrastructure Access Profile access-both'
        Connectionendpoint
            IPAddress = '1.1.1.1'
            name = 'access-both_1'
        Connectionendpoint
            IPAddress = '2.2.2.2'
            name = 'access-both_2'
        Connectionendpoint
            IPAddress = '3.3.3.3'
            name = 'access-both_3'
        SSHKey
            publicKey = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQC6om+jJ5CZJDNj10sdlM6kzJerCgr19hXx+bWBRRaWXeqz2zshR/MAzoVpAB5m9/NE+j7R9tHsuSMqGSZ8x6QTpbqgovgH3nUQURQiKpbxlY92QvE+I7Ari0n52qdRJkPC7Uw3nCxP2T7GtWslyw5OOhYZbxlNe+09rz27EiCAqoqAHttafvT+QfVBI+I5Zkbnzu3MY2p0m6MiwbR0gWYgyRETpLmVKz1rNeOpEQ2asI8i1ufVmYwHXwwxhXK8Ql/v5STnyAze7KM+/65mmppJK6mZigPD75327JACWGxJp8Z39UpSVaZb2nduhBh2qshATqFfmOCvGgqoZ5+i6O2R'
            name = 'east'
        SSHKey
            publicKey = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQDMfGiqdgyagyiwTnqoWu3kiWCOEelFtkN3dRkWG+Vn/S4dQpROKyRntyuz2G0CsyldNJigNCqg2HO+rABW9q2i7niOq0PQsFB4QxTB4yzGh3ipdmoB0TAKjtsWJYQoEDB8MtLCTShjxRszKaKMY4Ijjq3Ah74MP4/q0ZBeRw+6mdAawsM6TPX90vaTZiknGaNJNOXYh7EbZnGOlPVRDdRk8GkVvZ7qQRW//JbNeI1eijAfUoLTaDHLbRuVMnukurd4Yp+KDjZ+49Vlv8voiNec/F7Zl1AjrB4n/hNrh3/EyovGs6ydBll9TbuDsyafn/9y+8Mjt6cCPr6QID4Lzvj5'
            name = 'west'

```
