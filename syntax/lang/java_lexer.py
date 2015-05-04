#! /usr/bin/env python

import sys
from lexer import LETTER, DIGIT, _, State, RegExp, Lexer, Token, Character
from lexer import Optional, HEX
from parser import Grammar, TokenClass, _, language

identifier = (LETTER | '_') + (LETTER | DIGIT | '_') * _

keywords = ['abstract', 'continue', 'for', 'new', 'switch', 'assert',
            'default', 'goto', 'package', 'synchronized', 'boolean', 'do',
            'if', 'private', 'this', 'break', 'double', 'implements',
            'protected', 'throw', 'byte', 'else', 'import', 'public',
            'throws', 'case', 'enum', 'instanceof', 'return', 'transient',
            'catch', 'extends', 'int', 'short', 'try', 'char', 'final',
            'interface', 'static', 'void', 'class', 'finally', 'long',
            'strictfp', 'volatile', 'const', 'float', 'native', 'super',
            'while']

tokens = '( ) [ ] { } @ : . , ` ; = += -= *= /= //= %= &= |= ^= >>= <<= **='.split()
operators = '+ - * ** / % << >> & | ^ ~ < > <= >= == != <>'.split()
ws = RegExp('[ \t\f]')
whitespace = RegExp('[ \t\f]')+_
newline = Character('\n')
comments = Character('/') + Character('/') + RegExp('[^\\n]')*_
multiline_comments = (Character('/') + Character('*') +
                      (RegExp('[^*]') + RegExp('[^/]'))*_ +
                      Character('*') + Character('/'))

# Literals
number = DIGIT +_
binary = Character('0') + RegExp('[bB]') + RegExp('[10]') + _
octal = Character('0') + RegExp('[0-7]') + _
hexadecimal = Character("0") + RegExp('[xX]') + HEX + _

string = Character('"') + RegExp('[^"]')*_ + Character('"')

class Identifier(Token): pass
class Keyword(Token): pass
class Whitespace(Token): pass
class NewLine(Token): pass
class Comment(Token): pass
class Number(Token): pass
class String(Token): pass
class Boolean(Token): pass

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

        for boolean in ('true', 'false'):
            self / boolean / (lambda: Boolean())

        self / identifier         / (lambda: Identifier())
        self / whitespace         / (lambda: Whitespace(skip=True))
        self / comments           / (lambda: Comment(skip=True))
        self / multiline_comments / (lambda: Comment(skip=True))
        self / newline            / (lambda: NewLine(skip=True))
        self / number             / (lambda: Number())
        self / string             / (lambda: String())

class Output(object):
    def __init__(self):
        self.tokens = []

    def add(self, token):
        self.tokens.append(token)
        #sys.stdout.write(token.value)
        print("%s:'%s':%s" % (token.__class__.__name__, token.value, token.position))

def Package(foo):
    print foo

class JavaGrammar(Grammar):

    def __init__(self):
        super(JavaGrammar, self).__init__()

    @language
    def main(self):
        return ('+',
                self.package_statment,
                ('.*', self.import_statment),
                ('.*', self.class_def))

    @language
    def package_statment(self):
        '''package com.foo;
        '''
        return ('=>', Package,
                ('+',
                 'package',
                 Identifier,
                 ('.*', ('+', '.', Identifier)),
                 ';'))

    @language
    def import_statment(self):
        '''package com.foo;
        '''
        return ('=>', Package,
                ('+',
                 'import',
                 Identifier,
                 ('.*', ('+', '.', Identifier)),
                 ';'))

    @language
    def class_def(self):
        return ('=>', Package,
                ('+',
                 'public',
                 ('?', 'abstract'),
                 'class',
                 Identifier,
                 ('?', ('+', 'extends', Identifier)),
                 '{',
                 ('.*', self.field),
                 '}'))

    @language
    def annotation(self):
        return ('+',
                '@',
                Identifier,
                ('?', ('+',
                       '(', Identifier, '=', self.value,
                       ('.*', ('+', ',', Identifier, '=', self.value)),
                       ')')))

    @language
    def value(self):
        return ('|',
                Number,
                String,
                Boolean)

    @language
    def identifier_dotted(self):
        return ('+',
                Identifier,
                ('.*', ('+', '.', Identifier)))

    @language
    def field(self):
        return ('+',
                ('?', self.annotation),
                ('|', 'public', 'protected', 'private'),
                self.identifier_dotted,
                Identifier,
                ';')


if __name__ == '__main__':
    out = Output()
    lexer = Lexer(initial_state=Main, output=out)
    lexer.lex(open(sys.argv[1]).read())

    g = JavaGrammar()
    tokens = out.tokens #filter(lambda _: not isinstance(_, (Whitespace, NewLine, Comment)), out.tokens)
    g.derive(tokens)
