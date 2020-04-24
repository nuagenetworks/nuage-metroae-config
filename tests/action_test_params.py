import yaml


CREATE_OBJECTS_DICT = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Create-object:
        Select-by-field: test_select_1
        Type: DomainTemplate
    - Create-object:
        Select-by-field: test_select_2
        Type: Domain
- create-object:
    type: Enterprise
    actions:
    - create-object:
        select-by-field: test_select_3
        type: DomainTemplate
    - create-object:
        select-by-field: test_select_4
        type: Domain

""")


CREATE_OBJECTS_NO_TYPE = yaml.safe_load("""
actions:
- Create-object:
    Missing-type: Invalid

""")


CREATE_OBJECTS_SELECT_FIRST = yaml.safe_load("""
actions:
- Create-object:
    Select-By-field: $First
    Type: Level1
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


CREATE_OBJECTS_SELECT_LAST = yaml.safe_load("""
actions:
- Create-object:
    Select-By-field: $Last
    Type: Level1
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


FIND_NO_SELECT = yaml.safe_load("""
actions:
- Select-object:
    By-field: $child
    Type: Level1
    Value: NoMatch
    Actions:
    - Create-object:
        Actions:
        - Set-values:
            name: L2-O1
        Type: Level2
    - Select-object:
        By-field: name
        Type: Find
        Value: L2-O2

""")


FIND_SINGLE_LEVEL = yaml.safe_load("""
actions:
- Select-object:
    By-field: $child
    Type: Level1
    Value: find
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1
    - Select-object:
        By-field: name
        Type: Find
        Value: L2-O2

""")


FIND_TREE = yaml.safe_load("""
actions:
- Select-object:
    By-field: $child
    Type: Level1
    Value: level2
    Actions:
    - Select-object:
        By-field: $child
        Type: Level2
        Value: find
        Actions:
        - Create-object:
            Actions:
            - Set-values:
                name: L3-O1
            Type: Level3
        - Select-object:
            By-field: name
            Type: Find
            Value: L3-O2

""")


INVALID_ACTION_1 = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - not a dict

""")


INVALID_ACTION_2 = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - bad-type: {}

""")


INVALID_ACTION_3 = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Create-object:
        Select-by-field: test_select_1
        Type: DomainTemplate
      select-object: multiple

""")


ORDER_CREATE = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    Actions:
    - Create-object:
        Select-by-field: field1
        Type: Level2
        Actions:
        - Set-values:
            field1: L2-O1
    - Create-object:
        Select-by-field: field1
        Type: Level2
        Actions:
        - Set-values:
            field1: L2-O2
    - Set-values:
        field1: value1
        name: L1-O1

""")


ORDER_DISABLE_COMBINE_1 = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O1
    - Store-value:
        As-name: store_1
        from-field: name
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O2
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1
        - Store-value:
            As-name: store_2
            From-field: field1
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O2
        - Retrieve-value:
            From-name: store_1
            To-field: field1

""")


ORDER_DISABLE_COMBINE_2 = yaml.safe_load("""
actions:
- Select-object:
    By-field: name
    Disable-combine: true
    Type: Level1
    Value: L1-O1
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O3
        - Retrieve-value:
            From-name: store_2
            To-field: field1

""")


ORDER_MULTI_CREATE = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    Actions:
    - Create-object:
        Select-by-field: field1
        Type: Level2
        Actions:
        - Set-values:
            field1: L2-O1
            field2: value2
    - Create-object:
        Select-by-field: field1
        Type: Level2
        Actions:
        - Set-values:
            field1: L2-O2
            field2: value2
    - Set-values:
        field1: value1
        name: L1-O1

""")


ORDER_MULTI_SELECT_1 = yaml.safe_load("""
actions:
- Select-object:
    By-field:
    - name
    - field1
    Type: Level1
    Value:
    - L1-O1
    - value1
    Actions:
    - Select-object:
        By-field:
        - field1
        - field2
        Type: Level2
        Value:
        - L2-O2
        - value2
        Actions:
        - Set-values:
            field3: value3
        - Create-object:
            Select-by-field: field1
            Type: Level3
            Actions:
            - Set-values:
                field1: L3-O1
    - Create-object:
        Select-by-field: field1
        Type: Level2
        Actions:
        - Set-values:
            field1: L2-O3
            field2: value2
    - Set-values:
        field2: value2

