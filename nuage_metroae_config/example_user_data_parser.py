#!/Users/chennare/Sources/nuage-metro/venv/bin/python

import argparse
import os
import yaml
import re
from template import TemplateStore
from user_data_parser import UserDataParser


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

    args = parser.parse_args()

    parse(args)


def load_data(args, jinja2_template_data):
    group_user_data = {}
    remaining_user_data = {}

    if not os.path.exists(args.data_path) and os.path.isdir(args.data_path):
        print "Please provide a valid path for data files"

    # first load files that path the group pattern
    for fileName in os.listdir(args.data_path):
        udp = UserDataParser()
        udp.read_data(os.path.join(args.data_path, fileName))
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
            else:
                if templateName in remaining_user_data:
                    object_name_to_data = remaining_user_data[templateName]
                else:
                    object_name_to_data = {}
                object_name_to_data[template_object_name] = user_data
                remaining_user_data[templateName] = object_name_to_data

    return group_user_data, remaining_user_data


def parse(args):
    template_store = TemplateStore(None)
    template_store.read_templates(args.template_path)

    group_user_data, remaining_user_data = load_data(args, template_store.templates)
    dependencies_not_found = resolve_dependencies(group_user_data, remaining_user_data, template_store.templates)

    while len(dependencies_not_found) > 0:
        dependencies_not_found = resolve_dependencies(group_user_data, remaining_user_data, template_store.templates)

    file_data = []
    for key, value in group_user_data.items():
        for key, user_data in value.items():
            temp_dict = {}
            temp_dict["template"] = user_data[0]
            temp_dict["values"] = user_data[1]
            file_data.append(temp_dict)

    if args.output_file:
        with open(args.output_file, 'w') as f:
            yaml.dump(file_data, f)
            f.write('\n')
    else:
        for key, value in group_user_data.items():
            print yaml.dump(value)


def calculate_template_dependencies(template_dict, group_user_data):
    execlude_dependencies = {"application": ["l7_application_signature_name"],
                             "egress qos policy": ["parent_rate_limiter_name",
                                         "priority_queue_1_rate_limiter_name",
                                         "wrr_queue_3_rate_limiter_name",
                                         "wrr_queue_2_rate_limiter_name",
                                         "wrr_queue_4_rate_limiter_name"],
                             "ingress qos policy": ["parent_rate_limiter_name",
                                         "priority_queue_1_rate_limiter_name",
                                         "wrr_queue_3_rate_limiter_name",
                                         "wrr_queue_2_rate_limiter_name",
                                         "wrr_queue_4_rate_limiter_name"]}
    template_dependencies = {}

    for key in group_user_data:
        required_references = []
        execlude = []
        if key in execlude_dependencies:
            execlude = execlude_dependencies[key]

        template_variables = template_dict[key][0].variables
        for variable in template_variables:
            if variable["type"] == "reference" and variable["name"] not in execlude:
                required_references.append(variable["name"])
        template_dependencies[key] = required_references

    return template_dependencies


def resolve_dependencies(group_user_data, remaining_user_data, template_dict):
    template_dependencies = calculate_template_dependencies(template_dict,
                                                        group_user_data)
    dependencies_not_found = []
    pre_defined_vsd_objects = {("enterprise_profile_name", "Default Profile"),
                               ("enterprise_name", "Shared Infrastructure")}
    for templateName, value in group_user_data.items():
        for object_key, object_data in value.items():
            for dependency in template_dependencies[templateName]:
                if dependency in object_data[1]:
                    tuple_key = (dependency, object_data[1][dependency])
                    found = False
                    if tuple_key in pre_defined_vsd_objects:
                        found = True
                    else:
                        for key, value in group_user_data.items():
                            if tuple_key in value:
                                found = True

                    if not found and tuple_key not in dependencies_not_found:
                        dependencies_not_found.append(tuple_key)

    for val in dependencies_not_found:
        for templateName, objects in remaining_user_data.items():
          if val in objects.keys():
              template_user_data = group_user_data.get(templateName, {})
              template_user_data[val] = objects[val]
              group_user_data[templateName] = template_user_data

    print dependencies_not_found

    return dependencies_not_found


def get_object_name(yaml_data, jinja2_template_data):
    special_templates = {"DC Gateway Vlan": "access_vlan_numbers",
                        "Enterprise Permission": "first",
                        "Static Route": ["ipv4_network", "ipv6_network"],
                        "Network Performance Binding": "priority",
                        "Application Performance Management Binding": "priority"}

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
