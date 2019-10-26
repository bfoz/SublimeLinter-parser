import re

from .. import grammar
from ..grammar import Alternation, Concatenation, Repetition

""" Grammar for Python

    NOTE WELL: You should also follow all the steps listed at https://devguide.python.org/grammar/
"""

grammar.implicit_separator(re.compile(r'\s+'))

def root():
    """ The name of the root rule of the grammar """
    return file_input

# DEDENT = //
ENDMARKER = ''
INDENT = re.compile(r"[\t ]+")
NAME = re.compile(r"\w+")
NEWLINE = re.compile(r"\n")

BINARY_NUMBER = re.compile(r'0[bB][01_]+')
DECIMAL_NUMBER = re.compile(r'[+\-]?\d+(\.\d+)?')
HEXADECIMAL_NUMBER = re.compile(r'0[xX][0-9a-fA-F_]+')
OCTAL_NUMBER = re.compile(r'0[oO][0-7_]+')
NUMBER = Alternation(BINARY_NUMBER, DECIMAL_NUMBER, HEXADECIMAL_NUMBER, OCTAL_NUMBER)

STRING = re.compile(r"\w+")

""" 2.4 Literals (https://docs.python.org/3/reference/lexical_analysis.html#literals) """

""" 2.4.1. String and Bytes literals (https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals) """

# stringprefix    ::=  "r" | "u" | "R" | "U" | "f" | "F"
#                      | "fr" | "Fr" | "fR" | "FR" | "rf" | "rF" | "Rf" | "RF"
stringprefix = Alternation("r", "u", "R", "U", "f", "F", "fr", "Fr", "fR", "FR", "rf", "rF", "Rf", "RF")

# shortstringitem ::=  shortstringchar | stringescapeseq
# shortstringchar ::=  <any source character except "\" or newline or the quote>
# stringescapeseq ::=  "\" <any source character>
shortstringitem = re.compile(r"[a-zA-Z0-9 -!#-&(-\/:-@\[-`{-~]*")

# shortstring     ::=  "'" shortstringitem* "'" | '"' shortstringitem* '"'
shortstring = Alternation(Concatenation("'", shortstringitem, "'"), Concatenation('"', shortstringitem, '"'))

# longstringchar  ::=  <any source character except "\">
# longstringitem  ::=  longstringchar | stringescapeseq
longstringitem = re.compile(r"[a-zA-Z0-9 -!#-&(-\/:-@\[-`{-~]*")

# longstring      ::=  "'''" longstringitem* "'''" | '"""' longstringitem* '"""'
longstring = Concatenation("'''", longstringitem, "'''") | Concatenation('"""', longstringitem, '"""')

# stringliteral   ::=  [stringprefix](shortstring | longstring)
stringliteral = Concatenation(stringprefix.optional, Alternation(shortstring, longstring))

""" ---> test: or_test ['if' or_test 'else' test] | lambdef """
test = Alternation()
_test = test    # Alias for convenience

# testlist: test (',' test)* [',']
testlist = Concatenation(test, Concatenation(',', test).any, Repetition.optional(','))

# sliceop: ':' [test]
sliceop = Concatenation(':', _test.optional)

# subscript: test | [test] ':' [test] [sliceop]
subscript = _test | Concatenation(_test.optional, ':', _test.optional, sliceop.optional)

# subscriptlist: subscript (',' subscript)* [',']
subscriptlist = Concatenation(subscript, Concatenation(',', subscript).any, Repetition.optional(','))

# vfpdef: NAME
vfpdef = NAME

# varargslist: (vfpdef ['=' test] (',' vfpdef ['=' test])* [',' [
#         '*' [vfpdef] (',' vfpdef ['=' test])* [',' ['**' vfpdef [',']]]
#       | '**' vfpdef [',']]]
#   | '*' [vfpdef] (',' vfpdef ['=' test])* [',' ['**' vfpdef [',']]]
#   | '**' vfpdef [',']
# )
varargslist = Alternation(
    Concatenation(
        vfpdef,
        Concatenation('=', _test).optional,
        Concatenation(',', vfpdef, Concatenation('=', _test).optional).any,
        Concatenation(
            ',',
            Concatenation(
                '*',
                Repetition.optional(vfpdef),
                Concatenation(',', vfpdef, Concatenation('=', _test).optional).any,
                Alternation(
                    Concatenation(
                        ',',
                        Concatenation('**', vfpdef, Repetition.optional(',')).optional
                    ).optional,
                    Concatenation('**', vfpdef, Repetition.optional(','))
                )
            ).optional
        ).optional
    ),
    Concatenation(
        '*',
        Repetition.optional(vfpdef),
        Concatenation(
            ',',
            vfpdef,
            Concatenation('=', _test).optional
        ).any,
        Concatenation(',', Concatenation('**', vfpdef, Repetition.optional(',')).optional).optional
    ),
    Concatenation('**', vfpdef, Repetition.optional(','))
)

