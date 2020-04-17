## Feature Template: Captive Portal Profile
#### Description
Define a landing page for NSG WiFi Access network when the WiFi authentication mode is set to Captive Portal with the Captive Portal Profile feature template.

#### Usage
When adding WiFi access to an NSG the authentication mode to permit users to access the network can support different modes. In the case where the mode of authentication for a particular SSID is set to "Captive Portal" then a Captive Portal Profile must be created and added to the SSID configuration.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/captive_portal_profile.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define a landing page for NSG WiFi Access network when the WiFi authentication mode is set to Captive Portal with the Captive Portal Profile feature template.
- template: Captive Portal Profile
  values:
    - enterprise_name: ""                      # (reference) name of the Enteprise where the Captive Portal Profile is being created.
      captive_portal_profile_name: ""          # (string) name of the Captive Portal Profile.
      description: ""                          # (opt string) optional description of the Captive Portal Profile.
      captive_portal_page: ""                  # (string) webpage based Text to be displayed to the user accessing the WiFi network as the "Network Access Agreement". No formatting is necessary and supports basic HTML tags. For multiline page text a YAML multiline Block Style Indicator is required (pipe "|").

```

#### Parameters
Name | Required | Type | Description
---- | -------- | ---- | -----------
enterprise_name | required | reference | name of the Enteprise where the Captive Portal Profile is being created.
captive_portal_profile_name | required | string | name of the Captive Portal Profile.
description | optional | string | optional description of the Captive Portal Profile.
captive_portal_page | required | string | webpage based Text to be displayed to the user accessing the WiFi network as the "Network Access Agreement". No formatting is necessary and supports basic HTML tags. For multiline page text a YAML multiline Block Style Indicator is required (pipe "|").


#### Restrictions
**create:**
* Captive Portal Profile name must be unique within the Enterprise.

**revert:**
* Cannot revert a Captive Portal Profile that is attached to an Wireless Port SSID.

