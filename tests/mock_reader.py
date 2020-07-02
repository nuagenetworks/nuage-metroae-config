class MockReader(object):
    """
    Class for unit testing to record all actions taken to the reader and
    report them to the tests.
    """
    def __init__(self):
        self.recorded_actions = list()
        self.mock_results = list()
        self.mock_result_index = 0
        self.raise_exception_on = None
        self.mock_exception = None

    def get_recorded_actions(self):
        return self.recorded_actions

    def raise_exception(self, exception, on_action):
        self.mock_exception = exception
        self.raise_exception_on = on_action

    def add_mock_result(self, result):
        self.mock_results.append(result)

    def _record_action(self, action_str):
        self.recorded_actions.append(action_str)
        self._check_for_exception(action_str)

    def _check_for_exception(self, action_str):
        if (self.raise_exception_on is not None and
                self.raise_exception_on in action_str):
            raise self.mock_exception

    def set_validate_only(self, value=True):
        pass

    def is_validate_only(self):
        return False

    def set_return_empty_select_list(self, return_empty_select_list=True):
        self.return_empty_select_list = return_empty_select_list

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
        # Abstract prototype function
        self._record_action("stop-session")

    def connect(self, *args):
        """
        Creates a new connection with another device
        """
        # Abstract prototype function
        self._record_action("connect [%s]" % ",".join(args))

    def query(self, objects, attributes):
        """
        Reads attributes from device
        """
        filters = list()
        for obj in objects:
            filter = obj["filter"]
            if filter is not None:
                pairs = list()
                for key in sorted(filter.keys()):
                    value = filter[key]
                    if type(value) == list:
                        value = "[" + ",".join(value) + "]"
                    pairs.append("%s=%s" % (key, str(value)))
                filters.append("%s (%s)" % (obj["name"], ",".join(pairs)))
            else:
                filters.append("%s (None)" % obj["name"])

        if type(attributes) is not list:
            attributes = [attributes]

        self._record_action("query [%s] {%s}" % (','.join(filters),
                                                 ','.join(attributes)))

        if len(self.mock_results) > self.mock_result_index:
            result = self.mock_results[self.mock_result_index]
            self.mock_result_index += 1
            return result
        else:
            raise Exception("No more mock results to provide")

    def query_attribute(self, object, attribute):
        """
        Reads an attribute from an object
        """
        # Abstract prototype function
        raise NotImplementedError("Not called from query")
