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
*enterprise_name:* name of the Enteprise where the Captive Portal Profile is being created.<br>
*captive_portal_profile_name:* name of the Captive Portal Profile.<br>
*description:* optional description of the Captive Portal Profile.<br>
*captive_portal_page:* webpage based Text to be displayed to the user accessing the WiFi network as the "Network Access Agreement". No formatting is necessary and supports basic HTML tags. For multiline page text a YAML multiline Block Style Indicator is required (pipe "|").<br>


#### Restrictions
**create:**
* Captive Portal Profile name must be unique within the Enterprise.

**revert:**
* Cannot revert a Captive Portal Profile that is attached to an Wireless Port SSID.

#### Examples

##### Creating a Captive Portal Profile with basic HTML Tagging
This example creates a Captive Portal Profile with some basic formatting. Note that due to the userdata YAML formatting requirements the blob of text must be specifically indented on each line within the captive_portal_page: value. we use pipe ("|") to indicate that its multi-line input.  nsg-access-wifi-captive-portal-profile.yaml
```
- template: Captive Portal Profile
  values:
    - enterprise_name: DemoEnterprise
      captive_portal_profile_name: "Branch-Site-Wifi-Access"
      captive_portal_page: |
        <p>This is a restricted Network for authorized access only, unauthorized access is strictly prohibited</p>
        <ul>
        <li>access restriction 1<li/>
        <li>access restriction 2<li/>
        <ul/>

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        CaptivePortalProfile
            portalType = 'CLICK_THROUGH'
            captivePage = '<p>This is a restricted Network for authorized access only, unauthorized access is strictly prohibited</p>
<ul>
<li>access restriction 1<li/>
<li>access restriction 2<li/>
<ul/>'
            name = 'Branch-Site-Wifi-Access'
            description = 'Captive Portal Profile Branch-Site-Wifi-Access'

```
