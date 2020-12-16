#!/usr/bin/env python

import argparse
import jinja2
import logging
import os
import requests
import sys
import tarfile
import urllib3

from nuage_metroae_config.configuration import Configuration
from nuage_metroae_config.document_template_md import DOCUMENT_README_MD
from nuage_metroae_config.errors import MetroConfigError
from nuage_metroae_config.es_reader import EsReader
from nuage_metroae_config.query import Query
from nuage_metroae_config.template import TemplateStore
from nuage_metroae_config.user_data_parser import UserDataParser
from nuage_metroae_config.vsd_writer import VsdWriter, SOFTWARE_TYPE

# Disables annoying SSL certificate validation warnings
urllib3.disable_warnings()

ENGINE_VERSION = "1.0"

PROG_NAME = "metroae config"
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
ENV_ES_ADDRESS = 'ES_ADDRESS'
ENV_SOFTWARE_VERSION = 'SOFTWARE_VERSION'
ENV_LOG_FILE = 'LOG_FILE'
ENV_LOG_LEVEL = 'LOG_LEVEL'
ENV_VSD_CERTIFICATE = 'VSD_CERTIFICATE'
ENV_VSD_CERTIFICATE_KEY = 'VSD_CERTIFICATE_KEY'
VALIDATE_ACTION = 'validate'
CREATE_ACTION = 'create'
REVERT_ACTION = 'revert'
UPDATE_ACTION = 'update'
QUERY_ACTION = 'query'
LIST_ACTION = 'list'
SCHEMA_ACTION = 'schema'
EXAMPLE_ACTION = 'example'
DOCUMENT_ACTION = 'document'
TEMPLATE_ACTION = 'templates'
EXCEL_ACTION = 'excel'
UPGRADE_TEMPLATE_ACTION = 'update'
VERSION_ACTION = 'version'
HELP_ACTION = 'help'
TEMPLATE_TAR_LOCATION = "https://metroae-config-templates.s3.amazonaws.com/metroae_config.tar"
VSD_SPECIFICAIONS_LOCATION = "https://vsd-api-specifications.s3.us-east-2.amazonaws.com/specifications.tar"
TEMPLATE_DIR = "/metroae_data/standard-templates"
SPECIFICATION_DIR = "/metroae_data/vsd-api-specifications"
DOCUMENTATION_DIR = "/metroae_data/config_documentation"
EXCEL_DIR = "/metroae_data/excel"
EXCEL_FILE_PREFIX = "user_data_form_"
LOGS_DIR = "/metroae_data"
LOG_LEVEL_STRS = ["OUTPUT", "ERROR", "INFO", "DEBUG", "API"]

VERSION_OUTPUT = "MetroAE Config Engine version %s" % ENGINE_VERSION

REQUIRED_FIELDS_ERROR = """Template path or Data path or VSD specification path are not provided.
Please specify template path using -tp on command line or set an environment variable %s
Please specify VSD specification path using -sp on command line or set an environment variable %s""" % (ENV_TEMPLATE, ENV_VSD_SPECIFICATIONS)


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.action == HELP_ACTION:
        print(parser.print_help())
        exit(0)
    elif args.action == VERSION_ACTION or (hasattr(args, "version") and
                                           args.version):
        print(VERSION_OUTPUT)
        exit(0)
    elif args.action == QUERY_ACTION:
        if args.data_path is None and os.getenv(ENV_USER_DATA) is not None:
            args.data_path = os.getenv(ENV_USER_DATA).split()

        if (args.spec_path is None and
                os.getenv(ENV_VSD_SPECIFICATIONS) is not None):
            args.spec_path = os.getenv(ENV_VSD_SPECIFICATIONS).split()

        if args.spec_path is None:
            print(REQUIRED_FIELDS_ERROR)
            exit(1)

    elif (args.action in [VALIDATE_ACTION, CREATE_ACTION, UPDATE_ACTION,
                          REVERT_ACTION]):
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
            print(REQUIRED_FIELDS_ERROR)
            exit(1)

    elif args.action == TEMPLATE_ACTION and args.templateAction == LIST_ACTION:
        if args.template_path is None and os.getenv(ENV_TEMPLATE) is not None:
            args.template_path = os.getenv(ENV_TEMPLATE).split()

        if args.template_path is None:
            print("Please specify template path using -tp on command line or set an environment variable %s" % (ENV_TEMPLATE))
            exit(1)

    elif args.action in [SCHEMA_ACTION, EXAMPLE_ACTION, DOCUMENT_ACTION,
                         EXCEL_ACTION]:
        if args.template_path is None and os.getenv(ENV_TEMPLATE) is not None:
            args.template_path = os.getenv(ENV_TEMPLATE).split()

        if args.action != DOCUMENT_ACTION and len(args.template_names) == 0:
            print("Please specify template names on command line")
            exit(1)

        if args.template_path is None:
            print("Please specify template path using -tp on command line or set an environment variable %s" % (ENV_TEMPLATE))
            exit(1)

    metro_config = MetroConfig(args, args.action)
    metro_config.run()


