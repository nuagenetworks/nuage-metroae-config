
from nuage_metroae_config.configuration import Configuration
from nuage_metroae_config.es_reader import EsReader
from nuage_metroae_config.query import Query
from nuage_metroae_config.template import TemplateStore
from nuage_metroae_config.user_data_parser import UserDataParser
from nuage_metroae_config.vsd_writer import SOFTWARE_TYPE, VsdWriter
import urllib3

urllib3.disable_warnings()


class NuageMetroaeConfig(object):
    ENGINE_VERSION = "1.0"
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self.template_store = None
        self.spec_path = None
        self.vsd_writers = dict()
        self.current_vsd_writer = None
        self.es_readers = dict()
        self.current_reader = None
        self.configs = dict()
        self.current_config = None

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
            if version is not None:
                vsd_writer.set_software_version(version["software_version"])

        name = self._add_object_with_alias(self.vsd_writers, vsd_writer, alias)
        self.current_vsd_writer = vsd_writer
        self.current_reader = vsd_writer
        return name

    def switch_vsd_connection(self, alias):
        vsd_writer = self._get_vsd_writer(alias)
        self.current_vsd_writer = vsd_writer
        self.current_reader = vsd_writer

    def setup_es_connection(self, address, port=9200, alias=None):
        es_reader = EsReader()
        es_reader.set_session_params(address, port)

        name = self._add_object_with_alias(self.es_readers, es_reader, alias)
        self.current_reader = es_reader
        return name

    def switch_es_connection(self, alias):
        es_reader = self._get_es_reader(alias)
        self.current_reader = es_reader

    def create_config(self, alias=None, software_version=None):
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making a configuration")

        config = Configuration(self.template_store)
        if software_version is not None:
            config.set_software_version(SOFTWARE_TYPE, software_version)

        name = self._add_object_with_alias(self.configs, config, alias)
        self.current_config = config
        return name

    def switch_config(self, alias):
        config = self._get_config(alias)
        self.current_config = config

    def add_to_config(self, template_name, **variable_dict):
        if self.current_config is None:
            self.create_config()

        config = self.current_config
        config.add_template_data(template_name, **variable_dict)

    def add_to_config_from_file(self, user_data_file_or_path):
        if self.current_config is None:
            self.create_config()

        config = self.current_config
        parser = UserDataParser()
        parser.read_data(user_data_file_or_path)
        pairs = parser.get_template_name_data_pairs()
        for pair in pairs:
            template_name = pair[0]
            template_data = pair[1]
            config.add_template_data(template_name, **template_data)

    def apply_config(self):
        config, vsd_writer = self._get_current_config_and_writer()
        self._set_config_version(config, vsd_writer)

        vsd_writer.set_validate_only(True)
        config.apply(vsd_writer)
        vsd_writer.set_validate_only(False)
        config.apply(vsd_writer)

    def update_config(self):
        config, vsd_writer = self._get_current_config_and_writer()
        self._set_config_version(config, vsd_writer)

        vsd_writer.set_validate_only(True)
        config.update(vsd_writer)
        vsd_writer.set_validate_only(False)
        config.update(vsd_writer)

    def revert_config(self):
        config, vsd_writer = self._get_current_config_and_writer()
        self._set_config_version(config, vsd_writer)

        vsd_writer.set_validate_only(True)
        config.revert(vsd_writer)
        vsd_writer.set_validate_only(False)
        config.revert(vsd_writer)

    def validate_config(self):
        config, vsd_writer = self._get_current_config_and_writer()
        self._set_config_version(config, vsd_writer)

        vsd_writer.set_validate_only(True)
        config.apply(vsd_writer)
        vsd_writer.set_validate_only(False)

    def perform_query(self, query, **query_variables):
        reader = self.current_reader
        if reader is None:
            raise Exception("No VSD or ES connection has been made")

        query = Query()
        query.set_reader(reader)
        self._register_query_readers(query)

        results = query.execute(query, **query_variables)
        return results

    def perform_query_from_file(self, query_file, **query_variables):
        reader = self.current_reader
        if reader is None:
            raise Exception("No VSD or ES connection has been made")

        query = Query()
        query.set_reader(reader)
        self._register_query_readers(query)

        query.add_query_file(query_file)
        results = query.execute(None, **query_variables)
        return results

    def get_template_names(self, software_version=None):
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making template operations")
        template_names = self.template_store.get_template_names(
            SOFTWARE_TYPE, software_version)

        return template_names

    def get_template_documentation(self, template_name, software_version=None):
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making template operations")
        template = self._get_template(template_name,
                                      SOFTWARE_TYPE,
                                      software_version)

        return template.get_documentation()

    def get_template_example(self, template_name, software_version=None):
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making template operations")
        template = self._get_template(template_name,
                                      SOFTWARE_TYPE,
                                      software_version)

        return template.get_example()

    def get_template_schema(self, template_name, software_version=None):
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making template operations")
        template = self._get_template(template_name,
                                      SOFTWARE_TYPE,
                                      software_version)

        return template.get_schema()

    def _add_object_with_alias(self, store_dict, obj, alias=None):
        if alias is None:
            index = 1
            while ("alias-" + str(index)) in store_dict:
                index += 1
            name = "alias-" + str(index)
            store_dict[name] = obj
            return name
        else:
            store_dict[alias] = obj
            return alias

    def _get_config(self, alias):
        if self.current_config is None:
            raise Exception("No configuration has been created")

        if alias not in self.configs:
            raise Exception("No config of alias: " + alias)

        config = self.configs[alias]
        return config

    def _get_vsd_writer(self, alias):
        if self.current_vsd_writer not in self.vsd_writers:
            raise Exception("No VSD connection of alias: " + alias)

        vsd_writer = self.vsd_writers[alias]
        return vsd_writer

    def _get_current_config_and_writer(self):
        config = self.current_config
        if config is None:
            raise Exception("No configuration has been created")
        vsd_writer = self.current_vsd_writer
        if vsd_writer is None:
            raise Exception("No VSD connection has been made")

        return (config, vsd_writer)

    def _set_config_version(self, config, vsd_writer):
        if vsd_writer.robot_software_version is not None:
            software_version = vsd_writer.robot_software_version[
                "software_version"]
            config.set_software_version(SOFTWARE_TYPE, software_version)

    def _get_es_reader(self, alias):
        if alias not in self.es_readers:
            raise Exception("No ES connection of alias: " + alias)

        es_reader = self.es_readers[alias]
        return es_reader

    def _register_query_readers(self, query):
        if self.spec_path is not None:
            vsd_writer = VsdWriter()
            vsd_writer.add_api_specification_path(self.spec_path)
            query.register_reader("vsd", vsd_writer)

        es_reader = EsReader()
        query.register_reader("es", es_reader)

    def _get_template(self, template_name, software_version=None):
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making template operations")
        template = self.template_store.get_template(template_name,
                                                    SOFTWARE_TYPE,
                                                    software_version)
        return template
