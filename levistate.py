import argparse
from configuration import Configuration
from errors import LevistateError
from logger import Logger
from template import TemplateStore
from user_data_parser import UserDataParser
from vsd_writer import VsdWriter
# import vspk.v5_0 as vspk

DEFAULT_VSD_USERNAME = 'csproot'
DEFAULT_VSD_PASSWORD = 'csproot'
DEFAULT_VSD_ENTERPRISE = 'csp'
DEFAULT_URL = 'https://localhost:8080'

DESCRIPTION = """Command-line tool for running template commands.
    See README.md for more."""


def main():
    # For debugging vspk:
    #
    # session = vspk.NUVSDSession(username='csproot',
    #                             password='csproot',
    #                             enterprise='csp',
    #                             api_url='https://localhost:8080')
    # session.start()
    # root = session.user

    args = parse_args()
    levistate = Levistate(args)
    levistate.run()


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-tp', '--template-path', dest='template_path',
                        action='append', required=True,
                        help='Path containing template files')
    parser.add_argument('-sp', '--spec-path', dest='spec_path',
                        action='append', required=False,
                        help='Path containing object specifications')
    parser.add_argument('-dp', '--data-path', dest='data_path',
                        action='append', required=False,
                        help='Path containing user data')
    parser.add_argument('-t', '--template', dest='template_name',
                        action='store', required=False,
                        default=None,
                        help='Template name')
    parser.add_argument('-d', '--data', dest='data',
                        action='append', required=False,
                        help='Specify user data as key=value')
    parser.add_argument('-r', '--revert', dest='revert',
                        action='store_true', required=False,
                        help='Revert (delete) templates instead of applying')
    parser.add_argument('-v', '--vsd-url', dest='vsd_url',
                        action='store', required=False,
                        default=DEFAULT_URL,
                        help='URL to VSD REST API')
    parser.add_argument('-u', '--username', dest='username',
                        action='store', required=False,
                        default=DEFAULT_VSD_USERNAME,
                        help='Username for VSD')
    parser.add_argument('-p', '--password', dest='password',
                        action='store', required=False,
                        default=DEFAULT_VSD_PASSWORD,
                        help='Password for VSD')
    parser.add_argument('-e', '--enterprise', dest='enterprise',
                        action='store', required=False,
                        default=DEFAULT_VSD_ENTERPRISE,
                        help='Enterprise for VSD')
    parser.add_argument('-dr', '--dry-run', dest='dry_run',
                        action='store_true', required=False,
                        help='Perform validation only')
    parser.add_argument('-l', '--list', dest='list',
                        action='store_true', required=False,
                        help='Lists loaded templates')
    parser.add_argument('-s', '--schema', dest='schema',
                        action='store_true', required=False,
                        help='Displays template schema')
    parser.add_argument('-x', '--example', dest='example',
                        action='store_true', required=False,
                        help='Displays template user data example')

    return parser.parse_args()


class Levistate(object):

    def __init__(self, args):
        self.args = args
        self.template_data = list()
        self.logger = Logger()

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
        # except Exception as e:
        #     self.writer.log.error(str(e))
        #     print self.logger.get()
        #     print ""
        #     print "Error"
        #     print "-----"
        #     print str(e)
        #     exit(1)

        # print self.logger.get()

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
                    value = key_value_pair[1]
                    template_data[key] = value

            self.template_data.append((self.template_name, template_data))

    def list_info(self):
        if self.args.list:
            template_names = self.store.get_template_names()
            print "\n".join(template_names)
            return True

        if self.args.schema:
            template = self.store.get_template(self.args.template_name)
            print template.get_schema()
            return True

        if self.args.example:
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

        if self.args.dry_run is True:
            validate_actions = [True]
        else:
            validate_actions = [True, False]

        for validate_only in validate_actions:
            self.writer.set_validate_only(validate_only)
            if self.args.revert is True:
                config.revert(self.writer)
            else:
                config.apply(self.writer)

            self.writer.set_validate_only(False)

        # print str(config.root_action)


if __name__ == "__main__":
    main()
