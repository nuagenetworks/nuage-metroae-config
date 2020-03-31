#!/usr/bin/env python

import argparse
import json
import os
import re
import yaml

DESCRIPTION = """This tool helps build starter templates."""
ENV_VSD_SPECIFICATIONS = 'VSD_SPECIFICATIONS_PATH'
DEFAULT_VSD_SPECS = 'vsd-api-specifications'

INDENT = 2
INDENT_STR = " " * INDENT
TREE_ROOT = "me"

specs = dict()
parents = dict()

template_info = {
    "name": "CHANGE ME",
    "description": "CHANGE ME",
    "usage": "CHANGE ME",
    "version": "CHANGE ME",
    "template": "1.0",
    "engine": "1.0",
    "software": "Nuage Networks VSD",
    "indent_level": 0}

template_variables = list()
template_actions = list()


def read_specs(path):
    for filename in os.listdir(path):
        if filename.endswith(".spec"):
            spec_file = open("/".join((path, filename)), 'r')
            spec = json.loads(spec_file.read())
            rest_name = spec['model']['rest_name']
            if rest_name is not None:
                store_parents(spec)
                specs[rest_name] = spec

    return specs


def store_parents(spec):
    rest_name = spec['model']['rest_name']
    for child in spec["children"]:
        child_rest_name = child['rest_name']
        if child_rest_name not in parents:
            parents[child_rest_name] = list()
        parents[child_rest_name].append(rest_name)


def find_spec(entity_name):
    for rest_name, spec in specs.items():
        if ("entity_name" in spec["model"] and
                spec["model"]["entity_name"] == entity_name):
            return spec

    return None


def find_path(rest_name):
    if rest_name == TREE_ROOT:
        return list()
    else:
        if rest_name in parents and len(parents[rest_name]) > 0:
            parent = parents[rest_name][0]
        else:
            raise Exception("Could not find parents for " + rest_name)

    path = find_path(parent)
    if rest_name in path:
        raise Exception("Loop in parentage of " + rest_name)

    path.append(rest_name)

    return path


def run_commands(command_file):
    with open(command_file, "r") as f:
        commands = yaml.safe_load(f.read())

    for command_pair in commands:
        for command, value in command_pair.items():
            if command == "name":
                template_info["name"] = value
            elif command == "description":
                template_info["description"] = value
            elif command == "version":
                template_info["version"] = value
            elif command == "create":
                create_object(value, is_root=False)
            elif command == "create-root":
                create_object(value, is_root=True)
            elif command == "select":
                select_object(value, is_root=False)
            elif command == "select-root":
                select_object(value, is_root=True)
            elif command == "store":
                store(value)
            elif command == "retrieve":
                arg_pair = value.split()
                retrieve(arg_pair[0], arg_pair[1])
            else:
                raise Exception("Unknown command: " + command)


def create_object(value, is_root=True):

    spec = find_spec(value)
    if spec is None:
        raise Exception("Unknown object for create: " + value)

    if is_root:
        template_info["indent_level"] = 0

    lines = list()
    indent = INDENT_STR * (template_info["indent_level"] + 1)

    lines.append(indent + "- create-object:")
    indent += INDENT_STR
    indent += INDENT_STR
    lines.append(indent + "type: " + spec["model"]["entity_name"])
    lines.append(indent + "actions:")

    template_info["indent_level"] += 3
    set_values(lines, spec)

    template_actions.append(lines)


def set_values(lines, spec):

    indent = INDENT_STR * (template_info["indent_level"] + 1)

    lines.append(indent + "- set-values:")

    indent += INDENT_STR
    indent += INDENT_STR

    for attribute in spec["attributes"]:
        name = attribute["name"]
        snake = camel_to_snake_case(name)
        if attribute["required"] is False:
            lines.append("%s{%% if %s is defined %%}" % (indent, snake))

        lines.append("%s%s: {{ %s }}" % (indent, name, snake))

        if attribute["required"] is False:
            lines.append("%s{%% endif %%}" % indent)

        add_variable(attribute)


def store(object_name):
    lines = list()

    indent = INDENT_STR * (template_info["indent_level"] + 1)

    lines.append(indent + "- store-value:")

    indent += INDENT_STR
    indent += INDENT_STR

    snake = camel_to_snake_case(object_name)
    lines.append("%sas-name: %s_id" % (indent, snake))
    lines.append(indent + "from-field: id")

    template_actions.append(lines)


