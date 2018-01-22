EXPECTED_VERSION = {"software_version": "5.0.2",
                    "software_type": "Nuage Networks VSD"}

ENTERPRISE_TEMPLATE_VARS = {"enterprise_name": "test_enterprise",
                            "$group_1": "extra"}

EXPECTED_ENTERPRISE_SCHEMA = \
    {'schema': [
        {'type': 'string',
         'required_for_delete': True,
         'name': 'enterprise_name'}]}

EXPECTED_ENTERPRISE_TEMPLATE = \
    {'name': 'Enterprise',
     'variables': [
         {'type': 'string',
          'required_for_delete': True,
          'name': 'enterprise_name'}],
     'description': 'Creates an enterprise',
     'software-version': '5.0.2',
     'template-version': '1.0',
     'actions': [
         {'create-object':
             {'type': 'Enterprise',
              'actions': [{'set-values': {'name': 'test_enterprise'}}]}}],
     'software-type': 'Nuage Networks VSD'}

DOMAIN_TEMPLATE_VARS = {"enterprise_name": "test_enterprise",
                        "domain_name": "test_domain",
                        "$group_1": "extra"}

EXPECTED_DOMAIN_SCHEMA = \
    {'schema': [
        {'type': 'reference', 'required_for_delete': True,
         'name': 'enterprise_name'},
        {'type': 'string', 'required_for_delete': True,
         'name': 'domain_name'}]}

EXPECTED_DOMAIN_TEMPLATE = \
    {'name': 'Domain',
     'description': 'Creates a domain',
     'template-version': 1.0,
     'software-type': 'Nuage Networks VSD',
     'software-version': '5.0.2',
     'variables': [
         {'type': 'reference', 'required_for_delete': True,
          'name': 'enterprise_name'},
         {'type': 'string', 'required_for_delete': True,
          'name': 'domain_name'}],
     'actions': [
         {'select-object':
             {'type': 'Enterprise',
              'by-field': 'name',
              'value': 'test_enterprise',
              'actions': [
                  {'create-object':
                      {'type': 'DomainTemplate',
                       'actions': [
                           {'set-values':
                               {'name': 'template_test_domain'}},
                           {'store-value':
                               {'from-field': 'id',
                                'as-name': 'domain_template_id'}}]}},
                  {'create-object':
                      {'type': 'Domain',
                       'actions': [
                           {'set-values':
                               {'name': 'test_domain'}},
                           {'retrieve-value':
                               {'to-field': 'templateID',
                                'from-name': 'domain_template_id'}}]}}]}}]}

ACL_TEMPLATE_VARS = {
    'enterprise_name': 'test_enterprise',
    'domain_name': 'test_domain',
    'acl_name': 'test_acl',
    'default_allow_ip': True,
    'default_allow_non_ip': False,
    'policy_priority': 100,
    'allow_address_spoof': False,
    'default_install_acl_implicit_rules': True,
    'description': 'Test ACL',
    'entry_priority': 200,
    'protocol': 'tcp',
    'source_port': 80,
    'destination_port': '*',
    'ether_type': '0x0800',
    'action': 'forward',
    'location_type': 'subnet',
    'location_name': 'test_subnet',
    'network_type': 'any',
    'network_name': '',
    'stateful': True,
    'flow_logging_enabled': True,
    'stats_logging_enabled': True,
    "$group_1": "extra"}

EXPECTED_ACL_SCHEMA = \
    {'schema': [{'name': 'enterprise_name',
                 'required_for_delete': True,
                 'type': 'reference'},
                {'name': 'domain_name',
                 'required_for_delete': True,
                 'type': 'reference'},
                {'name': 'acl_name',
                 'required_for_delete': True,
                 'type': 'string'},
                {'name': 'default_allow_ip', 'type': 'boolean'},
                {'name': 'default_allow_non_ip', 'type': 'boolean'},
                {'name': 'policy_priority', 'type': 'integer'},
                {'name': 'allow_address_spoof', 'type': 'boolean'},
                {'name': 'default_install_acl_implicit_rules',
                 'type': 'boolean'},
                {'name': 'description', 'type': 'string'},
                {'name': 'entry_priority', 'type': 'integer'},
                {'name': 'protocol', 'type': 'string'},
                {'name': 'source_port', 'type': 'string'},
                {'name': 'destination_port', 'type': 'string'},
                {'name': 'ether_type', 'type': 'string'},
                {'choices': ['forward', 'drop'],
                 'name': 'action',
                 'type': 'choice'},
                {'choices': ['any', 'policygroup', 'subnet', 'zone'],
                 'name': 'location_type',
                 'type': 'choice'},
                {'name': 'location_name', 'type': 'string'},
                {'choices': ['any', 'policygroup', 'subnet', 'zone'],
                 'name': 'network_type',
                 'type': 'choice'},
                {'name': 'network_name', 'type': 'string'},
                {'name': 'stateful', 'type': 'boolean'},
                {'name': 'flow_logging_enabled', 'type': 'boolean'},
                {'name': 'stats_logging_enabled', 'type': 'boolean'}]}

