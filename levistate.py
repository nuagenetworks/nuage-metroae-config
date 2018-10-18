#!/usr/bin/env python

import argparse
import logging
import os
import tarfile
import urllib3
import wget

from configuration import Configuration
from errors import LevistateError
from template import TemplateStore
from user_data_parser import UserDataParser
from vsd_writer import VsdWriter

# Disables annoying SSL certificate validation warnings
urllib3.disable_warnings()

LEVISTATE_VERSION = "1.0"

DEFAULT_VSD_USERNAME = 'csproot'
DEFAULT_VSD_PASSWORD = 'csproot'
DEFAULT_VSD_ENTERPRISE = 'csp'
DEFAULT_URL = 'https://127.0.0.1:8443'
DEFAULT_LOG_LEVEL = 'DEBUG'
ENV_TEMPLATE = 'TEMPLATE_PATH'
ENV_USER_DATA = 'USER_DATA_PATH'
ENV_VSD_USERNAME = 'VSD_USERNAME'
ENV_VSD_PASSWORD = 'VSD_PASSWORD'
ENV_VSD_ENTERPRISE = 'VSD_ENTERPRISE'
ENV_VSD_URL = 'VSD_URL'
ENV_VSD_SPECIFICATIONS = 'VSD_SPECIFICATIONS_PATH'
ENV_LOG_FILE = 'LOG_FILE'
ENV_LOG_LEVEL = 'LOG_LEVEL'
VALIDATE_ACTION = 'validate'
CREATE_ACTION = 'create'
REVERT_ACTION = 'revert'
LIST_ACTION = 'list'
SCHEMA_ACTION = 'schema'
EXAMPLE_ACTION = 'example'
TEMPLATE_ACTION = 'templates'
UPGRADE_TEMPLATE_ACTION = 'update'
VERSION_ACTION = 'version'
HELP_ACTION = 'help'
TEMPLATE_TAR_LOCATION = "http://s3.us-east-2.amazonaws.com/levistate-templates/levistate.tar"
VSD_SPECIFICAIONS_LOCATION = "http://s3.us-east-2.amazonaws.com/vsd-api-specifications/specifications.tar"
TEMPLATE_DIR = "/data/standard-templates"
SPECIFICATION_DIR = "/data/vsd-api-specifications"
LOGS_DIR = "/data"
LOG_LEVEL_STRS = ["OUTPUT", "ERROR", "INFO", "DEBUG", "API"]

DESCRIPTION = """Version %s - This tool reads JSON or Yaml files of templates
and user-data to write a configuration to a VSD or to revert (remove) said
configuration.""" % LEVISTATE_VERSION

VERSION_OUTPUT = "Levistate Engine version %s" % LEVISTATE_VERSION

REQUIRED_FIELDS_ERROR = """Template path or Data path or VSD specification path are not provided.
Please specify template path using -tp on command line or set an environment variable %s
Please specify VSD specification path using -sp on command line or set an environment variable %s""" % (ENV_TEMPLATE, ENV_VSD_SPECIFICATIONS)


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.action == HELP_ACTION:
        print parser.print_help()
        exit(0)
    elif args.action == VERSION_ACTION or (hasattr(args, "version") and
                                           args.version):
        print VERSION_OUTPUT
        exit(0)
    elif (args.action == VALIDATE_ACTION or
          args.action == CREATE_ACTION or
          args.action == REVERT_ACTION):
        if args.template_path is None and os.getenv(ENV_TEMPLATE) is not None:
            args.template_path = os.getenv(ENV_TEMPLATE).split()

        if args.data_path is None and os.getenv(ENV_USER_DATA) is not None:
            args.data_path = os.getenv(ENV_USER_DATA).split()

        if (args.spec_path is None and
                os.getenv(ENV_VSD_SPECIFICATIONS) is not None):
            args.spec_path = os.getenv(ENV_VSD_SPECIFICATIONS).split()

        # Check to make sure we have template path and data path set
        if (args.template_path is None or
                args.spec_path is None):
            print REQUIRED_FIELDS_ERROR
            exit(1)

    elif args.action == TEMPLATE_ACTION and args.templateAction == LIST_ACTION:
        if args.template_path is None and os.getenv(ENV_TEMPLATE) is not None:
            args.template_path = os.getenv(ENV_TEMPLATE).split()

        if args.template_path is None:
            print "Please specify template path using -tp on command line or set an environment variable %s" % (ENV_TEMPLATE)
            exit(1)

    elif args.action == SCHEMA_ACTION or args.action == EXAMPLE_ACTION:
        if args.template_path is None and os.getenv(ENV_TEMPLATE) is not None:
            args.template_path = os.getenv(ENV_TEMPLATE).split()

        if len(args.template_names) == 0:
            print "Please specify template names on command line"
            exit(1)

        if args.template_path is None:
            print "Please specify template path using -tp on command line or set an environment variable %s" % (ENV_TEMPLATE)
            exit(1)

    levistate = Levistate(args, args.action)
    levistate.run()


