#!/usr/bin/python

import argparse
import os
import yaml
import re
from template import TemplateStore
from user_data_parser import UserDataParser


class TypeToObjectName():
    def __init__(self, type_name, type_dict):
        self.type_name = type_name
        self.type_dict = type_dict


class Expression():
    def __init__(self, key_name):
        self.key_name = key_name

    def get_keys(self, expression):
        keys = []
        split_keys = expression.split('"')

        for i in range(1, len(split_keys), 2):
            keys.append((self.key_name, split_keys[i]))

        return keys


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


GATEWAY_NAME_DICT = dict(NSGATEWAY="nsg_name", GATEWAY="gateway_name")

GATEWAY_NAME_TYPE = TypeToObjectName("gateway_type", GATEWAY_NAME_DICT)

INTERFACE_TYPE = TypeToObjectName("interface_type",
                                  {"WIRED": "nsg_access_port_name",
                                   "WIRELESS": "nsg_wifi_port_name"})

ACCESS_PORT_NAME_TYPE = TypeToObjectName("gateway_type",
                                         {"NSGATEWAY": INTERFACE_TYPE,
                                          "GATEWAY": "port_name"})

COMMON_LOCATION_TYPE = {"SUBNET": "subnet_name",
                        "ZONE": "zone_name",
                        "POLICYGROUP": "policy_group_name",
                        "PGEXPRESSION": "policy_group_expression_name",
                        "NETWORK_MACRO": "network_macro_name",
                        "NETWORK_MACRO_GROUP": "network_macro_group_name"}

SERVICE_CHAINING_POLICY_KEY = TypeToObjectName("action", {"REDIRECT": "redirection_target_name",
                                                          "FORWARD": "ingress_forwarding_policy_name"})

NETWORK_TYPE = TypeToObjectName("network_type", COMMON_LOCATION_TYPE)
LOCATION_TYPE = TypeToObjectName("location_type", COMMON_LOCATION_TYPE)
INGRESS_SOURCE_LOCATION_TYPE = TypeToObjectName("source_location_type", COMMON_LOCATION_TYPE)
INGRESS_DEST_LOCATION_TYPE = TypeToObjectName("destination_location_type", COMMON_LOCATION_TYPE)

EGRESS_SOURCE_LOCATION_TYPE = TypeToObjectName("source_location_type",
                                               COMMON_LOCATION_TYPE)
EGRESS_DEST_LOCATION_TYPE = TypeToObjectName("destination_location_type",
                                             COMMON_LOCATION_TYPE)

SERVICE_GROUP_TYPE = TypeToObjectName("l4_service_or_group_type", {"L4_SERVICE": "l4_service_name",
                                                                   "L4_SERVICE_GROUP": "l4_service_group_name"})

RANGE_KEYS = {"vlan_value": ["access_vlan_values", "vlan_values"],
              "access_vlan_value": ["access_vlan_values", "vlan_values"]}

EXECLUDE_DEPENDENCIES = {"application": ["l7_application_signature_name"]}

PRE_DEFINED_OBJECTS = {("enterprise_profile_name", "Default Profile"),
                       ("enterprise_name", "Shared Infrastructure"),
                       ("import_routing_policy_name", "RejectAll"),
                       ('export_routing_policy_name', 'DefaultOnly'),
                       ('saas_application_name', 'WebEx'),
                       ('network_name', 'ANY')}

LIST_DEPENDENCY_KEYS = {"monitor scope": {"destination_nsgs": "nsg_name",
                                          "source_nsgs": "nsg_name",
                                          "all_nsgs_filter_list": "nsg_name"},
                        "application performance management binding": {"domain_names": "domain_name",
                                                                       "l2_domain_names": "l2_domain_name"},
                        "network performance binding": {"domain_names": "domain_name",
                                                        "l2_domain_names": "l2_domain_name"},
                        "nsg access port": {"egress_qos_policy_names": "egress_qos_policy_name"}}

