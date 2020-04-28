from logger import Logger


class DeviceWriterBase(object):
    """
    Base class for writing configurations to devices.  This is an
    abstract base class, meaning that it cannot be instantiated
    on its own. It must act as a base for a device-specific derived class.
    """
    def __init__(self):
        """
        Abstract Base Class.  Cannot be instantiated directly. Use
        device-specific derived class.
        """
        self.validate_only = False
        self.log = Logger()
        self.log.set_to_stdout("ERROR", enabled=True)

    def set_logger(self, logger):
        self.log = logger

    def get_logger(self):
        return self.log

    def set_validate_only(self, value=True):
        if value != self.validate_only:
            if value is True:
                self.log.debug("*** Validate ***")
            else:
                self.log.debug("*** Writing ***")
        self.validate_only = value

    def is_validate_only(self):
        return self.validate_only

    # Abstract prototype functions
    # All types of device writer classes will need to implement these
    # functions in order to apply the configurations to the device.

    def get_version(self):
        """
        Returns the version running on the device in format:
            {"software_version": "xxx",
             "software_type": "xxx"}
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

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

    def create_object(self, object_name, context=None):
        """
        Creates an object in the current context, object is not saved to device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

    def select_object(self, object_name, by_field, value, context=None):
        """
        Selects an object in the current context
        """
        raise NotImplementedError("Abstract base function not implemented")

    def delete_object(self, context):
        """
        Deletes the object selected in the current context
        """
        raise NotImplementedError("Abstract base function not implemented")

    def set_values(self, context, **kwargs):
        """
        Sets values in the object selected in the current context and saves it
        """
        raise NotImplementedError("Abstract base function not implemented")

    def unset_values(self, context, **kwargs):
        """
        Unsets values of a selected object when being reverted
        """
        raise NotImplementedError("Abstract base function not implemented")

    def get_value(self, field, context):
        """
        Gets a value from the object selected in the current context
        """
        raise NotImplementedError("Abstract base function not implemented")

    def does_object_exist(self, context):
        """
        Return is the object already exists on the device or not
        """
        raise NotImplementedError("Abstract base function not implemented")
