INVALID_ACTION_1 = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": ["not a dict"]}}]}


INVALID_ACTION_2 = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [{"bad-type": {}}]}}]}


INVALID_ACTION_3 = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"Create-object":
                 {"Type": "DomainTemplate",
                  "Select-by-field": "test_select_1"},
              "select-object": "multiple"}]}}]}


CREATE_OBJECTS_DICT = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"Create-object":
                 {"Type": "DomainTemplate",
                  "Select-by-field": "test_select_1"}},
             {"Create-object":
                 {"Type": "Domain",
                  "Select-by-field": "test_select_2"}}]}},
    {"create-object":
        {"type": "Enterprise",
         "actions": [
             {"create-object":
                 {"type": "DomainTemplate",
                  "select-by-field": "test_select_3"}},
             {"create-object":
                 {"type": "Domain",
                  "select-by-field": "test_select_4"}}]}}]}


CREATE_OBJECTS_NO_TYPE = {"actions": [
    {"Create-object":
        {"Missing-type": "Invalid"}}]}


SELECT_OBJECTS_DICT = {"actions": [
    {"Select-object":
        {"Type": "Enterprise",
         "By-field": "name",
         "Value": "test_enterprise",
         "Actions": [
             {"Select-object":
                 {"Type": "DomainTemplate",
                  "By-field": "test_field_1",
                  "Value": "test_value_1"}},
             {"Select-object":
                 {"Type": "Domain",
                  "By-field": "test_field_2",
                  "Value": "test_value_2"}}]}},
    {"select-object":
        {"type": "Enterprise",
         "By-field": "name",
         "Value": "test_enterprise_2",
         "actions": [
             {"select-object":
                 {"type": "DomainTemplate",
                  "by-field": "test_field_3",
                  "value": "test_value_3"}},
             {"select-object":
                 {"type": "Domain",
                  "by-field": "test_field_4",
                  "value": "test_value_4"}}]}}]}


SELECT_OBJECTS_NO_TYPE = {"actions": [
    {"Select-object":
        {"Missing-type": "Invalid",
         "by-field": "name",
         "value": "value"}}]}


SELECT_OBJECTS_NO_FIELD = {"actions": [
    {"Select-object":
        {"type": "Enterprise",
         "by-field": None,
         "value": "value"}}]}


SELECT_OBJECTS_NO_VALUE = {"actions": [
    {"Select-object":
        {"type": "Enterprise",
         "by-field": "name",
         "missing-value": "Invalid"}}]}


SET_VALUES_DICT = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Select-by-field": "field1",
         "Actions": [
             {"Create-object":
                 {"Type": "DomainTemplate"}},
             {"Set-values":
                 {"field1": "value1",
                  "field2": True}},
             {"Create-object":
                 {"Type": "Domain"}},
             {"Set-values":
                 {"field3": None,
                  "field4": 4}}]}}]}


SET_VALUES_NO_OBJECT = {"actions": [
    {"Set-values":
        {"field1": "value1",
         "field2": True}}]}


SET_VALUES_CONFLICT = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"Set-values":
                 {"field1": "value1",
                  "field2": True}},
             {"Set-values":
                 {"field2": False,
                  "field4": 4}}]}}]}


STORE_RETRIEVE_DICT = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"Set-values":
                 {"name": "enterprise1"}},
             {"Create-object":
                 {"Type": "DomainTemplate",
                  "Actions": [
                      {"Store-value":
                          {"from-field": "id",
                           "As-name": "template_id"}},
                      {"Set-values":
                          {"name": "domain_template"}}]}},
             {"create-object":
                 {"type": "Domain",
                  "actions": [
                      {"Set-values":
                          {"name": "domain1"}},
                      {"Retrieve-value":
                          {"To-field": "templateID",
                           "From-name": "template_id"}}]}},
             {"create-object":
                 {"type": "Domain",
                  "actions": [
                      {"retrieve-value":
                          {"to-field": "templateID",
                           "from-name": "template_id"}},
                      {"set-values":
                          {"name": "domain2"}}]}}]}}]}


