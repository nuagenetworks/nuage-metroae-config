import argparse
from configuration import Configuration
from template import TemplateStore
from vsd_writer import DeviceWriterError, VsdWriter
# import vspk.v5_0 as vspk

DEFAULT_SPEC_PATH = "vsd-api-specifications"
DEFAULT_TEMPLATE_PATH = "templates"
DEFAULT_VSD_USERNAME = 'csproot'
DEFAULT_VSD_PASSWORD = 'csproot'
DEFAULT_VSD_ENTERPRISE = 'csp'
DEFAULT_URL = 'https://localhost:8080'


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
    parser = argparse.ArgumentParser(
        description='Command-line tool for running template commands')
    parser.add_argument('-tp', '--template-path', dest='template_path',
                        action='store', required=False,
                        default=DEFAULT_TEMPLATE_PATH,
                        help='Path containing template files')
    parser.add_argument('-sp', '--spec-path', dest='spec_path',
                        action='store', required=False,
                        default=DEFAULT_SPEC_PATH,
                        help='Path containing object specifications')
    parser.add_argument('-t', '--template', dest='template_name',
                        action='store', required=False,
                        default=None,
                        help='Template name')
    parser.add_argument('-d', '--data', dest='data',
                        action='append', required=False,
                        help='Specify extra variable as key=value')
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
    parser.add_argument('-r', '--revert', dest='revert',
                        action='store_true', required=False,
                        help='Revert (delete) templates instead of applying')

    return parser.parse_args()


