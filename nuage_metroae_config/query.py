import jinja2
from lark import Lark, Transformer
from .logger import Logger
import os
import time
import yaml
from six import string_types

from nuage_metroae_config.errors import QueryExecutionError, QueryParseError
from nuage_metroae_config.template import (JSONEscapingExtension,
                                           RegularExpressionExtension)
from nuage_metroae_config.variable_reader import VariableReader

query_grammer = Lark(r"""

    query_set     : _single_line | _multi_line
    _single_line  : _query_inline* query?
    _multi_line   : ( _query_inline | _query_line | COMMENT | _NEWLINE )+
    _query_line   : query _NEWLINE
    _query_inline : query ";"
    COMMENT       : "#" /[^\n\r]+/? _NEWLINE
    query         : _expression | assignment | _action

    _expression        : retrieve | _function | variable | combine
    assignment         : CNAME "=" ( boolean | _expression | string | list | integer )
    variable           : "$" CNAME _filter? _dot_object* attributes?
    retrieve           : objects attributes
    objects            : object _dot_object*
    object             : CNAME _filter?
    _dot_object        : "." object
    attributes         : _dot_attr | attr_set
    _dot_attr          : "." attribute
    attr_set           : ".{" ( all | _attr_set_list | variable ) "}"
    _attr_set_list     : attribute ( "," attribute )* ","?
    attribute          : CNAME
    _filter            : "[" filter_set "]"
    filter_set         : _filter_item ( "&" _filter_item )*
    _filter_item       : filter_attr | _filter_range | variable | integer
    filter_attr        : ( filter_special | filter_attr_name ) "=" ( variable | string | boolean | null | filter_attr_name | integer | list)
    filter_special     : "%" CNAME
    _filter_range      : filter_range_both | filter_range_start | filter_range_end
    filter_range_both  : ( integer | variable ) ":" ( integer | variable )
    filter_range_start : ( integer | variable ) ":"
    filter_range_end   : ":" ( integer | variable )
    filter_attr_name   : CNAME
    all                : "*"
    combine            : ( _expression | string | list | integer ) "+" ( _expression | string | list | integer )
    _function          : count | reverse
    count              : "count(" _expression ")"
    reverse            : "reverse(" _expression ")"

    _action            : connect_action | redirect_action | render_action | render_yaml_action | echo_action | output_action
    _argument_list     : argument _comma_arg*
    _comma_arg         : "," argument
    argument           : variable | string | integer
    connect_action     : "connect(" _argument_list ")"
    redirect_action    : "redirect_to_file(" argument ")"
    render_action      : "render_template(" argument ")"
    render_yaml_action : "render_yaml_template(" argument ")"
    echo_action        : "echo(" argument ")"
    output_action      : "output(" argument ")"

    list              : "[" _list_item_comma* _list_item? "]"
    _list_item        : variable | string | integer | boolean | null
    _list_item_comma  : _list_item ","
    string            : STRING_SQ | STRING_DQ | STRING_BLOCK_SQ | STRING_BLOCK_DQ
    _STRING_INNER     : /.*?/
    _STRING_ESC_INNER : _STRING_INNER /(?<!\\)(\\\\)*?/
    _STRING_BLOCK     : /(.|[\n\r])*?/
    _STRING_ESC_BLOCK : _STRING_BLOCK /(?<!\\)(\\\\)*?/
    STRING_SQ         : "'" _STRING_ESC_INNER "'"
    STRING_DQ         : "\"" _STRING_ESC_INNER "\""
    STRING_BLOCK_SQ   : "'''" _STRING_ESC_BLOCK "'''"
    STRING_BLOCK_DQ   : "\"\"\"" _STRING_ESC_BLOCK "\"\"\""
    integer           : SIGNED_INT
    !boolean          : "true" | "false"
    null              : "null"

    _NEWLINE          : NEWLINE

    %import common.SIGNED_NUMBER
    %import common.SIGNED_INT
    %import common.CNAME
    %import common.NEWLINE
    %import common.WS
    %ignore WS
    %ignore COMMENT

    """, start='query_set')