def get_parser():
    parser = argparse.ArgumentParser(prog=PROG_NAME)

    sub_parser = parser.add_subparsers(dest='action')

    create_parser = sub_parser.add_parser(CREATE_ACTION)
    add_parser_arguments(create_parser)

    revert_parser = sub_parser.add_parser(REVERT_ACTION)
    add_parser_arguments(revert_parser)

    validate_parser = sub_parser.add_parser(VALIDATE_ACTION)
    add_parser_arguments(validate_parser)

    update_parser = sub_parser.add_parser(UPDATE_ACTION)
    add_parser_arguments(update_parser)

    query_parser = sub_parser.add_parser(QUERY_ACTION)
    add_parser_arguments(query_parser)

    template_parser = sub_parser.add_parser(TEMPLATE_ACTION)
    template_sub_parser = template_parser.add_subparsers(dest='templateAction')
    list_parser = template_sub_parser.add_parser(LIST_ACTION)
    add_template_path_parser_argument(list_parser)

    template_sub_parser.add_parser(UPGRADE_TEMPLATE_ACTION)

    schema_parser = sub_parser.add_parser(SCHEMA_ACTION)
    add_template_parser_arguments(schema_parser)

    example_parser = sub_parser.add_parser(EXAMPLE_ACTION)
    add_template_parser_arguments(example_parser)

    document_parser = sub_parser.add_parser(DOCUMENT_ACTION)
    add_template_parser_arguments(document_parser)

    excel_parser = sub_parser.add_parser(EXCEL_ACTION)
    add_template_parser_arguments(excel_parser)

    sub_parser.add_parser(VERSION_ACTION)

    sub_parser.add_parser(HELP_ACTION)

    return parser


def add_template_path_parser_argument(parser):
    parser.add_argument('-tp', '--template_path', dest='template_path',
                        action='append', required=False,
                        default=None,
                        help='Path containing template files. Can also set using environment variable %s' % (ENV_TEMPLATE))
    parser.add_argument('--version', dest='version',
                        action='store_true', required=False,
                        help='Displays version information')
    parser.add_argument('-sv', '--software_version', dest='software_version',
                        action='store', required=False,
                        default=os.getenv(ENV_SOFTWARE_VERSION, None),
                        help='Override software version for VSD. Can also set using environment variable %s' % (ENV_SOFTWARE_VERSION))


def add_template_parser_arguments(parser):
    add_template_path_parser_argument(parser)

    parser.add_argument('template_names',
                        nargs="*",
                        help='Template names')