""")


ORDER_MULTI_SELECT_2 = yaml.safe_load("""
actions:
- Select-object:
    Type: Level1
    By-field:
    - field1
    - name
    Value:
    - value1
    - L1-O1
    Actions:
    - Select-object:
        Type: Level2
        By-field:
        - field1
        - field2
        Value:
        - L2-O3
        - value2
        Actions:
        - Set-values:
            field3: value3
        - Create-object:
            Select-by-field: field1
            Type: Level3
            Actions:
            - Set-values:
                field1: L3-O2
    - Create-object:
        Type: Level2
        Select-by-field: field1
        Actions:
        - Set-values:
            field1: L2-O4
    - Set-values:
        field3: value3

""")


ORDER_SELECT_1 = yaml.safe_load("""
actions:
- Select-object:
    By-field: name
    Type: Level1
    Value: L1-O1
    Actions:
    - Select-object:
        By-field: field1
        Type: Level2
        Value: L2-O2
        Actions:
        - Set-values:
            field2: value2
        - Create-object:
            Select-by-field: field1
            Type: Level3
            Actions:
            - Set-values:
                field1: L3-O1
    - Create-object:
        Select-by-field: field1
        Type: Level2
        Actions:
        - Set-values:
            field1: L2-O3
    - Set-values:
        field2: value2

""")


ORDER_SELECT_2 = yaml.safe_load("""
actions:
- Select-object:
    By-field: field1
    Type: Level1
    Value: value1
    Actions:
    - Select-object:
        By-field: field1
        Type: Level2
        Value: L2-O3
        Actions:
        - Set-values:
            field3: value3
        - Create-object:
            Select-by-field: field1
            Type: Level3
            Actions:
            - Set-values:
                field1: L3-O2
    - Create-object:
        Select-by-field: field1
        Type: Level2
        Actions:
        - Set-values:
            field1: L2-O4
    - Set-values:
        field3: value3

""")


ORDER_STORE_1 = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O1
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O2
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O2
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O3

""")


ORDER_STORE_2 = yaml.safe_load("""
actions:
- Select-object:
    By-field: name
    Type: Level1
    Value: L1-O2
    Actions:
    - Select-object:
        By-field: name
        Type: Level2
        Value: L2-O2
        Actions:
        - Store-value:
            As-name: store_1
            from-field: field1
- Select-object:
    By-field: name
    Type: Level1
    Value: L1-O1
    Actions:
    - select-object:
        By-field: name
        Type: Level2
        Value: L2-O1
        Actions:
        - Retrieve-value:
            From-name: store_1
            To-field: field1

""")


ORDER_STORE_3 = yaml.safe_load("""
actions:
- Select-object:
    By-field: name
    Type: Level1
    Value: L1-O2
    Actions:
    - Select-object:
        By-field: name
        Type: Level2
        Value: L2-O3
        Actions:
        - Store-value:
            As-name: store_1
            from-field: field1
    - select-object:
        By-field: name
        Type: Level2
        Value: L2-O2
        Actions:
        - Retrieve-value:
            From-name: store_1
            To-field: field1

""")


ORDER_STORE_4 = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O1

""")


ORDER_STORE_5 = yaml.safe_load("""
actions:
- Select-object:
    By-field: name
    Type: Level1
    Value: L1-O2
    Actions:
    - Store-value:
        As-name: store_1
        from-field: field1
- select-object:
    By-field: name
    Type: Level1
    Value: L1-O1
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1
        - Retrieve-value:
            From-name: store_1
            To-field: field1

""")


RETRIEVE_AS_LIST = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O1
    - Store-value:
        As-name: store_1
        from-field: name
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O2
    - Store-value:
        As-name: store_2
        from-field: name
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O3
    - Retrieve-value:
        As-List: true
        From-name: store_1
        To-field: field1
    - Retrieve-value:
        As-List: true
        From-name: store_2
        To-field: field1

""")


RETRIEVE_CONFLICT_1 = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - create-object:
        type: DomainTemplate
        actions:
        - Set-values:
            name: domain1
        - Store-value:
            As-name: template_id
            from-field: id
    - Create-object:
        Type: Domain
        Actions:
        - Set-values:
            name: domain1
            templateid: id1
        - Retrieve-value:
            From-name: template_id
            To-field: templateID

