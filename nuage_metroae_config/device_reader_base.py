from logger import Logger


class DeviceReaderBase(object):
    """
    Base class for reading information from devices.  This is an
    abstract base class, meaning that it cannot be instantiated
    on its own. It must act as a base for a device-specific derived class.
    """
    def __init__(self):
        """
        Abstract Base Class.  Cannot be instantiated directly. Use
        device-specific derived class.
        """
        self.log = Logger()
        self.log.set_to_stdout("ERROR", enabled=True)

    def set_logger(self, logger):
        self.log = logger

    def get_logger(self):
        return self.log

    def filter_results(self, results, filter):
        filtered = list()
        sort_asc = True
        sort_field = None
        start = None
        end = None

        if filter is None:
            return results
        elif type(filter) == dict:
            for field_name in filter:
                if field_name.startswith("%"):
                    if field_name == "%start":
                        start = filter[field_name]
                    elif field_name == "%end":
                        end = filter[field_name]
                    elif field_name in ["%sort", "%sort_asc"]:
                        sort_field = filter[field_name]
                        sort_asc = True
                    elif field_name == "%sort_desc":
                        sort_field = filter[field_name]
                        sort_asc = False
                    else:
                        raise Exception(
                            "Invalid filter %s for query" % field_name)
        else:
            raise Exception("Invalid filter for query")

        for result in results:
            if self._should_keep_result(result, filter):
                filtered.append(result)

        return filtered[slice(start, end)]

    def _should_keep_result(self, result, filter):
        for attr_name in filter:
            if not attr_name.startswith("%"):
                result_value = self.query_attribute(result, attr_name)
                if result_value != filter[attr_name]:
                    return False

        return True

    # Abstract prototype functions
    # All types of device writer classes will need to implement these
    # functions in order to apply the configurations to the device.

    def start_session(self):
        """
        Starts a session with device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

    def stop_session(self):
        """
        Stops the session with device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

    def connect(self, *args):
        """
        Creates a new connection with another device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

    def query(self, objects, attributes):
        """
        Reads attributes from device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

    def query_attribute(self, object, attribute):
        """
        Reads an attribute from an object
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")
