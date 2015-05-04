#! /usr/bin/env python

import re
import sys
import inspect

import lexer


class Language(object):

    def __init__(self):
        self.derivatives = {}

    def is_matchable(self):
        return False

    def derive(self, token):
        if token not in self.derivatives.keys():
            self.derivatives[token] = self._derive(token)
        return self.derivatives[token]

    def _derive(self, token):
        raise Exception('How did you get here? This is an abstract function.')

    def fix_matchable(self, language):
        value = result = False
        while True:
            value = language.is_matchable()
            if result == value:
                break
            result = value
        return result

    def ast(self):
        return []

    def __repr__(self):
        return self.__class__.__name__

    def __add__(self, other):
        if isinstance(other, list):
            assert len(other) == 1
            language = Optional.make(other[0])

        elif other == _:  # one or more
            language = Star.make(self)

        else:
            language = self._grammar.to_language(other)

        and_ = And.make(self, language)
        # TODO: we are passing out hack along the way
        and_._grammar = self._grammar
        return and_

    def __or__(self, other):
        if isinstance(other, list):
            assert len(other) == 1
            language = Optional.make(other[0])

        else:
            language = self._grammar.to_language(other)

        or_ = Or.make(self, language)
        # TODO: we are passing out hack along the way
        or_._grammar = self._grammar
        return or_

    def __mul__(self, other):
        lang = Star.make(self)
        # TODO: we are passing out hack along the way
        lang._grammar = self._grammar
        return lang


class Reject(Language):
    def __init__(self):
        super(Reject, self).__init__()

    def _derive(self, token):
        return self


class Match(Language):
    def __init__(self, ast):
        super(Match, self).__init__()
        self._ast = ast

    def is_matchable(self):
        return True

    def _derive(self, token):
        return reject

    def ast(self):
        return self._ast

reject = Reject()
_ = None


def is_match(language):
    '''Helper function to test if language is an instance of Match.
    '''
    return isinstance(language, Match)


class RegExp(Language):

    def __init__(self, regexp):
        super(RegExp, self).__init__()
        self.regexp = re.compile(regexp)

    def _derive(self, token):
        if self.regexp.match(token.value):
            return Match([token])
        return reject

    def __repr__(self):
        return 'RegExp(%s)' % self.regexp.pattern


class TokenClass(Language):

    def __init__(self, token_class):
        super(TokenClass, self).__init__()
        self.token_class = token_class

    def _derive(self, token):
        if isinstance(token, self.token_class):
            return Match([token])
        return reject

    def __repr__(self):
        return 'TokenClass(%s)' % self.token_class.__name__


class Or(Language):

    def __init__(self, left, right):
        super(Or, self).__init__()
        self.left = left
        self.right = right

    def is_matchable(self):
        return self.left.is_matchable() or self.right.is_matchable()

    def _derive(self, token):
        return Or.make(self.left.derive(token), self.right.derive(token))

    def ast(self):
        left_ast = self.left.ast()
        right_ast = self.right.ast()
        ast = []
        for l in left_ast:
            for r in right_ast:
                ast.extend([l, r])
        return ast

    def __repr__(self):
        return 'Or(%s, %s)' % (self.left, self.right)

    @staticmethod
    def make(left, right):
        if left is reject and right is reject:
            return reject

        if left is reject:
            return right

        if right is reject:
            return left

        # Ambiguity .. return forest for debugging
        if is_match(left) and is_match(right):
            return Match([left.ast(), right.ast()])

        if is_match(left):
            return Match(left.ast())

        if is_match(right):
            return Match(right.ast())

        return Or(left, right)


class And(Language):

    def __init__(self, left, right):
        super(And, self).__init__()
        self.left = left
        self.right = right

    def is_matchable(self):
        return self.left.is_matchable() and self.right.is_matchable()

    def _derive(self, token):
        if self.left.is_matchable():
            dleft = self.left.derive(token)
            dright = self.right.derive(token)

            return Or.make(And.make(dleft, self.right),
                           And.make(Match(self.left.ast()), dright))

        return And.make(self.left.derive(token), self.right)

    def ast(self):
        left_ast = self.left.ast()
        right_ast = self.right.ast()

        ast = []
        ast.extend(left_ast)
        ast.extend(right_ast)
        return ast

    def __repr__(self):
        return 'And(%s, %s)' % (self.left, self.right)

    @staticmethod
    def make(left, right):
        if left is reject or right is reject:
            return reject

        if is_match(left) and is_match(right):
            return Match(And(left, right).ast())

        return And(left, right)


class Star(Language):

    def __init__(self, language):
        super(Star, self).__init__()
        self.language = language

    def is_matchable(self):
        return True

    def _derive(self, token):
        return And.make(self.language.derive(token), Star.make(self.language))

    def ast(self):
        return self.language.ast()

    def __repr__(self):
        return 'Star(%s)' % self.language

    @staticmethod
    def make(language):
        if is_match(language):
            return Match(language.ast())

        if language is reject:
            return reject

        return Star(language)