POLICY_GROUP_EXPRESSION = Expression('policy_group_name')
REPLACEMENT_KEYS = \
    {"ingress qos policy": {"wrr_queue_2_rate_limiter_name": "rate_limiter_name",
                            "wrr_queue_3_rate_limiter_name": "rate_limiter_name",
                            "wrr_queue_4_rate_limiter_name": "rate_limiter_name",
                            "priority_queue_1_rate_limiter_name": "rate_limiter_name",
                            "parent_rate_limiter_name": "rate_limiter_name",
                            "priority_queue_1_rate_limiter_name": "rate_limiter_name",
                            "management_queue_rate_limiter_name": "rate_limiter_name",
                            "network_control_queue_rate_limiter_name": "rate_limiter_name"},
     "egress qos policy": {"wrr_queue_2_rate_limiter_name": "rate_limiter_name",
                           "wrr_queue_3_rate_limiter_name": "rate_limiter_name",
                           "wrr_queue_4_rate_limiter_name": "rate_limiter_name",
                           "priority_queue_1_rate_limiter_name": "rate_limiter_name",
                           "parent_rate_limiter_name": "rate_limiter_name",
                           "priority_queue_1_rate_limiter_name": "rate_limiter_name",
                           "management_queue_rate_limiter_name": "rate_limiter_name",
                           "network_control_queue_rate_limiter_name": "rate_limiter_name"},
     "bridge port": {"gateway_name": GATEWAY_NAME_TYPE,
                     "access_port_name": ACCESS_PORT_NAME_TYPE,
                     "vlan": "access_vlan_numbers"},
     "floating ip": {"shared_domain_name": "domain_name",
                     "shared_zone_name": "zone_name",
                     "shared_subnet_name": "subnet_name"},
     "dc gateway": {"gateway_enterprise_name": "enterprise_name"},
     "dc gateway vlan": {"vlan_enterprise_name": "enterprise_name"},
     "dc gateway port": {"port_enterprise_name": "enterprise_name"},
     "bidirectional security policy entry": {"network_name": NETWORK_TYPE,
                                             "location_name": LOCATION_TYPE,
                                             "location_zone_name": "zone_name",
                                             "network_zone_name": "zone_name"},
     "egress security policy entry": {"source_location_zone_name": "zone_name",
                                      "source_location_name": EGRESS_SOURCE_LOCATION_TYPE,
                                      "destination_location_name": EGRESS_DEST_LOCATION_TYPE,
                                      "l4_service_or_group_name": SERVICE_GROUP_TYPE,
                                      "destination_location_zone_name": "zone_name"},
     "ingress forwarding policy entry": {"source_location_zone_name": "zone_name",
                                         "destination_location_zone_name": "zone_name",
                                         "source_location_name": INGRESS_SOURCE_LOCATION_TYPE,
                                         "destination_location_name": INGRESS_DEST_LOCATION_TYPE,
                                         "l4_service_or_group_name": SERVICE_GROUP_TYPE,
                                         "source_network_macro_group_name": "network_macro_group_name"},
     "ingress security policy entry": {"source_location_zone_name": "zone_name",
                                       "destination_location_zone_name": "zone_name",
                                       "source_location_name": INGRESS_SOURCE_LOCATION_TYPE,
                                       "destination_location_name": INGRESS_DEST_LOCATION_TYPE,
                                       "l4_service_or_group_name": SERVICE_GROUP_TYPE},
     "service chaining policy": {"location_name": LOCATION_TYPE,
                                 "network_name": NETWORK_TYPE,
                                 "location_zone_name": "zone_name",
                                 "port_name": [('nsg_name', 'nsg_access_port_name'),
                                               ('gateway_name', 'port_name')]},
     "bgp neighbour": {"import_routing_policy_name": "routing_policy_name"},
     "virtual ip": {"port_name": [('nsg_name', 'nsg_access_port_name'),
                                  ('gateway_name', 'port_name')]},
     "redirection target binding": {"port_name": [('nsg_name', 'nsg_access_port_name'),
                                                  ('gateway_name', 'port_name')]},
     "policy group binding": {"port_name": [('nsg_name', 'nsg_access_port_name'),
                                            ('gateway_name', 'port_name')]},
     "policy group expression": {"expression": POLICY_GROUP_EXPRESSION}}

REPLACEMENT_KEY_TEMPLATES = {"DC Gateway Vlan": "access_vlan_values",
                             "Enterprise Permission": 0,
                             "Static Route": ["ipv4_network", "ipv6_network"],
                             "Virtual IP": ["virtual_ipv4_address",
                                            "virtual_ipv6_address"],
                             "Network Performance Binding": "priority",
                             "Application Performance Management Binding": "priority",
                             "DHCP Option": "type",
                             "DHCPv6 Option": "type",
                             "DHCP Pool": "minAddress",
                             "Floating IP": "last",
                             "Destination Url": "destination_url",
                             "Application Binding": 0,
                             "Service Chaining Policy": SERVICE_CHAINING_POLICY_KEY,
                             "Network Macro Group Binding": 0,
                             "L4 Service Group Binding": 0,
                             "Redirection Target Binding": 0,
                             "NSGateway Activate": 0,
                             "NSG ZFBInfo Download": 0}

