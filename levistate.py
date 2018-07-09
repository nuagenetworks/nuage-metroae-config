import argparse
import os

from configuration import Configuration
from errors import LevistateError
from logger import Logger
from template import TemplateStore
from user_data_parser import UserDataParser
from vsd_writer import VsdWriter

DEFAULT_VSD_USERNAME = 'csproot'
DEFAULT_VSD_PASSWORD = 'csproot'
DEFAULT_VSD_ENTERPRISE = 'csp'
DEFAULT_URL = 'https://localhost:8080'
ENV_TEMPLATE = 'TEMPLATE_PATH'
ENV_USER_DATA = 'USER_DATA_PATH'
ENV_VSD_USERNAME = 'VSD_USERNAME'
ENV_VSD_PASSWORD = 'VSD_PASSWORD'
ENV_VSD_ENTERPRISE = 'VSD_ENTERPRISE'
ENV_VSD_URL = 'VSD_URL'
ENV_VSD_SPECIFICATIONS = 'VSD_SPECIFICATIONS_PATH'
VALIDATE_ACTION = 'validate'
CREATE_ACTION = 'create'
REVERT_ACTION = 'revert'

DESCRIPTION = """This tool reads JSON or Yaml files of templates
and user-data to write a configuration to a VSD or to revert (remove) said
configuration.  See README.md for more."""

REQUIRED_FIELDS_ERROR = """Template path or Data path or VSD specification path are not provided.
Please specify template path using --tp on command line or set an environment variable TEMPLATE_PATH
Please specify user data path using --dp on command line or set an environment variable USER_DATA_PATH
Please specify VSD specification path using --sp on command line or set an environment variable VSD_SPECIFICATION_PATH"""

def main():
    args = parse_args()
    if args.template_path is None and os.getenv(ENV_TEMPLATE) is not None:
        args.template_path = os.getenv(ENV_TEMPLATE).split()
        
    if args.data_path is None and os.getenv(ENV_USER_DATA) is not None:
        args.data_path = os.getenv(ENV_USER_DATA).split()

    if args.spec_path is None and os.getenv(ENV_VSD_SPECIFICATIONS) is not None:
        args.spec_path = os.getenv(ENV_VSD_SPECIFICATIONS).split()
    
    #Check to make sure we have template path and data path set
    if args.template_path is None or args.data_path is None or args.spec_path is None:
        print REQUIRED_FIELDS_ERROR 
    else:
        levistate = Levistate(args, args.action)
        levistate.run()
    
def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    sub_parser = parser.add_subparsers(dest='action')
    create_parser = sub_parser.add_parser(CREATE_ACTION)
    revert_parser = sub_parser.add_parser(REVERT_ACTION)
    validate_parser = sub_parser.add_parser(VALIDATE_ACTION)
    
    add_parser_arguments(create_parser)
    add_parser_arguments(revert_parser)
    add_parser_arguments(validate_parser)
    
    return parser.parse_args()

def add_parser_arguments(parser):
    parser.add_argument('-tp', '--template-path', dest='template_path',
                        action='append', required=False,
                        default=None,
                        help='Path containing template files')
    parser.add_argument('-sp', '--spec-path', dest='spec_path',
                        action='append', required=False,
                        help='Path containing object specifications')
    parser.add_argument('-dp', '--data-path', dest='data_path',
                        action='append', required=False,
                        default=None,
                        help='Path containing user data')
    parser.add_argument('-t', '--template', dest='template_name',
                        action='store', required=False,
                        help='Template name')
    parser.add_argument('-d', '--data', dest='data',
                        action='append', required=False,
                        help='Specify user data as key=value')
    parser.add_argument('-v', '--vsd-url', dest='vsd_url',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_URL, DEFAULT_URL),
                        help='URL to VSD REST API')
    parser.add_argument('-u', '--username', dest='username',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_USERNAME, DEFAULT_VSD_USERNAME),
                        help='Username for VSD')
    parser.add_argument('-p', '--password', dest='password',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_PASSWORD, DEFAULT_VSD_PASSWORD),
                        help='Password for VSD')
    parser.add_argument('-e', '--enterprise', dest='enterprise',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_ENTERPRISE, DEFAULT_VSD_ENTERPRISE),
                        help='Enterprise for VSD')
    parser.add_argument('-lg', '--logs', dest='logs',
                        action='store_true', required=False,
                        help='Show logs after run')
    parser.add_argument('-l', '--list', dest='list',
                        action='store_true', required=False,
                        help='Lists loaded templates')
    parser.add_argument('-s', '--schema', dest='schema',
                        action='store_true', required=False,
                        help='Displays template schema')
    parser.add_argument('-x', '--example', dest='example',
                        action='store_true', required=False,
                        help='Displays template user data example')

