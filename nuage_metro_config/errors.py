
class MetroConfigError(Exception):
    """
    Base exception class for all errors in nuage_metro_config module
    """
    def __init__(self, message, location=None):
        super(MetroConfigError, self).__init__(message)
        self.locations = list()
        self.add_location(message)
        if location is not None:
            self.add_location(location)

    def get_display_string(self):
        return "\n".join(self.locations)

    def add_location(self, location):
        self.locations.insert(0, location)

    def get_locations(self):
        return self.locations

    def reraise_with_location(self, location):
        self.add_location(location)
        raise self


#
# Template level errors
#

class TemplateError(MetroConfigError):
    """
    Base exception class for all template level errors
    """
    pass


class TemplateParseError(TemplateError):
    """
    Exception class for errors parsing a template
    """
    pass


class MissingTemplateError(TemplateError):
    """
    Exception class when a template of specified name is not defined
    """
    pass


class UndefinedVariableError(TemplateError):
    """
    Exception class when a required variable value is not defined
    """
    pass


class VariableValueError(TemplateError):
    """
    Exception class when a variable contains the wrong value
    """
    pass


class ConflictError(TemplateError):
    """
    Exception class when there is a conflict during template processing
    """
    pass


class TemplateActionError(TemplateError):
    """
    Exception class when there is a problem with an action in a template
    """
    pass


#
# Template writing errors
#

class DeviceWriterError(MetroConfigError):
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


#
# User data parsing errors
#

class UserDataParseError(MetroConfigError):
    """
    Exception class for errors parsing user data files
    """
    pass
