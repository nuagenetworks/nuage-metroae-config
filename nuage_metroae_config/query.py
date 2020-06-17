# # ; "" '' """ '''
# = () +-*/ & |
# identifier[] . function()

from lark import Lark, Transformer

query_grammer = Lark(r"""

    query_set     : _single_line | _multi_line
    _single_line  : _query_inline* query?
    _multi_line   : ( _query_inline | _query_line | COMMENT | _NEWLINE )+
    _query_line   : query _NEWLINE
    _query_inline : query ";"
    COMMENT       : "#" /[^\n\r]+/? _NEWLINE
    query         : _expression | assignment | _action

    _expression     : retrieve | _function
    assignment      : CNAME "=" ( _expression | string )
    variable        : CNAME
    retrieve        : attribute _dot_attribute*
    _dot_attribute  : "." attribute
    attribute       : CNAME _filter?
    _filter          : "[" ( variable | string | SIGNED_INT | all_filter ) "]"
    all_filter      : "*"
    _function       : count
    count           : "count(" _expression ")"

    _action          : connect_action
    _argument_list   : argument _comma_arg*
    _comma_arg       : "," argument
    argument         : variable | string | SIGNED_INT
    connect_action   : "connect(" _argument_list ")"

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

    def __init__(self, override_variables):

        self.override_variables = override_variables
        self.variables = dict(override_variables)

    def query_set(self, qs):
        return filter(lambda x: x is not None, qs)

    def query(self, q):
        (result,) = q
        if result is None:
            pass
        elif type(result) == dict:
            for key in result:
                print "%s: %s" % (key, result[key])
        else:
            print str(result)
        return q[0]

    def assignment(self, t):
        (token, value) = t
        var_name = token.value
        if var_name not in self.override_variables:
            self.variables[var_name] = value
        return {var_name: value}

    def retrieve(self, t):
        attributes = list(t)
        return attributes

    def attribute(self, t):
        token = t[0]
        filter = None
        if len(t) > 1:
            filter = t[1]
        return {"name": token.value,
                "filter": filter}

    def all_filter(self, t):
        return "*"

    def connect_action(self, t):
        args = list(t)
        print "connect " + ", ".join(args)
        return None

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

    def string(self, t):
        (s,) = t
        if s[0] == "'":
            return s.strip("'")
        else:
            return s.strip('"')


class Query():

    def execute(self, query_text, **override_variables):

        tree = query_grammer.parse(query_text)
        print tree.pretty()
        results = QueryExecutor(override_variables).transform(tree)
        return results


text = '''

# This is a test

enterprise = "csp"
connect("vsd", "http://vsd1.example.met:8443", "csproot", "csproot", enterprise)
enterprise[*].domain; # inline comment
domain_count = count(enterprise[*].domain[*])

'''
# text = 'test = "test string"'
# text = 'connect("vsd", "http://vsd1.example.met:8443", "csproot", "csproot", enterprise); enterprise[*].domain'
# tree = query_grammer.parse(text)

# print tree.pretty()

print str(Query().execute(text))
