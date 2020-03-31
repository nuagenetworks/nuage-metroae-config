#!/usr/bin/env python

import argparse
import os
import subprocess

DESCRIPTION = """This tool is used to update the example ouput in templates"""
ENV_TEMPLATE = 'TEMPLATE_PATH'
ENV_SOFTWARE_VERSION = 'SOFTWARE_VERSION'
ENV_VSD_SPECIFICATIONS = 'VSD_SPECIFICATIONS_PATH'
TEMP_FILE = "/tmp/metroae-config-example.yml"
INDENT = 2
EXAMPLE_COMMAND = "(example)$ metroae config create user-data.yml"


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-tp', '--template-path', dest='template_path',
                        action='append', required=False,
                        default=os.getenv(ENV_TEMPLATE, None),
                        help='Path containing template files. Can also set '
                             'using environment variable %s' % (ENV_TEMPLATE))

    parser.add_argument('-sp', '--spec-path', dest='spec_path',
                        action='append', required=False,
                        default=os.getenv(ENV_VSD_SPECIFICATIONS, None),
                        help='Path containing object specifications. Can also'
                             ' set using environment variable %s' % (
                                 ENV_VSD_SPECIFICATIONS))

    parser.add_argument('-sv', '--software_version', dest='software_version',
                        action='store', required=False,
                        default=os.getenv(ENV_SOFTWARE_VERSION, None),
                        help='Override software version for VSD. Can also set'
                             ' using environment variable %s' % (
                                 ENV_SOFTWARE_VERSION))

    return parser.parse_args()


def update_templates(args):
    for file_name in os.listdir(args.template_path):
        if file_name.endswith(".yml") or file_name.endswith(".yaml"):
            print "Processing " + file_name
            full_path = os.path.join(args.template_path, file_name)
            with open(full_path, "r") as f:
                lines = update_template(f.read(), args)

            with open(full_path, "w") as f:
                f.write("\n".join(lines))


def update_template(contents, args):
    lines = contents.split("\n")

    cur_line_num = 0
    while cur_line_num >= 0:
        cur_line_num = find_next_line_num(lines, cur_line_num, "user-data: |")
        if cur_line_num >= 0:
            end_line_num = find_next_line_num(lines, cur_line_num,
                                              "sample-run: |")
            if end_line_num < 0:
                print("Error: no sample-run for user-data at line %s" %
                      cur_line_num)
                return

            create_user_data("\n".join(lines[cur_line_num + 1:end_line_num]))
            output = run_metroae_config(args)
            replace_output(lines, output, end_line_num)

            cur_line_num += 1

    return lines


def find_next_line_num(lines, cur_line_num, search_str):
    for i in range(cur_line_num, len(lines)):
        cur_line = lines[i]
        if search_str in cur_line:
            return i

    return -1


def create_user_data(contents):
    with open(TEMP_FILE, "w") as f:
        f.write(contents)


def run_metroae_config(args):
    out = subprocess.Popen(['./metroae_config.py',
                            'validate',
                            TEMP_FILE,
                            "-tp", args.template_path,
                            "-sp", args.spec_path,
                            "-sv", args.software_version],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if out.returncode != 0:
        print(stdout)
        # print(stderr)
        # exit(1)

    return stdout


def replace_output(lines, output, line_num):
    indent = identify_indent(lines[line_num])
    remove_content(lines, line_num + 1, indent)
    addl_indent = " " * INDENT

    content = [indent + addl_indent + EXAMPLE_COMMAND]
    content.extend([indent + addl_indent + x for x in output.split("\n")[1:]])

    for line in reversed(content):
        if line.strip() != "":
            lines.insert(line_num + 1, line)


def identify_indent(line):
    stripped_line = line.lstrip()
    indent_amount = len(line) - len(stripped_line)
    return line[0:indent_amount] + " "


def remove_content(lines, line_num, indent):
    while lines[line_num].strip() == "" or lines[line_num].startswith(indent):
        del lines[line_num]


def main():
    args = parse_args()

    if args.template_path is None:
        print("Please specify template-path argument")
        exit(1)

    if args.spec_path is None:
        print("Please specify spec-path argument")
        exit(1)

    if args.software_version is None:
        print("Please specify software_version argument")
        exit(1)

    update_templates(args)


if __name__ == "__main__":
    main()