def get_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    sub_parser = parser.add_subparsers(dest='action')

    create_parser = sub_parser.add_parser(CREATE_ACTION)
    add_parser_arguments(create_parser)

    revert_parser = sub_parser.add_parser(REVERT_ACTION)
    add_parser_arguments(revert_parser)

    validate_parser = sub_parser.add_parser(VALIDATE_ACTION)
    add_parser_arguments(validate_parser)

    template_parser = sub_parser.add_parser(TEMPLATE_ACTION)
    template_sub_parser = template_parser.add_subparsers(dest='templateAction')
    list_parser = template_sub_parser.add_parser(LIST_ACTION)
    add_template_path_parser_argument(list_parser)

    template_sub_parser.add_parser(UPGRADE_TEMPLATE_ACTION)

    schema_parser = sub_parser.add_parser(SCHEMA_ACTION)
    add_template_parser_arguments(schema_parser)

    example_parser = sub_parser.add_parser(EXAMPLE_ACTION)
    add_template_parser_arguments(example_parser)

    sub_parser.add_parser(VERSION_ACTION)

    sub_parser.add_parser(HELP_ACTION)

    return parser


def add_template_path_parser_argument(parser):
    parser.add_argument('-tp', '--template-path', dest='template_path',
                        action='append', required=False,
                        default=None,
                        help='Path containing template files. Can also set using environment variable %s' % (ENV_TEMPLATE))
    parser.add_argument('--version', dest='version',
                        action='store_true', required=False,
                        help='Displays version information')


def add_template_parser_arguments(parser):
    add_template_path_parser_argument(parser)

    parser.add_argument('template_names',
                        nargs="*",
                        help='Template names')


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
                        default=os.getenv(ENV_VSD_USERNAME,
                                          DEFAULT_VSD_USERNAME),
                        help='Username for VSD. Can also set using environment variable %s' % (ENV_VSD_USERNAME))
    parser.add_argument('-p', '--password', dest='password',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_PASSWORD,
                                          DEFAULT_VSD_PASSWORD),
                        help='Password for VSD. Can also set using environment variable %s' % (ENV_VSD_PASSWORD))
    parser.add_argument('-e', '--enterprise', dest='enterprise',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_ENTERPRISE,
                                          DEFAULT_VSD_ENTERPRISE),
                        help='Enterprise for VSD. Can also set using environment variable %s' % (ENV_VSD_ENTERPRISE))
    parser.add_argument('--debug', dest='debug',
                        action='store_true', required=False,
                        help='Output in debug mode')
    parser.add_argument('-lf', '--log-file', dest='log_file',
                        action='store', required=False,
                        default=os.getenv(ENV_LOG_FILE, ""),
                        help='Write logs to specified file. Can also set using environment variable %s' % (ENV_LOG_FILE))
    parser.add_argument('-ll', '--log-level', dest='log_level',
                        action='store', required=False,
                        default=os.getenv(ENV_LOG_LEVEL, DEFAULT_LOG_LEVEL),
                        help='Specify log level (%s) Can also set using environment variable %s' % (", ".join(LOG_LEVEL_STRS), ENV_LOG_LEVEL))
    parser.add_argument('datafiles', help="Optional datafile",
                        nargs='*', default=None)


class CustomLogHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        if stream is not None:
            super(CustomLogHandler, self).__init__(stream)
        else:
            super(CustomLogHandler, self).__init__()

    def emit(self, record):
        saved_message = record.msg
        messages = record.msg.split('\n')
        for message in messages:
            record.msg = message
            super(CustomLogHandler, self).emit(record)
        record.msg = saved_message