def retrieve(object_name, attribute):
    lines = list()

    indent = INDENT_STR * (template_info["indent_level"] + 1)

    lines.append(indent + "- retrieve-value:")

    indent += INDENT_STR
    indent += INDENT_STR

    snake = camel_to_snake_case(object_name)
    lines.append("%sfrom-name: %s_id" % (indent, snake))
    lines.append(indent + "to-field: " + attribute)

    template_actions.append(lines)


def add_variable(attribute):

    lines = list()

    name = attribute["name"]
    snake = camel_to_snake_case(name)

    lines.append(INDENT_STR + "- name: " + snake)
    lines.append(INDENT_STR + "  description: CHANGE ME")

    attr_type = attribute["type"]
    if attr_type == "enum":
        choices = attribute["allowed_choices"]
        lines.append(INDENT_STR + "  type: choice")
        lines.append(INDENT_STR + "  choices: [" + ", ".join(choices) + "]")
    elif attr_type == "list":
        item_type = attribute["subtype"]
        lines.append(INDENT_STR + "  type: list")
        lines.append(INDENT_STR + "  item-type: " + item_type)
    else:
        lines.append(INDENT_STR + "  type: " + attr_type)

    if attribute["required"] is False:
        lines.append(INDENT_STR + "  optional: true")

    default = attribute["default_value"]
    if default is not None:
        lines.append(INDENT_STR + "  default: " + str(default))

    template_variables.append(lines)


def select_object(value, is_root=True):

    spec = find_spec(value)
    if spec is None:
        raise Exception("Unknown object for select: " + value)

    if is_root:
        template_info["indent_level"] = 0

    lines = list()
    indent = INDENT_STR * (template_info["indent_level"] + 1)

    lines.append(indent + "- select-object:")
    indent += INDENT_STR
    indent += INDENT_STR
    lines.append(indent + "type: " + spec["model"]["entity_name"])
    lines.append(indent + "by-field: name")

    snake = camel_to_snake_case(value)
    lines.append(indent + "value: {{ %s_name }}" % snake)
    lines.append(indent + "actions:")

    add_variable({"name": snake + "_name",
                  "type": "reference",
                  "required": True,
                  "default_value": None})

    template_info["indent_level"] += 3

    template_actions.append(lines)


def camel_to_snake_case(camel):
    snake = re.sub(r"([A-Z])([A-Z])([a-z])", r"\1_\2\3", camel)
    snake = re.sub(r"([a-z])([A-Z])", r"\1_\2", snake)
    return snake.lower()


def generate_template():
    lines = list()

    generate_headers(lines)
    generate_variables(lines)
    generate_examples(lines)
    generate_actions(lines)

    return "\n".join(lines)


def generate_headers(lines):
    lines.append("name: " + template_info["name"])
    lines.append("description: " + template_info["description"])
    lines.append("usage: " + template_info["usage"])
    lines.append("restrictions:")
    lines.append("- operation: create")
    lines.append("  restriction-list:")
    lines.append("  - CHANGE ME")
    doc_file_name = ("template-" +
                     "-".join(template_info["name"].lower().split(" ")) +
                     ".md")
    lines.append("doc-file: " + doc_file_name)
    lines.append("template-version: " + template_info["template"])
    lines.append("engine-version: " + template_info["engine"])
    lines.append("software-type: " + template_info["software"])
    lines.append("software-version: " + template_info["version"])


def generate_variables(lines):
    lines.append("variables:")

    for variable in template_variables:
        lines.extend(variable)


def generate_examples(lines):
    lines.append("examples:")
    lines.append("- name: CHANGE ME")
    lines.append("  description: CHANGE ME")
    lines.append("  user-data: |")
    lines.append("    - template: " + template_info["name"])
    lines.append("      values:")
    lines.append("        CHANGE_ME: CHANGE ME")
    lines.append("  sample-run: |")
    lines.append("      SAMPLE RUN OUTPUT")


def generate_actions(lines):
    lines.append("actions:")

    for variable in template_actions:
        lines.extend(variable)


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('command_file', action='store',
                        help="File containing template creation commands.")

    parser.add_argument('-sp', '--spec-path', dest='spec_path',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_SPECIFICATIONS,
                                          DEFAULT_VSD_SPECS),
                        help=('Path containing object specifications. Can also'
                              ' set using environment variable %s') % (
                                  ENV_VSD_SPECIFICATIONS))

    return parser.parse_args()


def main():

    args = parse_args()

    read_specs(args.spec_path)

    run_commands(args.command_file)

    print generate_template()


if __name__ == "__main__":
    main()