class QueryExecutor(Transformer):
    """
    Private class for parsing and executing the query language tree
    """

    def __init__(self, reader, override_variables, reader_dict):

        self.reader = reader
        self.reader_dict = reader_dict
        self.override_variables = override_variables
        self.override_variables["now"] = int(time.time())
        self.variables = dict(override_variables)
        self.redirect_file = None
        self.echo = True
        self.output = True

        if self.reader is not None:
            self.reader.start_session()

    def query_set(self, qs):
        if self.reader is not None:
            self.reader.stop_session()
        if self.redirect_file is not None:
            self.redirect_file.close()

        return [x for x in qs if x is not None]

    def query(self, q):
        (result,) = q
        if result is not None:
            self._write_output(result)
        if self.output:
            return result
        else:
            return None

    def assignment(self, t):
        (token, value) = t
        var_name = token.value
        if var_name in self.override_variables:
            override = self.override_variables[var_name]
            self.log.debug("Override variable %s value %s with %s" % (
                var_name, value, override))
            value = override
        else:
            self.variables[var_name] = value

        result = {var_name: value}
        return result

    def retrieve(self, t):
        objects = t[0]
        attributes = t[1]
        if self.reader is None:
            raise QueryExecutionError("No reader for query")
        result = self.reader.query(objects, attributes)
        return result

    def objects(self, t):
        return list(t)

    def object(self, t):
        token = t[0]
        filter = None
        if len(t) > 1:
            filter = t[1]
        return {"name": token.value,
                "filter": filter}

    def attributes(self, t):
        return t[0]

    def attribute(self, t):
        return t[0].value

    def attr_set(self, t):
        attributes = list(t)
        if len(attributes) > 0 and type(attributes[0]) == list:
            return attributes[0]
        else:
            return attributes

    def all(self, t):
        return "*"

    def filter_set(self, t):
        filter_dict = dict()
        for add_filter in t:
            if type(add_filter) == dict:
                filter_dict.update(add_filter)
            elif type(add_filter) == list:
                if len(add_filter) != 2:
                    raise QueryExecutionError("Invalid range specified for "
                                              "filter")
                if add_filter[0] is None:
                    filter_dict["%end"] = add_filter[1]
                elif add_filter[1] is None:
                    filter_dict["%start"] = add_filter[0]
                else:
                    filter_dict["%start"] = add_filter[0]
                    filter_dict["%end"] = add_filter[1]
            elif type(add_filter) == int:
                filter_dict["%start"] = add_filter
                if add_filter != -1:
                    filter_dict["%end"] = add_filter + 1
            elif add_filter == "*":
                filter_dict["%all"] = True
            else:
                raise QueryExecutionError("Invalid filter type")

        return filter_dict

    def filter_attr(self, t):
        (name, value) = t
        return {name: value}

    def filter_special(self, t):
        (name,) = t
        return str("%" + name.lower())

    def filter_attr_name(self, t):
        (name,) = t
        return name.value

    def filter_range_both(self, t):
        return list(t)

    def filter_range_start(self, t):
        return [t[0], None]

    def filter_range_end(self, t):
        return [None, t[0]]

    def combine(self, t):
        (op1, op2) = t
        if type(op1) == list and type(op2) == list:
            op1.extend(op2)
        elif isinstance(op1, string_types) and isinstance(op2, string_types):
            op1 = op1 + op2
        elif type(op1) == int and isinstance(op2, string_types):
            op1 = str(op1) + op2
        elif isinstance(op1, string_types) and type(op2) == int:
            op1 = op1 + str(op2)
        elif type(op1) == int and type(op2) == int:
            op1 = op1 + op2
        else:
            raise Exception("Incompatible types for combine")

        return op1

    def connect_action(self, t):
        args = list(t)
        self.log.debug("Connect to " + ", ".join(args))
        if len(args) < 1 or args[0].lower() not in self.reader_dict:
            raise QueryExecutionError("Invalid type for connection")

        if self.reader is not None:
            self.reader.stop_session()

        self.reader = self.reader_dict[args[0].lower()]
        self.reader.connect(*args[1:])

        return None

    def redirect_action(self, t):
        args = list(t)
        self.log.debug("Redirecting output to file: " + args[0])
        self.redirect_file = open(args[0], "w")
        return None

    def render_action(self, t):
        return self.render_common(t, is_yaml=False)

    def render_yaml_action(self, t):
        return self.render_common(t, is_yaml=True)

    def render_common(self, t, is_yaml=False):
        args = list(t)
        self.log.debug("Rendering template")
        if is_yaml:
            extensions = (JSONEscapingExtension,
                          RegularExpressionExtension)
        else:
            extensions = (RegularExpressionExtension,)

        template = jinja2.Template(args[0],
                                   extensions=extensions,
                                   autoescape=False,
                                   undefined=jinja2.StrictUndefined)

        output = template.render(**self.variables)
        return output

    def echo_action(self, t):
        args = list(t)
        if len(args) != 1:
            raise QueryExecutionError("Invalid number of arguments to "
                                      "echo('true' | 'false')")
        if args[0].lower() in ["true", "on", "yes", "t", "y"]:
            self.echo = True
            self.log.debug("Echo on")
        elif args[0].lower() in ["false", "off", "no", "f", "n"]:
            self.echo = False
            self.log.debug("Echo off")
        else:
            raise QueryExecutionError("Invalid argument to "
                                      "echo('true' | 'false'): %s" % args[0])

        return None

    def output_action(self, t):
        args = list(t)
        if len(args) != 1:
            raise QueryExecutionError("Invalid number of arguments to "
                                      "output('true' | 'false')")
        if args[0].lower() in ["true", "on", "yes", "t", "y"]:
            self.output = True
            self.log.debug("Output on")
        elif args[0].lower() in ["false", "off", "no", "f", "n"]:
            self.output = False
            self.log.debug("Output off")
        else:
            raise QueryExecutionError("Invalid argument to "
                                      "output('true' | 'false'): %s" % args[0])

        return None

    def count(self, t):
        (values,) = t
        if type(values) != list:
            raise QueryExecutionError("Invalid data type for count")

        return len(values)

    def reverse(self, t):
        (values,) = t
        if type(values) != list:
            raise QueryExecutionError("Invalid data type for reverse")

        return list(reversed(values))

    def argument(self, t):
        (arg,) = t
        return arg

    def variable(self, t):
        var_name = t[0].value
        if var_name not in self.variables:
            raise Exception("Unassigned variable " + var_name)

        if len(t) > 1:
            var_reader = VariableReader()
            var_reader.set_data(self.variables[var_name])
            last_object = t[-1]
            objects = t[1:-1]
            if type(last_object) == dict:
                if "filter" in last_object and last_object["filter"] is None:
                    attributes = last_object["name"]
                else:
                    attributes = None
                    objects = t[1:]
            else:
                attributes = last_object

            if (len(objects) > 0 and type(objects[0]) is dict and
                    "filter" not in objects[0]):
                objects[0] = {"name": var_name, "filter": objects[0]}
            else:
                objects.insert(0, {"name": var_name, "filter": None})

            result = var_reader.query(objects, attributes)

            return result

        return self.variables[var_name]

    def list(self, t):
        return list(t)

    def string(self, t):
        (s,) = t
        if s[0] == "'":
            return s.strip("'")
        else:
            return s.strip('"')

    def integer(self, t):
        (i,) = t
        return int(i)

    def boolean(self, t):
        (b,) = t
        if b == "true":
            return True
        elif b == "false":
            return False
        else:
            raise Exception("Invalid boolean value")

    def null(self, t):
        return None

    def _set_logger(self, logger):
        self.log = logger

    def _write_output(self, output):
        output = self._format_result(output)
        if self.output:
            if self.echo:
                self.log.output(output)
            else:
                self.log.debug(output)
            if self.redirect_file is not None:
                self.redirect_file.write(output + "\n")
        else:
            self.log.debug(output)

    def _format_result(self, result):
        if result is None:
            return "null"
        elif type(result) == dict or type(result) == list:
            return yaml.dump(result, Dumper=NoAliasDumper,
                             default_flow_style=False).strip("\n")
        elif isinstance(result, str):
            return result
        else:
            return str(result)

    def _get_variables(self):
        return self.variables