class Levistate(object):

    def __init__(self, args, action):
        self.args = args
        self.template_data = list()
        self.action = action

    def setup_logging(self):
        OUTPUT_LEVEL_NUM = logging.ERROR + 5
        logging.addLevelName(OUTPUT_LEVEL_NUM, "OUTPUT")

        def output(self, msg, *args, **kwargs):
            if self.isEnabledFor(OUTPUT_LEVEL_NUM):
                self._log(OUTPUT_LEVEL_NUM, msg, args, **kwargs)
        logging.Logger.output = output

        log_level = self.args.log_level.upper()
        if log_level not in LOG_LEVEL_STRS:
            print "Invalid log level: " + str(log_level)
            exit(1)

        if log_level == "API":
            bambou_logger = logging.getLogger("bambou")
            bambou_logger.setLevel(logging.DEBUG)

            self.logger = logging.getLogger("bambou.levistate")
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger = logging.getLogger("levistate")
            level = logging.getLevelName(log_level)
            self.logger.setLevel(level)

        log_formatter = logging.Formatter("%(levelname)-6s: %(message)s")

        if self.args.log_file:
            file_path = self.args.log_file
            if not file_path.startswith("/") and os.path.isdir(LOGS_DIR):
                file_path = os.path.join(LOGS_DIR, file_path)

            file = open(file_path, "w")
            file_handler = CustomLogHandler(file)
            file_handler.setFormatter(log_formatter)
            if log_level == "API":
                bambou_logger.addHandler(file_handler)
            else:
                self.logger.addHandler(file_handler)

        if self.args.debug:
            debug_handler = CustomLogHandler()
            debug_handler.setFormatter(log_formatter)
            if log_level == "API":
                bambou_logger.addHandler(debug_handler)
            else:
                self.logger.addHandler(debug_handler)
        else:
            output_handler = logging.StreamHandler()
            output_handler.setLevel(OUTPUT_LEVEL_NUM)
            self.logger.addHandler(output_handler)

    def run(self):

        if (self.action == TEMPLATE_ACTION and
                self.args.templateAction == UPGRADE_TEMPLATE_ACTION):
            self.upgrade_templates()
            return

        self.setup_logging()

        self.setup_template_store()
        if self.list_info():
            return
        self.setup_vsd_writer()
        self.parse_user_data()
        self.parse_extra_vars()

        had_error = False
        error_output = ""
        try:
            self.apply_templates()
        except LevistateError as e:
            error_output = e.get_display_string()
            self.logger.error(error_output)
            self.logger.exception("Stack trace")
            had_error = True
        except Exception as e:
            error_output = str(e)
            self.logger.exception(error_output)
            had_error = True

        if had_error:
            print ""
            print "Error"
            print "-----"
            print error_output
            exit(1)

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

        if (self.action == TEMPLATE_ACTION and
                self.args.templateAction == LIST_ACTION):
            template_names = self.store.get_template_names()
            print "\n".join(template_names)
            return True

        if self.action == SCHEMA_ACTION:
            for template_name in self.args.template_names:
                template = self.store.get_template(template_name)
                print template.get_schema()
            return True

        if self.action == EXAMPLE_ACTION:
            for template_name in self.args.template_names:
                template = self.store.get_template(template_name)
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
        parser = UserDataParser()
        if self.args.datafiles is not None and len(self.args.datafiles) > 0:
            for datafile in self.args.datafiles:
                if datafile is not None:
                    if not os.path.exists(datafile):
                        if self.args.data_path is not None:
                            datafile = os.path.join(self.args.data_path[0],
                                                    datafile)
                        if not os.path.exists(datafile):
                            print("Could not find user data file %s if "
                                  "using the docker container please make "
                                  "sure it is accessible to the docker" %
                                  (datafile))
                            exit(1)
                    parser.read_data(datafile)
        else:
            if self.args.data_path is None or len(self.args.data_path) == 0:
                print("Please specify a user data file or path")
                exit(1)
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

    def download_and_extract(self, url, dirName):
        if not os.path.isdir(dirName):
            os.mkdir(dirName)
        os.chdir(dirName)

        filename = wget.download(url)
        tfile = tarfile.TarFile(filename)
        tfile.extractall()
        os.remove(tfile.name)

    def upgrade_templates(self):
        if (self.action == TEMPLATE_ACTION and
                self.args.templateAction == UPGRADE_TEMPLATE_ACTION):
            print("Upgrading templates...")
            dirName = TEMPLATE_DIR
            url = TEMPLATE_TAR_LOCATION
            self.download_and_extract(url, dirName)

            dirName = SPECIFICATION_DIR
            url = VSD_SPECIFICAIONS_LOCATION
            self.download_and_extract(url, dirName)


if __name__ == "__main__":
    main()
