## Feature Template: Wifi Port
#### Description
Define a Wifi Port on an nsg instance within an enterprise

#### Usage
A service provider or enterprise can deploy WiFi-enabled NSGs in branch locations to provide Access Point (AP) capabilities. Wifi Port template lets you create the Wifi Port on the NSG

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/wifi_port.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define a Wifi Port on an nsg instance within an enterprise
- template: Wifi Port
  values:
    - nsg_name: ""                             # (reference) name of the nsg where wifi port will be created.
      enterprise_name: ""                      # (reference) name of the enterpise where nsg exists.
      wifi_port_name: ""                       # (string) name of the wifi port.
      description: ""                          # (opt string) optional description of the wifi port.
      wifi_band: 2.4GHz                        # (['2.4GHz', '5.0GHz']) frequency band for wifi port. defaults to 2.4GHz.
      country_code: AT                         # (opt ['AT', 'AU', 'BE', 'BR', 'CA', 'CH', 'CN', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GR', 'HK', 'HU', 'ID', 'IE', 'IL', 'IN', 'IT', 'JP', 'KR', 'LT', 'LU', 'LV', 'MY', 'NL', 'NO', 'NZ', 'PH', 'PL', 'PT', 'SE', 'SG', 'SI', 'SK', 'TH', 'TW', 'US', 'ZA']) country where wifi is operated. defaults to US.
      wifi_mode: a                             # (['a', 'a/ac', 'a/n', 'a/n/ac', 'b/g', 'b/g/n']) defaults to 'a'.
      frequency_channel: 0                     # (opt integer 0..14, 36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165) channel for wifi frequency. defaults to 36.
      generic_config: ""                       # (opt string) include those attributes that are not essential for beaconing as akey value pair.

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
nsg_name | required | reference | name of the nsg where wifi port will be created.
enterprise_name | required | reference | name of the enterpise where nsg exists.
wifi_port_name | required | string | name of the wifi port.
description | optional | string | optional description of the wifi port.
wifi_band | required | choice | frequency band for wifi port. defaults to 2.4GHz.
country_code | optional | choice | country where wifi is operated. defaults to US.
wifi_mode | required | choice | defaults to 'a'.
frequency_channel | optional | integer | channel for wifi frequency. defaults to 36.
generic_config | optional | string | include those attributes that are not essential for beaconing as akey value pair.


#### Restrictions
**create:**
* NSG must pre exist.
* Only one Wifi Port per NSG.

**revert:**
* Cannot revert a Wifi Port when it is attached as bridge port to a subnet in L3 Domain.