def add_parser_arguments(parser):
    add_template_path_parser_argument(parser)
    parser.add_argument('-sp', '--spec_path', dest='spec_path',
                        action='append', required=False,
                        help='Path containing object specifications. Can also set using environment variable %s' % (ENV_VSD_SPECIFICATIONS))
    parser.add_argument('-dp', '--data_path', dest='data_path',
                        action='append', required=False,
                        default=None,
                        help='Path containing user data. Can also set using environment variable %s' % (ENV_USER_DATA))
    parser.add_argument('-d', '--data', dest='data',
                        action='append', required=False,
                        help='Specify user data as key=value')
    parser.add_argument('-v', '--vsd_url', dest='vsd_url',
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
    parser.add_argument('-c', '--certificate', dest='certificate',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_CERTIFICATE,
                                          None),
                        help='Certificate used to authenticate with VSD. Can also set using environment variable %s' % (ENV_VSD_CERTIFICATE))
    parser.add_argument('-ck', '--certificate_key', dest='certificate_key',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_CERTIFICATE_KEY,
                                          None),
                        help='Certificate Key used to authenticate with VSD. Can also set using environment variable %s' % (ENV_VSD_CERTIFICATE))

    parser.add_argument('-e', '--enterprise', dest='enterprise',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_ENTERPRISE,
                                          DEFAULT_VSD_ENTERPRISE),
                        help='Enterprise for VSD. Can also set using environment variable %s' % (ENV_VSD_ENTERPRISE))
    parser.add_argument('-es', '--es_address', dest='es_address',
                        action='store', required=False,
                        default=os.getenv(ENV_ES_ADDRESS, None),
                        help='Address with optional ":<port>" for ElasticSearch. Can also set using environment variable %s' % (ENV_ES_ADDRESS))
    parser.add_argument('-q', '--query', dest='query',
                        action='store', required=False,
                        help='Query string to perform in query action'),
    parser.add_argument('--debug', dest='debug',
                        action='store_true', required=False,
                        help='Output in debug mode')
    parser.add_argument('-lf', '--log_file', dest='log_file',
                        action='store', required=False,
                        default=os.getenv(ENV_LOG_FILE, ""),
                        help='Write logs to specified file. Can also set using environment variable %s' % (ENV_LOG_FILE))
    parser.add_argument('-ll', '--log_level', dest='log_level',
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


class MetroConfig(object):

    def __init__(self, args, action):
        self.args = args
        self.template_data = list()
        self.query_files = list()
        self.query_variables = dict()
        self.action = action
        self.device_version = None
        self.excel_parser = None

    def setup_logging(self):
        if "log_level" not in self.args:
            return

        OUTPUT_LEVEL_NUM = logging.ERROR + 5
        logging.addLevelName(OUTPUT_LEVEL_NUM, "OUTPUT")

        def output(self, msg, *args, **kwargs):
            if self.isEnabledFor(OUTPUT_LEVEL_NUM):
                self._log(OUTPUT_LEVEL_NUM, msg, args, **kwargs)

        logging.Logger.output = output

        log_level = self.args.log_level.upper()
        if log_level not in LOG_LEVEL_STRS:
            print("Invalid log level: " + str(log_level))
            exit(1)

        if log_level == "API":
            bambou_logger = logging.getLogger("bambou")
            bambou_logger.setLevel(logging.DEBUG)

            self.logger = logging.getLogger("bambou.nuage_metroae_config")
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger = logging.getLogger("nuage_metroae_config")
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
            output_handler = logging.StreamHandler(sys.stdout)
            output_handler.setLevel(OUTPUT_LEVEL_NUM)
            self.logger.addHandler(output_handler)

    def run(self):

        if (self.action == TEMPLATE_ACTION and
                self.args.templateAction == UPGRADE_TEMPLATE_ACTION):
            self.upgrade_templates()
            return

        self.setup_logging()

        if self.action == QUERY_ACTION:
            self.setup_reader()
            self.parse_extra_vars()
            if self.args.query is None:
                self.parse_user_data()
        else:
            self.setup_template_store()
            if self.list_info():
                return
            self.setup_vsd_writer()
            self.parse_user_data()
            self.parse_extra_vars()

        had_error = False
        error_output = ""
        try:
            if self.action == QUERY_ACTION:
                self.perform_query()
            else:
                self.apply_templates()
        except MetroConfigError as e:
            error_output = e.get_display_string()
            self.logger.error(error_output)
            self.logger.exception("Stack trace")
            had_error = True
        except Exception as e:
            error_output = str(e)
            self.logger.exception(error_output)
            had_error = True

        if had_error:
            print("")
            print("Error")
            print("-----")
            print(error_output)
            exit(1)
        else:
            if self.action == VALIDATE_ACTION:
                print(">>> All actions valid")
            else:
                print(">>> All actions successfully applied")

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
                    if self.action == QUERY_ACTION:
                        self.query_variables[key] = value
                    else:
                        template_data[key] = value

            if self.action != QUERY_ACTION:
                self.template_data.append((self.args.template_name,
                                           template_data))

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
            template_names = self.store.get_template_names(
                self.get_software_type(),
                self.get_software_version())
            print("\n".join(template_names))
            return True

        if self.action == SCHEMA_ACTION:
            for template_name in self.args.template_names:
                template = self.store.get_template(template_name,
                                                   self.get_software_type(),
                                                   self.get_software_version())
                print(template.get_schema())
            return True

        if self.action == EXAMPLE_ACTION:
            for template_name in self.args.template_names:
                template = self.store.get_template(template_name,
                                                   self.get_software_type(),
                                                   self.get_software_version())
                print(template.get_example())
            return True

        if self.action == DOCUMENT_ACTION:
            if len(self.args.template_names) == 0:
                self.write_template_documentation()
            else:
                for template_name in self.args.template_names:
                    template = self.store.get_template(
                        template_name,
                        self.get_software_type(),
                        self.get_software_version())
                    print(template.get_documentation())
            return True

        if self.action == EXCEL_ACTION:
            self.write_excel_input_form(self.args.template_names)
            return True

        return False

    def write_template_documentation(self):
        print("Generating documentation")
        if not os.path.exists(DOCUMENTATION_DIR):
            os.makedirs(DOCUMENTATION_DIR)
        template_names = self.store.get_template_names(
            self.get_software_type(),
            self.get_software_version())

        template_info = list()

        for template_name in template_names:
            template = self.store.get_template(
                template_name,
                self.get_software_type(),
                self.get_software_version())

            doc_file = template.get_doc_file_name()
            if doc_file is not None:
                template_info.append({
                    "name": template_name,
                    "file": doc_file})

                full_path = os.path.join(DOCUMENTATION_DIR, doc_file)
                print("Writing %s documentation to %s" % (template_name,
                                                          full_path))
                doc_text = template.get_documentation()
                with open(full_path, "w") as f:
                    f.write(doc_text)

        self.write_documentation_readme(template_info)

    def write_documentation_readme(self, template_info):
        template = jinja2.Template(
            DOCUMENT_README_MD,
            autoescape=False,
            undefined=jinja2.StrictUndefined)

        full_path = os.path.join(DOCUMENTATION_DIR, "README.md")

        readme = template.render(**{"template_info": template_info})

        with open(full_path, "w") as f:
            f.write(readme)

    def write_excel_input_form(self, template_names):
        excel = self.create_excel_generator(template_names)

        excel_file_name = self.find_new_excel_file_name()

        excel.write_workbook(excel_file_name)

        print(">>> Successfully created Excel form for %d templates: %s" % (
            len(template_names), excel_file_name))

    def create_excel_generator(self, template_names):
        try:
            from excel_template_generator import ExcelTemplateGenerator
        except ImportError:
            print("Could not import excel libraries.  Requires: "
                  "excel_template_generator and openpyxl")
            exit(1)

        excel = ExcelTemplateGenerator()
        excel.settings["schema_order"] = template_names
        excel.settings["show_version"] = False
        excel.settings["row_sections_present"] = False
        excel.settings["num_list_entries"] = 100
        excel.settings["row_label_color"] = "8888FF"
        excel.settings["row_label_text_color"] = "FFFFFF"

        schemas = self.get_schemas(template_names)
        excel.settings["schemas"] = schemas

        return excel

    def get_schemas(self, template_names):
        schemas = dict()
        for name in template_names:
            template = self.store.get_template(
                name,
                self.get_software_type(),
                self.get_software_version())
            schema = template.get_schema()
            schemas[name] = schema

        return schemas

    def find_new_excel_file_name(self):
        file_num_suffix = 1

        if not os.path.isdir(EXCEL_DIR):
            os.mkdir(EXCEL_DIR)

        excel_file_name = os.path.join(EXCEL_DIR, EXCEL_FILE_PREFIX +
                                       str(file_num_suffix) + ".xlsx")
        while os.path.isfile(excel_file_name):
            file_num_suffix += 1
            excel_file_name = os.path.join(EXCEL_DIR, EXCEL_FILE_PREFIX +
                                           str(file_num_suffix) + ".xlsx")

        return excel_file_name

    def read_and_parse_excel(self, excel_file):
        parser = self.create_excel_parser()

        from excel_parser import ExcelParseError
        try:
            data = parser.read_xlsx(excel_file)
        except ExcelParseError:
            print("Error")
            print("-----")
            print("In Excel file: " + excel_file)
            for error in parser.errors:
                print("%s %s | %s" % (error["schema_title"], error["position"],
                                      error["message"]))
            exit(1)

        for template_name, var_set_entries in data.iteritems():
            for var_set in var_set_entries:
                self.template_data.append((template_name, var_set))

    def create_excel_parser(self):
        if self.excel_parser is not None:
            return self.excel_parser

        try:
            from excel_parser import ExcelParser
        except ImportError:
            print("Could not import excel libraries.  Requires: "
                  "excel_parser, json-schema and openpyxl")
            exit(1)

        self.excel_parser = ExcelParser()

        self.excel_parser.settings["use_schema_titles"] = True
        self.excel_parser.settings["row_sections_present"] = False

        template_names = self.store.get_template_names(
            self.get_software_type(),
            self.get_software_version())

        schemas = self.get_schemas(template_names)
        self.excel_parser.settings["schemas"] = schemas

        return self.excel_parser

    def setup_reader(self):
        if self.args.es_address is not None:
            self.setup_es_reader()
        else:
            self.setup_vsd_writer()

    def setup_es_reader(self):
        self.writer = EsReader()
        self.writer.set_logger(self.logger)
        if ":" in self.args.es_address:
            addr_pair = self.args.es_address.split(":")
            address = addr_pair[0]
            port = addr_pair[1]
        else:
            address = self.args.es_address
            port = None

        self.writer.set_session_params(address, port)

    def setup_vsd_writer(self):
        self.writer = VsdWriter()
        self.writer.set_logger(self.logger)
        for path in self.args.spec_path:
            self.writer.read_api_specifications(path)
        self.writer.set_session_params(self.args.vsd_url,
                                       username=self.args.username,
                                       password=self.args.password,
                                       enterprise=self.args.enterprise,
                                       certificate=(self.args.certificate,
                                                    self.args.certificate_key)
                                       )
        if self.device_version is None:
            self.device_version = self.writer.get_version()

        if self.get_software_version() is not None:
            self.writer.set_software_version(self.get_software_version())

    def setup_template_store(self):
        self.store = TemplateStore(ENGINE_VERSION)

        if self.args.software_version is not None:
            self.device_version = {
                "software_version": self.args.software_version,
                "software_type": SOFTWARE_TYPE}

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
                            print(("Could not find user data file %s if "
                                   "using the docker container please make "
                                   "sure it is accessible to the docker" %
                                   (datafile)))
                            exit(1)
                    if self.action == QUERY_ACTION:
                        self.query_files.append(datafile)
                    else:
                        if datafile.endswith(".xlsx"):
                            self.read_and_parse_excel(datafile)
                        else:
                            parser.read_data(datafile)
        else:
            if self.args.data_path is None or len(self.args.data_path) == 0:
                print("Please specify a user data file or path")
                exit(1)
            for path in self.args.data_path:
                if self.action == QUERY_ACTION:
                    self.query_files.append(path)
                else:
                    parser.read_data(path)
        if self.action != QUERY_ACTION:
            self.template_data.extend(parser.get_template_name_data_pairs())

    def apply_templates(self):
        config = Configuration(self.store)
        config.set_software_version(self.get_software_type(),
                                    self.get_software_version())
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
            elif self.action == UPDATE_ACTION:
                config.update(self.writer)
            else:
                config.apply(self.writer)

            self.writer.set_validate_only(False)

            if self.action == VALIDATE_ACTION:
                print(str(config.root_action))

    def perform_query(self):
        query = Query()
        query.set_logger(self.logger)
        query.set_reader(self.writer)
        self.register_query_readers(query)

        if self.args.query is None:
            for file in self.query_files:
                query.add_query_file(file)
        results = query.execute(self.args.query, **self.query_variables)
        self.logger.debug("Query results")
        self.logger.debug(str(results))

    def register_query_readers(self, query):
        vsd_writer = VsdWriter()
        vsd_writer.set_logger(self.logger)
        for path in self.args.spec_path:
            vsd_writer.add_api_specification_path(path)
        query.register_reader("vsd", vsd_writer)

        es_reader = EsReader()
        es_reader.set_logger(self.logger)
        query.register_reader("es", es_reader)

    def get_software_type(self):
        if self.device_version is not None:
            return self.device_version['software_type']
        else:
            return None

    def get_software_version(self):
        if self.device_version is not None:
            return self.device_version['software_version']
        else:
            return None

    def download_and_extract(self, url, dirName):
        if not os.path.isdir(dirName):
            os.mkdir(dirName)
        os.chdir(dirName)

        filename = os.path.basename(url)

        r = requests.get(url, stream=True)

        with open(filename, 'wb') as f:
            for chunk in r:
                f.write(chunk)

        tfile = tarfile.TarFile(filename)
        tfile.extractall()
        os.remove(tfile.name)

    def upgrade_templates(self):
        if (self.action == TEMPLATE_ACTION and
                self.args.templateAction == UPGRADE_TEMPLATE_ACTION):

            print("Updating templates...")
            dirName = TEMPLATE_DIR
            url = TEMPLATE_TAR_LOCATION
            self.download_and_extract(url, dirName)

            dirName = SPECIFICATION_DIR
            url = VSD_SPECIFICAIONS_LOCATION
            self.download_and_extract(url, dirName)


if __name__ == "__main__":
    main()