class Levistate(object):

    def __init__(self, args):
        self.args = args
        self.template_data = {}

    def run(self):

        self.parse_extra_vars()
        self.setup_vsd_writer()
        self.setup_template_store()

        try:
            self.apply_template(self.args.template_name, self.template_data)
        except DeviceWriterError as e:
            self.writer.log_error(str(e))
        except Exception as e:
            self.writer.log_error(str(e))

        print self.writer.get_logs()

    def parse_extra_vars(self):
        if self.args.data is not None:
            for data in self.args.data:
                for var in data.split(','):
                    key_value_pair = var.split('=')
                    if len(key_value_pair) != 2:
                        raise Exception("Invalid extra-vars argument, must "
                                        "be key=value format: " + var)
                    key = key_value_pair[0]
                    value = key_value_pair[1]
                    self.template_data[key] = value

    def setup_vsd_writer(self):
        self.writer = VsdWriter()
        self.writer.read_api_specifications(self.args.spec_path)
        self.writer.set_session_params(self.args.vsd_url)

    def setup_template_store(self):
        self.store = TemplateStore()
        self.store.read_templates(self.args.template_path)

    def apply_template(self, template_name, template_data):
        config = Configuration(self.store)
        config.add_template_data(template_name, **template_data)
        config.apply(self.writer)
        print str(config.root_action)

    #
    # Old prototype code
    #

    # def run(self):
    #     try:
    #         self.start_vsd_session()

    #         if self.args.revert:
    #             self.revert_acl_template(
    #                 enterprise_name='demo_ent',
    #                 domain_name='demo_domain_1',
    #                 policy_name='demo_policy_1')
    #             self.revert_domain_template(
    #                 enterprise_name='demo_ent',
    #                 domain_name='demo_domain_1')
    #             self.revert_enterprise_template(enterprise_name='demo_ent')
    #         else:
    #             self.apply_enterprise_template(enterprise_name='demo_ent',
    #                                            description='Demo enterprise')
    #             self.apply_domain_template(
    #                 enterprise_name='demo_ent',
    #                 domain_name='demo_domain_1',
    #                 description='This is a demo domain')
    #             self.apply_acl_template(
    #                 enterprise_name='demo_ent',
    #                 domain_name='demo_domain_1',
    #                 policy_name='demo_policy_1',
    #                 description='This is a demo policy',
    #                 protocol='6',
    #                 sourcePort='*',
    #                 destinationPort='80',
    #                 action='FORWARD',
    #                 etherType='*')

    #     except DeviceWriterError as e:
    #         self.vsd_writer.log_error(str(e))
    #     except Exception as e:
    #         self.vsd_writer.log_error(str(e))

    #     self.stop_vsd_session()
    #     print ""
    #     print self.vsd_writer.get_logs()

    def start_vsd_session(self):
        self.vsd_writer.read_api_specifications(self.args.spec_path)
        self.vsd_writer.set_session_params(self.args.vsd_url)
        self.vsd_writer.start_session()

    def stop_vsd_session(self):
        self.vsd_writer.stop_session()

    def apply_enterprise_template(self, **kwargs):
        print "Applying enterprise template: %s" % kwargs
        context = self.vsd_writer.create_object("Enterprise")
        context = self.vsd_writer.set_values(context,
                                             name=kwargs['enterprise_name'],
                                             description=kwargs['description'])

    def revert_enterprise_template(self, **kwargs):
        print "Reverting enterprise template: %s" % kwargs
        context = self.vsd_writer.select_object("Enterprise", "name",
                                                kwargs['enterprise_name'])
        context = self.vsd_writer.delete_object(context)

    def apply_domain_template(self, **kwargs):
        print "Applying domain template: %s" % kwargs
        ent_context = self.vsd_writer.select_object("Enterprise", "name",
                                                    kwargs['enterprise_name'])
        context = self.vsd_writer.create_object("DomainTemplate", ent_context)
        template_name = "template-" + kwargs['domain_name']
        template_descr = "Template for domain " + kwargs['domain_name']
        context = self.vsd_writer.set_values(context,
                                             name=template_name,
                                             description=template_descr)
        template_id = self.vsd_writer.get_value('id', context)
        context = self.vsd_writer.create_object("Domain", ent_context)
        context = self.vsd_writer.set_values(context,
                                             name=kwargs['domain_name'],
                                             templateID=template_id,
                                             description=kwargs['description'])

    def revert_domain_template(self, **kwargs):
        print "Reverting domain template: %s" % kwargs
        ent_context = self.vsd_writer.select_object("Enterprise", "name",
                                                    kwargs['enterprise_name'])
        context = self.vsd_writer.select_object("Domain", "name",
                                                kwargs['domain_name'],
                                                ent_context)
        context = self.vsd_writer.delete_object(context)
        template_name = "template-" + kwargs['domain_name']
        context = self.vsd_writer.select_object("DomainTemplate", "name",
                                                template_name, ent_context)
        context = self.vsd_writer.delete_object(context)

    def apply_acl_template(self, **kwargs):
        print "Applying acl template: %s" % kwargs
        context = self.vsd_writer.select_object("Enterprise", "name",
                                                    kwargs['enterprise_name'])
        dom_context = self.vsd_writer.select_object("Domain", "name",
                                                    kwargs['domain_name'],
                                                    context)

        context = self.vsd_writer.create_object("IngressACLTemplate",
                                                dom_context)
        context = self.vsd_writer.set_values(context,
                                             name=kwargs['policy_name'],
                                             description=kwargs['description'])
        context = self.vsd_writer.create_object("IngressACLEntryTemplate",
                                                context)
        context = self.vsd_writer.set_values(context,
                                             dscp='*',
                                             # protocol=kwargs['protocol'],
                                             # sourcePort=kwargs['sourcePort'],
                                             # destinationPort=kwargs['destinationPort'],
                                             locationType='ANY',
                                             action=kwargs['action'],
                                             etherType=kwargs['etherType'])
        context = self.vsd_writer.create_object("EgressACLTemplate",
                                                dom_context)
        context = self.vsd_writer.set_values(context,
                                             name=kwargs['policy_name'],
                                             description=kwargs['description'])
        context = self.vsd_writer.create_object("EgressACLEntryTemplate",
                                                context)
        context = self.vsd_writer.set_values(context,
                                             dscp='*',
                                             # protocol=kwargs['protocol'],
                                             # sourcePort=kwargs['sourcePort'],
                                             # destinationPort=kwargs['destinationPort'],
                                             locationType='ANY',
                                             action=kwargs['action'],
                                             etherType=kwargs['etherType'])

    def revert_acl_template(self, **kwargs):
        print "Reverting subnet template: %s" % kwargs
        context = self.vsd_writer.select_object("Enterprise", "name",
                                                kwargs['enterprise_name'])
        dom_context = self.vsd_writer.select_object("Domain", "name",
                                                    kwargs['domain_name'],
                                                    context)
        context = self.vsd_writer.select_object("EgressACLTemplate", "name",
                                                kwargs['policy_name'],
                                                dom_context)
        context = self.vsd_writer.delete_object(context)
        context = self.vsd_writer.select_object("IngressACLTemplate", "name",
                                                kwargs['policy_name'],
                                                dom_context)
        context = self.vsd_writer.delete_object(context)


if __name__ == "__main__":
    main()
