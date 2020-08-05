#!/usr/bin/python

import argparse
import os
import yaml
import re
from template import TemplateStore
from user_data_parser import UserDataParser


class ObjectTypeToName():
    def __init__(self, type_name, type_dict):
        self.type_name = type_name
        self.type_dict = type_dict

GATEWAY_NAME_DICT = dict(NSGATEWAY="nsg_name", GATEWAY="gateway_name")

GATEWAY_NAME_TYPE = ObjectTypeToName("gateway_type", GATEWAY_NAME_DICT)

INTERFACE_TYPE = ObjectTypeToName("interface_type",
                                  {"WIRED":"nsg_access_port_name",
                                   "WIRELESS": "nsg_wifi_port_name"})

ACCESS_PORT_NAME_TYPE = ObjectTypeToName("gateway_type",\
                            {"NSGATEWAY":INTERFACE_TYPE,
                             "GATEWAY":"port_name"})

RANGE_KEYS = ["access_vlan_numbers"]

EXECLUDE_DEPENDENCIES = {"application": ["l7_application_signature_name"]}

PRE_DEFINED_OBJECTS = {("enterprise_profile_name", "Default Profile"),
                               ("enterprise_name", "Shared Infrastructure")}

LIST_DEPENDENCY_KEYS = {"monitor scope": {"destination_nsgs": "nsg_name",
                                            "source_nsgs": "nsg_name",
                                            "all_nsgs_filter_list": "nsg_name"},
                        "application performance management binding": {"domain_names": "domain_name",
                                                                       "l2_domain_names": "l2_domain_name"},
                        "network performance binding": {"domain_names": "domain_name",
                                                        "l2_domain_names": "l2_domain_name"}}