EXTRA_KEYS = {'nsg access port': ['vlan_values']}


def main():
    parser = argparse.ArgumentParser(prog="User Data parser")
    parser.add_argument('-dp', '--data_path', dest='data_path',
                        action='store', required=True,
                        default=None,
                        help='Path containing user data.')
    parser.add_argument('-tp', '--template_path', dest='template_path',
                        action='store', required=True,
                        default=None,
                        help='Path containing template information.')
    parser.add_argument('-g', '--group', dest='group', action='store',
                        required=True, default=None,
                        help='Group name')
    parser.add_argument('-d', '--destination_file', dest='output_file',
                        action='store', required=False,
                        default=None,
                        help='Path to the destination file')
    parser.add_argument('-v', '--version', dest='version',
                        action='store', required=False,
                        default=None,
                        help='Version of VSD')
    parser.add_argument('-e', '--example', dest='example',
                        action='store_true', required=False,
                        default=None,
                        help='Dumps minimum templates required for a group')

    args = parser.parse_args()

    parse(args)


def filter_data_file(sorted_file_names, version):
    filtered_file_list = []
    for i in range(0, len(sorted_file_names)):
        if version:
            if re.match('.*v[0-9].*', sorted_file_names[i]):
                if version == sorted_file_names[i].split('_')[-1][1:]:
                    if sorted_file_names[i].startswith(sorted_file_names[i - 1][:-4]):
                        filtered_file_list.pop()

                    filtered_file_list.append(sorted_file_names[i])
            elif sorted_file_names[i + 1].startswith(sorted_file_names[i][:-4]):
                filtered_file_list.append(sorted_file_names[i])
        else:
            if not re.match('.*v[0-9].*', sorted_file_names[i]):
                filtered_file_list.append(sorted_file_names[i])
            else:
                if not sorted_file_names[i].startswith(sorted_file_names[i - 1][:-4]):
                    filtered_file_list.append(sorted_file_names[i])

    return filtered_file_list


def load_data(args, jinja2_template_data):
    group_user_data = {}
    remaining_user_data = {}
    extra_keys_dict = {}
    groups_dict = {}

    if not os.path.exists(args.data_path) and os.path.isdir(args.data_path):
        print "Please provide a valid path for data files"

    # first load files that path the group pattern
    for file_name in filter_data_file(sorted(os.listdir(args.data_path)), args.version):
        udp = UserDataParser()
        udp.read_data(os.path.join(args.data_path, file_name))
        udp.get_template_name_data_pairs()
        for user_data in udp.data:
            template_name = user_data[0].lower()
            template_object_name = get_object_name(user_data[1], jinja2_template_data[template_name])

            if re.match(args.group + ".*", file_name):
                object_name_to_data = group_user_data.get(template_name, {})
                object_name_to_data[template_object_name] = user_data
                group_user_data[template_name] = object_name_to_data
            elif args.group in ["vnsaar", "vnswifi", "network"] and template_name == "nsg network port":
                object_name_to_data = group_user_data.get(template_name, {})
                object_name_to_data[template_object_name] = user_data
                group_user_data[template_name] = object_name_to_data
            elif args.group in ["security", "advrouting"] and template_name in ["bridge port",
                                                                                "application binding",
                                                                                "monitor scope",
                                                                                "application performance management binding",
                                                                                "enterprise permission"]:
                object_name_to_data = group_user_data.get(template_name, {})
                object_name_to_data[template_object_name] = user_data
                group_user_data[template_name] = object_name_to_data
            elif args.group == "vnsnsg" and template_name in ["bridge port",
                                                              "application binding",
                                                              "monitor scope",
                                                              "application performance management binding",
                                                              "enterprise permission"]:
                object_name_to_data = group_user_data.get(template_name, {})
                object_name_to_data[template_object_name] = user_data
                group_user_data[template_name] = object_name_to_data

            else:
                if template_name in remaining_user_data:
                    object_name_to_data = remaining_user_data[template_name]
                else:
                    object_name_to_data = {}
                object_name_to_data[template_object_name] = user_data
                remaining_user_data[template_name] = object_name_to_data

            if template_name in EXTRA_KEYS:
                for k in EXTRA_KEYS[template_name]:
                    template_dict = extra_keys_dict.get(template_name, {})
                    if k in user_data[1]:
                        template_dict[(k, tuple(user_data[1][k]))] = user_data

                    extra_keys_dict[template_name] = template_dict

        groups_dict.update(udp.groups)

    return group_user_data, remaining_user_data, extra_keys_dict, groups_dict


