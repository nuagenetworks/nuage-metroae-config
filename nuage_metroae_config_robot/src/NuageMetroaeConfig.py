
from nuage_metroae_config.configuration import Configuration
from nuage_metroae_config.errors import MetroConfigError
from nuage_metroae_config.es_reader import EsReader
from nuage_metroae_config.query import Query
from nuage_metroae_config.template import TemplateStore
from nuage_metroae_config.user_data_parser import UserDataParser
from nuage_metroae_config.vsd_writer import SOFTWARE_TYPE, VsdWriter
from robot.api import logger

import urllib3

urllib3.disable_warnings()


def log_output(msg):
    print(msg)


logger.output = log_output


class NuageMetroaeConfig(object):
    """Library for Nuage MetroAE Config in Robot Framework

    This library allows for the configuration of Nuage Networks VSDs through
    template based configurations.  It also implements the `query tool` that
    allows data to be pulled from a the VSD APIs and ElasticSearch (ES).

    See the documentation for nuage_metroae_config for more information
    [https://github.com/nuagenetworks/nuage-metroae-config|Nuage MetroAE Config]
    """
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
        self.last_query = None

    def setup_config(self, template_path_or_file, vsd_spec_path,
                     vsd_url, username="csproot",
                     password="csproot", enterprise="csp",
                     certificate=None, certificate_key=None,
                     software_version=None):
        """ Setup Config: Sets up everything that is needed to configure a VSD.
        This effectively calls the following in series:
        - Load Config Templates
        - Set VSD Spec Path
        - Setup VSD Connection

        ``template_path_or_file`` Path to the configuration templates or a
                                  single file.  The templates are in a Jinja2
                                  substituted YAML format.  See
                                  [https://github.com/nuagenetworks/nuage-metroae-config|Nuage MetroAE Config]

        ``vsd_spec_path`` The path to the VSD API specifications that are read
                          in and used as the configuration model.  These can be
                          obtained at
                          [https://github.com/nuagenetworks/vsd-api-specifications|VSD API Specs]

        ``vsd_url`` URL to the VSD to be configured.  E.g. https://vsd.example.com:8443

        ``username`` Username on the VSD

        ``password`` Password for the VSD username (can be anything if
                     certificate login is used)

        ``enterprise`` Enterprise (organization) on the VSD

        ``certificiate`` Certificate for login (Replaces username/password)

        ``certificate_key`` Certificate key, must be present if using
                            certificate login

        ``software_version`` Explicitly set the VSD software version for
                             configuration.  If not set, the version will be
                             discovered automatically.  It is recommended not
                             to set this unless it is needed to be overridden.
        """
        self.load_config_templates(template_path_or_file)
        self.set_vsd_spec_path(vsd_spec_path)
        alias = self.setup_vsd_connection(vsd_url, username, password, enterprise,
                                          certificate, certificate_key,
                                          software_version)

        return alias

    def load_config_templates(self, path_or_file):
        """ Load Config Templates: Reads in templates into the internal store

        ``path_or_file`` Path to the configuration templates or a
                         single file.  The templates are in a Jinja2
                         substituted YAML format.  See
                         [https://github.com/nuagenetworks/nuage-metroae-config|Nuage MetroAE Config]
        """
        if self.template_store is None:
            self.template_store = TemplateStore(
                NuageMetroaeConfig.ENGINE_VERSION)

        self.template_store.read_templates(path_or_file)

    def clear_config_templates(self):
        """ Clear Config Templates: Completely clears the internal template store
        """
        self.template_store = None

    def set_vsd_spec_path(self, vsd_spec_path):
        """ Set VSD Spec Path: Sets the path for the VSD API specifications

        ``vsd_spec_path`` The path to the VSD API specifications that are read
                          in and used as the configuration model.  These can be
                          obtained at
                          [https://github.com/nuagenetworks/vsd-api-specifications|VSD API Specs]
        """
        self.spec_path = vsd_spec_path

    def setup_vsd_connection(self, vsd_url, username="csproot",
                             password="csproot", enterprise="csp",
                             certificate=None, certificate_key=None,
                             software_version=None, alias=None):
        """ Setup VSD Connection: Sets up a connection to a VSD.  Requires the VSD API specifications to be provided beforehand.

        ``vsd_url`` URL to the VSD to be configured.  E.g. https://vsd.example.com:8443

        ``username`` Username on the VSD

        ``password`` Password for the VSD username (can be anything if
                     certificate login is used)

        ``enterprise`` Enterprise (organization) on the VSD

        ``certificiate`` Certificate for login (Replaces username/password)

        ``certificate_key`` Certificate key, must be present if using
                            certificate login

        ``software_version`` Explicitly set the VSD software version for
                             configuration.  If not set, the version will be
                             discovered automatically.  It is recommended not
                             to set this unless it is needed to be overridden.

        ``alias`` Provide a handle name for this connection which can be used
                  to switch connections.  This is useful if managing multiple
                  VSDs.  If not specified, a new unique alias is assigned and
                  returned.
        """
        if self.spec_path is None:
            raise Exception("'Set VSD Spec Path' keyword must be called before"
                            " making a VSD connection")

        vsd_writer = VsdWriter()
        vsd_writer.read_api_specifications(self.spec_path)
        vsd_writer.set_logger(logger)
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
        """ Switch VSD Connection: Switches the current VSD connection to a different alias.  This can be used when managing multiple VSD connections.

            ``alias`` The alias of the VSD connection to switch to.  This is
                      returned from `Setup VSD Connection`
        """
        vsd_writer = self._get_vsd_writer(alias)
        self.current_vsd_writer = vsd_writer
        self.current_reader = vsd_writer

    def setup_es_connection(self, address, port=9200, alias=None):
        """ Setup ES Connection: Sets up a connection to an ElasticSearch. This connection supports only queries and not configuration.

        ``address`` Address of the ElasticSearch to query

        ``port`` Port for the ElasticSearch.  Default is 9200

        ``alias`` Provide a handle name for this connection which can be used
                  to switch connections.  This is useful if managing multiple
                  ESs.  If not specified, a new unique alias is assigned and
                  returned.
        """

        es_reader = EsReader()
        es_reader.set_logger(logger)
        es_reader.set_session_params(address, port)

        name = self._add_object_with_alias(self.es_readers, es_reader, alias)
        self.current_reader = es_reader
        return name

    def switch_es_connection(self, alias):
        """ Switch ES Connection: Switches the current ES connection to a different alias.  This can be used when managing multiple ES connections.

            ``alias`` The alias of the ES connection to switch to.  This is
                      returned from `Setup ES Connection`
        """

        es_reader = self._get_es_reader(alias)
        self.current_reader = es_reader

    def new_config(self, alias=None, software_version=None):
        """ New Config: Creates a new configuration where template data can be added.

            ``alias`` Provide a handle name for this config which can be used
                      to switch configurations.  This is useful if managing
                      multiple configs.  If not specified, a new unique alias
                      is assigned and returned.

        """
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making a configuration")

        config = Configuration(self.template_store)
        config.set_logger(logger)
        if software_version is not None:
            config.set_software_version(SOFTWARE_TYPE, software_version)

        name = self._add_object_with_alias(self.configs, config, alias)
        self.current_config = config
        return name

    def switch_config(self, alias):
        """ Switch Config: Switches the current configuration to a different alias.  This can be used when managing multiple configurations.

            ``alias`` The alias of the config to switch to.  This is
                      returned from `New Config`
        """

        config = self._get_config(alias)
        self.current_config = config

    def add_to_config(self, template_name, **variable_dict):
        """ Add To Config: Adds a template instance into the current config.

        E.g.
        Add To Config    L3 Domain    enterprise_name=enterprise1    domain_name=domain1

        ``template_name`` The name of the template to add to the config

        ``variable_dict`` A dictionary of variable values that will be
                          substituted into the template and added to the
                          current config.
        """
        if self.current_config is None:
            self.new_config()

        config = self.current_config
        config.add_template_data(template_name, **variable_dict)

    def add_to_config_from_file(self, user_data_file_or_path):
        """ Add To Config From File: Adds template instances into the current config from YAML user-data files.
                                     For format details see:
                                     [https://github.com/nuagenetworks/nuage-metroae-config|Nuage MetroAE Config]

        ``user_data_file_or_path`` File name containing YAML template user-data
                                   or path containing multiple of these files.
        """
        if self.current_config is None:
            self.new_config()

        config = self.current_config
        parser = UserDataParser()
        parser.read_data(user_data_file_or_path)
        pairs = parser.get_template_name_data_pairs()
        for pair in pairs:
            template_name = pair[0]
            template_data = pair[1]
            config.add_template_data(template_name, **template_data)

    def apply_config(self):
        """ Apply Config: Applies the current configuration to a VSD via the current VSD connection.
        """
        config, vsd_writer = self._get_current_config_and_writer()
        self._set_config_version(config, vsd_writer)

        try:
            vsd_writer.set_validate_only(True)
            config.apply(vsd_writer)
            vsd_writer.set_validate_only(False)
            config.apply(vsd_writer)
        except MetroConfigError as e:
            error_output = e.get_display_string()
            logger.error(error_output)
            raise e

    def update_config(self):
        """ Update Config: Applies the current configuration to a VSD via the current VSD connection.  Update differs from apply where update will not error if some of the config already exists.
        """
        config, vsd_writer = self._get_current_config_and_writer()
        self._set_config_version(config, vsd_writer)

        try:
            vsd_writer.set_validate_only(True)
            config.update(vsd_writer)
            vsd_writer.set_validate_only(False)
            config.update(vsd_writer)
        except MetroConfigError as e:
            error_output = e.get_display_string()
            logger.error(error_output)
            raise e

    def revert_config(self):
        """ Revert Config: Reverts (removes/deletes) the current configuration from a VSD via the current VSD connection.
        """
        config, vsd_writer = self._get_current_config_and_writer()
        self._set_config_version(config, vsd_writer)

        try:
            vsd_writer.set_validate_only(True)
            config.revert(vsd_writer)
            vsd_writer.set_validate_only(False)
            config.revert(vsd_writer)
        except MetroConfigError as e:
            error_output = e.get_display_string()
            logger.error(error_output)
            raise e

    def validate_config(self):
        """ Validate Config: Validates that the current configuration is free from any syntatic errors without performing any actual operations on the VSD.  Still requires a VSD connection, however.
        """
        config, vsd_writer = self._get_current_config_and_writer()
        self._set_config_version(config, vsd_writer)

        try:
            vsd_writer.set_validate_only(True)
            config.apply(vsd_writer)
            vsd_writer.set_validate_only(False)
        except MetroConfigError as e:
            error_output = e.get_display_string()
            logger.error(error_output)
            raise e

    def perform_query(self, query_text, **query_variables):
        """ Perform Query: Gathers data from the current VSD or ES connection using the query language syntax.  Result data will be returned.
                           More information about `query` can be found at:
                           [https://github.com/nuagenetworks/nuage-metroae-config|Nuage MetroAE Config]

        ``query_text`` The query language string to perform on the VSD or ES.
        ``query_variables`` A dictionary of variable values to provide or
                            override during the query.
        """
        reader = self.current_reader
        if reader is None:
            raise Exception("No VSD or ES connection has been made")

        query = Query()
        self.last_query = query
        query.set_logger(logger)
        query.set_reader(reader)
        self._register_query_readers(query)

        results = query.execute(query_text, **query_variables)
        return results

    def perform_query_from_file(self, query_file, **query_variables):
        """ Perform Query From File: Gathers data from the current VSD or ES connection using a file in the query language syntax.  Result data will be returned.
                                     More information about `query` can be found at:
                                     [https://github.com/nuagenetworks/nuage-metroae-config|Nuage MetroAE Config]

        ``query_file`` A file containing query language to perform on the VSD
                       or ES.
        ``query_variables`` A dictionary of variable values to provide or
                            override during the query.
        """

        reader = self.current_reader
        if reader is None:
            raise Exception("No VSD or ES connection has been made")

        query = Query()
        self.last_query = query
        query.set_logger(logger)
        query.set_reader(reader)
        self._register_query_readers(query)

        query.add_query_file(query_file)
        results = query.execute(None, **query_variables)
        return results

    def get_query_variables(self):
        """ Get Query Variable: Gets a variable value dict from the last query
        """
        if self.last_query is None:
            raise Exception("No previous query has been performed")

        return self.last_query.get_variables()

    def get_template_names(self, software_version=None):
        """ Get Template Names: Returns a list of all of the template names loaded in.  This requires the template store to have been loaded beforehand.

        ``software_version`` Restrict the templates to the VSD software version
                             specified.  If not specified, the latest versions
                             will be provided.
        """
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making template operations")
        template_names = self.template_store.get_template_names(
            SOFTWARE_TYPE, software_version)

        return template_names

    def get_template_documentation(self, template_name, software_version=None):
        """ Get Template Documentation: Returns the documentation for the specified template name.  This requires the template store to have been loaded beforehand.

        ``software_version`` Restrict the template to the VSD software version
                             specified.  If not specified, the latest version
                             will be provided.
        """
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making template operations")
        template = self._get_template(template_name,
                                      software_version)

        return template.get_documentation()

    def get_template_example(self, template_name, software_version=None):
        """ Get Template Example: Returns example user data for the specified template name.  This requires the template store to have been loaded beforehand.

        ``software_version`` Restrict the template to the VSD software version
                             specified.  If not specified, the latest version
                             will be provided.
        """
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making template operations")
        template = self._get_template(template_name,
                                      software_version)

        return template.get_example()

    def get_template_schema(self, template_name, software_version=None):
        """ Get Template Schema: Returns a JSON schema for the specified template name.  This requires the template store to have been loaded beforehand.

        ``software_version`` Restrict the template to the VSD software version
                             specified.  If not specified, the latest version
                             will be provided.
        """
        if self.template_store is None:
            raise Exception("'Load Config Templates' keyword must be called "
                            " before making template operations")
        template = self._get_template(template_name,
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