# lambdef: 'lambda' [varargslist] ':' test
lambdef = Concatenation('lambda', varargslist.optional, ':', _test)

# yield_arg: 'from' test | testlist
yield_arg = Concatenation('from', _test) | testlist

# yield_expr: 'yield' [yield_arg]
yield_expr = Concatenation('yield', yield_arg.optional)

""" ---> expression """
# expr: xor_expr ('|' xor_expr)*
expression = Concatenation()
expr = expression   # Alias for convenience

# <> isn't actually a valid comparison operator in Python. It's here for the
# sake of a __future__ import described in PEP 401 (which really works :-)
# comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
comp_op = Alternation(
    '<',
    '>',
    '==',
    '>=',
    '<=',
    '<>',
    '!=',
    'in',
    Concatenation('not', 'in'),
    'is',
    Concatenation('is', 'not')
)

# comparison: expr (comp_op expr)*
comparison = Concatenation(expr, Concatenation(comp_op, expr).any)

# not_test: 'not' not_test | comparison
not_test = Concatenation(Repetition.one_or_more('not'), comparison)

# and_test: not_test ('and' not_test)*
and_test = Concatenation(
    not_test,
    Concatenation('and', not_test).any,
)

# or_test: and_test ('or' and_test)*
or_test = Concatenation(
    and_test,
    Concatenation('or', and_test).any,
)

# star_expr: '*' expr
star_expr = Concatenation('*', expr)

# exprlist: (expr|star_expr) (',' (expr|star_expr))* [',']
exprlist = Concatenation(
    (expression|star_expr),
    Concatenation(',', (expression|star_expr)).any,
    Repetition.optional(',')
)

""" ---> test_nocond: or_test | lambdef_nocond """
test_nocond = Alternation()

# lambdef_nocond: 'lambda' [varargslist] ':' test_nocond
lambdef_nocond = Concatenation('lambda', varargslist.optional, ':', test_nocond)

test_nocond.append(or_test)
test_nocond.append(lambdef_nocond)
""" <--- test_nocond """

""" ---> comp_iter: comp_for | comp_if """
comp_iter = Alternation()

# sync_comp_for: 'for' exprlist 'in' or_test [comp_iter]
sync_comp_for = Concatenation('for', exprlist, 'in', or_test, comp_iter.optional)

# comp_for: ['async'] sync_comp_for
comp_for = Concatenation(Repetition.optional('async'), sync_comp_for)

# comp_if: 'if' test_nocond [comp_iter]
comp_if = Concatenation('if', test_nocond, comp_iter.optional)

comp_iter.append(comp_for)
comp_iter.append(comp_if)
""" <--- comp_iter """

# The reason that keywords are test nodes instead of NAME is that using NAME
# results in an ambiguity. ast.c makes sure it's a NAME.
# "test '=' test" is really "keyword '=' test", but we have no such token.
# These need to be in a single rule to avoid grammar that is ambiguous
# to our LL(1) parser. Even though 'test' includes '*expr' in star_expr,
# we explicitly match '*' here, too, to give it proper precedence.
# Illegal combinations and orderings are blocked in ast.c:
# multiple (test comp_for) arguments are blocked; keyword unpackings
# that precede iterable unpackings are blocked; etc.
# argument: ( test [comp_for] |
#             test '=' test |
#             '**' test |
#             '*' test )
argument = Alternation(
    Concatenation(_test, comp_for.optional),
    Concatenation(_test, '=', _test),
    Concatenation('**', _test),
    Concatenation('*', _test),
)

