## Feature Template: L3 Domain
#### Examples

##### Creating a Domain with Minimal Data
In this example, the minimum required data is passed to create an L3 domain.  network-domain-default.yaml
```
- template: L3 Domain
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        DomainTemplate
            name = 'template_L3-Domain-US'
            [store id to name domain_template_id]
        Domain
            underlayEnabled = 'DISABLED'
            PATEnabled = 'DISABLED'
            aggregateFlowsEnabled = False
            name = 'L3-Domain-US'
            flowCollectionEnabled = 'DISABLED'
            templateID = [retrieve domain_template_id (DomainTemplate:id)]
            description = 'Domain L3-Domain-US'

```

##### Creating a Domain with PAT to Underlay Enabled
This example adds the parameters required to enable PAT to underlay on the domain.  network-domain-options.yaml
```
- template: L3 Domain
  values:
    enterprise_name: DemoEnterprise
    domain_name: L3-Domain-US
    descrption: "Domain with PAT to Underlay"
    underlay_enabled: enabled
    address_translation: enabled

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        DomainTemplate
            name = 'template_L3-Domain-US'
            [store id to name domain_template_id]
        Domain
            underlayEnabled = 'ENABLED'
            PATEnabled = 'ENABLED'
            aggregateFlowsEnabled = False
            name = 'L3-Domain-US'
            flowCollectionEnabled = 'DISABLED'
            templateID = [retrieve domain_template_id (DomainTemplate:id)]
            description = 'Domain L3-Domain-US'

```