""")


RETRIEVE_CONFLICT_2 = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - create-object:
        type: DomainTemplate
        actions:
        - Set-values:
            name: domain1
        - Store-value:
            As-name: template_id
            from-field: id
    - Create-object:
        Type: Domain
        Actions:
        - Retrieve-value:
            From-name: template_id
            To-field: templateID
        - Set-values:
            name: domain1
            templateid: id1

""")


RETRIEVE_BEFORE_STORE = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - create-object:
        type: Domain
        actions:
        - Set-values:
            name: domain1
        - Retrieve-value:
            From-name: template_id
            To-field: templateID
    - Create-object:
        Type: DomainTemplate
        Actions:
        - Store-value:
            As-name: template_id
            from-field: id
        - Set-values:
            name: domain_template

""")


RETRIEVE_NO_FIELD = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Create-object:
        Type: Domain
        Actions:
        - Retrieve-value:
            From-name: template_id
            Missing-to-field: Invalid

""")


RETRIEVE_NO_OBJECT = yaml.safe_load("""
actions:
- Retrieve-value:
    from-name: template_id
    to-field: id

""")


RETRIEVE_NO_NAME = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Create-object:
        Type: Domain
        Actions:
        - Retrieve-value:
            From-name: null
            to-field: id

""")


SELECT_MULTIPLE_MISSING = yaml.safe_load("""
actions:
- Select-object:
    Type: Level1
    By-field:
    - field1
    - field2
    Value:
    - value_1
    - value_4
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_MULTIPLE_SUCCESS_1 = yaml.safe_load("""
actions:
- Select-object:
    Type: Level1
    By-field:
    - field1
    - field2
    Value:
    - value_1
    - value_2
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_MULTIPLE_SUCCESS_2 = yaml.safe_load("""
actions:
- Select-object:
    Type: Level1
    By-field:
    - field1
    - field2
    Value:
    - value_3
    - value_4
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_MULTIPLE_REVERT_SUCCESS_1 = yaml.safe_load("""
actions:
- Select-object:
    Type: Level1
    By-field:
    - field1
    - field2
    Value:
    - value_5
    - value_6
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_MULTIPLE_REVERT_SUCCESS_2 = yaml.safe_load("""
actions:
- Select-object:
    Type: Level1
    By-field:
    - field1
    - field2
    Value:
    - value_7
    - value_8
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_OBJECTS_BY_POSITION_FIRST = yaml.safe_load("""
actions:
- Select-object:
    Type: Level1
    By-field: $Position
    Value: 0
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_OBJECTS_BY_POSITION_LAST = yaml.safe_load("""
actions:
- Select-object:
    By-field: $Position
    Type: Level1
    Value: -1
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_OBJECTS_BY_POSITION_OOB = yaml.safe_load("""
actions:
- Select-object:
    By-field: $Position
    Type: Level1
    Value: 2
    Actions:
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_OBJECTS_DICT = yaml.safe_load("""
actions:
- Select-object:
    Type: Enterprise
    By-field: name
    Value: test_enterprise
    Actions:
    - Select-object:
        Type: DomainTemplate
        By-field: test_field_1
        Value: test_value_1
    - Select-object:
        Type: Domain
        By-field: test_field_2
        Value: test_value_2
- select-object:
    type: Enterprise
    By-field: name
    Value: test_enterprise_2
    actions:
    - select-object:
        type: DomainTemplate
        by-field: test_field_3
        value: test_value_3
    - select-object:
        type: Domain
        by-field: test_field_4
        value: test_value_4

""")


SELECT_OBJECTS_MULTIPLE = yaml.safe_load("""
actions:
- Select-object:
    type: Enterprise
    by-field:
    - name
    - count
    value:
    - enterprise1
    - 5

""")


SELECT_OBJECTS_MULTIPLE_BAD_TYPE = yaml.safe_load("""
actions:
- Select-object:
    type: Enterprise
    by-field:
    - name
    value: 5

""")


SELECT_OBJECTS_MULTIPLE_WITH_SINGLE = yaml.safe_load("""
actions:
- Select-object:
    type: Enterprise
    by-field:
    - name
    value:
    - enterprise1

""")


SELECT_OBJECTS_MULTIPLE_MISMATCH = yaml.safe_load("""
actions:
- Select-object:
    type: Enterprise
    by-field:
    - name
    - count
    value:
    - enterprise1
    - 5
    - extra

""")


SELECT_OBJECTS_NO_FIELD = yaml.safe_load("""
actions:
- Select-object:
    type: Enterprise
    by-field: null
    value: value

""")


SELECT_OBJECTS_NO_TYPE = yaml.safe_load("""
actions:
- Select-object:
    Missing-type: Invalid
    by-field: name
    value: value

""")


SELECT_OBJECTS_NO_VALUE = yaml.safe_load("""
actions:
- Select-object:
    type: Enterprise
    by-field: name
    missing-value: Invalid

""")


SELECT_RETRIEVE_MISSING_RETRIEVE = yaml.safe_load("""
actions:
- Select-object:
    By-field: name
    Type: Object1
    Value: value_1
    Actions:
    - Store-value:
        As-name: object_id
        From-field: objectId
- Select-object:
    By-field: $retrieve-value
    Type: Object2
    Value: WRONG_VALUE
    Actions:
    - Retrieve-value:
        From-name: object_id
        To-field: id
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_RETRIEVE_NOT_RETRIEVE = yaml.safe_load("""
actions:
- Select-object:
    Type: Object1
    By-field: name
    Value: value_1
    Actions:
    - Store-value:
        As-name: object_id
        From-field: objectId
- Select-object:
    Type: Object2
    By-field: $retrieve-value
    Value: id
    Actions:
    - Set-values:
        id: NOT_RETRIEVE
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SELECT_RETRIEVE_VALUE = yaml.safe_load("""
actions:
- Select-object:
    Type: Object1
    By-field: name
    Value: value_1
    Actions:
    - Store-value:
        As-name: object_id
        From-field: objectId
- Select-object:
    Type: Object2
    By-field: $retrieve-value
    Value: id
    Actions:
    - Retrieve-value:
        From-name: object_id
        To-field: id
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1

""")


SET_VALUES_DICT = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Select-by-field: field1
    Actions:
    - Create-object:
        Type: DomainTemplate
    - Set-values:
        field1: value1
        field2: true
    - Create-object:
        Type: Domain
    - Set-values:
        field3: null
        field4: 4

""")


SET_VALUES_CONFLICT = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Set-values:
        field1: value1
        field2: true
    - Set-values:
        field2: false
        field4: 4

""")


SET_VALUES_NO_OBJECT = yaml.safe_load("""
actions:
- Set-values:
    field1: value1
    field2: true

""")


STORE_NO_FIELD = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Create-object:
        Type: DomainTemplate
        Actions:
        - Store-value:
            As-name: template_id
            Missing-from-field: Invalid

""")


STORE_NO_OBJECT = yaml.safe_load("""
actions:
- Store-value:
    as-name: template_id
    from-field: id

""")


STORE_NO_NAME = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Create-object:
        Type: DomainTemplate
        Actions:
        - Store-value:
            As-name: null
            from-field: id

""")


STORE_RETRIEVE_DICT = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Set-values:
        name: enterprise1
    - Create-object:
        Type: DomainTemplate
        Actions:
        - Store-value:
            As-name: template_id
            from-field: id
        - Set-values:
            name: domain_template
    - create-object:
        type: Domain
        actions:
        - Set-values:
            name: domain1
        - Retrieve-value:
            From-name: template_id
            To-field: templateID
    - create-object:
        type: Domain
        actions:
        - retrieve-value:
            from-name: template_id
            to-field: templateID
        - set-values:
            name: domain2

""")


STORE_SAME_TWICE = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - create-object:
        type: DomainTemplate
        actions:
        - Set-values:
            name: domain1
        - Store-value:
            As-name: template_id
            from-field: id
    - Create-object:
        Type: Domain
        Actions:
        - Store-value:
            As-name: template_id
            from-field: templateID
        - Set-values:
            name: domain_template

""")


STORE_RETRIEVE_TO_OBJECT = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Set-values:
        name: enterprise1
    - Create-object:
        Type: NSGatewayTemplate
        Actions:
        - Store-value:
            As-name: template_id
            from-field: id
        - Set-values:
            name: nsg_template
    - create-object:
        type: Job
        actions:
        - Set-values:
            parameters:
                type: ISO
        - Retrieve-value:
            From-name: template_id
            To-field: parameters.entityID

""")


STORE_RETRIEVE_TO_OBJECT_NOT_SET = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Set-values:
        name: enterprise1
    - Create-object:
        Type: NSGatewayTemplate
        Actions:
        - Store-value:
            As-name: template_id
            from-field: id
        - Set-values:
            name: nsg_template
    - create-object:
        type: Job
        actions:
        - Set-values:
            wrongName:
                type: ISO
        - Retrieve-value:
            From-name: template_id
            To-field: parameters.entityID

""")


STORE_RETRIEVE_TO_OBJECT_NOT_DICT = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Set-values:
        name: enterprise1
    - Create-object:
        Type: NSGatewayTemplate
        Actions:
        - Store-value:
            As-name: template_id
            from-field: id
        - Set-values:
            name: nsg_template
    - create-object:
        type: Job
        actions:
        - Set-values:
            parameters: not a dictionary
        - Retrieve-value:
            From-name: template_id
            To-field: parameters.entityID

""")


