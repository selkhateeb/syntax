#! /usr/bin/env python
import sys
from syntax import LETTER, DIGIT, _, State, RegExp, Lexer, Token, Character
from syntax import Optional, HEX

identifier = (LETTER | '_') + (LETTER | DIGIT | '_') *_

keywords = ['and', 'del', 'from', 'not', 'while', 'as', 'elif', 'global', 'or',
            'with', 'assert', 'else', 'if', 'pass', 'yield', 'break', 'except',
            'import', 'print', 'class', 'exec', 'in', 'raise', 'continue',
            'finally', 'is', 'return', 'def', 'for', 'lambda', 'try', ]

tokens = '( ) [ ] { } @ : . , ` ; = += -= *= /= //= %= &= |= ^= >>= <<= **='.split()
operators = '+ - * ** / // % << >> & | ^ ~ < > <= >= == != <>'.split()

ws = RegExp('[ \t\f]')
whitespace = RegExp('[ \t\f]')+_
newline = Character('\n') + ws*_
comments = Character('#') + RegExp('[^\\n]')*_
line_continuation = '\\\n'

escapeseq = Character('\\') + RegExp(r'[\x00-\x7F]')
longstringchar = RegExp('[^\\\]')
shortstringchar_single_qoute =  RegExp("[^\\\\\n']")
shortstringchar_double_qoute =  RegExp('[^\\\\\n"]')
longstringitem = longstringchar | escapeseq
shortstringitem_single_qoute =  shortstringchar_single_qoute | escapeseq
shortstringitem_double_qoute =  shortstringchar_double_qoute | escapeseq
q = Character("'")
dq = Character('"')
longstring =  ((q + q + q + longstringitem*_ + q + q + q)
               | (dq + dq + dq + longstringitem*_ + dq + dq + dq))
shortstring = (q + shortstringitem_single_qoute*_ + q
               | dq + shortstringitem_double_qoute*_ + dq)

stringprefix =  (Character("r")
                 | Character("u")
                 | Character("ur")
                 | Character("R")
                 | Character("U")
                 | Character("UR")
                 | Character("Ur")
                 | Character("uR")
                 | Character("b")
                 | Character("B")
                 | Character("br")
                 | Character("Br")
                 | Character("bR")
                 | Character("BR"))
stringliteral =  Optional(stringprefix) + (shortstring | longstring)

digit = DIGIT
hexdigit = HEX
nonzerodigit =  RegExp('[1-9]')
octdigit =  RegExp('[0-7]')
bindigit =  RegExp('[01]')
octinteger = Character("0") + RegExp('[oO]') + octdigit+_ | Character("0") + octdigit+_
hexinteger = Character("0") + RegExp('[xX]') + hexdigit+_
bininteger = Character("0") + RegExp('[bB]') + bindigit+_
decimalinteger =  nonzerodigit + digit*_ | "0"
integer = decimalinteger | octinteger | hexinteger | bininteger
longinteger =  integer + RegExp("[lL]")


class Identifier(Token): pass
class Keyword(Token): pass
class Whitespace(Token): pass
class NewLine(Token): pass
class Comment(Token): pass
class LineContinuation(Token): pass
class Indent(Token): pass
class Dedent(Token): pass

# TODO: implement rules for the following tokens
class StringLiteral(Token): pass
class Integer(Token): pass
class LongInteger(Token): pass
class FloatInteger(Token): pass
class ImagNumber(Token): pass


class Main(State):
    '''Entry point for the lexer.
    '''

    def __init__(self):
        super(Main, self).__init__()
        self.indentation = [0]

        for keyword in keywords:
            self / keyword / (lambda: Keyword())

        for token in tokens:
            self / token / (lambda: Token())

        for operator in operators:
            self / operator / (lambda: Token())

        self / identifier        / (lambda: Identifier())
        self / whitespace        / (lambda: Whitespace())
        self / comments          / (lambda: Comment())
        self / line_continuation / (lambda: LineContinuation())
#        self / stringliteral     /
        self / shortstring       / (lambda: StringLiteral())
        self / longstring        / (lambda: StringLiteral())


        self / integer           / (lambda: Integer())
        self / longinteger       / (lambda: LongInteger())

        #self / newline    >> self.indent
        self / newline    / (lambda: NewLine())


    def indent(self, state, lexer):
        print 'indent'
        indent = state.matched_input.replace('\n', '').replace('\t', '        ')
        level = len(indent)
        if level > self.indentation[-1]:
            self.indentation.append(level)
            token = Indent()
            token.value = state.matched_input
            token.position = lexer.position
            lexer.emit(token, state)
        elif level < self.indentation[-1] and level in self.indentation:
            while level != self.indentation[-1]:
                self.indentation.pop()
                token = Dedent()
                token.value = state.matched_input  # TODO: should we shrink the input as we dedent?
                token.position = lexer.position    # TODO: This might screw up position calculations.
                lexer.emit(token, state)

        else:  # level == self.indentation[-1]
            token = NewLine()
            token.value = state.matched_input
            token.position = lexer.position
            lexer.emit(token, state)

        state.matched_input = ''
        return self


class Output(object):
    def add(self, token):
        print("%s:'%s':%s" % (token.__class__.__name__, token.value, token.position))

if __name__ == '__main__':
    lexer = Lexer(initial_state=Main, output=Output())
    lexer.lex(open(sys.argv[1]).read())
    #lexer.lex('\n                                   ')
