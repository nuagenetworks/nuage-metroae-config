## Feature Template: Network Performance Measurement
#### Description
Network Performance Measurement Template gives the ability to turn on continuous probes between all NSGs for a given domain
for the purpose of measuring One-Way loss, delay, jitter.

#### Usage
In order to understad the overlay network health between NSGs, test traffic is initiated by constructing probes. These probes are designed by Performance Monitor template and are attached to NPM. NPM initiates probes independent of traffic ingressing the NSGs and calculates probe results by analyzing the response to received probe packets.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/network_performance_measurement.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Network Performance Measurement Template gives the ability to turn on continuous probes between all NSGs for a given domain
for the purpose of measuring One-Way loss, delay, jitter.
- template: Network Performance Measurement
  values:
    - enterprise_name: ""                      # (reference) name of the enterpirse where NPM is created.
      network_performance_measurement_name: "" # (string) name to identify NPM.
      performance_monitor_name: ""             # (reference) name of the probe that needs to be run via Performance Monitor.

```

#### Parameters
*enterprise_name:* name of the enterpirse where NPM is created.<br>
*network_performance_measurement_name:* name to identify NPM.<br>
*performance_monitor_name:* name of the probe that needs to be run via Performance Monitor.<br>


#### Restrictions
**create:**
* Enterpirse should pre exist.
* Performance Monitor should pre exist.

**revert:**
* Cannot revert a NPM when it is attached to a Domain.

