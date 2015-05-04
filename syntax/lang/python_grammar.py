#! /usr/bin/env python

from pyparsing import *

# expr_stmt: testlist (augassign (yield_expr|testlist) |
#                      ('=' (yield_expr|testlist))*)



augassign = oneOf('+= -= *= /= %= &= |= ^= <<= >>= **= //=')

comp_op = (oneOf('< > == >= <= <> != in is')
           | (Literal('not') + Literal('in'))
           | (Literal('is') + Literal('not')))







expr = xor_expr ('|' xor_expr)*

comparison = expr + ZeroOrMore(comp_op + expr)

not_test = Keyword('not') + not_test | comparison

and_test = not_test + ZeroOrMore(Keyword('and') + not_test)

or_test = and_test + ZeroOrMore(Keyword('or') + and_test)

test = (or_test + Optional(Keyword('if') + or_test + Keyword('else') + test)
        | lambdef)

testlist = test + ZeroOrMore(',' + test) + Optional(',')

yield_expr = Keyword('yield') + Optional(testlist)

expr_stmt = testlist + (augassign + (yield_expr | testlist) |
                        ZeroOrMore('=' + (yield_expr | testlist)))