STORE_NO_OBJECT = {"actions": [
    {"Store-value":
        {"from-field": "id",
         "as-name": "template_id"}}]}


RETRIEVE_NO_OBJECT = {"actions": [
    {"Retrieve-value":
        {"to-field": "id",
         "from-name": "template_id"}}]}


STORE_NO_FIELD = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"Create-object":
                 {"Type": "DomainTemplate",
                  "Actions": [
                      {"Store-value":
                          {"Missing-from-field": "Invalid",
                           "As-name": "template_id"}}]}}]}}]}


RETRIEVE_NO_FIELD = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"Create-object":
                 {"Type": "Domain",
                  "Actions": [
                      {"Retrieve-value":
                          {"Missing-to-field": "Invalid",
                           "From-name": "template_id"}}]}}]}}]}


STORE_NO_NAME = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"Create-object":
                 {"Type": "DomainTemplate",
                  "Actions": [
                      {"Store-value":
                          {"from-field": "id",
                           "As-name": None}}]}}]}}]}


RETRIEVE_NO_NAME = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"Create-object":
                 {"Type": "Domain",
                  "Actions": [
                      {"Retrieve-value":
                          {"to-field": "id",
                           "From-name": None}}]}}]}}]}


RETRIEVE_BEFORE_STORE = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"create-object":
                 {"type": "Domain",
                  "actions": [
                      {"Set-values":
                          {"name": "domain1"}},
                      {"Retrieve-value":
                          {"To-field": "templateID",
                           "From-name": "template_id"}}]}},
             {"Create-object":
                 {"Type": "DomainTemplate",
                  "Actions": [
                      {"Store-value":
                          {"from-field": "id",
                           "As-name": "template_id"}},
                      {"Set-values":
                          {"name": "domain_template"}}]}}]}}]}


STORE_SAME_TWICE = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"create-object":
                 {"type": "DomainTemplate",
                  "actions": [
                      {"Set-values":
                          {"name": "domain1"}},
                      {"Store-value":
                          {"from-field": "id",
                           "As-name": "template_id"}}]}},
             {"Create-object":
                 {"Type": "Domain",
                  "Actions": [
                      {"Store-value":
                          {"from-field": "templateID",
                           "As-name": "template_id"}},
                      {"Set-values":
                          {"name": "domain_template"}}]}}]}}]}


RETRIEVE_CONFLICT_1 = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"create-object":
                 {"type": "DomainTemplate",
                  "actions": [
                      {"Set-values":
                          {"name": "domain1"}},
                      {"Store-value":
                          {"from-field": "id",
                           "As-name": "template_id"}}]}},
             {"Create-object":
                 {"Type": "Domain",
                  "Actions": [
                      {"Set-values":
                          {"name": "domain1",
                           "templateid": "id1"}},
                      {"Retrieve-value":
                          {"To-field": "templateID",
                           "From-name": "template_id"}}]}}]}}]}


RETRIEVE_CONFLICT_2 = {"actions": [
    {"Create-object":
        {"Type": "Enterprise",
         "Actions": [
             {"create-object":
                 {"type": "DomainTemplate",
                  "actions": [
                      {"Set-values":
                          {"name": "domain1"}},
                      {"Store-value":
                          {"from-field": "id",
                           "As-name": "template_id"}}]}},
             {"Create-object":
                 {"Type": "Domain",
                  "Actions": [
                      {"Retrieve-value":
                          {"To-field": "templateID",
                           "From-name": "template_id"}},
                      {"Set-values":
                          {"name": "domain1",
                           "templateid": "id1"}}]}}]}}]}