def parse(args):
    template_store = TemplateStore(None)
    template_store.read_templates(args.template_path)

    group_user_data, remaining_user_data, extra_keys_dict, groups_dict = load_data(args, template_store.templates)
    dependencies_not_found = resolve_dependencies(group_user_data,
                                                  remaining_user_data,
                                                  extra_keys_dict,
                                                  template_store.templates)
    while len(dependencies_not_found) > 0:
        dependencies_not_found = resolve_dependencies(group_user_data,
                                                      remaining_user_data,
                                                      extra_keys_dict,
                                                      template_store.templates)

    file_data = []
    for key, value in group_user_data.items():
        for key, user_data in value.items():
            temp_dict = {}
            temp_dict["template"] = user_data[0]
            if not args.example:
                temp_dict["values"] = user_data[1]
            else:
                template = template_store.templates[user_data[0]]
                for variable in template.variables:
                    temp_dict["values"]
            file_data.append(temp_dict)

    for key, value in groups_dict.items():
        group_dict = {}
        group_dict["group"] = key
        group_dict["values"] = value
        file_data.append(group_dict)

    if args.output_file:
        with open(args.output_file, 'w') as f:
            yaml.dump(file_data, f, Dumper=NoAliasDumper)
            f.write('\n')
    else:
        for key, value in group_user_data.items():
            print yaml.dump(value, Dumper=NoAliasDumper)


def calculate_template_dependencies(template_dict, group_user_data):

    template_dependencies = {}

    for key in group_user_data:
        required_references = []
        execlude = []
        if key in EXECLUDE_DEPENDENCIES:
            execlude = EXECLUDE_DEPENDENCIES[key]

        template_variables = template_dict[key][0].variables
        for variable in template_variables:
            variable_type = variable["type"]
            if variable_type == "list":
                variable_type = variable["item-type"]
            if variable_type == "reference" and variable["name"] not in execlude:
                required_references.append(variable["name"])
        template_dependencies[key] = required_references

    return template_dependencies


def find_dependency(tuple_key, user_data):

    if tuple_key in PRE_DEFINED_OBJECTS:
        return True, None, None, tuple_key
    else:
        for template_name, value in user_data.items():
            if tuple_key[0] in RANGE_KEYS:
                for value_keys, data in value:

                    matched = False
                    for range_key in RANGE_KEYS[tuple_key[0]]:
                        if range_key == value_keys:
                            matched = True
                            break

                    if not matched:
                        continue

                    object_name = data
                    if type(object_name) == int:
                        if int(tuple_key[1]) == object_name:
                            return (True,
                                    value[(tuple_key[0], data)],
                                    template_name,
                                    (value_keys, data))
                    else:
                        if type(object_name) == str:
                            object_name = object_name.split(',')
                        for name in object_name:
                            if type(name) == str and '-' in name:
                                range_keys = [int(x) for x in name.split('-')]
                                if range_keys[0] <= tuple_key[1] \
                                        <= range_keys[1]:
                                    return (True,
                                            value[(value_keys, data)],
                                            template_name,
                                            (value_keys, data))
                            elif int(tuple_key[1]) == int(name):
                                return (True,
                                        value[(value_keys, data)],
                                        template_name,
                                        (value_keys, data))

            if tuple_key in value:
                return True, value[tuple_key], template_name, tuple_key

    return False, None, None, None


def resolve_list_dependencies(template_name,
                              dependency,
                              group_user_data,
                              extra_keys_dict,
                              curr_object_data):
    dependencies_not_found = []
    dependency_key = LIST_DEPENDENCY_KEYS[template_name][dependency]

    for value in curr_object_data[dependency]:
        if value == "":
            continue

        tuple_key = (dependency_key, value)
        found, data, temp_template_name, temp_key = find_dependency(tuple_key,
                                                                    group_user_data)

        if not found:
            found, data, temp_template_name, temp_key = find_dependency(tuple_key,
                                                                        extra_keys_dict)

        if not found and tuple_key not in dependencies_not_found:
            dependencies_not_found.append(tuple_key)

    return dependencies_not_found


