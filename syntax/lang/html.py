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


class Id(Token): pass
class WhiteSpace(Token): pass
class Equal(Token): pass
class StringStart(Token): pass
class StringContent(Token): pass
class StringEnd(Token): pass
class Attribute(Token): pass

id = RegExp('[^\'"<>/=\s]') +_
whitspace = RegExp('\s') +_
attribute = id + Character('=')


class String(State):
    '''
    '''

    def __init__(self, marker):
        super(String, self).__init__()

        self.on(marker).emit_then_switch_to(StringEnd, StartTag)

        self.on( RegExp('[^' + marker + ']')*_ ).emit(StringContent)


class StartTag(State):
    '''Represents everything between '<' and '>'
    '''

    def __init__(self):
        super(StartTag, self).__init__()

        self.on('>').emit_then_switch_to(End, Main)
        self.on('"').emit_then_switch_to(StringStart, lambda: String('"'))
        self.on("'").emit_then_switch_to(StringStart, lambda: String("'"))

        self.on( whitspace ).emit( WhiteSpace )
        self.on( id        ).emit( Id         )
        self.on( attribute ).emit( Attribute  )


class Main(State):
    '''Main starting State for the lexer tokenizer.
    '''

    def __init__(self):
        super(Main, self).__init__()

        #self.on('<').switch_to(StartTag)
        #self.on('<').consume_then_switch_to(StartTag)
        self.on('<').emit_then_switch_to(Start, StartTag)

        # self.on( comment ).emit( lambda: Comment() )
        # self.on( end     ).emit( lambda: End()     )
        # self.on( void    ).emit( lambda: Void()    )
        # self.on( start   ).emit( lambda: Start()   )
        # self.on( text    ).emit( lambda: Text()    )


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


    @language
    def start_tag(self):
        def _(tokens):
            return StartTagNode(tokens[1], tokens[2:-2])

        return ('=>', _,
                ('+', Start, Id, ('.+', self.attribute), End))


    @language
    def attribute(self):

        def attribute(tokens):
            '''
            one of:
             - [ Id ]
             - [ Attribute, Id ]
             - [ Attribute, StringStart, StringContent, StringEnd ]

            '''
            print tokens
            return {
                1: lambda _: AttributeNode(_),
                2: lambda n, v: AttributeNode(n, v),
                4: lambda n,_1, v, _2: AttributeNode(n, v)
            }[len(tokens)](*tokens)


        return ('=>', attribute,
                ('|',
                 Id,
                 ('+', Attribute, Id),
                 ('+', Attribute, StringStart, StringContent, StringEnd)))




class AttributeNode(object):
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def accept(self, visitor):
        vistor.visitAttributeName(self.name)
        if self.value:
            vistor.visitAttributeValue(self.name)

    def __repr__(self):
        return '%s="%s"' % (self.name, self.value)


class StartTagNode(object):

    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes

    def accept(self, visitor):
        visitor.visitStartTagName(self.name)
        for attribute in self.attributes:
            attribute.accept(visitor)

    def __repr__(self):
        return '%s%s' % (self.name, self.attributes)


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
    if sys.argv[1:]:
        for _ in sys.argv[1:]:
            print _
            parse(_)

    else:
        out = Output()
        lexer = Lexer(initial_state=Main, output=out)
        lexer.lex('<starting fr to=a ff="kfljsd">')
        print '\n'.join([str(_) for _ in out.tokens])


        print "Starting to Parse ... "
        g = HtmlGrammar()
        d = g.start_tag()
        #print g.attribute()
        ds = [d]
        for i, token in enumerate(out.tokens):
            if isinstance(token, WhiteSpace):
                continue
            #print token
            try:
                d = d.derive(token)
                ds.append(d)
                #print d
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

