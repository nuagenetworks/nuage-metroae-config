## Feature Template: ZFB Auto Assignment
#### Examples

##### Creating a ZFB Auto Assignment.
This example creates a ZFB Auto Assignment for auto-assigning incoming auto-bootstrapping requests to a pre existing Enterprise.nsg-zfb-auto-assignment.yaml
```
- template: ZFB Auto Assignment
  values:
    - enterprise_name: "DemoEnterprise"
      zfb_auto_assignment_name: "West-Branch-001"
      description: "Auto assign West-Branch-001 to DemoEnterprise"
      priority: 10
      zfb_match_attribute: "SERIAL_NUMBER"
      zfb_match_attribute_values: ["NS1550Q0448"]

```
```
(example)$ metroae config create user-data.yml
    [select Enterprise (name of DemoEnterprise)]
        [store id to name enterprise_id]
    ZFBAutoAssignment
        name = 'West-Branch-001'
        ZFBMatchAttributeValues = ['NS1550Q0448']
        associatedEnterpriseName = 'DemoEnterprise'
        priority = 10
        associatedEnterpriseID = [retrieve enterprise_id (Enterprise:id)]
        ZFBMatchAttribute = 'SERIAL_NUMBER'
        description = 'Auto assign West-Branch-001 to DemoEnterprise'

```
