EXPECTED_DOMAINS_DATA = [
    ('Enterprise', {'enterprise_name': 'test_enterprise'}),
    ('Domain', {'enterprise_name': 'test_enterprise',
                'domain_name': 'public'}),
    ('Domain', {'enterprise_name': 'test_enterprise',
                'domain_name': 'private'})]

EXPECTED_ACLS_DATA = [
    ('Enterprise', {'enterprise_name': 'test_enterprise'}),
    ('Domain', {'enterprise_name': 'test_enterprise',
                'domain_name': 'public'}),
    ('Bidirectional ACL', {'enterprise_name': 'test_enterprise',
                           'domain_name': 'public',
                           'acl_name': 'test_acl',
                           'default_allow_ip': True,
                           'default_allow_non_ip': False,
                           'policy_priority': 100,
                           'allow_address_spoof': False,
                           'default_install_acl_implicit_rules': True,
                           'description': 'Test ACL',
                           'entry_priority': 200,
                           'protocol': 6,
                           'source_port': 80,
                           'destination_port': '*',
                           'ether_type': '0x0800',
                           'action': 'forward',
                           'location_type': 'any',
                           'location_name': '',
                           'network_type': 'any',
                           'network_name': '',
                           'stateful': True,
                           'flow_logging_enabled': True,
                           'stats_logging_enabled': True})]

EXPECTED_ACLS_GROUPS_DATA = [
    ('Bidirectional ACL', {'policy_priority': 100,
                           'description': 'Test ACL 1',
                           'acl_name': 'test_acl_1',
                           '$group_1': 'http',
                           'protocol': 6,
                           'source_port': 80,
                           'ether_type': '0x0800',
                           'action': 'forward',
                           'entry_priority': 200,
                           'destination_port': '*',
                           'enterprise_name': 'test_enterprise',
                           'domain_name': 'private'}),
    ('Bidirectional ACL', {'policy_priority': 300,
                           'description': 'Test ACL 2',
                           'acl_name': 'test_acl_2',
                           'entry_priority': 400,
                           'domain_name': 'private',
                           'action': 'deny',
                           'protocol': 6,
                           'source_port': 23,
                           'ether_type': '0x0800',
                           '$group_1': 'ssh',
                           'destination_port': '*',
                           'enterprise_name': 'test_enterprise'}),
    ('Bidirectional ACL', {'policy_priority': 500,
                           'description': 'Test ACL 3',
                           'acl_name': 'test_acl_3',
                           'entry_priority': 600,
                           'domain_name': 'private',
                           'action': 'deny',
                           'protocol': 6,
                           'source_port': 80,
                           'ether_type': '0x0800',
                           '$group_1': 'http',
                           'destination_port': '*',
                           'enterprise_name': 'test_enterprise'})]