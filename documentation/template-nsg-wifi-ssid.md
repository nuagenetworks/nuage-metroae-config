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
*nsg_name:* name of the nsg where wifi port exists.<br>
*enterprise_name:* name of the enterpise where nsg wifi port exists.<br>
*wifi_port_name:* name of the wifi port on the nsg.<br>
*ssid_connection_name:* name for the SSID connection that gets displayed to the end user.<br>
*description:* optional description of the SSID connection.<br>
*broadcast_ssid:* display SSID name to end users. Defaults to True.<br>
*authentication_mode:* sets the authentication mode for end users to use Wifi. Defaults to open.<br>
*authentication_passphrase:* required only when authentication mode is set to wep/wpa/wpa2/wpa_otp/wpa_wpa2.<br>
*captive_portal_profile_name:* required only when authentication mode is set to captive_portal.<br>
*captive_portal_redirection:* required only when captive_portal_profile_name is set.<br>
*captive_portal_redirection_url:* required only when captive_portal_profile_name is set and captive_portal_redirection is set to configured_url.<br>
*generic_config:* <br>
*mac_white_list:* <br>
*mac_black_list:* <br>


#### Restrictions
**create:**
* Enterprise must pre exist.
* NSG must pre exist.
* Wifi Port must pre exist on the NSG.
* If authentication mode is captive_portal, captive profile must pre exist in the enterprise.

**revert:**
* Cannot revert a SSID connection once Wifi Port is attahced as bridge port to a subnet in L3 Domain.

#### Examples

##### Create a SSID template  on a Wifi Port
This example creates a single SSID connection with minimal data.  nsg-wifi-ssid-minimal.yaml
```
- template: SSID Connection
  values:
    - nsg_name: West-Branch-001
      enterprise_name: DemoEnterprise
      wifi_port_name: West-Branch-Building1-Wifi-Port
      broadcast_ssid: True
      ssid_connection_name: "Nuage"
      authentication_mode: open

```
```
[metroae-user@metroae-host]# metroae config create nsg-wifi-ssid-minimal.yaml
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of West-Branch-001)]
            [select WirelessPort (name of West-Branch-Building1-Wifi-Port)]
                SSIDConnection
                    broadcastSSID = True
                    authenticationMode = 'OPEN'
                    description = 'SSID Connection Nuage'
                    name = 'Nuage'
                    redirectOption = 'ORIGINAL_REQUEST'

```

##### Create SSID connection with captive portal
This example creates SSID connection on Wifi port with captive portal information.nsg-wifi-ssid-captive-portal.yaml
```
- template: SSID Connection
  values:
    - nsg_name: West-Branch-001
      enterprise_name: DemoEnterprise
      wifi_port_name: West-Branch-Building1-Wifi-Port
      broadcast_ssid: True
      ssid_connection_name: "Nuage-Guest"
      authentication_mode: captive_portal
      captive_portal_profile_name: West-Branch-Wifi-Guest-Portal
      captive_portal_redirection: original_request

```
```
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [select CaptivePortalProfile (name of West-Branch-Wifi-Guest-Portal)]
            [store id to name captive_portal_profile_id]
        [select NSGateway (name of West-Branch-001)]
            [select WirelessPort (name of West-Branch-Building1-Wifi-Port)]
                SSIDConnection
                    broadcastSSID = True
                    description = 'SSID Connection Nuage-Guest'
                    associatedCaptivePortalProfileID = [retrieve captive_portal_profile_id (CaptivePortalProfile:id)]
                    authenticationMode = 'CAPTIVE_PORTAL'
                    redirectOption = 'ORIGINAL_REQUEST'
                    name = 'Nuage-Guest'

```

##### Create SSID connection with secure access
This example creates SSID connection on Wifi port with secure password based access.nsg-wifi-ssid-secure.yaml.
```
- template: SSID Connection
  values:
    - nsg_name: West-Branch-001
      enterprise_name: DemoEnterprise
      wifi_port_name: West-Branch-Building1-Wifi-Port
      broadcast_ssid: True
      ssid_connection_name: "Nuage-Secure"
      authentication_mode: wpa2
      authentication_passphrase: nuagesecure
      mac_white_list: ["02:42:bd:fe:94:5a", "02:42:bd:fe:94:5b"]
      mac_black_list: ["fa:16:3e:77:85:3e", "fa:16:3e:77:85:3d"]

```
```
Device: Nuage Networks VSD 5.4.1
    [select Enterprise (name of DemoEnterprise)]
        [select NSGateway (name of West-Branch-001)]
            [select WirelessPort (name of West-Branch-Building1-Wifi-Port)]
                SSIDConnection
                    broadcastSSID = True
                    redirectOption = 'ORIGINAL_REQUEST'
                    whiteList = ['02:42:bd:fe:94:5a', '02:42:bd:fe:94:5b']
                    description = 'SSID Connection Nuage-Secure'
                    authenticationMode = 'WPA2'
                    blackList = ['fa:16:3e:77:85:3e', 'fa:16:3e:77:85:3d']
                    passphrase = 'nuagesecure'
                    name = 'Nuage-Secure'

```
