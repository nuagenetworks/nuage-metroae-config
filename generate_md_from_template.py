#!/usr/bin/env python

import argparse
import csv
import re
import sys
import yaml
from jinja2 import Template

DESCRIPTION = """This tool is used to generate an MD file from a levistate feature template."""
METADATA_RE = "([\s\S]*)\nactions:"

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    #parser.add_argument('md_file_dir', action='store',
                        #help="path to the directory where the md files are stored.")

    parser.add_argument('template_file', action='store',
                        help="path to the template file to parse.")

    return parser.parse_args()


def main():

    args = parse_args()
    with open(args.template_file, mode='r') as t:
        template_data = t.read()
    template_metadata = re.search(METADATA_RE, template_data)
    yaml_data = yaml.safe_load(template_metadata.group(1))
    print template_metadata.group(1)
    with open('feature_md.j2') as file_:
        template = Template(file_.read(), trim_blocks=True)
    print template.render(yaml_data)


if __name__ == "__main__":
    main()
