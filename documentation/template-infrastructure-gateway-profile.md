## Feature Template: Infrastructure Gateway Profile
#### Description
Define specific configuration items that apply to an NSG with the Infrastructure Gateway Profile feature template.

#### Usage
As part of defining an NSG Template that creates NSGs, certain configuration settings must be pushed to the NSG. Some of these configuration settings are collected under the Infrastructure Gateway Profile. This profile is attached to an NSG Template and applies to any NSGs that are created using the defined template.

#### Template File Name
/Users/mpiecuch/levistate-templates/templates/infrastructure_gateway_profile.yml

#### User Data Requirements
If you do not provide values for the optional parameters listed below, then default values are used.

```
# Define specific configuration items that apply to an NSG with the Infrastructure Gateway Profile feature template.
- template: Infrastructure Gateway Profile
  values:
    - infrastructure_gateway_profile_name: ""  # (string) name of the Infrastructure Profile.
      description: ""                          # (opt string) optional description of the infrastructure profile.
      proxy_dns_fqdn: ""                       # (string) FQDN of the Proxy server that is used for VSD communication.
      use_two_factor_authentication: False     # (opt boolean) optional enablement of two factor authentication.
      enable_auto_deactivation: False          # (opt boolean) enable NSG to be de-activated if connectivity to the controller is lost. Default is disabled.
      auto_deactivation_time: ""               # (opt string) duration of time in which NSG will be de-activated once timer starts (loss of connectivity to controllers). Default is 7 days. Format follows ISO 8601 Duration format P<#ofDays>DT<##ofHrs>H<#ofMins>M.
      controllerless_forwarding_mode: DISABLED # (opt ['DISABLED', 'LOCAL_AND_REMOTE', 'LOCAL_ONLY']) forwarding mode after NSG has lost connectivity with all controllers. Defaults to DISABLED.
      controllerless_local_duration: ""        # (opt string) duration in which limited forwarding (local flows only) is maintained by the NSG when it has lost connectivity to all controllers.  Default is 7 days. Format follows ISO 8601 Duration format P<#ofDays>DT<##ofHrs>H<#ofMins>M.
      controllerless_remote_duration: ""       # (opt string) duration in which normal forwarding (local and remote flows) is maintained by the NSG when it has lost connectivity to all controllers.  Default is 3 days. Format follows ISO 8601 Duration format P<#ofDays>DT<##ofHrs>H<#ofMins>M.
      openflow_fastpath_sync_timeout: 0        # (opt integer) interval at which the kernel flows are optimized using an algorithm for evicting flows. Default is 1000 ms.
      openflow_eviction_threshold: 0           # (opt integer)
      openflow_audit_timer: 0                  # (opt integer) duration in seconds for which full operational state is maintained after an NSG loses connectivity to all its controllers. Default is 180 s.
      system_sync_time: ""                     # (opt string) optional Upgrade and Configuration Time in crontab format. "Min Hr * * DaysofWeek".
      upgrade_policy: DOWNLOAD_AND_UPGRADE_AT_WINDOW # (opt ['DOWNLOAD_AND_UPGRADE_AT_WINDOW', 'DOWNLOAD_AND_UPGRADE_NOW', 'DOWNLOAD_ONLY', 'NONE', 'UPGRADE_AT_BOOTSTRAPPING', 'UPGRADE_NOW']) defaults to NONE. Policy on when to apply NSG upgrades.
      upgrade_metadata_url: ""                 # (opt string) location/Path to the upgrade metadata file.
      stats_collector_port: 0                  # (opt integer) port on which the NSG will export stats to the Proxy. Defaults to 39090.
      ntp_server_key_id: 0                     # (opt integer) NTP Key ID as defined in VSC for NTP sync.
      ntp_server_key: ""                       # (opt string)
      remote_logging_mode: DISABLED            # (opt ['DISABLED', 'RSYSLOG']) defaults to Disabled. Optional enablement of rsyslog.
      remote_log_server_address: ""            # (opt string) If remote logging is enabled, IP address of rsyslog server.
      remote_log_server_port: 0                # (opt integer) If remote logging is enabled,  Protocol port of the rsyslog server.

```

#### Parameters
*infrastructure_gateway_profile_name:* name of the Infrastructure Profile.<br>
*description:* optional description of the infrastructure profile.<br>
*proxy_dns_fqdn:* FQDN of the Proxy server that is used for VSD communication.<br>
*use_two_factor_authentication:* optional enablement of two factor authentication.<br>
*enable_auto_deactivation:* enable NSG to be de-activated if connectivity to the controller is lost. Default is disabled.<br>
*auto_deactivation_time:* duration of time in which NSG will be de-activated once timer starts (loss of connectivity to controllers). Default is 7 days. Format follows ISO 8601 Duration format P<#ofDays>DT<##ofHrs>H<#ofMins>M.<br>
*controllerless_forwarding_mode:* forwarding mode after NSG has lost connectivity with all controllers. Defaults to DISABLED.<br>
*controllerless_local_duration:* duration in which limited forwarding (local flows only) is maintained by the NSG when it has lost connectivity to all controllers.  Default is 7 days. Format follows ISO 8601 Duration format P<#ofDays>DT<##ofHrs>H<#ofMins>M.<br>
*controllerless_remote_duration:* duration in which normal forwarding (local and remote flows) is maintained by the NSG when it has lost connectivity to all controllers.  Default is 3 days. Format follows ISO 8601 Duration format P<#ofDays>DT<##ofHrs>H<#ofMins>M.<br>
*openflow_fastpath_sync_timeout:* interval at which the kernel flows are optimized using an algorithm for evicting flows. Default is 1000 ms.<br>
*openflow_eviction_threshold:* <br>
*openflow_audit_timer:* duration in seconds for which full operational state is maintained after an NSG loses connectivity to all its controllers. Default is 180 s.<br>
*system_sync_time:* optional Upgrade and Configuration Time in crontab format. "Min Hr * * DaysofWeek".<br>
*upgrade_policy:* defaults to NONE. Policy on when to apply NSG upgrades.<br>
*upgrade_metadata_url:* location/Path to the upgrade metadata file.<br>
*stats_collector_port:* port on which the NSG will export stats to the Proxy. Defaults to 39090.<br>
*ntp_server_key_id:* NTP Key ID as defined in VSC for NTP sync.<br>
*ntp_server_key:* <br>
*remote_logging_mode:* defaults to Disabled. Optional enablement of rsyslog.<br>
*remote_log_server_address:* If remote logging is enabled, IP address of rsyslog server.<br>
*remote_log_server_port:* If remote logging is enabled,  Protocol port of the rsyslog server.<br>


#### Restrictions
**create:**
* Name of the gateway profile must be unique.
* controllerless_remote_duration cannot exceed controllerless_local_duration, which cannot exceed auto_deactivation_time.

**revert:**
* Cannot revert a profile that is attached to a NSG template.

