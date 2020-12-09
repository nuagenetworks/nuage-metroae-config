
from nuage_metroae_config.template import TemplateStore
from nuage_metroae_config.vsd_writer import SOFTWARE_TYPE, VsdWriter


class NuageMetroaeConfig(object):
    ENGINE_VERSION = "1.0"
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self.template_store = None
        self.spec_path = None
        self.vsd_writers = dict()
        self.current_vsd_writer = None

    def setup_config(self, template_path_or_file, vsd_spec_path,
                     vsd_url, username="csproot",
                     password="csproot", enterprise="csp",
                     certificate=None, certificate_key=None,
                     software_version=None):
        self.load_config_templates(template_path_or_file)
        self.set_vsd_spec_path(vsd_spec_path)
        self.setup_vsd_connection(vsd_url, username, password, enterprise,
                                  certificate, certificate_key,
                                  software_version)

    def load_config_templates(self, path_or_file):
        if self.template_store is None:
            self.template_store = TemplateStore(
                NuageMetroaeConfig.ENGINE_VERSION)

        self.template_store.read_templates(path_or_file)

    def clear_config_templates(self):
        self.template_store = None

    def set_vsd_spec_path(self, vsd_spec_path):
        self.spec_path = vsd_spec_path

    def setup_vsd_connection(self, vsd_url, username="csproot",
                             password="csproot", enterprise="csp",
                             certificate=None, certificate_key=None,
                             software_version=None, alias=None):
        if self.spec_path is None:
            raise Exception("'Set VSD Spec Path' keyword must be called before"
                            " making a VSD connection")

        vsd_writer = VsdWriter()
        vsd_writer.read_api_specifications(self.spec_path)
        cert_pair = None
        if certificate is not None or certificate_key is not None:
            if certificate is None or certificate_key is None:
                raise Exception("Both certificate and certificate_key "
                                "parameters must be specified if using "
                                "certificates")
            cert_pair = [certificate, certificate_key]

        vsd_writer.set_session_params(vsd_url, username, password, enterprise,
                                      cert_pair)

        if software_version is not None:
            vsd_writer.robot_software_version = {
                "software_version": software_version,
                "software_type": SOFTWARE_TYPE}
        else:
            version = None
            try:
                version = vsd_writer.get_version()
            except Exception:
                # Warn, could not get software version
                pass
            vsd_writer.robot_software_version = version

        name = self._add_object_with_alias(self.vsd_writers, vsd_writer, alias)
        self.current_vsd_writer = name
        return name

    def switch_vsd_connection(self, alias):
        if alias not in self.vsd_writers:
            raise Exception("No VSD connection of alias: " + alias)

        self.current_vsd_writer = alias

    def _add_object_with_alias(self, store_dict, obj, alias=None):
        if alias is None:
            index = 1
            while ("obj" + str(index)) in store_dict:
                index += 1
            name = "obj" + str(index)
            store_dict[name] = obj
            return name
        else:
            store_dict[alias] = obj
            return alias
