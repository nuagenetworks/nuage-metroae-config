## Feature Template: Underlay
#### Examples

##### Creating a Single Underlay
This example configures a single underlay tag. nsg-infrastructure-single-underlay.yaml
```
- template: Underlay
  values:
    - underlay_name: Underlay-MPLS-1
      description: Underlay Tag for MPLS Provider 1

```
```
(example)$ metroae config create user-data.yml
    Underlay
        name = 'Underlay-MPLS-1'
        description = 'Underlay Tag for MPLS Provider 1'

```

##### Creating Multiple Underlays with a Single Template
This example configures three underlays with a single user data template.  nsg-infrastructure-multiple-underlay.yaml
```
- template: Underlay
  values:
    - underlay_name: Underlay-MPLS-1
      description: Underlay Tag for MPLS Provider 1
    - underlay_name: Underlay-MPLS-2
      description: Underlay Tag for MPLS Provider 2
    - underlay_name: Underlay-Internet-1
      decription: Underlay Tag for Internet Provider 1

```
```
(example)$ metroae config create user-data.yml
    Underlay
        name = 'Underlay-MPLS-1'
        description = 'Underlay Tag for MPLS Provider 1'
    Underlay
        name = 'Underlay-MPLS-2'
        description = 'Underlay Tag for MPLS Provider 2'
    Underlay
        name = 'Underlay-Internet-1'
        description = 'Underlay Underlay-Internet-1'

```
