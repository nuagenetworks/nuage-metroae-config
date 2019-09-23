#!/usr/bin/env python

import argparse
import os
import re
import yaml
from jinja2 import Template
import md_template

DESCRIPTION = """This tool is used to generate an MD file from a levistate feature template."""
TEMPLATE_METADATA_RE = "([\s\S]*)\nactions:"


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('template_file', action='store',
                        help="path to the template file to parse")

    parser.add_argument('md_directory', action='store',
                        help="path to the directory where the md file will be written")

    return parser.parse_args()


def main():

    args = parse_args()
    with open(args.template_file, mode='r') as t:
        template_data = t.read()
    docfile_metadata = re.search(TEMPLATE_METADATA_RE, template_data)
    yaml_data = yaml.safe_load(docfile_metadata.group(1) + "\nfile_name: " + os.path.basename(args.template_file))
    template = Template(md_template.template, trim_blocks=True)
    with open(args.md_directory + "/" + yaml_data['doc-file'], mode='w') as md:
        md.write(template.render(yaml_data))


if __name__ == "__main__":
    main()
