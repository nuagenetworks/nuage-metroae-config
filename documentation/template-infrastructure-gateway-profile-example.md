## Feature Template: Infrastructure Gateway Profile
#### Examples

##### Creating a Basic NSG Infrastructure Profile with Minimal settings
This example creates a profile with mandatory attributes and minimal optional attributes for upgrades.  nsg-infrastructure-gateway-profile-minimal.yaml
```
- template: Infrastructure Gateway Profile
  values:
    - infrastructure_gateway_profile_name: West-NSG-profile-default
      description: "basic infrastructure profile"
      proxy_dns_fqdn: proxy.demoenterprise.net
      upgrade_policy: download_and_upgrade_at_window
      upgrade_metadata_url: "http://upgrade.demoenterprise.net/nsg/upgrade.json"

```
```
(example)$ metroae config create user-data.yml
    InfrastructureGatewayProfile
        flowEvictionThreshold = 2500
        NTPServerKeyID = 0
        name = 'West-NSG-profile-default'
        upgradeAction = 'DOWNLOAD_AND_UPGRADE_AT_WINDOW'
        proxyDNSName = 'proxy.demoenterprise.net'
        statsCollectorPort = 39090
        useTwoFactor = False
        metadataUpgradePath = 'http://upgrade.demoenterprise.net/nsg/upgrade.json'
        remoteLogMode = 'DISABLED'
        datapathSyncTimeout = 1000
        openFlowAuditTimer = 180
        description = 'basic infrastructure profile'

```

##### Creating an NSG Infrastructure Profile that Allows for Controllerless Operation
This example creates a profile with mandatory attributes along with enabling controllerless operation with customer timers of 0.5 day for remote, 1 day for local and 2 days for deactivation.  nsg-infrastructure-gateway-profile-controllerless.yaml
```
- template: Infrastructure Gateway Profile
  values:
    - infrastructure_gateway_profile_name: West-NSG-profile-controllerless
      description: "basic infrastructure profile"
      proxy_dns_fqdn: proxy.demoenterprise.net
      enable_auto_deactivation: true
      auto_deactivation_time: P1DT12H0M
      controllerless_forwarding_mode: LOCAL_AND_REMOTE
      controllerless_local_duration: P1DT0H0M
      controllerless_remote_duration: P0DT12H0M
      upgrade_policy: upgrade_at_bootstrapping
      upgrade_metadata_url: "http://upgrade.demoenterprise.net/nsg/upgrade.json"

```
```
(example)$ metroae config create user-data.yml
    InfrastructureGatewayProfile
        NTPServerKeyID = 0
        description = 'basic infrastructure profile'
        flowEvictionThreshold = 2500
        proxyDNSName = 'proxy.demoenterprise.net'
        statsCollectorPort = 39090
        upgradeAction = 'UPGRADE_AT_BOOTSTRAPPING'
        deadTimer = 'P1DT12H0M'
        controllerLessRemoteDuration = 'P0DT12H0M'
        useTwoFactor = False
        metadataUpgradePath = 'http://upgrade.demoenterprise.net/nsg/upgrade.json'
        remoteLogMode = 'DISABLED'
        datapathSyncTimeout = 1000
        controllerLessForwardingMode = 'LOCAL_AND_REMOTE'
        deadTimerEnabled = True
        controllerLessDuration = 'P1DT0H0M'
        openFlowAuditTimer = 180
        name = 'West-NSG-profile-controllerless'

```