REPLACEMENT_KEYS = \
    {"ingress qos policy":
        {"wrr_queue_2_rate_limiter_name": "rate_limiter_name",
        "wrr_queue_3_rate_limiter_name": "rate_limiter_name",
        "wrr_queue_4_rate_limiter_name": "rate_limiter_name",
        "priority_queue_1_rate_limiter_name": "rate_limiter_name",
        "parent_rate_limiter_name": "rate_limiter_name",
        "priority_queue_1_rate_limiter_name" : "rate_limiter_name",
        "management_queue_rate_limiter_name" : "rate_limiter_name",
        "network_control_queue_rate_limiter_name": "rate_limiter_name"},
    "egress qos policy":
        {"wrr_queue_2_rate_limiter_name": "rate_limiter_name",
        "wrr_queue_3_rate_limiter_name": "rate_limiter_name",
        "wrr_queue_4_rate_limiter_name": "rate_limiter_name",
        "priority_queue_1_rate_limiter_name": "rate_limiter_name",
        "parent_rate_limiter_name": "rate_limiter_name",
        "priority_queue_1_rate_limiter_name" : "rate_limiter_name",
        "management_queue_rate_limiter_name" : "rate_limiter_name",
        "network_control_queue_rate_limiter_name": "rate_limiter_name"},
    "bridge port":{"gateway_name":GATEWAY_NAME_TYPE,
        "access_port_name":ACCESS_PORT_NAME_TYPE,
        "vlan": "access_vlan_numbers"},
    "floating ip":{"shared_domain_name":"domain_name",
                   "shared_zone_name":"zone_name",
                   "shared_subnet_name":"subnet_name"},
    "dc gateway":{"gateway_enterprise_name": "enterprise_name"},
    "dc gateway vlan":{"vlan_enterprise_name": "enterprise_name"},
    "dc gateway port":{"port_enterprise_name": "enterprise_name"},
    }


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
    parser.add_argument('-g', '--group', dest='group', action='store'
                        ,required=True, default=None,
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


def filter_data_file(sortedFileNames, version):
    filtered_file_list = []
    for i in range(0, len(sortedFileNames)):
        if version:
            if re.match('.*v[0-9].*', sortedFileNames[i]):
                if version == sortedFileNames[i].split('_')[-1][1:]:
                    if sortedFileNames[i].startswith(sortedFileNames[i - 1][:-4]):
                        filtered_file_list.pop()

                    filtered_file_list.append(sortedFileName[i])
            elif sortedFileNames[i + 1].startswith(sortedFileNames[i][:-4]):
                filtered_file_list.append(sortedFileNames[i])
        else:
            if not re.match('.*v[0-9].*', sortedFileNames[i]):
                filtered_file_list.append(sortedFileNames[i])
            else:
                if not sortedFileNames[i].startswith(sortedFileNames[i - 1][:-4]):
                  filtered_file_list.append(sortedFileNames[i])

    return filtered_file_list


def load_data(args, jinja2_template_data):
    group_user_data = {}
    remaining_user_data = {}
    groups_dict = {}

    if not os.path.exists(args.data_path) and os.path.isdir(args.data_path):
        print "Please provide a valid path for data files"

    # first load files that path the group pattern
    previousFileName = ""
    for fileName in filter_data_file(sorted(os.listdir(args.data_path)),
                                     args.version):
        udp = UserDataParser()
        udp.read_data(os.path.join(args.data_path, fileName))
        udp.get_template_name_data_pairs()
        for user_data in udp.data:
            templateName = user_data[0].lower()
            template_object_name = get_object_name(user_data[1], jinja2_template_data[templateName])

            if re.match(args.group +".*", fileName):
                if templateName in group_user_data:
                    object_name_to_data = group_user_data[templateName]
                else:
                    object_name_to_data = {}
                object_name_to_data[template_object_name] = user_data
                group_user_data[templateName] = object_name_to_data
            elif (args.group == "vnsaar" or
                  args.group == "vnswifi" or
                  args.group == "network") and\
                  templateName == "nsg network port":
                  if templateName in group_user_data:
                      object_name_to_data = group_user_data[templateName]
                  else:
                      object_name_to_data = {}
                  object_name_to_data[template_object_name] = user_data
                  group_user_data[templateName] = object_name_to_data
            else:
                if templateName in remaining_user_data:
                    object_name_to_data = remaining_user_data[templateName]
                else:
                    object_name_to_data = {}
                object_name_to_data[template_object_name] = user_data
                remaining_user_data[templateName] = object_name_to_data

        groups_dict.update(udp.groups)

    return group_user_data, remaining_user_data, groups_dict


def parse(args):
    template_store = TemplateStore(None)
    template_store.read_templates(args.template_path)

    group_user_data, remaining_user_data, groups_dict = load_data(args, template_store.templates)
    dependencies_not_found = resolve_dependencies(group_user_data, remaining_user_data, template_store.templates)

    while len(dependencies_not_found) > 0:
        dependencies_not_found = resolve_dependencies(group_user_data, remaining_user_data, template_store.templates)

    file_data = []
    for key, value in group_user_data.items():
        for key, user_data in value.items():
            temp_dict = {}
            temp_dict["template"] = user_data[0]
            if not args.example:
                temp_dict["values"] = user_data[1]
            else:
                template = template_store.templates[user_data[0]]
                variables_list = []
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
            yaml.dump(file_data, f)
            f.write('\n')
    else:
        for key, value in group_user_data.items():
            print yaml.dump(value)


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
        return True, None, None
    else:
        for key, value in user_data.items():
            if tuple_key[0] in RANGE_KEYS:

                for value_keys, data in value:

                    if tuple_key[0] != value_keys:
                        continue
                    object_name = data
                    if type(object_name) == int:
                        if int(tuple_key[1]) == object_name:
                            return True, value[(tuple_key[0], data)], key
                    else:
                        for name in object_name.split(','):
                            #print name, tuple_key[1]
                            if '-' in name:
                                range_keys = [int(x) for x in name.split('-')]
                                if range_keys[0] < tuple_key[1] < range_keys[1]:
                                    #print "found", tuple_key, value[tuple_key]
                                    return True, value[(tuple_key[0], data)], key
                            elif int(tuple_key[1]) == int(name):

                                #print "found", tuple_key, data, value
                                return True, value[(tuple_key[0], data)], key

            elif tuple_key in value:
                return True, value[tuple_key], key

    return False, None, None


def resolve_list_dependencies(templateName,
                              dependency,
                              group_user_data,
                              curr_object_data):
    dependencies_not_found = []
    dependency_key = LIST_DEPENDENCY_KEYS[templateName][dependency]

    for value in curr_object_data[dependency]:
        tuple_key = (dependency_key, value)
        found, data, tempTemplateName = find_dependency(tuple_key, group_user_data)

        if not found and\
            tuple_key not in dependencies_not_found:
            dependencies_not_found.append(tuple_key)

    return dependencies_not_found


def get_replacement_keys(templateName, dependency, curr_object_data):
    if templateName in REPLACEMENT_KEYS and \
        dependency in REPLACEMENT_KEYS[templateName]:
        tuple_key = (REPLACEMENT_KEYS[templateName][dependency],
                    curr_object_data[dependency])

        if isinstance(REPLACEMENT_KEYS[templateName][dependency],
                      ObjectTypeToName):
            objectTypeToName = REPLACEMENT_KEYS[templateName][dependency]
            key_type = objectTypeToName.type_name
            key = objectTypeToName.type_dict[curr_object_data[key_type].upper()]
            if isinstance(key, ObjectTypeToName):
                key_type = key.type_name
                key = key.type_dict[curr_object_data[key_type].upper()]
                tuple_key =(key, curr_object_data[dependency])
            else:
                tuple_key = (key, curr_object_data[dependency])

        return tuple_key

    return None


def resolve_single_dependencies(templateName,
                                dependency,
                                group_user_data,
                                curr_object_data):
    dependencies_not_found = []
    tuple_key = (dependency, curr_object_data[dependency])
    replacement_tuple_key = get_replacement_keys(templateName,
                                                 dependency,
                                                 curr_object_data)
    tuple_key = replacement_tuple_key if replacement_tuple_key is not None else tuple_key
    found, data, tempTemplateName = find_dependency(tuple_key, group_user_data)

    if not found and\
        tuple_key not in dependencies_not_found:
        dependencies_not_found.append(tuple_key)

    return dependencies_not_found


def resolve_dependencies(group_user_data, remaining_user_data, template_dict):
    template_dependencies = calculate_template_dependencies(template_dict,
                                                            group_user_data)
    dependencies_not_found = []

    for templateName, value in group_user_data.items():
        for object_key, object_data in value.items():
            for dependency in template_dependencies[templateName]:
                if dependency in object_data[1]:
                    if templateName in LIST_DEPENDENCY_KEYS and\
                      dependency in LIST_DEPENDENCY_KEYS[templateName]:
                        dependencies_not_found.extend(
                            resolve_list_dependencies(templateName,
                                                      dependency,
                                                      group_user_data,
                                                      object_data[1]))
                    else:
                        dependencies_not_found.extend(
                            resolve_single_dependencies(templateName,
                                                        dependency,
                                                        group_user_data,
                                                        object_data[1]))

    for val in dependencies_not_found:
        found, data, templateName = find_dependency(val, remaining_user_data)
        if found:
            template_user_data = group_user_data.get(templateName, {})
            template_user_data[val] = data
            group_user_data[templateName] = template_user_data

    print dependencies_not_found

    return dependencies_not_found


def get_object_name(yaml_data, jinja2_template_data):
    special_templates = {"DC Gateway Vlan": "access_vlan_numbers",
                        "Enterprise Permission": "first",
                        "Static Route": ["ipv4_network", "ipv6_network"],
                        "Network Performance Binding": "priority",
                        "Application Performance Management Binding": "priority",
                        "DHCP Option": "type",
                        "DHCPv6 Option": "type",
                        "DHCP Pool": "minAddress",
                        "Floating IP": "last",
                        "Destination Url": "destination_url",
                        "Application Binding": "first"}

    if jinja2_template_data[0].get_name() in special_templates:
        key = special_templates[jinja2_template_data[0].get_name()]
        if type(key) == list:
            for k in key:
                if k in yaml_data:
                    key = k
                    break

        if key in yaml_data:
            return (key, yaml_data[key])
        else:
            return (key, key)

    for variable in jinja2_template_data[0].variables:
        if re.match(".*name", variable["name"]) is not None and variable["type"] != "reference":
            return (variable["name"], yaml_data[variable["name"]])

if __name__ == "__main__":
    main()
