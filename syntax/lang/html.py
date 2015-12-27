#! /usr/bin/env python

import re
import sys

from syntax import LETTER, DIGIT, _, State, RegExp, Lexer, Token, Character
from syntax import Grammar, HEX, language, word, Optional
from syntax import parser


## Lexer Grammer.
start = Character('<') + ( RegExp('[^<>]')+_) + Character('>')
text = RegExp('[^<>]')+_
end = Character('<') + Character('/') + (RegExp('[^<>]')+_) + Character('>')

void_elements = (word('area') | 'base' | 'br' | 'col' | 'command' |
                 'embed' | 'hr' | 'img' | 'input' | 'link' | 'keygen'
                 | 'meta' | 'param' | 'source' | 'track' | 'wbr' | '!DOCTYPE')

void = (Character('<') + void_elements + (RegExp('[^<>]')*_) + Character('>'))
comment = (word('<!--') + (RegExp('.')*_) + word('-->'))


## Tokens emitted by the lexer.
class Start(Token): pass
class End(Token): pass
class Void(Token): pass
class Text(Token): pass
class Comment(Token): pass


class Main(State):
    '''Main starting State for the lexer tokenizer.
    '''

    def __init__(self):
        super(Main, self).__init__()

        self / comment / (lambda: Comment())
        self / end / (lambda: End())
        self / void / (lambda: Void())
        self / start / (lambda: Start())
        self / text / (lambda: Text())


class Output(object):
    '''Lexer output operations.

    Simply append them to a list of tokens. This is just a simple way to do it.
    We could actually start parsing the tokens as soon as we get them.
    '''
    def __init__(self):
        self.tokens = []

    def add(self, token):
        self.tokens.append(token)


class HtmlGrammar(Grammar):
    '''Parser grammar definitions.
    '''

    def __init__(self):
        super(HtmlGrammar, self).__init__()

    @language
    def main(self):
        return ('=>', node_creator(Node),
                ('.+',
                 ('|', self.void_tag, self.text, self.tag)))

    @language
    def tag(self):
        return ('=>', node_creator(TagNode),
                ('+',
                 Start,
                 ('.*', ('|', self.tag, self.void_tag, self.text)),
                 End))

    @language
    def void_tag(self):
        return ('=>', node_creator(VoidTagNode), Void)

    @language
    def text(self):
        return ('=>', node_creator(TextNode),
                ('|', Text, Comment))


# TODO: This should be translated into __new__
def node_creator(type):
    def _(tokens):
        if tokens:
            return type(tokens)
    return _


class ParseError(Exception): pass


class Node(object):
    def __init__(self, tokens):
        self.children = tokens

    def accept(self, visitor):
        for child in self.children:
            child.accept(visitor)


class TagNode(Node):
    startTagRegExp = re.compile('<([^\s/]+).*>', re.M and re.S)
    endTagRegExp = re.compile('</([^\s]+).*>', re.M and re.S)
    def __init__(self, tokens):
        self.children = []
        self.startTag = self.startTagRegExp.match(tokens[0].value).group(1)
        self.endTag = None
        if len(tokens) > 1 and isinstance(tokens[-1], End):
            self.endTag = self.endTagRegExp.match(tokens[-1].value).group(1)
            if self.endTag != self.startTag:
                error = ParseError('end tag mismatch. expected %s, but '
                                   'got %s' % (self.startTag,
                                               self.endTag))
                error.actual = self.endTag
                error.expected = self.startTag
                raise error

        for token in tokens:
            if isinstance(token, Node):
                self.children.append(token)


        self.text = tokens

    def __repr__(self):
        return 'Node of (%s)' % self.text

    def accept(self, visitor):
        visitor.visitStartTag(self.startTag)
        for child in self.children:
            child.accept(visitor)

        if self.endTag:
            visitor.visitEndTag(self.endTag)


class VoidTagNode(Node):
    def __init__(self, tree):
        self.tag = tree[0]

    def accept(self, visitor):
        visitor.visitVoidTag(self.tag.value)


class TextNode(Node):
    def __init__(self, tree):
        self.text = tree[0]

    def accept(self, visitor):
        visitor.visitText(self.text.value)

class Printer:
    def __init__(self):
        self.indentation = 0
    def visitStartTag(self, tag):
        print '%s<%s>' %('  ' * self.indentation, tag)
        self.indentation += 1

    def visitEndTag(self, tag):
        self.indentation -= 1
        print '%s</%s>' %('  ' * self.indentation, tag)

    def visitVoidTag(self, tag):
        print '%s%s' %('  ' * self.indentation, tag)

    def visitText(self, text):
        print '%s%s' %('  ' * self.indentation, text)


def parse(filename):
    out = Output()
    lexer = Lexer(initial_state=Main, output=out)
    lexer.lex(open(filename).read())

    g = HtmlGrammar()
    d = g.main()
    ds = [d]
    for i, token in enumerate(out.tokens):
        try:
            d = d.derive(token)
            ds.append(d)
            if isinstance(d, parser.Reject):
                print token.value
                raise Exception(str(token))
        except ParseError, e:
            print e
            print('%s:%s' % (token.value, token.position))
            break

    #print d.ast()
    tree = d.ast()[0]
    print tree
    tree.accept(Printer())


if __name__ == '__main__':
    for _ in sys.argv[1:]:
        print _
        parse(_)
