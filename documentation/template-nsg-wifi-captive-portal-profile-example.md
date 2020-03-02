## Feature Template: Captive Portal Profile
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
