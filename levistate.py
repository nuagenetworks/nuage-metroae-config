import argparse
import os
import git

from configuration import Configuration
from errors import LevistateError
from logger import Logger
from template import TemplateStore
from user_data_parser import UserDataParser
from vsd_writer import VsdWriter

DEFAULT_VSD_USERNAME = 'csproot'
DEFAULT_VSD_PASSWORD = 'csproot'
DEFAULT_VSD_ENTERPRISE = 'csp'
DEFAULT_URL = 'https://127.0.0.1:8080'
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
LIST_ACTION = 'list'
SCHEMA_ACTION = 'schema'
EXAMPLE_ACTION = 'example'
UPGRADE_TEMPLATE_ACTION = 'upgrade-templates'

DESCRIPTION = """This tool reads JSON or Yaml files of templates
and user-data to write a configuration to a VSD or to revert (remove) said
configuration.  See README.md for more."""

REQUIRED_FIELDS_ERROR = """Template path or Data path or VSD specification path are not provided.
Please specify template path using --tp on command line or set an environment variable %s
Please specify user data path using --dp on command line or set an environment variable %s
Please specify VSD specification path using --sp on command line or set an environment variable %s""" % (ENV_TEMPLATE, ENV_USER_DATA, ENV_VSD_SPECIFICATIONS) 

def main():
    args = parse_args()
    
    if args.action == VALIDATE_ACTION or args.action == CREATE_ACTION or args.action == REVERT_ACTION: 
        if args.template_path is None and os.getenv(ENV_TEMPLATE) is not None:
            args.template_path = os.getenv(ENV_TEMPLATE).split()
            
        if args.data_path is None and os.getenv(ENV_USER_DATA) is not None:
            args.data_path = os.getenv(ENV_USER_DATA).split()
    
        if args.spec_path is None and os.getenv(ENV_VSD_SPECIFICATIONS) is not None:
            args.spec_path = os.getenv(ENV_VSD_SPECIFICATIONS).split()
        
        #Check to make sure we have template path and data path set
        if args.template_path is None or args.data_path is None or args.spec_path is None:
            print REQUIRED_FIELDS_ERROR 
            exit(1)
            
    elif args.action == LIST_ACTION:
        if args.template_path is None and os.getenv(ENV_TEMPLATE) is not None:
            args.template_path = os.getenv(ENV_TEMPLATE).split()
        
        if args.template_path is None:
            print "Please specify template path using --tp on command line or set an environment variable %s" % (ENV_TEMPLATE)
            exit(1)
            
    elif args.action == SCHEMA_ACTION or args.action == EXAMPLE_ACTION:
        if args.template_path is None and os.getenv(ENV_TEMPLATE) is not None:
            args.template_path = os.getenv(ENV_TEMPLATE).split()
            
        if args.template_name is None:
            print "Please specify template name using --t on command line"
            exit(1)
        
        if args.template_path is None:
            print "Please specify template path using --tp on command line or set an environment variable %s" % (ENV_TEMPLATE)
            exit(1)
     
    levistate = Levistate(args, args.action)
    levistate.run()
    
def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    sub_parser = parser.add_subparsers(dest='action')
    
    create_parser = sub_parser.add_parser(CREATE_ACTION)
    add_parser_arguments(create_parser)
    
    revert_parser = sub_parser.add_parser(REVERT_ACTION)
    add_parser_arguments(revert_parser)
    
    validate_parser = sub_parser.add_parser(VALIDATE_ACTION)
    add_parser_arguments(validate_parser)
    
    list_parser = sub_parser.add_parser(LIST_ACTION)
    add_template_path_parser_argument(list_parser)
    
    schema_parser = sub_parser.add_parser(SCHEMA_ACTION)
    add_template_parser_arguements(schema_parser)
    
    example_parser = sub_parser.add_parser(EXAMPLE_ACTION)
    add_template_parser_arguements(example_parser)
    
    upgrade_templates = sub_parser.add_parser(UPGRADE_TEMPLATE_ACTION)
    
    return parser.parse_args()

def add_template_path_parser_argument(parser):
    parser.add_argument('-tp', '--template-path', dest='template_path',
                        action='append', required=False,
                        default=None,
                        help='Path containing template files. Can also set using environment variable %s' % (ENV_TEMPLATE))

def add_template_parser_arguements(parser):
    add_template_path_parser_argument(parser)
    
    parser.add_argument('-t', '--template', dest='template_name',
                        action='store', required=False,
                        help='Template name')
    
def add_parser_arguments(parser):
    add_template_path_parser_argument(parser)
    parser.add_argument('-sp', '--spec-path', dest='spec_path',
                        action='append', required=False,
                        help='Path containing object specifications. Can also set using environment variable %s' % (ENV_VSD_SPECIFICATIONS))
    parser.add_argument('-dp', '--data-path', dest='data_path',
                        action='append', required=False,
                        default=None,
                        help='Path containing user data. Can also set using environment variable %s' % (ENV_USER_DATA))
    parser.add_argument('-d', '--data', dest='data',
                        action='append', required=False,
                        help='Specify user data as key=value')
    parser.add_argument('-v', '--vsd-url', dest='vsd_url',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_URL, DEFAULT_URL),
                        help='URL to VSD REST API. Can also set using environment variable %s' % (ENV_VSD_URL))
    parser.add_argument('-u', '--username', dest='username',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_USERNAME, DEFAULT_VSD_USERNAME),
                        help='Username for VSD. Can also set using environment variable %s' % (ENV_VSD_USERNAME))
    parser.add_argument('-p', '--password', dest='password',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_PASSWORD, DEFAULT_VSD_PASSWORD),
                        help='Password for VSD. Can also set using environment variable %s' % (ENV_VSD_PASSWORD))
    parser.add_argument('-e', '--enterprise', dest='enterprise',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_ENTERPRISE, DEFAULT_VSD_ENTERPRISE),
                        help='Enterprise for VSD. Can also set using environment variable %s' % (ENV_VSD_ENTERPRISE))
    parser.add_argument('-lg', '--logs', dest='logs',
                        action='store_true', required=False,
                        help='Show logs after run')


class Levistate(object):

    def __init__(self, args, action):
        self.args = args
        self.template_data = list()
        self.logger = Logger()
        self.action = action

    def run(self):
        
        if self.action == UPGRADE_TEMPLATE_ACTION:
            self.upgrade_templates()
            return
        
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
        
        if self.action == LIST_ACTION:
            template_names = self.store.get_template_names()
            print "\n".join(template_names)
            return True

        if self.action == SCHEMA_ACTION:
            template = self.store.get_template(self.args.template_name)
            print template.get_schema()
            return True

        if self.action == EXAMPLE_ACTION:
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
                
    def upgrade_templates(self):
        if self.action == UPGRADE_TEMPLATE_ACTION:
            dirName = "/data/standard-templates"
            url = "https://github.mv.usa.alcatel.com/CASO/levistate-templates.git"
            if not os.path.isdir(dirName):
                os.mkdir(dirName)
                repo = git.Repo.init(dirName)
                repo.clone(url)    
            else:
                repo = git.Repo.init(dirName)
                origin = repo.create_remote('origin/master', url)
                origin.fetch()
                origin.pull(origin.refs[0].remote_head())
    
if __name__ == "__main__":
    main()
