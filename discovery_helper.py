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


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def setup_template_store(template_path):
    helper_data["store"] = TemplateStore(ENGINE_VERSION)

    for path in template_path:
        helper_data["store"].read_templates(path)


def run_commands(command_file):
    with open(command_file, "r") as f:
        commands = yaml.safe_load(f.read())

    template_name = commands["template"]
    software_version = commands.get("software-version")
    obj_type = commands.get("type")

    template = helper_data["store"].get_template(template_name,
                                                 SOFTWARE_TYPE,
                                                 software_version)

    pinned_values = commands.get("values")

    build_query(template, obj_type, pinned_values)


def build_query(template, obj_type, pinned_values):
    variables = get_probe_variables(template, pinned_values)

    debug(template._replace_vars_with_kwargs(**variables))
    debug("---")
    parsed_template = template._parse_with_vars(**variables)
    actions = get_dict_field_no_case(parsed_template, "actions")
    query_data = {"template": template.get_name(),
                  "pinned_values": pinned_values,
                  "type": obj_type,
                  "var_map": dict(),
                  "store_map": dict()}
    parents = list()
    walk_actions(actions, parents, query_data)

    debug(yaml.dump(query_data, Dumper=NoAliasDumper,
                    default_flow_style=False))
    debug("---")

    write_query(query_data)


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
            parse_store_action(action_dict[action_key], parents, query_data)
        elif action_type == "retrieve-value":
            parse_retrieve_action(action_dict[action_key], parents, query_data)


def parse_create_action(create_dict, parents, query_data):
    object_name = get_dict_field_no_case(create_dict, "type")
    by_field = get_dict_field_no_case(create_dict, "select-by-field")
    if by_field is None:
        by_field = "name"

    parents_copy = list(parents)
    parents_copy.append({"object_name": object_name, "by_field": by_field})

    if object_name.lower() == query_data["type"].lower():
        query_data["parents"] = parents_copy

    actions = get_dict_field_no_case(create_dict, "actions")
    walk_actions(actions, parents_copy, query_data)


def parse_select_action(select_dict, parents, query_data):
    object_name = get_dict_field_no_case(select_dict, "type")
    by_field = get_dict_field_no_case(select_dict, "by-field")
    value = get_dict_field_no_case(select_dict, "value")
    variable_name = find_variable_mapping(value)

    parents_copy = list(parents)
    parents_copy.append({"object_name": object_name,
                         "by_field": by_field,
                         "variable": variable_name})

    actions = get_dict_field_no_case(select_dict, "actions")
    walk_actions(actions, parents_copy, query_data)


def parse_store_action(store_dict, parents, query_data):
    parent_object = parents[-1]["object_name"]

    store_name = get_dict_field_no_case(store_dict, "as-name")

    query_data["store_map"][store_name] = {"type": parent_object,
                                           "store_parents": parents}


def parse_retrieve_action(retrieve_dict, parents, query_data):

    store_name = get_dict_field_no_case(retrieve_dict, "from-name")
    field_name = get_dict_field_no_case(retrieve_dict, "to-field")

    query_data["store_map"][store_name]["retrieve_parents"] = parents
    query_data["store_map"][store_name]["retrieve_field"] = field_name


def parse_set_values(set_values_dict, parents, query_data):
    for field, value in set_values_dict.items():
        map_field_to_variable(parents, field, value, query_data)


def map_field_to_variable(parents, field, value, query_data):
    parent_object = parents[-1]["object_name"]
    variable_name = find_variable_mapping(value)
    if parent_object not in query_data["var_map"]:
        query_data["var_map"][parent_object] = dict()

    query_data["var_map"][parent_object][field] = variable_name

    # object_name = camel_to_snake_case(parent_object)
    # if variable_name is not None:

    #     output("".join([INDENT_STR * 2, "  ",
    #                    variable_name, ': {{ ',
    #                    object_name, '["', field.lower(), '"] }}']))
    # else:
    #     output("".join([INDENT_STR * 2, "  # No variable for ",
    #                    parent_object, ".", field]))


def find_variable_mapping(value):
    value_str = str(value).lower()
    variable_name = None
    if VAR_TOKEN in value_str:
        start_index = value_str.find(VAR_TOKEN) + len(VAR_TOKEN)
        end_index = value_str.find(VAR_END_TOKEN)
        variable_name = value_str[start_index:end_index]

    return variable_name


def write_query(query_data):
    write_query_headers(query_data)
    write_main_object_query(query_data)
    write_store_queries(query_data)
    write_user_data_template(query_data)
    write_query_footers(query_data)


def write_query_headers(query_data):
    output("# Query for discovering %s objects for template %s user-data "
           "from VSD\n",
           query_data["type"],
           query_data["template"])

    output("# Data for discovery_helper")

    helper_args = yaml.dump({"template": query_data["template"],
                             "type": query_data["type"],
                             "values": query_data["pinned_values"]},
                            Dumper=NoAliasDumper,
                            default_flow_style=False)

    output("\n# " + "\n# ".join(helper_args.split("\n")))

    output('echo("off")')
    output('debug = "off"')
    output("echo($debug)\n")


def write_main_object_query(query_data):
    parents = query_data["parents"]
    object_name = parents[-1]["object_name"]
    parent_tokens = list()
    for parent in parents[:-1]:
        parent_tokens.append("%s[%%group=%s]" % (parent["object_name"],
                                                 parent["by_field"]))
    parent_tokens.append(object_name)
    output("%ss = %s.{*}", camel_to_snake_case(object_name),
           ".".join(parent_tokens))