class Levistate(object):

    def __init__(self, args, action):
        self.args = args
        self.template_data = list()
        self.logger = Logger()
        self.action = action

    def run(self):

        self.setup_template_store()
        if self.list_info():
            return
        self.setup_vsd_writer()
        self.parse_user_data()
        self.parse_extra_vars()

        try:
            self.apply_templates()
        except LevistateError as e:
            self.logger.error(e.get_display_string())
            print self.logger.get()
            print ""
            print "Error"
            print "-----"
            print e.get_display_string()
            exit(1)

        if self.args.logs:
            print self.logger.get()

    def parse_extra_vars(self):
        if self.args.data is not None:
            template_data = dict()
            for data in self.args.data:
                for var in data.split(','):
                    key_value_pair = var.split('=')
                    if len(key_value_pair) != 2:
                        raise Exception("Invalid extra-vars argument, must "
                                        "be key=value format: " + var)
                    key = key_value_pair[0]
                    value = self.parse_var_value(key_value_pair[1])
                    template_data[key] = value

            self.template_data.append((self.args.template_name, template_data))
            # print str(template_data)

    def parse_var_value(self, value):
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        try:
            return int(value)
        except ValueError:
            pass

        return value

    def list_info(self):
        if self.args.list:
            template_names = self.store.get_template_names()
            print "\n".join(template_names)
            return True

        if self.args.schema:
            if self.args.template_name is None:
                print "Requires template to be specified with -t"
            else:
                template = self.store.get_template(self.args.template_name)
                print template.get_schema()
            return True

        if self.args.example:
            if self.args.template_name is None:
                print "Requires template to be specified with -t"
            else:
                template = self.store.get_template(self.args.template_name)
                print template.get_example()
            return True

        return False

    def setup_vsd_writer(self):
        self.writer = VsdWriter()
        self.writer.set_logger(self.logger)
        for path in self.args.spec_path:
            self.writer.read_api_specifications(path)
        self.writer.set_session_params(self.args.vsd_url,
                                       username=self.args.username,
                                       password=self.args.password,
                                       enterprise=self.args.enterprise,
                                       )

    def setup_template_store(self):
        self.store = TemplateStore()
        
        for path in self.args.template_path:
            self.store.read_templates(path)

    def parse_user_data(self):
        if self.args.data_path is not None:
            parser = UserDataParser()
            for path in self.args.data_path:
                parser.read_data(path)
            self.template_data = parser.get_template_name_data_pairs()
            # For debugging user data
            # print str(self.template_data)

    def apply_templates(self):
        config = Configuration(self.store)
        config.set_logger(self.logger)
        for data in self.template_data:
            template_name = data[0]
            template_data = data[1]
            config.add_template_data(template_name, **template_data)

        if self.action == VALIDATE_ACTION:
            validate_actions = [True]
        else:
            validate_actions = [True, False]

        for validate_only in validate_actions:
            self.writer.set_validate_only(validate_only)
            if self.action == REVERT_ACTION:
                config.revert(self.writer)
            else:
                config.apply(self.writer)

            self.writer.set_validate_only(False)

            if self.action == VALIDATE_ACTION:
                print str(config.root_action)


if __name__ == "__main__":
    main()
