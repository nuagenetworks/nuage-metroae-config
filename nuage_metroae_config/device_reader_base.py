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

    def query(self, attributes):
        """
        Reads attributes from device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")