class Query():
    """
    A class which can retrieve information from a device using a
    DeviceReaderBase reader object.  The information to be retrieved is defined
    by query language text.
    """

    def __init__(self):
        self.reader = None
        self.reader_dict = dict()
        self.query_files = list()
        self.log = Logger()
        self.log.set_to_stdout("ERROR", enabled=True)
        self.variables = None

    def set_logger(self, logger):
        """
        Set a custom logger for actions taken.  This should be based on the
        logging Python library.  It will need to define an 'output' log level
        which is intended to print to stdout.
        """
        self.log = logger

    def set_reader(self, reader):
        """
        Set the primary reader object for performing queries on the device.
        The reader needs to be derived from the DeviceReaderBase class.
        """
        self.reader = reader

    def get_variables(self):
        """
        Returns a dictionary of all variables and values set during queries.
        """
        return self.variables

    def register_reader(self, reader_type, reader):
        """
        Register a reader object for each 'connect' type for performing queries
        on the device.  This allows devices to be switched within the query
        text.  The readers need to be derived from the DeviceReaderBase class.
        """
        self.reader_dict[reader_type.lower()] = reader

    def add_query_file(self, path_or_file_name):
        """
        Reads and parses query sets from either all query files in a
        directory path, or a single query file specified by filename.
        Query files are expected to have .query extension
        """
        if (os.path.isdir(path_or_file_name)):
            for file_name in sorted(os.listdir(path_or_file_name)):
                if file_name.endswith(".query"):
                    full_path = os.path.join(path_or_file_name, file_name)
                    self.query_files.append(full_path)
        elif os.path.isfile(path_or_file_name):
            self.query_files.append(path_or_file_name)
        else:
            raise QueryExecutionError("File or path not found: " +
                                      path_or_file_name)

    def execute(self, query_text=None, **override_variables):
        """
        Executes the query defined in query_text.  Variables in the query
        text can be overriden using the override_variables kwargs dict.  The
        results of the query are returned as a list with an entry for each
        query text line.  If query_text is None, then query text is pulled
        from query files defined by add_query_file.
        """
        if query_text is None:
            results = list()
            for query_file in self.query_files:

                with open(query_file, "r") as f:
                    results.extend(self._perform_query(f.read(),
                                                       override_variables))

            if len(results) == 1:
                return results[0]
            else:
                return results

        else:
            results = self._perform_query(query_text, override_variables)

        return results

    def _perform_query(self, query_text, override_variables):
        try:
            tree = query_grammer.parse(query_text)
        except Exception as e:
            raise QueryParseError(str(e))
        self.log.debug(tree.pretty())
        qe = QueryExecutor(self.reader, override_variables, self.reader_dict)
        qe._set_logger(self.log)
        try:
            results = qe.transform(tree)
            self.variables = qe._get_variables()
        except Exception as e:
            raise QueryExecutionError(str(e))
        return results


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def jinja_date_format(value, format):
    return time.strftime(format, time.localtime(value))


jinja2.filters.FILTERS['date_format'] = jinja_date_format
