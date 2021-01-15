#!/usr/bin/env python

import argparse
import os
import re
import yaml

from nuage_metroae_config.template import TemplateStore
from nuage_metroae_config.util import get_dict_field_no_case

ENGINE_VERSION = "1.0.1"
SOFTWARE_TYPE = "Nuage Networks VSD"

DESCRIPTION = """This tool helps build starter discovery queries."""
ENV_TEMPLATE = 'TEMPLATE_PATH'

VAR_TOKEN = "var__"
VAR_END_TOKEN = "__var"
INDENT = 2
INDENT_STR = " " * INDENT

helper_data = dict()


def setup_template_store(template_path):
    helper_data["store"] = TemplateStore(ENGINE_VERSION)

    for path in template_path:
        helper_data["store"].read_templates(path)


def run_commands(command_file):
    with open(command_file, "r") as f:
        commands = yaml.safe_load(f.read())

    template_name = commands["template"]
    software_version = commands.get("software-version")

    template = helper_data["store"].get_template(template_name,
                                                 SOFTWARE_TYPE,
                                                 software_version)

    pinned_values = commands.get("values")

    build_query(template, pinned_values)


def build_query(template, pinned_values):
    variables = get_probe_variables(template, pinned_values)

    print(template._replace_vars_with_kwargs(**variables))
    parsed_template = template._parse_with_vars(**variables)
    actions = get_dict_field_no_case(parsed_template, "actions")
    query_data = dict()
    parents = list()
    walk_actions(actions, parents, query_data)


def get_probe_variables(template, pinned_values):
    variables = dict()
    if pinned_values is not None:
        for name, value in pinned_values.items():
            if value is not None:
                variables[name] = value
    else:
        pinned_values = dict()

    schema = template._convert_variables_to_schema()
    property_dict = schema["items"]["properties"]

    for name, props in property_dict.items():
        if name not in pinned_values:
            variables[name] = VAR_TOKEN + name + VAR_END_TOKEN

    return variables


def walk_actions(actions, parents, query_data):
    for action_dict in actions:
        if type(action_dict) != dict:
            raise Exception("Invalid action: " + str(action_dict))

        action_keys = list(action_dict.keys())
        if (len(action_keys) != 1):
            raise Exception("Invalid action: " + str(action_keys))

        action_key = action_keys[0]
        action_type = str(action_key).lower()
        if action_type == "create-object":
            parse_create_action(action_dict[action_key], parents, query_data)
        elif action_type == "select-object":
            parse_select_action(action_dict[action_key], parents, query_data)
        elif action_type == "set-values":
            parse_set_values(action_dict[action_key], parents, query_data)
        elif action_type == "store-value":
            pass
        elif action_type == "retrieve-value":
            pass


def parse_create_action(create_dict, parents, query_data):
    object_name = get_dict_field_no_case(create_dict, "type")
    parents_copy = list(parents)
    parents_copy.append(object_name)
    actions = get_dict_field_no_case(create_dict, "actions")
    walk_actions(actions, parents_copy, query_data)


def parse_select_action(select_dict, parents, query_data):
    object_name = get_dict_field_no_case(select_dict, "type")
    parents_copy = list(parents)
    parents_copy.append(object_name)
    actions = get_dict_field_no_case(select_dict, "actions")
    walk_actions(actions, parents_copy, query_data)


def parse_set_values(set_values_dict, parents, query_data):
    for field, value in set_values_dict.items():
        map_field_to_variable(parents, field, value, query_data)


def map_field_to_variable(parents, field, value, query_data):
    parent_object = parents[-1]
    variable_name = find_variable_mapping(value)
    if variable_name is not None:
        object_name = camel_to_snake_case(parent_object)

        print("".join([INDENT_STR * 2, "  ",
                       variable_name, ': {{ ',
                       object_name, '["', field.lower(), '"] }}']))
    else:
        print("".join([INDENT_STR * 2, "  # No variable for ",
                       parent_object, ".", field]))


def find_variable_mapping(value):
    value_str = str(value).lower()
    variable_name = None
    if VAR_TOKEN in value_str:
        start_index = value_str.find(VAR_TOKEN) + len(VAR_TOKEN)
        end_index = value_str.find(VAR_END_TOKEN)
        variable_name = value_str[start_index:end_index]

    return variable_name


def camel_to_snake_case(camel):
    snake = re.sub(r"([A-Z])([A-Z])([a-z])", r"\1_\2\3", camel)
    snake = re.sub(r"([a-z])([A-Z])", r"\1_\2", snake)
    return snake.lower()


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('command_file', action='store',
                        help="File containing discovery query creation commands.")

    parser.add_argument('-tp', '--template_path', dest='template_path',
                        action='append', required=False,
                        default=[os.getenv(ENV_TEMPLATE, None)],
                        help='Path containing template files. Can also set using environment variable %s' % (ENV_TEMPLATE))

    return parser.parse_args()


def main():

    args = parse_args()

    setup_template_store(args.template_path)

    run_commands(args.command_file)


if __name__ == "__main__":
    main()