# arglist: argument (',' argument)*  [',']
arglist = Concatenation(argument, Concatenation(',', argument).any, Repetition.optional(','))

# dictorsetmaker: ( ((test ':' test | '**' expr)
#                    (comp_for | (',' (test ':' test | '**' expr))* [','])) |
#                   ((test | star_expr)
#                    (comp_for | (',' (test | star_expr))* [','])) )
dictorsetmaker = Alternation(
    Concatenation(
        Concatenation(test, ':', test) | Concatenation('**', expr),
        Alternation(
            comp_for,
            Concatenation(
                Concatenation(
                    ',',
                    Alternation(
                        Concatenation(test, ':', test),
                        Concatenation('**', expr)
                    )
                ).any,
                Repetition.optional(',')
            )
        )
    ),
    Concatenation(
        _test | star_expr,
        comp_for | Concatenation(Concatenation(',', (_test | star_expr)).any, Repetition.optional(','))
    )
)

# testlist_comp: (test|star_expr) ( comp_for | (',' (test|star_expr))* [','] )
testlist_comp = Concatenation(
    (_test|star_expr),
    Alternation(
        comp_for,
        Concatenation(
            Concatenation(',', (_test|star_expr)).any,
            Repetition.optional(',')
        )
    )
)

# trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
trailer = Alternation(
    Concatenation('(', arglist.optional, ')'),
    Concatenation('[', subscriptlist, ']'),
    Concatenation('.', NAME),
)

# atom: ('(' [yield_expr|testlist_comp] ')' |
#        '[' [testlist_comp] ']' |
#        '{' [dictorsetmaker] '}' |
#        NAME | NUMBER | STRING+ | '...' | 'None' | 'True' | 'False')
atom = Alternation(
    Concatenation('(', Alternation(yield_expr, testlist_comp).optional, ')'),
    Concatenation('[', testlist_comp.optional, ']'),
    Concatenation('{', dictorsetmaker.optional, '}'),
    NAME,
    NUMBER,
    STRING,
    stringliteral,
    '...',
    'None',
    'True',
    'False',
)

# atom_expr: ['await'] atom trailer*
atom_expr = Concatenation(Repetition.optional('await'), atom, trailer.any)

""" ---> factor: ('+'|'-'|'~') factor | power """
factor = Concatenation(Alternation('+', '-', '~').any)

# power: atom_expr ['**' factor]
power = Concatenation(atom_expr, Concatenation('**', factor).optional)

factor.append(power)
""" <--- factor """

# term: factor (('*'|'@'|'/'|'%'|'//') factor)*
term = Concatenation(factor, Concatenation(Alternation('*', '@', '/', '%', '//'), factor).any)

# arith_expr: term (('+'|'-') term)*
arith_expr = Concatenation(term, Concatenation(Alternation('+', '-'), term).any)

# shift_expr: arith_expr (('<<'|'>>') arith_expr)*
shift_expr = Concatenation(arith_expr, Concatenation(Alternation('<<', '>>'), arith_expr).any)

# and_expr: shift_expr ('&' shift_expr)*
and_expr = Concatenation(shift_expr, Concatenation('&', shift_expr).any)

# xor_expr: and_expr ('^' and_expr)*
xor_expr = Concatenation(and_expr, Concatenation('^', and_expr).any)

expression.append(xor_expr)
expression.append(Concatenation('|', xor_expr).any)

""" <--- expression """

test.append(
    Concatenation(
        or_test,
        Concatenation(
            'if',
            or_test,
            'else',
            test
        ).optional,
    ),
)
test.append(lambdef)
""" <--- test """

# @group Statements

# testlist_star_expr: (test|star_expr) (',' (test|star_expr))* [',']
testlist_star_expr = Concatenation(
    Alternation(
        test,
        star_expr,
    ),
    Concatenation(',', Alternation(test, star_expr)).any,
    Repetition.optional(','),
)

# For normal and annotated assignments, additional restrictions enforced by the interpreter

# annassign: ':' test ['=' test]
annassign = Concatenation(':', _test, Concatenation('=', _test).optional)

# augassign: ('+=' | '-=' | '*=' | '@=' | '/=' | '%=' | '&=' | '|=' | '^=' |
#             '<<=' | '>>=' | '**=' | '//=')
augassign = Alternation(
    '+=',
    '-=',
    '*=',
    '@=',
    '/=',
    '%=',
    '&=',
    '|=',
    '^=',
    '<<=',
    '>>=',
    '**=',
    '//='
)

# expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|testlist) |
#                      ('=' (yield_expr|testlist_star_expr))*)
expr_stmt = Concatenation(
    testlist_star_expr,
    Alternation(
        annassign,
        Concatenation(augassign, (yield_expr|testlist)),
        Concatenation(
            '=',
            Alternation(yield_expr, testlist_star_expr),
        ).any,
    ),
)

# del_stmt: 'del' exprlist
del_stmt = Concatenation('del', exprlist)

# pass_stmt: 'pass'
pass_stmt = 'pass'

# break_stmt: 'break'
break_stmt = 'break'

# continue_stmt: 'continue'
continue_stmt =  'continue'

# return_stmt: 'return' [testlist]
return_stmt = Concatenation('return', testlist.optional)

# yield_stmt: yield_expr
yield_stmt = yield_expr

# raise_stmt: 'raise' [_test ['from' _test]]
raise_stmt = Concatenation('raise', Concatenation(_test, Concatenation('from', _test).optional).optional)

# flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
flow_stmt = Alternation(break_stmt, continue_stmt, return_stmt, raise_stmt, yield_stmt)

# dotted_name: NAME ('.' NAME)*
dotted_name = Concatenation(NAME, Concatenation('.', NAME).any)

# dotted_as_name: dotted_name ['as' NAME]
dotted_as_name = Concatenation(dotted_name, Concatenation('as', NAME).optional)

# dotted_as_names: dotted_as_name (',' dotted_as_name)*
dotted_as_names = Concatenation(dotted_as_name, Concatenation(',', dotted_as_name).any)

# import_name: 'import' dotted_as_names
import_name = Concatenation('import', dotted_as_names)

# import_as_name: NAME ['as' NAME]
import_as_name = Concatenation(NAME, Concatenation('as', NAME).optional)

# import_as_names: import_as_name (',' import_as_name)* [',']
import_as_names = Concatenation(import_as_name, Concatenation(',', import_as_name).any, Repetition.optional(','))

# note below: the ('.' | '...') is necessary because '...' is tokenized as ELLIPSIS
# import_from: ('from' (('.' | '...')* dotted_name | ('.' | '...')+)
#               'import' ('*' | '(' import_as_names ')' | import_as_names))
import_from = Concatenation(
    'from',
    Alternation(
        Concatenation(Alternation('.', '...').any, dotted_name),
        Alternation('.', '...').one_or_more
    ),
    'import',
    Alternation(
        '*',
        Concatenation('(', import_as_names, ')'),
        import_as_names
    )
)

# import_stmt: import_name | import_from
import_stmt = import_name | import_from

# global_stmt: 'global' NAME (',' NAME)*
global_stmt = Concatenation('global', NAME, Concatenation(',', NAME).any)

# nonlocal_stmt: 'nonlocal' NAME (',' NAME)*
nonlocal_stmt = Concatenation('nonlocal', NAME, Concatenation(',', NAME).any)

# assert_stmt: 'assert' test [',' test]
assert_stmt = Concatenation('assert', _test, Concatenation(',', _test).optional)

# small_stmt: (expr_stmt | del_stmt | pass_stmt | flow_stmt |
#              import_stmt | global_stmt | nonlocal_stmt | assert_stmt)
small_stmt = Alternation(
    expr_stmt,
    del_stmt,
    pass_stmt,
    flow_stmt,
    import_stmt,
    global_stmt,
    nonlocal_stmt,
    assert_stmt,
)

# simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
SimpleStatement = Concatenation(small_stmt, Concatenation(';', small_stmt).any, Repetition.optional(';'))

# NB compile.c makes sure that the default except clause is last
# except_clause: 'except' [test ['as' NAME]]
except_clause = Concatenation('except', Concatenation(_test, Concatenation('as', NAME).optional))

# tfpdef: NAME [':' test]
tfpdef = Concatenation(NAME, Concatenation(':', _test).optional)

