# # ; "" '' """ '''
# = () +-*/ & |
# identifier[] . function()

import jinja2
from lark import Lark, Transformer
from logger import Logger
import os
import time


query_grammer = Lark(r"""

    query_set     : _single_line | _multi_line
    _single_line  : _query_inline* query?
    _multi_line   : ( _query_inline | _query_line | COMMENT | _NEWLINE )+
    _query_line   : query _NEWLINE
    _query_inline : query ";"
    COMMENT       : "#" /[^\n\r]+/? _NEWLINE
    query         : _expression | assignment | _action

    _expression     : retrieve | _function | variable
    assignment      : CNAME "=" ( _expression | string | list )
    variable        : "$" CNAME
    retrieve        : objects attributes
    objects         : object _dot_object*
    object          : CNAME _filter?
    _dot_object     : "." object
    attributes      : _dot_attr | attr_set
    _dot_attr       : "." attribute
    attr_set        : ".{" ( all | _attr_set_list | variable ) "}"
    _attr_set_list  : attribute ( "," attribute )* ","?
    attribute       : CNAME
    _filter         : "[" ( variable | string | SIGNED_INT | all ) "]"
    all             : "*"
    _function       : count
    count           : "count(" _expression ")"

    _action          : connect_action | redirect_action | render_action
    _argument_list   : argument _comma_arg*
    _comma_arg       : "," argument
    argument         : variable | string | SIGNED_INT
    connect_action   : "connect(" _argument_list ")"
    redirect_action  : "redirect_to_file(" argument ")"
    render_action    : "render_template(" argument ")"

    list              : "[" _list_item_comma* _list_item? "]"
    _list_item        : variable | string | SIGNED_INT
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

    def __init__(self, reader, override_variables):

        self.reader = reader
        self.override_variables = override_variables
        self.override_variables["now"] = int(time.time())
        self.variables = dict(override_variables)
        self.redirect_file = None

    def query_set(self, qs):
        if self.redirect_file is not None:
            self.redirect_file.close()
        return filter(lambda x: x is not None, qs)

    def query(self, q):
        (result,) = q
        if result is not None:
            self._write_output(result)
        return result

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

    def connect_action(self, t):
        args = list(t)
        print "Connect to " + ", ".join(args)
        return None

    def redirect_action(self, t):
        args = list(t)
        self.log.debug("Redirecting output to file: " + args[0])
        self.redirect_file = open(args[0], "w")
        return None

    def render_action(self, t):
        args = list(t)
        self.log.debug("Rendering template")
        template = jinja2.Template(args[0],
                                   autoescape=False,
                                   undefined=jinja2.StrictUndefined)

        output = template.render(**self.variables)
        return output

    def count(self, t):
        (values,) = t
        return len(values)

    def argument(self, t):
        (arg,) = t
        return arg

    def variable(self, t):
        (var_name,) = t
        if var_name not in self.variables:
            raise Exception("Unassigned variable " + var_name)
        return self.variables[var_name]

    def list(self, t):
        return list(t)

    def string(self, t):
        (s,) = t
        if s[0] == "'":
            return s.strip("'")
        else:
            return s.strip('"')

    def _set_logger(self, logger):
        self.log = logger

    def _write_output(self, output):
        output = self._format_result(output)
        self.log.output(output)
        if self.redirect_file is not None:
            self.redirect_file.write(output + "\n")

    def _format_result(self, result, top_level=True):
        output = ""
        if result is None:
            output += "null"
        elif type(result) == dict:
            if top_level:
                for key in result:
                    output += "%s: %s\n" % (
                        key, self._format_result(result[key], top_level=False))
                output = output.strip("\n")
            else:
                output += "{"
                first = True
                for key in result:
                    if not first:
                        output += ", "
                        first = False
                    output += "%s: %s" % (
                        key, self._format_result(result[key], top_level=False))
                output += "}"

        elif type(result) == list:
            if len(result) > 0 and type(result[0]) == dict:
                for item in result:
                    first = True
                    for key in item:
                        if first:
                            output += "\n- "
                            first = False
                        else:
                            output += "  "
                        output += "%s: %s\n" % (
                            key, self._format_result(item[key],
                                                     top_level=False))
            else:
                output += "["
                output += ", ".join(
                    [self._format_result(
                        x, top_level=False) for x in result])
                output += "]"
        elif isinstance(result, basestring):
            if top_level:
                output += result
            else:
                output += "'"
                output += result.replace("'", "''")
                output += "'"
        else:
            output += str(result)

        return output


class Query():

    def __init__(self):
        self.reader = None
        self.query_files = list()
        self.log = Logger()
        self.log.set_to_stdout("ERROR", enabled=True)

    def set_logger(self, logger):
        self.log = logger

    def set_reader(self, reader):
        self.reader = reader

    def add_query_file(self, path_or_file_name):
        """
        Reads and parses query sets from either all query files in a
        directory path, or a single query file specified by filename.
        Query files are expected to have .query extension
        """
        if (os.path.isdir(path_or_file_name)):
            for file_name in os.listdir(path_or_file_name):
                if file_name.endswith(".query"):
                    full_path = os.path.join(path_or_file_name, file_name)
                    self.query_files.append(full_path)
        elif os.path.isfile(path_or_file_name):
            self.query_files.append(path_or_file_name)
        else:
            raise Exception("File or path not found: " +
                            path_or_file_name)

    def execute(self, query_text=None, **override_variables):

        self.reader.start_session()

        if query_text is None:
            results = list()
            for query_file in self.query_files:

                with open(query_file, "r") as f:
                    results.append(self._perform_query(f.read(),
                                                       override_variables))

            if len(results) == 1:
                return results[0]
            else:
                return results

        else:
            results = self._perform_query(query_text, override_variables)

        self.reader.stop_session()

        return results

    def _perform_query(self, query_text, override_variables):
        tree = query_grammer.parse(query_text)
        self.log.debug(tree.pretty())
        qe = QueryExecutor(self.reader, override_variables)
        qe._set_logger(self.log)
        return qe.transform(tree)


text = '''

# This is a test

enterprise = "csp"
connect("vsd", "http://vsd1.example.met:8443", "csproot", "csproot", enterprise)
enterprise[*].domain; # inline comment
domain_count = count(enterprise[*].domain[*])
connect("ES", "http://vstat1.example.met", "csproot", "csproot", enterprise)

'''
# text = 'test = "test string"'
# text = 'connect("vsd", "http://vsd1.example.met:8443", "csproot", "csproot", enterprise); enterprise[*].domain'
# tree = query_grammer.parse(text)

# print tree.pretty()

# print str(Query().execute(text))
