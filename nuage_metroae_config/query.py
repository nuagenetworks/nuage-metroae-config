# # ; "" '' """ '''
# = () +-*/ & |
# identifier[] . function()

from lark import Lark

query_parser = Lark(r"""

    query_list    : _single_line | _multi_line
    _single_line  : _query_inline* query?
    _multi_line   : ( _query_inline | _query_line | comment | NEWLINE )+
    _query_line   : query NEWLINE
    _query_inline : query ";"
    comment       : "#" /[^\n\r]+/? NEWLINE
    query         : _expression | assignment | _action

    _expression     : retrieve
    assignment      : variable "=" ( _expression | string )
    variable        : CNAME
    retrieve        : attribute _dot_attribute*
    _dot_attribute  : "." attribute
    attribute       : CNAME filter?
    filter          : "[" ( variable | string | SIGNED_INT | all_filter ) "]"
    all_filter      : "*"

    _action          : connect_action
    _argument_list   : arg _comma_arg*
    _comma_arg       : "," arg
    arg              : variable | string | SIGNED_INT
    connect_action   : "connect(" _argument_list ")"


    connect_type    : variable | string
    connect_address : "," variable | string
    connect_user    : "," variable | string
    connect_pass    : "," variable | string

    string            : STRING_SQ | STRING_DQ | STRING_BLOCK_SQ | STRING_BLOCK_DQ
    _STRING_INNER     : /.*?/
    _STRING_ESC_INNER : _STRING_INNER /(?<!\\)(\\\\)*?/
    _STRING_BLOCK     : /(.|[\n\r])*?/
    _STRING_ESC_BLOCK : _STRING_BLOCK /(?<!\\)(\\\\)*?/
    STRING_SQ         : "'" _STRING_ESC_INNER "'"
    STRING_DQ         : "\"" _STRING_ESC_INNER "\""
    STRING_BLOCK_SQ   : "'''" _STRING_ESC_BLOCK "'''"
    STRING_BLOCK_DQ   : "\"\"\"" _STRING_ESC_BLOCK "\"\"\""


    %import common.SIGNED_NUMBER
    %import common.SIGNED_INT
    %import common.CNAME
    %import common.NEWLINE
    %import common.WS
    %ignore WS

    """, start='query_list')


text = '''

# This is a test

enterprise = "csp"
connect("vsd", "http://vsd1.example.met:8443", "csproot", "csproot", enterprise)
enterprise[*].domain; # inline comment

'''
# text = 'connect("vsd", "http://vsd1.example.met:8443", "csproot", "csproot", enterprise); enterprise[*].domain'
tree = query_parser.parse(text)

print tree.pretty()

