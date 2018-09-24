class MockWriter(object):
    """
    Class for unit testing to record all actions taken to the writer and
    report them to the tests.
    """
    def __init__(self):
        self.recorded_actions = []
        self.current_context_index = 0
        self.current_get_value_index = 0
        self.raise_exception_on = None
        self.mock_exception = None

    def get_recorded_actions(self):
        return self.recorded_actions

    def raise_exception(self, exception, on_action):
        self.mock_exception = exception
        self.raise_exception_on = on_action

    def _record_action(self, action_str):
        self.recorded_actions.append(action_str)
        self._check_for_exception(action_str)

    def _check_for_exception(self, action_str):
        if action_str == self.raise_exception_on:
            raise self.mock_exception

    def _new_context(self):
        self.current_context_index += 1
        return "context_" + str(self.current_context_index)

    def _new_get_value(self):
        self.current_get_value_index += 1
        return "value_" + str(self.current_get_value_index)

    def set_validate_only(self, value=True):
        pass

    def is_validate_only(self):
        return False

    #
    # Implement all required Abstract Base Class prototype functions.
    #

    def start_session(self):
        """
        Starts a session with device
        """
        self._record_action("start-session")

    def stop_session(self):
        """
        Stops the session with device
        """
        self._record_action("stop-session")

    def create_object(self, object_name, context=None):
        """
        Creates an object in the current context, object is not saved to device
        """
        self._record_action("create-object %s [%s]" % (object_name,
                                                       str(context)))
        return self._new_context()

    def select_object(self, object_name, by_field, value, context=None):
        """
        Selects an object in the current context
        """
        self._record_action("select-object %s %s = %s [%s]" % (object_name,
                                                               by_field,
                                                               str(value),
                                                               str(context)))
        return self._new_context()

    def delete_object(self, context):
        """
        Deletes the object selected in the current context
        """
        self._record_action("delete-object [%s]" % str(context))
        return self._new_context()

    def set_values(self, context, **kwargs):
        """
        Sets values in the object selected in the current context and saves it
        """
        values = []
        for key in sorted(kwargs.keys()):
            values.append("%s=%s" % (key, str(kwargs[key])))

        self._record_action("set-values %s [%s]" % (','.join(values),
                                                    str(context)))
        return self._new_context()

    def get_value(self, field, context):
        """
        Gets a value from the object selected in the current context
        """
        self._record_action("get-value %s [%s]" % (field, str(context)))
        return self._new_get_value()