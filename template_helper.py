#!/usr/bin/env python

import argparse
import os
import re
import yaml

DESCRIPTION = """This tool helps build starter templates."""
ENV_VSD_SPECIFICATIONS = 'VSD_SPECIFICATIONS_PATH'
DEFAULT_VSD_SPECS = 'vsd-api-specifications'

JINJA_START = "$S"
JINJA_END = "$E"

template_headers = {
    "name": "CHANGE ME",
    "description": "CHANGE ME",
    "version": "CHANGE ME",
    "template": "1.0",
    "levistate": "1.0",
    "software": "Nuage Networks VSD"}

template_variables = list()
template_actions = list()


def read_specs(path):
    specs = {}
    for filename in os.listdir(path):
        if filename.endswith("enterprise.spec"):
            spec_file = open("/".join((path, filename)), 'r')
            spec = yaml.safe_load(spec_file.read())
            rest_name = spec['model']['rest_name']
            if rest_name is not None:
                specs[rest_name] = spec
                if 'root' in spec['model'] and spec['model']['root']:
                    specs['@root'] = rest_name

    return specs


def find_spec(specs, entity_name):
    for rest_name, spec in specs.items():
        if ("entity_name" in spec["model"] and
                spec["model"]["entity_name"] == entity_name):
            return spec

    return None


def run_commands(specs, command_file):
    with open(command_file, "r") as f:
        commands = yaml.safe_load(f.read())

    for command_pair in commands:
        for command, value in command_pair.items():
            if command == "name":
                template_headers["name"] = value
            elif command == "description":
                template_headers["description"] = value
            elif command == "version":
                template_headers["version"] = value
            elif command == "create":
                create_object(specs, value)
            else:
                raise Exception("Unknown command: " + command)


def create_object(specs, value):
    spec = find_spec(specs, value)
    if spec is None:
        raise Exception("Unknown object for create: " + value)

    actions = [set_values(spec)]
    obj = {
        "create-object": {"type": spec["model"]["entity_name"],
                          "actions": actions}}

    template_actions.append(obj)


def set_values(spec):
    attributes = dict()

    for attribute in spec["attributes"]:
        name = attribute["name"]
        snake = camel_to_snake_case(name)
        attributes[name] = JINJA_START + snake + JINJA_END
        add_variable(attribute)

    return {"set-values": attributes}


def add_variable(attribute):
    lines = list()

    name = attribute["name"]
    snake = camel_to_snake_case(name)

    lines.append("- name: " + snake)

    attr_type = attribute["type"]
    if attr_type == "enum":
        choices = attribute["allowed_choices"]
        lines.append("  type: choice")
        lines.append("  choices: [" + ", ".join(choices) + "]")
    elif attr_type == "list":
        item_type = attribute["subtype"]
        lines.append("  type: list")
        lines.append("  item-type: " + item_type)
    else:
        lines.append("  type: " + attr_type)

    if attribute["required"] is False:
        lines.append("  optional: true")

    default = attribute["default_value"]
    if default is not None:
        lines.append("  default: " + default)

    template_variables.append(lines)


def camel_to_snake_case(camel):
    snake = re.sub(r"([A-Z])([A-Z])([a-z])", r"\1_\2\3", camel)
    snake = re.sub(r"([a-z])([A-Z])", r"\1_\2", snake)
    return snake.lower()


def generate_template():
    lines = list()

    generate_headers(lines)
    generate_variables(lines)
    generate_actions(lines)

    return "\n".join(lines)


def generate_headers(lines):
    lines.append("name: " + template_headers["name"])
    lines.append("description: " + template_headers["description"])
    lines.append("template-version: " + template_headers["template"])
    lines.append("levistate-version: " + template_headers["levistate"])
    lines.append("software-type: " + template_headers["software"])
    lines.append("software-version: " + template_headers["version"])


def generate_variables(lines):
    for variable in template_variables:
        lines.extend(variable)


def generate_actions(lines):

    actions = yaml.safe_dump({"actions": template_actions},
                             default_flow_style=False, default_style='')

    actions = actions.replace(JINJA_START, "{{ ")
    actions = actions.replace(JINJA_END, " }}")
    lines.extend(actions.split("\n"))


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

    specs = read_specs(args.spec_path)

    run_commands(specs, args.command_file)

    print generate_template()

if __name__ == "__main__":
    main()
