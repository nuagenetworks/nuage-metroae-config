class DeviceWriterError(Exception):
    """
    Exception class for all template writing errors
    """
    pass


class SessionNotStartedError(DeviceWriterError):
    """
    Exception class when session is used when not started.
    """
    pass


class SessionError(DeviceWriterError):
    """
    Exception class when there is an error in the session
    """
    pass


class MissingSelectionError(DeviceWriterError):
    """
    Exception class when an object was not found during selection
    """
    pass


class MultipleSelectionError(DeviceWriterError):
    """
    Exception class when multiple objects were found during selection
    """
    pass


class InvalidAttributeError(DeviceWriterError):
    """
    Exception class when an attribute on an object does not exist
    """
    pass


class InvalidValueError(DeviceWriterError):
    """
    Exception class when setting an attribute to an invalid value
    """
    pass


class InvalidObjectError(DeviceWriterError):
    """
    Exception class when an object or child of an object does not exist
    """
    pass


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
        self.log_entries = list()

    def log(self, log_type, message):
        self.log_entries.append((log_type, message))

    def log_error(self, message):
        self.log('ERROR', message)

    def log_debug(self, message):
        self.log('DEBUG', message)

    def get_logs(self):
        log_output = []
        for entry in self.log_entries:
            log_output.append("%s: %s" % entry)

        return '\n'.join(log_output)

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

    def get_value(self, field, context):
        """
        Gets a value from the object selected in the current context
        """
        raise NotImplementedError("Abstract base function not implemented")
