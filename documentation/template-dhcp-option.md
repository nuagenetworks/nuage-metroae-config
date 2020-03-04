## Feature Template: DHCP Option
#### Description
Add DHCP Options to VSD managed DHCP

#### Usage
DHCP Options can be added to Subnets within L3 Domains or L2 Domains where DHCP is provided by VSD. The options added will be included in the DHCP lease response from the client that requested DHCP lease from the VRS/NSG.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/dhcp_option.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Add DHCP Options to VSD managed DHCP
- template: DHCP Option
  values:
    - enterprise_name: ""                      # (reference) name of the enterprise in which to create the DHCP Pool.
      domain_name: ""                          # (opt reference) If configuring on L3 Domain the name of the domain in which to add the DHCP Option.
      zone_name: ""                            # (opt reference) If configuring on L3 Domain the name of the zone in which to add the DHCP Option.
      subnet_name: ""                          # (opt reference) If configuring on L3 Domain the name of the subnet in which to add the DHCP Option.
      l2_domain_name: ""                       # (opt reference) If configuring on L2 Domain the name of the domain in which to add the DHCP Option.
      type: 0                                  # (integer) DHCP Option as defined by IANA https://www.iana.org/assignments/bootp-dhcp-parameters/bootp-dhcp-parameters.xhtml.
      values: []                               # (list of string) Value for DHCP Option, format is a list but defined by the Option type.

```

#### Parameters
*enterprise_name:* name of the enterprise in which to create the DHCP Pool.<br>
*domain_name:* If configuring on L3 Domain the name of the domain in which to add the DHCP Option.<br>
*zone_name:* If configuring on L3 Domain the name of the zone in which to add the DHCP Option.<br>
*subnet_name:* If configuring on L3 Domain the name of the subnet in which to add the DHCP Option.<br>
*l2_domain_name:* If configuring on L2 Domain the name of the domain in which to add the DHCP Option.<br>
*type:* DHCP Option as defined by IANA https://www.iana.org/assignments/bootp-dhcp-parameters/bootp-dhcp-parameters.xhtml.<br>
*values:* Value for DHCP Option, format is a list but defined by the Option type.<br>


#### Restrictions
**create:**
* Each DHCP Option can only be configured once per Subnet or L2 Domain.
* Must follow appropriate format for each DHCP Option.
* Must include either L2 Domain or L3 Domain name, zone and subnet.
* Only one option can be created per dataset.

**revert:**
* Revert is not supported for DHCP Options

