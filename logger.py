class Logger(object):
    """
    Class to manage the logging and user output of the Levistate module
    """
    def __init__(self):
        self.log_entries = list()
        self.log_type_to_stdout = dict()
        self.log_type_to_stdout['OUTPUT'] = True

    def log(self, message, log_type="LOG"):
        for line in message.split('\n'):
            self.log_entries.append((log_type, line))
            if (log_type in self.log_type_to_stdout and
                    self.log_type_to_stdout[log_type] is True):
                print line

    def error(self, message):
        self.log(message, 'ERROR')

    def debug(self, message):
        self.log(message, 'DEBUG')

    def output(self, message):
        self.log(message, 'OUTPUT')

    def get(self):
        log_output = []
        for entry in self.log_entries:
            log_output.append("%s: %s" % entry)

        return '\n'.join(log_output)

    def set_to_stdout(self, log_type, enabled=True):
        self.log_type_to_stdout[log_type] = enabled
