#!/usr/bin/env python

import argparse
import os
import yaml

DESCRIPTION = """This tool is used to pull text from .md files and write to a
 documentation data file"""


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('md_file_dir', action='store',
                        help="Directory where the md files are stored.")

    parser.add_argument('doc_data_file', action='store',
                        help="Name of file to store documentation data.")

    return parser.parse_args()


def parse_md_files(doc_data, path):
    for file_name in os.listdir(path):
        if file_name.endswith(".md"):
            print "Processing " + file_name
            full_path = os.path.join(path, file_name)
            with open(full_path, "r") as f:
                parse_md_file(doc_data, file_name, f.read())


def parse_md_file(doc_data, file_name, file_text):
    lines = file_text.split("\n")
    section_line_num = 0
    file_data = {"doc-file": file_name}
    section_line_num = find_next_section_line_num(lines, section_line_num)
    while section_line_num >= 0:
        section_line_num = parse_section(file_data, lines, section_line_num)

    doc_data[file_data["template-name"]] = file_data


def find_next_section_line_num(lines, cur_line_num):
    for i in range(cur_line_num, len(lines)):
        cur_line = lines[i]
        if len(cur_line) > 0 and cur_line[0] == "#":
            return i

    return -1


def parse_section(file_data, lines, section_line_num):
    header_name = get_section_header_name(lines[section_line_num])

    if header_name.lower().startswith("feature template: "):
        parse_template_name(file_data, header_name)
    elif header_name.lower().startswith("description"):
        parse_description(file_data, lines, section_line_num)
    elif header_name.lower().startswith("usage"):
        parse_usage(file_data, lines, section_line_num)
    elif header_name.lower().startswith("parameters"):
        parse_parameters(file_data, lines, section_line_num)
    elif header_name.lower().startswith("restrictions"):
        parse_restrictions(file_data, lines, section_line_num)
    elif header_name.lower().startswith("examples"):
        parse_examples(file_data, lines, section_line_num)

    return find_next_section_line_num(lines, section_line_num + 1)


def get_section_header_name(header):
    i = 0
    while header[i] in ["#", " "]:
        i += 1
    return header[i:]


def parse_template_name(file_data, header_name):
    file_data["template-name"] = header_name[18:].strip()


def parse_description(file_data, lines, section_line_num):
    text = parse_text(file_data, lines, section_line_num)
    file_data["description"] = text


def parse_usage(file_data, lines, section_line_num):
    text = parse_text(file_data, lines, section_line_num)
    file_data["usage"] = text


def parse_text(file_data, lines, section_line_num):
    end_line = find_next_section_line_num(lines, section_line_num + 1)
    text = ""
    if end_line > 0:
        text = "\n".join(lines[section_line_num + 1: end_line])

    return text


def parse_parameters(file_data, lines, section_line_num):
    parameters = dict()
    end_line = find_next_section_line_num(lines, section_line_num + 1)
    if end_line > 0:
        for i in range(section_line_num + 1, end_line):
            parse_parameter(parameters, lines[i])

    file_data["parameters"] = parameters


def parse_parameter(parameters, line):
    end_pos = line.find(":*")
    if end_pos > 0:
        key = line[1:end_pos]
        value = line[end_pos + 3:]
        parameters[key] = value


def parse_restrictions(file_data, lines, section_line_num):
    end_section = find_next_section_line_num(lines, section_line_num + 1)
    restrictions = []
    restriction_list = None

    for i in range(section_line_num + 1, end_section):
        if lines[i].startswith("**"):
            restriction_list = list()
            operation = {"operation": lines[i][2:-3],
                         "restriction-list": restriction_list}
            restrictions.append(operation)
        elif lines[i].startswith("* "):
            restriction_list.append(lines[i][2:].strip())

    file_data["restrictions"] = restrictions


def parse_examples(file_data, lines, section_line_num):
    examples = list()
    example_line_num = find_next_section_line_num(lines, section_line_num + 1)
    while example_line_num > 0:
        example_line_num = parse_example(examples, lines, example_line_num)

    file_data["examples"] = examples


def parse_example(examples, lines, example_line_num):
    example = dict()

    example["name"] = get_section_header_name(lines[example_line_num])

    description_lines = list()
    i = example_line_num + 1
    done = False
    while not done:
        if (i < len(lines) and not lines[i].startswith("```") and
                not lines[i].startswith("#")):
            description_lines.append(lines[i])
            i += 1
        else:
            done = True

    example["description"] = "\n".join(description_lines)

    if i >= len(lines):
        return -1

    if not lines[i].startswith("```"):
        return i

    i += 1

    user_data_lines = list()
    done = False
    while not done:
        if not lines[i].startswith("```"):
            user_data_lines.append(lines[i])
        else:
            done = True
        i += 1

    example["user-data"] = "\n".join(user_data_lines)

    i += 2
    sample_run_lines = list()
    done = False
    while not done:
        if not lines[i].startswith("```"):
            sample_run_lines.append(lines[i])
        else:
            done = True
        i += 1

    example["sample-run"] = "\n".join(sample_run_lines)

    examples.append(example)
    example_line_num = find_next_section_line_num(lines, example_line_num + 1)
    return example_line_num


def main():
    args = parse_args()
    doc_data = dict()

    parse_md_files(doc_data, args.md_file_dir)
    print "Writing " + args.doc_data_file
    with open(args.doc_data_file, "w") as f:
        f.write(yaml.safe_dump(doc_data,
                               default_flow_style=False,
                               default_style=''))


if __name__ == "__main__":
    main()
