#!/usr/bin/env python

import argparse
import csv
import re
import sys
import yaml

DESCRIPTION = """This tool is used to pull text from MD files and insert it into templates."""
DESCRIPTION_RE = "\#\#\#\# Description\s*\n(.*)\n"

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('names_file', action='store',
                        help="path to the file that contains the comma-separated md_file,template_file names.")

    parser.add_argument('md_file_dir', action='store',
                        help="path to the directory where the md files are stored.")

    parser.add_argument('template_file_dir', action='store',
                        help="path to the directory where the template files are stored.")

    return parser.parse_args()


def main():

    args = parse_args()

    with open(args.names_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            description = ""
            data = ""
            template = dict()
            md_file_name = args.md_file_dir+"/"+row["md_file_name"]
            template_file_name = args.template_file_dir+"/"+row["template_file_name"]
            with open(md_file_name, 'r') as file:
                data = file.read()
            if data:
                description = re.search(DESCRIPTION_RE, data)
            else:
                sys.exit(md_file_name+" appears to be empty. Quitting.")
            if description:
                print row["template_file_name"]+" Description: "+description.group(1)+"\n"
                with open(template_file_name) as f:
                    template = yaml.load(f)
                if template:
                    template['description'] = description
                    with open(template_file_name, 'w') as f:
                        yaml.dump(doc, f)
                else:
                    sys.exit(template_file_name+" load failed. Is it empty? It is valid YAML? Quitting.")
            else:
                sys.exit("Description not found in "+template_file_name+" file. Quitting.")


if __name__ == "__main__":
    main()