def get_replacement_keys(template_name, dependency, curr_object_data):
    tuple_keys = []
    if template_name in REPLACEMENT_KEYS and \
            dependency in REPLACEMENT_KEYS[template_name]:
        tuple_key = (REPLACEMENT_KEYS[template_name][dependency], curr_object_data[dependency])

        if isinstance(REPLACEMENT_KEYS[template_name][dependency], TypeToObjectName):
            object_name = REPLACEMENT_KEYS[template_name][dependency]
            key_type = object_name.type_name
            if curr_object_data[key_type].upper() in object_name.type_dict:
                key = object_name.type_dict[curr_object_data[key_type].upper()]
                if isinstance(key, TypeToObjectName):
                    key_type = key.type_name
                    key = key.type_dict[curr_object_data[key_type].upper()]
                    tuple_key = (key, curr_object_data[dependency])
                else:
                    tuple_key = (key, curr_object_data[dependency])
            else:
                tuple_key = (dependency, curr_object_data[key_type].upper())
        elif type(REPLACEMENT_KEYS[template_name][dependency]) == list:
            tmp_list = REPLACEMENT_KEYS[template_name][dependency]
            for tuple in tmp_list:
                if tuple[0] in curr_object_data:
                    tuple_key = (tuple[1], curr_object_data[dependency])
                    break

        elif isinstance(REPLACEMENT_KEYS[template_name][dependency], Expression):
            exp = REPLACEMENT_KEYS[template_name][dependency]
            return exp.get_keys(curr_object_data[dependency])

        tuple_keys.append(tuple_key)

    return tuple_keys


def resolve_single_dependencies(template_name,
                                dependency,
                                group_user_data,
                                extra_keys_dict,
                                curr_object_data):

    tuple_keys = [(dependency, curr_object_data[dependency])]
    dependencies_not_found = []
    replacement_tuple_keys = get_replacement_keys(template_name,
                                                  dependency,
                                                  curr_object_data)
    tuple_keys = replacement_tuple_keys if len(replacement_tuple_keys) > 0 else tuple_keys
    for key in tuple_keys:
        found, data, temp_template_name, temp_key = find_dependency(key,
                                                                    group_user_data)

        if not found:
            found, data, temp_template_name, temp_key = find_dependency(key,
                                                                        extra_keys_dict)
        if not found:
            dependencies_not_found.append(key)

    return dependencies_not_found


def resolve_dependencies(group_user_data,
                         remaining_user_data,
                         extra_keys_dict,
                         template_dict):
    template_dependencies = calculate_template_dependencies(template_dict,
                                                            group_user_data)
    dependencies_not_found = []

    for template_name, value in group_user_data.items():
        for object_key, object_data in value.items():
            for dependency in template_dependencies[template_name]:
                if dependency in object_data[1]:
                    if template_name in LIST_DEPENDENCY_KEYS and\
                            dependency in LIST_DEPENDENCY_KEYS[template_name]:
                        dependencies_not_found.extend(resolve_list_dependencies(template_name,
                                                                                dependency,
                                                                                group_user_data,
                                                                                extra_keys_dict,
                                                                                object_data[1]))
                    else:
                        dependencies_not_found.extend(resolve_single_dependencies(template_name,
                                                                                  dependency,
                                                                                  group_user_data,
                                                                                  extra_keys_dict,
                                                                                  object_data[1]))

    for val in dependencies_not_found:
        found, data, template_name, key = find_dependency(val,
                                                          remaining_user_data)

        if not found:
            found, data, template_name, key = find_dependency(val,
                                                              extra_keys_dict)
        if found:
            template_user_data = group_user_data.get(template_name, {})
            template_user_data[key] = data
            group_user_data[template_name] = template_user_data

    print dependencies_not_found

    return dependencies_not_found


def get_object_name(yaml_data, jinja2_template_data):
    if jinja2_template_data[0].get_name() in REPLACEMENT_KEY_TEMPLATES:
        key = REPLACEMENT_KEY_TEMPLATES[jinja2_template_data[0].get_name()]
        if type(key) == list:
            for k in key:
                if k in yaml_data:
                    key = k
                    break

        elif isinstance(key, TypeToObjectName):
            for variable in jinja2_template_data[0].variables:
                if re.match(".*name", variable["name"]) is not None and \
                   variable["type"] != "reference":
                    return (key.type_dict[yaml_data[key.type_name]], yaml_data[variable["name"]])

        elif type(key) == int:
            key += 1
            REPLACEMENT_KEY_TEMPLATES[jinja2_template_data[0].get_name()] = key
            return (jinja2_template_data[0].get_name(),
                    jinja2_template_data[0].get_name() + str(key))

        if key in yaml_data:
            return (key, yaml_data[key])
        else:
            return (key, key)

    for variable in jinja2_template_data[0].variables:
        if re.match(".*name", variable["name"]) is not None and variable["type"] != "reference":
            return (variable["name"], yaml_data[variable["name"]])


if __name__ == "__main__":
    main()
