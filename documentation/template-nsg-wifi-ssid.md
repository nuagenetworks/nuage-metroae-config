## Feature Template: SSID Connection
#### Description
Define SSID configuration for NSG Wifi Port

#### Usage
The SSID properties of NSG Wifi port can be configured using SSID Connection template.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/ssid_connection.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define SSID configuration for NSG Wifi Port
- template: SSID Connection
  values:
    - nsg_name: ""                             # (reference) name of the nsg where wifi port exists.
      enterprise_name: ""                      # (reference) name of the enterpise where nsg wifi port exists.
      wifi_port_name: ""                       # (reference) name of the wifi port on the nsg.
      ssid_connection_name: ""                 # (string) name for the SSID connection that gets displayed to the end user.
      description: ""                          # (opt string) optional description of the SSID connection.
      broadcast_ssid: False                    # (opt boolean) display SSID name to end users. Defaults to True.
      authentication_mode: captive_portal      # (opt ['captive_portal', 'open', 'wep', 'wpa', 'wpa2', 'wpa_otp', 'wpa_wpa2']) sets the authentication mode for end users to use Wifi. Defaults to open.
      authentication_passphrase: ""            # (opt string) required only when authentication mode is set to wep/wpa/wpa2/wpa_otp/wpa_wpa2.
      captive_portal_profile_name: ""          # (opt reference) required only when authentication mode is set to captive_portal.
      captive_portal_redirection: configured_url # (opt ['configured_url', 'original_request']) required only when captive_portal_profile_name is set.
      captive_portal_redirection_url: ""       # (opt string) required only when captive_portal_profile_name is set and captive_portal_redirection is set to configured_url.
      generic_config: ""                       # (opt string)
      mac_white_list: []                       # (opt list of string)
      mac_black_list: []                       # (opt list of string)

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
nsg_name | required | reference | name of the nsg where wifi port exists.
enterprise_name | required | reference | name of the enterpise where nsg wifi port exists.
wifi_port_name | required | reference | name of the wifi port on the nsg.
ssid_connection_name | required | string | name for the SSID connection that gets displayed to the end user.
description | optional | string | optional description of the SSID connection.
broadcast_ssid | optional | boolean | display SSID name to end users. Defaults to True.
authentication_mode | optional | choice | sets the authentication mode for end users to use Wifi. Defaults to open.
authentication_passphrase | optional | string | required only when authentication mode is set to wep/wpa/wpa2/wpa_otp/wpa_wpa2.
captive_portal_profile_name | optional | reference | required only when authentication mode is set to captive_portal.
captive_portal_redirection | optional | choice | required only when captive_portal_profile_name is set.
captive_portal_redirection_url | optional | string | required only when captive_portal_profile_name is set and captive_portal_redirection is set to configured_url.
generic_config | optional | string | 
mac_white_list | optional | list | 
mac_black_list | optional | list | 


#### Restrictions
**create:**
* Enterprise must pre exist.
* NSG must pre exist.
* Wifi Port must pre exist on the NSG.
* If authentication mode is captive_portal, captive profile must pre exist in the enterprise.

**revert:**
* Cannot revert a SSID connection once Wifi Port is attahced as bridge port to a subnet in L3 Domain.