def write_store_queries(query_data):
    object_name = query_data["type"]
    for store_name, store_info in query_data["store_map"].items():
        write_store_query(store_name, store_info, object_name)


def write_store_query(store_name, store_info, object_name):
    parent_object = store_info["retrieve_parents"][-1]["object_name"]
    if parent_object.lower() == object_name.lower():
        store_objects = [x["object_name"] for x in store_info["store_parents"]]
        store_path = ".".join(store_objects)
        output("%ss = %s.id", store_name, store_path)
        output("%ss = %s[id=$%ss].{*}", camel_to_snake_case(store_objects[-1]),
               store_path, store_name)
    else:
        output("# WARNING: Store variable %s does not map to %s object",
               store_name, object_name)


def write_user_data_template(query_data):
    output('\nuser_data = """')
    output(" - template: %s", query_data["template"])
    output("   values:")
    write_user_data_vars(query_data)
    output('"""')


def write_user_data_vars(query_data):
    parents = query_data["parents"]
    object_name = parents[-1]["object_name"]

    last_parent = None
    parents = query_data["parents"]
    for parent in parents:
        if last_parent is None:
            output("{%%- for %s in %ss %%}",
                   camel_to_snake_case(parent["object_name"]),
                   camel_to_snake_case(object_name))
        else:
            output("{%%- for %s in %s[1] %%}",
                   camel_to_snake_case(parent["object_name"]),
                   camel_to_snake_case(last_parent["object_name"]))

        last_parent = parent

    output("%s-", INDENT_STR * 2)

    written_vars = list()

    write_parent_fields(query_data, written_vars)
    write_var_fields(query_data, written_vars)

    for parent in parents[:-1]:
        output("{%% endfor -%%}")

    output("{%% endfor %%}")


def write_parent_fields(query_data, written_vars):

    parents = query_data["parents"]
    for parent in parents:
        if "variable" in parent:
            variable = parent["variable"]
            if variable is not None:
                written_vars.append(variable)
                output("%s  %s: {{ %s[0] }}", INDENT_STR * 2, variable,
                       camel_to_snake_case(parent["object_name"]))
            else:
                output("%s# WARNING: No variable mapping for %s parent",
                       INDENT_STR * 2, parent["object_name"])


def write_var_fields(query_data, written_vars):
    parents = query_data["parents"]
    object_name = parents[-1]["object_name"]
    var_map = query_data["var_map"]

    if object_name in var_map:
        write_var_field_set(object_name, var_map[object_name], written_vars)
    else:
        output("%s# WARNING: main object %s has no values set",
               INDENT_STR * 2, object_name)

    store_map = query_data["store_map"]
    for parent_object_name, object_var_map in var_map.items():
        if parent_object_name != object_name:
            store_map_entry = find_store_map_entry_by_type(store_map,
                                                           parent_object_name)
            if store_map_entry is not None:

                snake_case = camel_to_snake_case(parent_object_name)
                output("{%%- for %s in %ss -%%}", snake_case, snake_case)
                output('{%%- if %s["%s"] == %s["id"] %%}',
                       camel_to_snake_case(object_name),
                       store_map_entry["retrieve_field"].lower(),
                       snake_case)

                write_var_field_set(parent_object_name, object_var_map,
                                    written_vars)

                output('{%%- endif -%%}')
                output('{%%- endfor -%%}')
            else:
                output("%s# WARNING: cannot find store/retrieve for %s object",
                       INDENT_STR * 2, parent_object_name)


def write_var_field_set(parent_object_name, object_var_map, written_vars):
    object_name = camel_to_snake_case(parent_object_name)

    for field, variable_name in object_var_map.items():
        if variable_name not in written_vars:
            if variable_name is not None:
                written_vars.append(variable_name)
                output('{%%- if %s["%s"] != None %%}',
                       object_name, field.lower())
                output("".join([INDENT_STR * 2, "  ",
                               variable_name, ': {{ ',
                               object_name, '["', field.lower(), '"] }}']))
                output('{%%- endif %%}')
            else:
                output("".join([INDENT_STR * 2,
                                "  # WARNING: No variable for ",
                                parent_object_name, ".", field]))


def find_store_map_entry_by_type(store_map, object_type):
    for store_var, store_map_entry in store_map.items():
        if store_map_entry["type"].lower() == object_type.lower():
            return store_map_entry

    return None


def write_query_footers(query_data):
    output('\necho("on")')
    output("render_template($user_data)")


def camel_to_snake_case(camel):
    snake = re.sub(r"([A-Z])([A-Z])([a-z])", r"\1_\2\3", camel)
    snake = re.sub(r"([a-z])([A-Z])", r"\1_\2", snake)
    return snake.lower()


def debug(output_str, *args):
    if helper_data["debug"]:
        print(output_str % args)


def output(output_str, *args):
    print(output_str % args)


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('command_file', action='store',
                        help="File containing discovery query creation commands.")

    parser.add_argument('-tp', '--template_path', dest='template_path',
                        action='append', required=False,
                        default=[os.getenv(ENV_TEMPLATE, None)],
                        help='Path containing template files. Can also set using environment variable %s' % (ENV_TEMPLATE))

    parser.add_argument('-d', '--debug', action='store_true', dest='debug',
                        default=False, help="Enable debug output")

    return parser.parse_args()


def main():

    args = parse_args()

    helper_data["debug"] = args.debug

    setup_template_store(args.template_path)

    run_commands(args.command_file)


if __name__ == "__main__":
    main()