# typedargslist: (tfpdef ['=' test] (',' tfpdef ['=' test])* [',' [
#         '*' [tfpdef] (',' tfpdef ['=' test])* [',' ['**' tfpdef [',']]]
#       | '**' tfpdef [',']]]
#   | '*' [tfpdef] (',' tfpdef ['=' test])* [',' ['**' tfpdef [',']]]
#   | '**' tfpdef [','])
typedargslist = Alternation(
    Concatenation(
        tfpdef,
        Concatenation('=', _test),
        Concatenation(
            ',',
            tfpdef,
            Concatenation('=', _test).optional
        ).any,
        Concatenation(
            ',',
            Concatenation(
                '*',
                tfpdef.optional,
                Concatenation(
                    ',',
                    tfpdef,
                    Concatenation('=', _test).optional
                ).any,
                Alternation(
                    Concatenation(
                        ',',
                        Concatenation('**', tfpdef, Repetition.optional(',')).optional
                    ).optional,
                    Concatenation('**', tfpdef, Repetition.optional(','))
                )
            ).optional
        ).optional
    ),
    Concatenation('*',
        tfpdef.optional,
        Concatenation(
            ',',
            tfpdef,
            Concatenation('=', _test).optional
        ).any,
        Concatenation(
            ',',
            Concatenation('**', tfpdef, Repetition.optional(',')).optional
        ).optional
    ),
    Concatenation('**', tfpdef, Repetition.optional(','))
)

""" ---> stmt """
# stmt: simple_stmt | compound_stmt
stmt = Alternation()

# suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
suite = SimpleStatement | Concatenation(NEWLINE, INDENT, stmt.one_or_more)

# parameters: '(' [typedargslist] ')'
parameters = Concatenation('(', typedargslist.optional, ')')

# funcdef: 'def' NAME parameters ['->' test] ':' suite
funcdef = Concatenation('def', NAME, parameters, Concatenation('->', _test).optional, ':', suite)

# async_funcdef: 'async' funcdef
async_funcdef = Concatenation('async', funcdef)

# classdef: 'class' NAME ['(' [arglist] ')'] ':' suite
classdef = Concatenation('class', NAME, Concatenation('(', arglist.optional, ')').optional, ':', suite)

# decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
decorator = Concatenation('@', dotted_name, Concatenation('(', arglist.optional, ')'), NEWLINE)

# decorators: decorator+
decorators = decorator.one_or_more

# decorated: decorators (classdef | funcdef | async_funcdef)
decorated = Concatenation(decorators, Alternation(classdef, funcdef, async_funcdef))

# for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
for_stmt = Concatenation('for', exprlist, 'in', testlist, ':', suite, Concatenation('else', ':', suite).optional)

# with_item: test ['as' expr]
with_item = Concatenation(_test, Concatenation('as', expression).optional)

# with_stmt: 'with' with_item (',' with_item)*  ':' suite
with_stmt = Concatenation('with', with_item, Concatenation(',', with_item).any,  ':', suite)

# async_stmt: 'async' (funcdef | with_stmt | for_stmt)
async_stmt = Concatenation('async', Alternation(funcdef, with_stmt, for_stmt))

# if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
if_stmt = Concatenation('if', _test, ':', suite, Concatenation('elif', _test, ':', suite).any, Concatenation('else', ':', suite).optional)

# while_stmt: 'while' test ':' suite ['else' ':' suite]
while_stmt = Concatenation('while', _test, ':', suite, Concatenation('else', ':', suite).optional)

# try_stmt: ('try' ':' suite
#      ((except_clause ':' suite)+
#       ['else' ':' suite]
#       ['finally' ':' suite] |
#      'finally' ':' suite))
try_stmt = Concatenation(
    'try', ':', suite,
    Alternation(
        Concatenation(
            Concatenation(except_clause, ':', suite).one_or_more,
            Concatenation('else', ':', suite).optional,
            Concatenation('finally', ':', suite).optional
        ),
        Concatenation('finally', ':', suite)
    )
)

# compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated | async_stmt
compound_stmt = Alternation(if_stmt, while_stmt, for_stmt, try_stmt, with_stmt, funcdef, classdef, decorated, async_stmt)

stmt.append(SimpleStatement)
stmt.append(compound_stmt)
""" <--- stmt """

# file_input: (NEWLINE | stmt)* ENDMARKER
file_input = Alternation(NEWLINE, stmt).any
