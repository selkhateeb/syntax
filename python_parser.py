from python_lexer import Identifier, NewLine, Indent, Dedent, Token

from parser import Grammar, TokenClass, _, language

#TODO: what is NAME, NUMBER, STRING
NAME = Identifier
NEWLINE = NewLine
INDENT = Indent
DEDENT = Dedent
NUMBER = Identifier #TODO
STRING = Identifier #TODO
ENDMARKER = Identifier #TODO


class PythonGrammar(Grammar):

    def __init__(self):
        super(PythonGrammar, self).__init__()

    @language
    def single_input(self):
        '''single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
        '''
        return ('|',
                NEWLINE,
                self.simple_stmt,
                ('+', self.compound_stmt, NEWLINE))

    @language
    def file_input(self):
        '''file_input: (NEWLINE | stmt)* ENDMARKER
        '''
        return ('+',
                ('.*', ('|', NEWLINE, self.stmt)),
                ENDMARKER)

    @language
    def eval_input(self):
        '''eval_input: testlist NEWLINE* ENDMARKER
        '''
        return ('+', self.testlist, ('.*', NEWLINE), ENDMARKER)

    @language
    def decorator(self):
        '''decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
        '''
        return ('+', '@', self.dotted_name,
                ('+', '(', ('?', self.arglist), ')'), NEWLINE)

    @language
    def decorators(self):
        '''decorators: decorator+
        '''
        return ('.+', self.decorator)

    @language
    def decorated(self):
        '''decorated: decorators (classdef | funcdef)
        '''
        return ('+', self.decorators, ('|', self.classdef, self.funcdef))

    @language
    def funcdef(self):
        '''funcdef: 'def' NAME parameters ':' suite
        '''
        return ('+', 'def', NAME, self.parameters, ':', self.suite)

    @language
    def parameters(self):
        '''parameters: '(' [varargslist] ')'
        '''
        return ('+', '(', ('?', self.varargslist), ')')

    @language
    def varargslist(self):
        '''varargslist:
        (
         (fpdef ['=' test] ',')*
         ('*' NAME [',' '**' NAME] | '**' NAME) |
         fpdef ['=' test] (',' fpdef ['=' test])* [','])
        '''
        return ('|',
                ('+',
                ('.*', ('+', self.fpdef, ('?', ('+', '=', self.test)), ',')),
                 ('|',
                 ('+', '*', NAME, ('?', ('+', ',', '**', NAME))),
                  ('+', '**', NAME))),
                ('+', self.fpdef, ('?', ('+', '=', self.test)),
                 ('.*', ('+', ',', self.fpdef, ('?', ('+', '=', self.test)))),
                 ('?', ',')))

    @language
    def fpdef(self):
        '''fpdef: NAME | '(' fplist ')'
        '''
        return ('|',
                NAME,
                ('+', '(', self.fplist, ')'))

    @language
    def fplist(self):
        '''fplist: fpdef (',' fpdef)* [',']
        '''
        return ('+', self.fpdef,
                ('.*', ('+', ',', self.fpdef)),
                ('?', ','))

    @language
    def stmt(self):
        '''stmt: simple_stmt | compound_stmt
        '''
        return ('|', self.simple_stmt, self.compound_stmt)

    @language
    def simple_stmt(self):
        '''simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
        '''
        return ('+', self.small_stmt,
                ('.*', ('+', ';', self.small_stmt)),
                ('?', ';'),
                NEWLINE)

    @language
    def small_stmt(self):
        '''small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
             import_stmt | global_stmt | exec_stmt | assert_stmt)
        '''
        return ('|', self.expr_stmt, self.print_stmt, self.del_stmt,
                self.pass_stmt, self.import_stmt, self.global_stmt,
                self.expr_stmt, self.assert_stmt)

    @language
    def expr_stmt(self):
        '''expr_stmt: testlist (augassign (yield_expr|testlist) |
                     ('=' (yield_expr|testlist))*)
        '''
        return ('+', self.testlist,
                ('|', ('+', self.augassign,
                       ('|', self.yield_expr, self.testlist)),
                 ('.*', ('+', '=', ('|', self.yield_expr, self.testlist)))))

    @language
    def augassign(self):
        '''augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
            '<<=' | '>>=' | '**=' | '//=')
        '''
        return ('|', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=',
                '<<=', '>>=', '**=', '//=')


    @language
    def print_stmt(self):
        '''print_stmt: 'print' ( [ test (',' test)* [','] ] |
                       '>>' test [ (',' test)+ [','] ] )
        '''
        return ('+', 'print',
                ('|', ('?', ('+', self.test, ('.*', ('+', ',', self.test)),
                             ('?', ','))),
                 ('+', '>>', self.test, ('?', ('+',
                                               ('.+', ('+', ',', self.test)),
                                               ',')))))

    @language
    def del_stmt(self):
        '''del_stmt: 'del' exprlist
        '''
        return ('+', 'del', self.exprlist)

    @language
    def pass_stmt(self):
        '''pass_stmt: 'pass'
        '''
        return 'pass'


    @language
    def flow_stmt(self):
        '''flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt
        | yield_stmt
        '''
        return ('|', self.break_stmt, self.continue_stmt, self.return_stmt,
                self.raise_stmt, self.yield_stmt)

    def break_stmt(self):
        '''break_stmt: 'break'
        '''
        return 'break'

    def continue_stmt(self):
        '''continue_stmt: 'continue'
        '''
        return 'continue'

    @language
    def return_stmt(self):
        '''return_stmt: 'return' [testlist]
        '''
        return ('+', 'return', ('?', self.testlist))

    def yield_stmt(self):
        '''yield_stmt: yield_expr
        '''
        return self.yield_expr

    @language
    def raise_stmt(self):
        '''raise_stmt: 'raise' [test [',' test [',' test]]]
        '''
        return ('+', 'raise',
                ('?', ('+', self.test,
                       ('+', ',', self.test, ('?', ('+', ',', self.test))))))

    @language
    def import_stmt(self):
        '''import_stmt: import_name | import_from
        '''
        return ('|', self.import_name, self.import_from)


    @language
    def import_name(self):
        '''import_name: 'import' dotted_as_names
        '''
        return ('+', 'import', self.dotted_as_names)


    @language
    def import_from(self):
        '''import_from: ('from' ('.'* dotted_name | '.'+)
              'import' ('*' | '(' import_as_names ')' | import_as_names))
        '''
        return ('+', 'from', ('|', ('+', ('.*', '.'), self.dotted_name),
                              ('.+', '.')),
                'import', ('|', '*', ('+', '(', self.import_as_names, ')'),
                           self.import_as_names))

    @language
    def import_as_name(self):
        '''import_as_name: NAME ['as' NAME]
        '''
        return ('+', NAME, ('?', ('+', 'as', NAME)))

    @language
    def dotted_as_name(self):
        '''dotted_as_name: dotted_name ['as' NAME]
        '''
        return ('+', self.dotted_name, ('?', ('+', 'as', NAME)))

    @language
    def import_as_names(self):
        '''import_as_names: import_as_name (',' import_as_name)* [',']
        '''
        return ('+', self.import_as_name,
                ('.*', ('+', ',', self.import_as_name)),
                ('?', ','))

    @language
    def dotted_as_names(self):
        '''dotted_as_names: dotted_as_name (',' dotted_as_name)*
        '''
        return ('+', self.dotted_as_name,
                ('.*', ('+', ',', self.dotted_as_name)))

    @language
    def dotted_name(self):
        '''dotted_name: NAME ('.' NAME)*
        '''
        return ('+', NAME, ('.*', ('+', '.', NAME)))

    @language
    def global_stmt(self):
        '''global_stmt: 'global' NAME (',' NAME)*
        '''
        return ('+', 'global', NAME, ('.*', ('+', ',', NAME)))

    @language
    def exec_stmt(self):
        '''exec_stmt: 'exec' expr ['in' test [',' test]]
        '''
        return ('+', 'exec', self.expr,
                ('?', ('+', 'in', self.test, ('?', ('+', ',', self.test)))))

    @language
    def assert_stmt(self):
        '''assert_stmt: 'assert' test [',' test]
        '''
        return ('+', 'assert', self.test, ('?', ('+', ',', self.test)))


    @language
    def compound_stmt(self):
        '''compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt
        | with_stmt | funcdef | classdef | decorated
        '''
        return ('+', self.if_stmt, self.while_stmt, self.for_stmt,
                self.try_stmt, self.with_stmt, self.funcdef, self.classdef,
                self.decorated)

    @language
    def if_stmt(self):
        '''if_stmt: 'if' test ':' suite ('elif' test ':' suite)*
        ['else' ':' suite]
        '''
        return ('+', 'if', self.test, ':', self.suite,
                ('.*', ('+', 'elif', self.test, ':', self.suite)),
                ('?', ('+', 'else', ':', self.suite)))

    @language
    def while_stmt(self):
        '''while_stmt: 'while' test ':' suite ['else' ':' suite]
        '''
        return ('+', 'while', self.test, ':', self.suite,
                ('?', ('+', 'else', ':', self.suite)))

    @language
    def for_stmt(self):
        '''for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
        '''
        return ('+', 'for', self.exprlist, 'in', self.testlist, ':',
                self.suite, ('?', ('+', 'else', ':', self.suite)))

    @language
    def try_stmt(self):
        '''try_stmt: ('try' ':' suite
              ((except_clause ':' suite)+ ['else' ':' suite]
              ['finally' ':' suite] |
              'finally' ':' suite))
        '''
        return ('+', 'try', ':', self.suite,
                ('|',
                 ('+',
                  ('.+', ('+', self.except_clause, ':', self.suite)),
                  ('?', ('+', 'else', ':', self.suite)),
                  ('?', ('+', 'finally', ':', self.suite))),
                 ('+', 'finally', ':', self.suite)))

    @language
    def with_stmt(self):
        '''with_stmt: 'with' with_item (',' with_item)*  ':' suite
        '''
        return ('+', 'with', self.with_item,
                ('.*', ('+', ',', self.with_item)), ':', self.suite)

    @language
    def with_item(self):
        '''with_item: test ['as' expr]
        '''
        return ('+', self.test, ('?', ('+', 'as', self.expr)))

    @language
    def except_clause(self):
        ''' except_clause: 'except' [test [('as' | ',') test]]
        '''
        return ('+', 'except',
                ('?', ('+', self.test, ('?', ('+', ('|', 'as', ','),
                                              self.test)))))

    @language
    def suite(self):
        '''suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
        '''
        return ('|', self.simple_stmt,
                ('+', NEWLINE, INDENT, ('.+', self.stmt), DEDENT))

    @language
    def testlist_safe(self):
        '''testlist_safe: old_test [(',' old_test)+ [',']]
        '''
        return ('+', self.old_test,
                ('?',
                 ('+', ('.+', ('+', ',', self.old_test)),
                  ('?', ','))))

    @language
    def old_test(self):
        '''old_test: or_test | old_lambdef
        '''
        return ('|', self.or_test, self.old_lambdef)

    @language
    def old_lambdef(self):
        '''old_lambdef: 'lambda' [varargslist] ':' old_test
        '''
        return ('+', 'lambda', ('?', self.varargslist), ':', self.old_test)

    @language
    def test(self):
        return ('|',
                ('?', ('+', 'if', self.or_test, 'else', self.test)),
                self.lambdef)

    @language
    def or_test(self):
        '''or_test: and_test ('or' and_test)*
        '''
        return ('+', self.and_test, ('.*', ('+', 'or', self.and_test)))

    @language
    def and_test(self):
        '''and_test: not_test ('and' not_test)*
        '''
        return ('+', self.not_test, ('.*', ('+', 'and', self.not_test)))

    @language
    def not_test(self):
        '''not_test: 'not' not_test | comparison
        '''
        return ('|', ('+', 'not', self.not_test), self.comparison)

    @language
    def comparison(self):
        '''comparison: expr (comp_op expr)*
        '''
        return ('+', self.expr, ('.*', ('+', self.comp_op, self.expr)))

    @language
    def comp_op(self):
        '''comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'
                    |'is' 'not'
        '''
        return ('|', '<', '>', '==', '>=', '<=', '<>',
                '!=', 'in', ('+', 'not', 'in'), 'is', ('+', 'is', 'not'))

    @language
    def expr(self):
        '''expr: xor_expr ('|' xor_expr)*
        '''
        return ('+', self.xor_expr, ('.*', ('+', '|', self.xor_expr)))

    @language
    def xor_expr(self):
        '''xor_expr: and_expr ('^' and_expr)*
        '''
        return ('+', self.xor_expr, ('.*', ('+', '^', self.and_expr)))

    @language
    def and_expr(self):
        '''and_expr: shift_expr ('&' shift_expr)*
        '''
        return ('+', ('.*', ('+', '&', self.shift_expr)))

    @language
    def shift_expr(self):
        '''shift_expr: arith_expr (('<<'|'>>') arith_expr)*
        '''
        return ('+', self.arith_expr,
                ('.*', ('+', ('|', '<<', '>>'), self.arith_expr)))

    @language
    def arith_expr(self):
        '''arith_expr: term (('+'|'-') term)*
        '''
        return ('+', self.term, ('.*', ('+', ('|', '+', '-'), self.term)))

    @language
    def term(self):
        '''term: factor (('*'|'/'|'%'|'//') factor)*
        '''
        return ('+', self.factor,
                ('.*', ('+', ('|', '*', '/', '%', '//'), self.factor)))

    @language
    def factor(self):
        '''factor: ('+'|'-'|'~') factor | power
        '''
        return ('|', ('+', ('|', '+', '-', '~'), self.factor), self.power)

    @language
    def power(self):
        '''power: atom trailer* ['**' factor]
        '''
        return ('+', self.atom, ('.*', self.trailer),
                ('?', ('+', '**', self.factor)))

    @language
    def atom(self):
        '''
        atom: ('(' [yield_expr|testlist_comp] ')' |
              '[' [listmaker] ']' |
              '{' [dictorsetmaker] '}' |
              '`' testlist1 '`' |
              NAME | NUMBER | STRING+)
        '''
        return ('|',
                ('+', '(',
                 ('?', ('|', self.yield_expr, self.testlist_comp)),
                 ')'),
                ('+', '[', ('?', self.listmaker), ']'),
                ('+', '{', ('?', self.dictorsetmaker), '}'),
                ('+', '`', self.testlist1, '`'),
                NAME, NUMBER, ('.+', STRING))

    @language
    def listmaker(self):
        '''listmaker: test ( list_for | (',' test)* [','] )
        '''
        return ('+', self.test,
                ('|', self.list_for,
                 ('+', ('.*', ('+', ',', self.test)), ('?', ','))))

    @language
    def testlist_comp(self):
        '''testlist_comp: test ( comp_for | (',' test)* [','] )
        '''
        return ('+', self.test,
                ('|', self.comp_for,
                 ('+', ('.*', ('+', ',', self.test)), ('?', ','))))

    @language
    def lambdef(self):
        '''lambdef: 'lambda' [varargslist] ':' test
        '''
        return ('+', 'lambda', ('?', self.varargslist), ':', self.test)

    @language
    def trailer(self):
        '''trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
        '''
        return ('|',
                ('+', '(', ('?', self.arglist), ')'),
                ('+', '[', self.subscriptlist, ']'),
                ('+', '.', NAME))

    @language
    def subscriptlist(self):
        '''subscriptlist: subscript (',' subscript)* [',']
        '''
        return ('+', self.subscript,
                ('.*', ('+', ',', self.subscript)), ('?', ','))

    @language
    def subscript(self):
        '''subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
        '''
        return ('|',
                ('+', '.', '.', '.'),
                self.test,
                ('+', ('?', self.test), ':', ('?', self.test),
                 ('?', self.sliceop)))

    @language
    def sliceop(self):
        '''sliceop: ':' [test]
        '''
        return ('+', ':', ('?', self.test))

    @language
    def exprlist(self):
        '''exprlist: expr (',' expr)* [',']
        '''
        return ('+', self.expr, ('.*', ('+', ',', self.expr)), ('?', ','))

    @language
    def testlist(self):
        '''testlist: test (',' test)* [',']
        '''
        return ('+', self.test, ('.*', ('+', ',', self.test)), ('?', ','))


    @language
    def dictorsetmaker(self):
        ''' dictorsetmaker:
        ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
          (test (comp_for | (',' test)* [','])) )
        '''
        return ('|',
                ('+', self.test, ':', self.test,
                 ('|',
                  self.comp_for,
                  ('+', ('.*', ('+', ',', self.test, ':', self.test)),
                   ('?', ',')))),
                ('+', self.test,
                 ('|', self.comp_for,
                  ('+', ('.*', ('+', ',', self.test)),
                   ('?', ',')))))

    @language
    def classdef(self):
        '''classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
        '''
        return ('+', 'class', NAME,
                ('?', ('+', '(', ('?', self.testlist), ')')),
                ':', self.suite)

    @language
    def arglist(self):
        '''arglist: (argument ',')* (argument [',']
                         |'*' test (',' argument)* [',' '**' test]
                         |'**' test)
        '''
        return ('+',
                ('.*', ('+', self.argument, ',')),
                ('|',
                 ('+', self.argument, ('?', ',')),
                 ('+', '*', self.test,
                  ('.*', ('+', ',', self.argument)),
                  ('?', ('+', ',', '**', self.test))),
                 ('+', '**', self.test)))


    @language
    def argument(self):
        '''argument: test [comp_for] | test '=' test
        '''
        return ('|',
                ('+', self.test, ('?', self.comp_for)),
                ('+', self.test, '=', self.test))

    @language
    def list_iter(self):
        '''list_iter: list_for | list_if
        '''
        return ('|', self.list_for, self.list_if)

    @language
    def list_for(self):
        '''list_for: 'for' exprlist 'in' testlist_safe [list_iter]
        '''
        return ('+', 'for', self.exprlist, 'in',
                self.testlist_safe, ('?', self.list_iter))

    @language
    def list_if(self):
        '''list_if: 'if' old_test [list_iter]
        '''
        return ('+', 'if', self.old_test, ('?', self.list_iter))

    @language
    def comp_iter(self):
        '''comp_iter: comp_for | comp_if
        '''
        return ('|', self.comp_for, self.comp_if)

    @language
    def comp_for(self):
        '''comp_for: 'for' exprlist 'in' or_test [comp_iter]
        '''
        return ('+', 'for', self.exprlist, 'in', self.or_test,
                ('?', self.comp_iter))

    @language
    def comp_if(self):
        '''comp_if: 'if' old_test [comp_iter]
        '''
        return ('+', 'if', self.old_test, ('?', self.comp_iter))


    @language
    def testlist1(self):
        '''testlist1: test (',' test)*
        '''
        return ('+', self.test, ('.*', ('+', ',', self.test)))

    @language
    def yield_expr(self):
        '''yield_expr: 'yield' [testlist]
        '''
        return ('+', 'yield', ('?', self.testlist))


def T(v):
    t = Token()
    t.value = v
    return t

if __name__ == '__main__':
    g = PythonGrammar()

    g.single_input()
    print g.file_input()
    g.eval_input()

    d = g.file_input()
    id = Identifier()
    id.value = 're'
    for t in [T('import'), id]:
        d = d.derive(t)
        print d
