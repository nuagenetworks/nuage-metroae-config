## Feature Template: SSID Connection
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
(example)$ metroae config create user-data.yml
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
(example)$ metroae config create user-data.yml
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
(example)$ metroae config create user-data.yml
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