class Reduce(Language):

    def __init__(self, language, ast_creator):
        super(Reduce, self).__init__()
        self.language = language
        self.ast_creator = ast_creator

    def is_matchable(self):
        return self.language.is_matchable()

    def _derive(self, token):
        return Reduce.make(self.language.derive(token), self.ast_creator)

    def ast(self):
        return [self.ast_creator(self.language.ast())]

    def __repr__(self):
        return 'Reduce(%s)' % self.language

    @staticmethod
    def make(language, ast_creator):
        if language is reject:
            return reject

        if is_match(language):
            return Match([ast_creator(language.ast())])

        return Reduce(language, ast_creator)


class Optional(Language):

    def __init__(self, language):
        super(Optional, self).__init__()
        self.language = language

    def is_matchable(self):
        return True

    def _derive(self, token):
        return self.language.derive(token)

    def ast(self):
        return self.language.ast()

    def __repr__(self):
        return 'Optional(%s)' % self.language

    @staticmethod
    def make(language):
        if is_match(language):
            return Match(language.ast())

        if language is reject:
            return reject

        return Optional(language)


class Function(Language):
    def __init__(self, name, language):
        super(Function, self).__init__()
        self.name = name
        self.language = language
        self.called = False
        self.value = []

    def _derive(self, token):
        return self.language.derive(token)

    def ast(self):
        if self.called:
            return self.value

        self.called = True
        value = result = None

        while(True):
            value = self.language.ast()
            if result == value:
                break
            result = value

        self.value = result
        return result

    def __repr__(self):
        return 'Function(%s)' % self.name


class Cached(Language):

    def __init__(self, name, cache):
        super(Cached, self).__init__()
        self.name = name
        self.cache = cache
        self.called = False
        self.value = []

    def _derive(self, token):
        return self.cache[self.name].derive(token)

    def ast(self):
        if self.called:
            return self.value

        self.called = True
        value = result = None
        lang = self.cache[self.name]

        while(True):
            value = lang.ast()
            if result == value:
                break
            result = value

        self.value = result
        return result

    def __repr__(self):
        return 'Cached(%s)' % self.name


class _Builder(object):

    def __init__(self):
        self.cache = {}
        self.recursion = []

    def to_language(self, thing):
        lang = None

        if isinstance(thing, basestring) or isinstance(thing, str):
            lang = RegExp('^' + re.escape(thing) + '$')

        elif isinstance(thing, Language):
            lang = thing

        elif inspect.isclass(thing) and issubclass(thing, lexer.Token):
            lang = TokenClass(thing)

        # Function
        elif not inspect.isclass(thing) and hasattr(thing, '__call__'):
            lang = self.function_to_language(thing)

        elif isinstance(thing, list):
            assert len(thing) == 1
            lang = self.opt_(self.to_language(thing[0]))

        if lang:
            lang._grammar = self
            return lang

        raise Exception('Unknown thing %s' % thing)

    def function_to_language(self, fn):
        name = fn.func_name
        if name in self.recursion:
            self.recursion.remove(name)
            return Cached(name, self.cache)

        self.recursion.append(name)
        if name not in self.cache.keys():
            self.cache[name] = Function(name, self.to_language(fn()))
        return self.cache[name]

    def and_(self, first, *args):
        if not args:
            return first
        if len(args) == 1:
            return And.make(self.to_language(first), self.to_language(args[0]))

        result = And.make(self.to_language(first), self.to_language(args[0]))
        for arg in args[1:]:
            result = And.make(result, self.to_language(arg))
        return result

    def or_(self, first, *args):
        if len(args) == 1:
            return Or.make(self.to_language(first), self.to_language(args[0]))
        result = Or.make(self.to_language(first), self.to_language(args[0]))

        for arg in args[1:]:
            result = Or.make(result, self.to_language(arg))
        return result

    def opt(self, thing):
        return Optional.make(self.to_language(thing))

    def oneOrMore(self, parser):
        return And.make(self.to_language(parser),
                        Star.make(self.to_language(parser)))

    def zeroOrMore(self, parser):
        return Star.make(self.to_language(parser))

    def reduce(self, action, parser):
        return Reduce.make(self.to_language(parser), action)

    def get_fn(self, fn):
        return {
            '+': self.and_,
            '|': self.or_,
            '?': self.opt,
            '.*': self.zeroOrMore,
            '.+': self.oneOrMore,
            '=>': self.reduce,
        }[fn]


class Grammar(_Builder):
    def main(self):
        raise "Must be overriden and specifies entrypoint grammer."

    def derive(self, tokens):
        d = self.main()
        for t in tokens:
            if not t.skip:
                d = d.derive(t)
            if isinstance(d, Reject):
                print "Rejected: %s" % t
                d = self.main()
                break
        return d


def sexp_grammar_eval(grammar, thing):
    if not isinstance(thing, tuple):
        return thing

    else:
        fn = grammar.get_fn(thing[0])
        return apply(fn, [sexp_grammar_eval(grammar, _) for _ in thing[1:]])


def language(func, *args):
    def fn(grammar):
        return sexp_grammar_eval(grammar, func(grammar))

    # Keep the function name to be used for caching
    fn.func_name = func.func_name
    return fn