ORDER_CREATE = {"actions": [
    {"Create-object":
        {"Type": "Level1",
         "Actions": [
             {"Create-object":
                 {"Type": "Level2",
                  "Select-by-field": "field1",
                  "Actions": [
                      {"Set-values":
                          {"field1": "L2-O1"}}]}},
             {"Create-object":
                 {"Type": "Level2",
                  "Select-by-field": "field1",
                  "Actions": [
                      {"Set-values":
                          {"field1": "L2-O2"}}]}},
             {"Set-values":
                 {"name": "L1-O1",
                  "field1": "value1"}}]}}]}


ORDER_SELECT_1 = {"actions": [
    {"Select-object":
        {"Type": "Level1",
         "By-field": "name",
         "Value": "L1-O1",
         "Actions": [
             {"Select-object":
                 {"Type": "Level2",
                  "By-field": "field1",
                  "Value": "L2-O2",
                  "Actions": [
                      {"Set-values":
                          {"field2": "value2"}},
                      {"Create-object":
                          {"Type": "Level3",
                           "Select-by-field": "field1",
                           "Actions": [
                               {"Set-values":
                                   {"field1": "L3-O1"}}]}}]}},
             {"Create-object":
                 {"Type": "Level2",
                  "Select-by-field": "field1",
                  "Actions": [
                      {"Set-values":
                          {"field1": "L2-O3"}}]}},
             {"Set-values":
                 {"field2": "value2"}}]}}]}


ORDER_SELECT_2 = {"actions": [
    {"Select-object":
        {"Type": "Level1",
         "By-field": "field1",
         "Value": "value1",
         "Actions": [
             {"Select-object":
                 {"Type": "Level2",
                  "By-field": "field1",
                  "Value": "L2-O3",
                  "Actions": [
                      {"Set-values":
                          {"field3": "value3"}},
                      {"Create-object":
                          {"Type": "Level3",
                           "Select-by-field": "field1",
                           "Actions": [
                               {"Set-values":
                                   {"field1": "L3-O2"}}]}}]}},
             {"Create-object":
                 {"Type": "Level2",
                  "Select-by-field": "field1",
                  "Actions": [
                      {"Set-values":
                          {"field1": "L2-O4"}}]}},
             {"Set-values":
                 {"field3": "value3"}}]}}]}


ORDER_STORE_1 = {"actions": [
    {"Create-object":
        {"Type": "Level1",
         "Actions": [
             {"Set-values":
                 {"name": "L1-O1"}},
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O1"}}]}}]}},
    {"Create-object":
        {"Type": "Level1",
         "Actions": [
             {"Set-values":
                 {"name": "L1-O2"}},
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O2"}}]}},
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O3"}}]}}]}}]}


ORDER_STORE_2 = {"actions": [
    {"Select-object":
        {"Type": "Level1",
         "By-field": "name",
         "Value": "L1-O2",
         "Actions": [
             {"Select-object":
                 {"Type": "Level2",
                  "By-field": "name",
                  "Value": "L2-O2",
                  "Actions": [
                      {"Store-value":
                          {"from-field": "field1",
                           "As-name": "store_1"}}]}}]}},
    {"Select-object":
        {"Type": "Level1",
         "By-field": "name",
         "Value": "L1-O1",
         "Actions": [
             {"select-object":
                 {"Type": "Level2",
                  "By-field": "name",
                  "Value": "L2-O1",
                  "Actions": [
                      {"Retrieve-value":
                          {"To-field": "field1",
                           "From-name": "store_1"}}]}}]}}]}


ORDER_STORE_3 = {"actions": [
    {"Select-object":
        {"Type": "Level1",
         "By-field": "name",
         "Value": "L1-O2",
         "Actions": [
             {"Select-object":
                 {"Type": "Level2",
                  "By-field": "name",
                  "Value": "L2-O3",
                  "Actions": [
                      {"Store-value":
                          {"from-field": "field1",
                           "As-name": "store_1"}}]}},
             {"select-object":
                 {"Type": "Level2",
                  "By-field": "name",
                  "Value": "L2-O2",
                  "Actions": [
                      {"Retrieve-value":
                          {"To-field": "field1",
                           "From-name": "store_1"}}]}}]}}]}


ORDER_STORE_4 = {"actions": [
    {"Create-object":
        {"Type": "Level1",
         "Actions": [
             {"Set-values":
                 {"name": "L1-O1"}}]}}]}


ORDER_STORE_5 = {"actions": [
    {"Select-object":
        {"Type": "Level1",
         "By-field": "name",
         "Value": "L1-O2",
         "Actions": [
             {"Store-value":
                 {"from-field": "field1",
                  "As-name": "store_1"}}]}},
    {"select-object":
        {"Type": "Level1",
         "By-field": "name",
         "Value": "L1-O1",
         "Actions": [
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O1"}},
                      {"Retrieve-value":
                          {"To-field": "field1",
                           "From-name": "store_1"}}]}}]}}]}


ORDER_DISABLE_COMBINE_1 = {"actions": [
    {"Create-object":
        {"Type": "Level1",
         "Actions": [
             {"Set-values":
                 {"name": "L1-O1"}},
             {"Store-value":
                 {"from-field": "name",
                  "As-name": "store_1"}}]}},
    {"Create-object":
        {"Type": "Level1",
         "Actions": [
             {"Set-values":
                 {"name": "L1-O2"}},
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O1"}},
                      {"Store-value":
                          {"From-field": "field1",
                           "As-name": "store_2"}}]}},
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O2"}},
                      {"Retrieve-value":
                          {"To-field": "field1",
                           "From-name": "store_1"}}]}}]}}]}