EXPECTED_ACL_TEMPLATE = \
    {'name': 'Bidirectional ACL',
     'description': 'Creates a set of ingress and egress ACLs',
     'template-version': 1.0,
     'software-type': 'Nuage Networks VSD',
     'software-version': '5.0.2',
     'variables': [
         {'type': 'reference', 'required_for_delete': True,
          'name': 'enterprise_name'},
         {'type': 'reference', 'required_for_delete': True,
          'name': 'domain_name'},
         {'type': 'string', 'required_for_delete': True, 'name': 'acl_name'},
         {'type': 'boolean', 'name': 'default_allow_ip'},
         {'type': 'boolean', 'name': 'default_allow_non_ip'},
         {'type': 'integer', 'name': 'policy_priority'},
         {'type': 'boolean', 'name': 'allow_address_spoof'},
         {'type': 'boolean', 'name': 'default_install_acl_implicit_rules'},
         {'type': 'string', 'name': 'description'},
         {'type': 'integer', 'name': 'entry_priority'},
         {'type': 'string', 'name': 'protocol'},
         {'type': 'string', 'name': 'source_port'},
         {'type': 'string', 'name': 'destination_port'},
         {'type': 'string', 'name': 'ether_type'},
         {'type': 'choice', 'name': 'action', 'choices': ['forward', 'drop']},
         {'type': 'choice', 'name': 'location_type',
          'choices': ['any', 'policygroup', 'subnet', 'zone']},
         {'type': 'string', 'name': 'location_name'},
         {'type': 'choice', 'name': 'network_type',
          'choices': ['any', 'policygroup', 'subnet', 'zone']},
         {'type': 'string', 'name': 'network_name'},
         {'type': 'boolean', 'name': 'stateful'},
         {'type': 'boolean', 'name': 'flow_logging_enabled'},
         {'type': 'boolean', 'name': 'stats_logging_enabled'}],
     'actions': [
         {'select-object':
             {'type': 'Enterprise',
              'by-field': 'name',
              'value': 'test_enterprise',
              'actions': [
                  {'select-object':
                      {'type': 'Domain',
                       'by-field': 'name',
                       'value': 'test_domain',
                       'actions': [
                           {'select-object':
                               {'type': 'Subnet',
                                'by-field': 'name',
                                'value': 'test_subnet',
                                'actions': [
                                    {'store-value':
                                        {'as-name': 'location_id',
                                         'from-field': 'id'}}]}},
                           {'create-object':
                               {'type': 'IngressACLTemplate',
                                'actions': [
                                    {'set-values':
                                        {'priority': 100,
                                         'allowAddressSpoof': False,
                                         'defaultAllowIP': True,
                                         'defaultAllowNonIP': False,
                                         'name': 'test_acl'}},
                                    {'create-object':
                                        {'type':
                                         'IngressACLEntryTemplate',
                                         'actions': [
                                             {'set-values':
                                                 {'priority': 200,
                                                  'protocol': 'tcp',
                                                  'description': 'Test ACL',
                                                  'etherType': '0x0800',
                                                  'statsLoggingEnabled': True,
                                                  'DSCP': '*',
                                                  'stateful': True,
                                                  'sourcePort': 80,
                                                  'destinationPort': '*',
                                                  'locationType': 'SUBNET',
                                                  'action': 'FORWARD',
                                                  'networkType': 'ANY',
                                                  'flowLoggingEnabled': True}},
                                             {'retrieve-value':
                                                 {'from-name': 'location_id',
                                                  'to-field': 'locationID'}},
                                             {'set-values':
                                                 {'networkID': ''}}]}}]}},
                           {'create-object':
                               {'type': 'EgressACLTemplate',
                                'actions': [
                                    {'set-values':
                                        {'priority': 100,
                                         'defaultInstallACLImplicitRules':
                                             True,
                                         'defaultAllowIP': True,
                                         'defaultAllowNonIP': False,
                                         'name': 'test_acl'}},
                                    {'create-object':
                                        {'type':
                                            'EgressACLEntryTemplate',
                                         'actions': [
                                             {'set-values':
                                                 {'priority': 200,
                                                  'protocol': 'tcp',
                                                  'description': 'Test ACL',
                                                  'etherType': '0x0800',
                                                  'statsLoggingEnabled': True,
                                                  'DSCP': '*',
                                                  'stateful': True,
                                                  'sourcePort': 80,
                                                  'destinationPort': '*',
                                                  'locationType': 'SUBNET',
                                                  'action': 'FORWARD',
                                                  'networkType': 'ANY',
                                                  'flowLoggingEnabled': True}},
                                             {'retrieve-value':
                                                 {'from-name': 'location_id',
                                                  'to-field': 'locationID'}},
                                             {'set-values':
                                                 {'networkID':
                                                     ''}}]}}]}}]}}]}}]}