STORE_RETRIEVE_TO_OBJECT_ALREADY_SET = yaml.safe_load("""
actions:
- Create-object:
    Type: Enterprise
    Actions:
    - Set-values:
        name: enterprise1
    - Create-object:
        Type: NSGatewayTemplate
        Actions:
        - Store-value:
            As-name: template_id
            from-field: id
        - Set-values:
            name: nsg_template
    - create-object:
        type: Job
        actions:
        - Set-values:
            parameters:
                type: ISO
                entityID: already set
        - Retrieve-value:
            From-name: template_id
            To-field: parameters.entityID

""")


SAVE_TO_FILE = yaml.safe_load("""
actions:
- Create-object:
    Type: Job
    Actions:
      - set-values:
          command: GET_ZFB_INFO
          parameters:
              mediaType: ISO
      - Save-to-file:
          File-path: /tmp/pytest_save_to_file.txt
          Append-to-file: false
          From-field: result
          Write-to-console: True

""")


SAVE_TO_FILE_AND_CONSOLE = yaml.safe_load("""
actions:
- Create-object:
    Type: Job
    Actions:
      - set-values:
          command: GET_ZFB_INFO
          parameters:
              mediaType: ISO
      - Save-to-file:
          File-path: /tmp/pytest_save_to_file.txt
          Append-to-file: false
          From-field: result
          Write-to-console: true
""")


