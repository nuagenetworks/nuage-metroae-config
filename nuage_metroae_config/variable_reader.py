from .device_reader_base import DeviceReaderBase


class VariableReader(DeviceReaderBase):
    """
    Extracts results from internal variables.  This class is a derived class
    from the DeviceReaderBase Abstract Base Class.
    """

    def __init__(self):
        """
        Derived class from DeviceWriterBase.
        """
        super(VariableReader, self).__init__()
        self.data = list()

    def set_data(self, data):
        """
        Sets the data to extract results from
        """
        self.data = data

    def start_session(self):
        """
        Starts a session (not needed to be called)
        """
        self.log.debug("Session start")

    def stop_session(self):
        """
        Stops the session (not needed to be called)
        """
        self.log.debug("Session stopping")

    def query(self, objects, attributes):
        """
        Reads attributes from internal data
        """
        location = "Query %s : %s" % (objects, attributes)

        self.log.debug(location)

        return self._query(objects, attributes)

    def query_attribute(self, obj, attribute):
        """
        Reads an attribute from an object
        """
        if type(obj) == dict and attribute in obj:
            return obj[attribute]

        return None

    #
    # Private functions to do the work
    #

    def _query(self, objects, attributes):

        return self.filter_results_level(self.data, objects, attributes, 0,
                                         list())
