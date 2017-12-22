import argparse
from vsd_writer import TemplateWriterError, VsdWriter
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
        self.vsd_writer = VsdWriter()

    def run(self):
        try:
            self.start_vsd_session()

            if self.args.revert:
                # self.revert_subnet_template(
                #     enterprise_name='metro-test',
                #     domain_name='demo_domain_1',
                #     subnet_name='demo_subnet_1')
                self.revert_domain_template(
                    enterprise_name='demo_ent',
                    domain_name='demo_domain_1')
                self.revert_enterprise_template(enterprise_name='demo_ent')
            else:
                self.apply_enterprise_template(enterprise_name='demo_ent',
                                               description='Demo enterprise')
                self.apply_domain_template(
                    enterprise_name='demo_ent',
                    domain_name='demo_domain_1',
                    # template_id='3b791e3b-93a5-4d22-b38e-2336aad7132d',
                    description='This is a demo domain')
                # self.apply_subnet_template(
                #     enterprise_name='metro-test',
                #     domain_name='domaintemplate',
                #     subnet_name='subnettemplate',
                #     address='1.1.1.1',
                #     netmask='255.255.255.0',
                #     description='This is a demo subnet template')

        except TemplateWriterError as e:
            self.vsd_writer.log_error(str(e))
        except Exception as e:
            self.vsd_writer.log_error(str(e))

        self.stop_vsd_session()
        print ""
        print self.vsd_writer.get_logs()

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

    def apply_subnet_template(self, **kwargs):
        print "Applying subnet template: %s" % kwargs
        context = self.vsd_writer.select_object("Enterprise", "name",
                                                kwargs['enterprise_name'])
        context = self.vsd_writer.select_object("DomainTemplate", "name",
                                                kwargs['domain_name'], context)
        context = self.vsd_writer.create_object("SubnetTemplate", context)
        context = self.vsd_writer.set_values(context,
                                             name=kwargs['subnet_name'],
                                             description=kwargs['description'],
                                             address=kwargs['address'],
                                             netmask=kwargs['netmask'])

    def revert_subnet_template(self, **kwargs):
        print "Reverting subnet template: %s" % kwargs
        context = self.vsd_writer.select_object("Enterprise", "name",
                                                kwargs['enterprise_name'])
        context = self.vsd_writer.select_object("Domain", "name",
                                                kwargs['domain_name'], context)
        context = self.vsd_writer.select_object("SubnetTemplate", "name",
                                                kwargs['subnet_name'], context)
        context = self.vsd_writer.delete_object(context)


if __name__ == "__main__":
    main()