SAVE_TO_FILE_NO_FILE = yaml.safe_load("""
actions:
- Create-object:
    Type: Job
    Actions:
      - set-values:
          command: GET_ZFB_INFO
          parameters:
              mediaType: ISO
      - Save-to-file:
          Append-to-file: false
          From-field: result

""")


SAVE_TO_FILE_APPEND = yaml.safe_load("""
actions:
- Create-object:
    Type: Job
    Actions:
      - set-values:
          command: GET_ZFB_INFO
          parameters:
              mediaType: ISO
      - Save-to-file:
          File-path: /tmp/pytest_save_to_file.txt
          Prefix-string: "no:"
          Suffix-string: ":value"
      - Save-to-file:
          File-path: /tmp/pytest_save_to_file.txt
          Append-to-file: true
          Prefix-string: "prefix:"
          From-field: result
          Suffix-string: ":suffix"
          Write-to-console: False
""")

UPDATE_ROOT_OBJECT = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O1
""")

UPDATE_ROOT_UPDATE_NOT_SUPPORTED_OBJECT = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    update-supported: False
    Actions:
    - Set-values:
        name: L1-O1
    - store-value:
        as-name: level1_id
        from-field: id
""")

UPDATE_CHILD_OBJECT_WITH_FIRST_SELECTOR = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    update-supported: False
    Actions:
    - Set-values:
        name: L1-O1
    - Create-object:
        type: Level2
        select-by-field: $first
        Actions:
        - Set-values:
            value: L2
""")

UPDATE_CHILD_OBJECT_WITH_LAST_SELECTOR = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    update-supported: False
    Actions:
    - Set-values:
        name: L1-O1
    - Create-object:
        type: Level2
        select-by-field: $last
        Actions:
        - Set-values:
            value: L2
""")

UPDATE_SELECT_ROOT_OBJECT = yaml.safe_load("""
actions:
- Select-object:
    Type: Level1
    by-field: name
    value: L1-01
    Actions:
    - Set-values:
        name: L1-O1
    - store-value:
        as-name: level1_id
        from-field: id
""")

UPDATE_CREATE_CHILD_OBJECT = yaml.safe_load("""
actions:
- Create-object:
    Type: Level1
    Actions:
    - Set-values:
        name: L1-O1
    - Create-object:
        Type: Level2
        Actions:
        - Set-values:
            name: L2-O1
""")
