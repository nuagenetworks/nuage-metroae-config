import collections

from .actions import Action
from .logger import Logger


class Configuration(object):
    """
    Container for template instances.
    """
    def __init__(self, template_store):
        """
        Requires a TemplateStore object to be provided.
        """
        self.store = template_store
        self.software_version = None
        self.software_type = None
        self.data = collections.OrderedDict()
        self.log = Logger()
        self.is_update = False

    def set_logger(self, logger):
        """
        Set a custom logger for actions taken.  This should be based on the
        logging Python library.  It will need to define an 'output' log level
        which is intended to print to stdout.
        """
        self.log = logger

    def get_logger(self):
        return self.log

    def set_software_version(self, software_type=None, software_version=None):
        """
        Sets the current software version of templates that is desired.
        If not called, the latest software version of templates will be
        used.
        """
        self.software_type = software_type
        self.software_version = software_version

    def get_template_names(self):
        """
        Returns a list of all template names currently loaded in store.
        In reality, this just calls the template_store function with
        the currently set software_version and software_type.
        """
        return self.store.get_template_names(self.software_type,
                                             self.software_version)

    def get_template(self, name):
        """
        Returns a Template object of the specified name.  In reality,
        this just calls the template_store function with the currently
        set software_version and software_type.
        """
        return self.store.get_template(name,
                                       self.software_type,
                                       self.software_version)

    def add_template_data(self, template_name, **template_data):
        """
        Adds template data (user data) for the specified template name.
        Data is specified in a kwargs dictionary with keys as the
        attribute/variable name.  The data is validated against the
        corresponding template schema.  An id is returned for reference.
        """
        template = self.get_template(template_name)
        template.validate_template_data(**template_data)
        return self._append_data(template_name, dict(template_data))

    def get_template_data(self, id):
        """
        Returns the template data in dictionary form.  The id comes
        from the corresponding add_template_data call.
        """
        data = self._get_data(id)
        if data is not None:
            return dict(data)

        return None

    def update_template_data(self, id, **template_data):
        """
        Updates the specified template data.  Data is specified in a kwargs
        dictionary with keys as the attribute/variable name.  The data is
        validated against the corresponding template schema.  The id comes
        from the corresponding add_template_data call.
        """
        template = self.get_template(self._get_template_key(id))
        template.validate_template_data(**template_data)
        return self._set_data(id, dict(template_data))

    def remove_template_data(self, id):
        """
        Removes the specified template data.  The id comes
        from the corresponding add_template_data call.
        """
        return self._set_data(id, None)

    def apply(self, writer):
        """
        Applies this configuration to the provided device
        writer.  Returns True if ok, otherwise an exception is
        raised.
        """
        self._execute_templates(writer, is_revert=False)
        return True

    def update(self, writer):
        """
        Applies this configuration to the provided device
        writer as an update.  This means objects that exist will
        not be considered conflicts.  Returns True if ok, otherwise
        an exception is raised.
        """
        self._execute_templates(writer, is_update=True)
        return True

    def revert(self, writer):
        """
        Reverts (removes or undo) this configuration from the
        provided device writer.  Returns True if ok, otherwise
        an exception is raised.
        """
        self._execute_templates(writer, is_revert=True)

        return True

    #
    # Private functions to do the work
    #

    def _append_data(self, template_name, template_data):
        key = template_name.lower()
        index = 0
        if key in self.data:
            index = len(self.data[key])
        else:
            self.data[key] = list()

        self.data[key].append(template_data)

        return {"key": key, "index": index}

    def _set_data(self, id, template_data):
        key, index = self._get_data_index(id)

        self.data[key][index] = template_data

        return id

    def _get_data(self, id):
        key, index = self._get_data_index(id)

        return self.data[key][index]

    def _get_data_index(self, id):
        key = id['key']
        index = id['index']
        if key not in self.data:
            raise IndexError("Invalid template data id")

        length = len(self.data[key])
        if (index >= length):
            raise IndexError("Invalid template data id")

        return key, index

    def _get_template_key(self, id):
        return id['key']

    def _execute_templates(self, writer, is_revert=False, is_update=False):
        self.root_action = Action(None)
        self.root_action.set_logger(self.log)
        self.is_update = is_update
        if is_revert is True:
            self._walk_data(self._revert_data)
        else:
            self._walk_data(self._apply_data)
        self.root_action.reorder()
        self.log.debug(str(self.root_action))
        writer.start_session()
        self.root_action.execute(writer)
        writer.stop_session()

    def _walk_data(self, callback_func):
        for template_name, data_list in self.data.items():
            template = self.get_template(template_name)
            for data in data_list:
                if data is not None:
                    callback_func(template, data)

    def _apply_data(self, template, data):
        template_dict = template._parse_with_vars(**data)
        self.root_action.reset_state()
        self.root_action.set_revert(False)
        self.root_action.set_update(self.is_update)
        self.root_action.set_template_name(template.get_name())
        self.root_action.read_children_actions(template_dict)

    def _revert_data(self, template, data):
        template_dict = template._parse_with_vars(**data)
        self.root_action.reset_state()
        self.root_action.set_revert(True)
        self.root_action.set_template_name(template.get_name())
        self.root_action.read_children_actions(template_dict)
