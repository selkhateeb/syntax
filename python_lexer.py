#! /usr/bin/env python
from lexer import LETTER, DIGIT, _, State, RegExp, Lexer, Token, Character

identifier = (LETTER | '_') + (LETTER | DIGIT | '_') *_

keywords = ['and', 'del', 'from', 'not', 'while', 'as', 'elif', 'global', 'or',
            'with', 'assert', 'else', 'if', 'pass', 'yield', 'break', 'except',
            'import', 'print', 'class', 'exec', 'in', 'raise', 'continue',
            'finally', 'is', 'return', 'def', 'for', 'lambda', 'try', ]

whitespace = RegExp('[ \t\f]')+_
newline = Character('\n') + whitespace*_
comments = Character('#') + RegExp('[^\n]')*_
line_continuation = '\\\n'

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

        self / identifier / (lambda: Identifier())
        self / whitespace / (lambda: Whitespace())
        self / comments   / (lambda: Comment())
        self / line_continuation / (lambda: LineContinuation())

        self / newline    >> self.indent

    def indent(self, state, lexer):
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
    lexer.lex('foo bar tar def \n    return \nfinally final \\\nfinally # else    \nelif')
