#!/usr/bin/env python

import argparse
import json
import os
import re
import yaml

DESCRIPTION = """This tool is used to pull text from MD files and insert it into templates."""


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('md_file', action='store',
                        help="path to the md file to parse.")

    parser.add_argument('template_file', action='store',
                        help="path to the template file to update.")

    return parser.parse_args()


def main():

    args = parse_args()


if __name__ == "__main__":
    main()
