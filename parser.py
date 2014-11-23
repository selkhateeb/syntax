#! /usr/bin/env python

import re

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
        right_ast = right.ast()
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

    @staticmethod
    def make(language):
        if is_match(language):
            return Match(language.ast())

        if language is reject:
            return reject

        return Optional(language)