ORDER_DISABLE_COMBINE_2 = {"actions": [
    {"Select-object":
        {"Type": "Level1",
         "By-field": "name",
         "Value": "L1-O1",
         "Disable-combine": True,
         "Actions": [
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O3"}},
                      {"Retrieve-value":
                          {"To-field": "field1",
                           "From-name": "store_2"}}]}}]}}]}


CREATE_OBJECTS_SELECT_FIRST = {"actions": [
    {"Create-object":
        {"Type": "Level1",
         "Select-By-field": "$First",
         "Actions": [
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O1"}}]}}]}}]}


SELECT_OBJECTS_BY_POSITION_FIRST = {"actions": [
    {"Select-object":
        {"Type": "Level1",
         "By-field": "$Position",
         "Value": 0,
         "Actions": [
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O1"}}]}}]}}]}


SELECT_OBJECTS_BY_POSITION_LAST = {"actions": [
    {"Select-object":
        {"Type": "Level1",
         "By-field": "$Position",
         "Value": -1,
         "Actions": [
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O1"}}]}}]}}]}


SELECT_OBJECTS_BY_POSITION_OOB = {"actions": [
    {"Select-object":
        {"Type": "Level1",
         "By-field": "$Position",
         "Value": 2,
         "Actions": [
             {"Create-object":
                 {"Type": "Level2",
                  "Actions": [
                      {"Set-values":
                          {"name": "L2-O1"}}]}}]}}]}


RETRIEVE_AS_LIST = {"actions": [
    {"Create-object":
        {"Type": "Level1",
         "Actions": [
             {"Set-values":
                 {"name": "L1-O1"}},
             {"Store-value":
                 {"from-field": "name",
                  "As-name": "store_1"}}]}},
    {"Create-object":
        {"Type": "Level1",
         "Actions": [
             {"Set-values":
                 {"name": "L1-O2"}},
             {"Store-value":
                 {"from-field": "name",
                  "As-name": "store_2"}}]}},
    {"Create-object":
        {"Type": "Level1",
         "Actions": [
             {"Set-values":
                 {"name": "L1-O3"}},
             {"Retrieve-value":
                 {"To-field": "field1",
                  "From-name": "store_1",
                  "As-List": True}},
             {"Retrieve-value":
                 {"To-field": "field1",
                  "From-name": "store_2",
                  "As-List": True}}]}}]}
