from actions import Action


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
        self.data = dict()

    def set_software_version(self, software_version, software_type=None):
        """
        Sets the current software version of templates that is desired.
        If not called, the latest software version of templates will be
        used.
        """
        raise NotImplementedError(
            "Template software versioning not yet implemented")

    def get_template_names(self):
        """
        Returns a list of all template names currently loaded in store.
        In reality, this just calls the template_store function with
        the currently set software_version and software_type.
        """
        return self.store.get_template_names(self.software_version,
                                             self.software_type)

    def get_template(self, name):
        """
        Returns a Template object of the specified name.  In reality,
        this just calls the template_store function with the currently
        set software_version and software_type.
        """
        return self.store.get_template(name,
                                       self.software_version,
                                       self.software_type)

    def add_template_data(self, template_name, **template_data):
        """
        Adds template data (user data) for the specified template name.
        Data is specified in a kwargs dictionary with keys as the
        attribute/variable name.  The data is validated against the
        corresponding template schema.  An id is returned for reference.
        """
        self.get_template(template_name)
        # TODO: verify data with template.get_schema()
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
        self.get_template(self._get_template_key(id))
        # TODO: verify data with template.get_schema()
        return self._set_data(id, dict(template_data))

    def remove_template_data(self, id):
        """
        Removes the specified template data.  The id comes
        from the corresponding add_template_data call.
        """
        return self._set_data(id, None)

    def validate(self, writer):
        """
        Validates this configuration against the provided device
        writer.  Returns True if ok, otherwise an exception is
        raised.
        """
        raise NotImplementedError("Template validation not yet implemented")

    def apply(self, writer):
        """
        Applies this configuration to the provided device
        writer.  Returns True if ok, otherwise an exception is
        raised.
        """
        self.root_action = Action(None)
        self.writer = writer
        self._walk_data(self._apply_data)

    def update(self, writer):
        """
        Applies this configuration to the provided device
        writer as an update.  This means objects that exist will
        not be considered conflicts.  Returns True if ok, otherwise
        an exception is raised.
        """
        pass

    def revert(self, writer):
        """
        Reverts (removes or undo) this configuration from the
        provided device writer.  Returns True if ok, otherwise
        an exception is raised.
        """
        pass

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

    def _walk_data(self, callback_func):
        for template_name, data_list in self.data.iteritems():
            template = self.get_template(template_name)
            for data in data_list:
                if data is not None:
                    callback_func(template, data)

    def _apply_data(self, template, data):
        template_dict = template._parse_with_vars(**data)
        self.root_action.reset_state()
        self.root_action.read_children_actions(template_dict)
