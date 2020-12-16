#!/usr/bin/env python

import argparse
import os
import yaml

DESCRIPTION = """This tool is used to add documentation data into the
 templates from a doc data file."""


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('doc_data_file', action='store',
                        help="Name of file to containing documentation data.")

    parser.add_argument('template_file_dir', action='store',
                        help="Directory where the template files are stored.")

    return parser.parse_args()


def read_doc_data(doc_data_file):
    with open(doc_data_file, "r") as f:
        doc_data_yaml = f.read()

    return yaml.safe_load(doc_data_yaml)


def read_template_info(template_file_dir):
    template_info = dict()
    for file_name in os.listdir(template_file_dir):
        if file_name.endswith(".yml") or file_name.endswith(".yaml"):
            print("Reading " + file_name)
            full_path = os.path.join(template_file_dir, file_name)
            with open(full_path, "r") as f:
                template_yaml = f.read()
            lines = template_yaml.split("\n")
            template_key = lines[0][6:].lower().strip()
            template_info[template_key] = full_path

    return template_info


def add_doc_data_to_all_templates(doc_data, template_info):
    for template_name, data in doc_data.items():
        print("Processing " + template_name)
        template_path = template_info[template_name.lower()]
        add_doc_data_to_template(data, template_path)


def add_doc_data_to_template(data, template_path):
    with open(template_path, "r") as f:
        template_file = f.read()

    lines = template_file.split("\n")

    insert_parameters(lines, data)
    insert_docfile(lines, data)
    insert_restrictions(lines, data)
    insert_usage(lines, data)
    update_description(lines, data)
    insert_examples(lines, data)

    with open(template_path, "w") as f:
        f.write("\n".join(lines))


def insert_parameters(lines, data):
    for name, descr in data["parameters"].items():
        i = find_line(lines, "  - name: " + name.lower())
        if i >= 0:
            insert_lines = yaml.safe_dump({"description": descr.strip()},
                                          default_flow_style=False,
                                          default_style='').strip().split("\n")
            lines[i + 1:i + 1] = ["    " + x for x in insert_lines]
        else:
            raise Exception("Could not find variable: " + name)


def insert_docfile(lines, data):
    i = find_line(lines, "description:")
    if i >= 0:
        lines[i + 1:i + 1] = ["doc-file: " + data["doc-file"]]


def insert_usage(lines, data):
    i = find_line(lines, "description:")
    if i >= 0:
        insert_lines = yaml.safe_dump({"usage": data["usage"].strip()},
                                      default_flow_style=False,
                                      default_style='').split("\n")
        lines[i + 1:i + 1] = insert_lines


def insert_restrictions(lines, data):
    i = find_line(lines, "description:")
    if i >= 0:
        insert_lines = yaml.safe_dump(
            {"restrictions": data["restrictions"]},
            default_flow_style=False,
            default_style='').split("\n")
        lines[i + 1:i + 1] = insert_lines


def update_description(lines, data):
    i = find_line(lines, "description:")
    if i >= 0:
        lines[i] = yaml.safe_dump({"description": data["description"].strip()},
                                  default_flow_style=False,
                                  default_style='')


def insert_examples(lines, data):
    example_lines = list()
    example_lines.append("examples:")

    for example in data["examples"]:
        example_lines.append("  - name: " + example["name"].strip())
        descr_lines = yaml.safe_dump(
            {"description": example["description"].strip()},
            default_flow_style=False,
            default_style='').split("\n")
        for descr_line in descr_lines:
            if descr_line.strip() != "":
                example_lines.append("    " + descr_line)
            else:
                example_lines.append("")
        if "user-data" in example:
            example_lines.append("    user-data: |")
            data_lines = example["user-data"].split("\n")
            for data_line in data_lines:
                if data_line.strip() != "":
                    example_lines.append("      " + data_line)
                else:
                    example_lines.append("")
        if "sample-run" in example:
            example_lines.append("    sample-run: |")
            run_lines = example["sample-run"].split("\n")
            for run_line in run_lines:
                if run_line.strip() != "":
                    example_lines.append("      " + run_line)
                else:
                    example_lines.append("")

    i = find_line(lines, "actions:")
    if i >= 0:
        lines[i:i] = example_lines


def find_line(lines, search_str):
    for i in range(len(lines)):
        if lines[i].startswith(search_str):
            return i

    return -1


def main():
    args = parse_args()
    doc_data = read_doc_data(args.doc_data_file)
    template_info = read_template_info(args.template_file_dir)

    add_doc_data_to_all_templates(doc_data, template_info)


if __name__ == "__main__":
    main()
