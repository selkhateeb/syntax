import unittest
from syntax import parser
from syntax import lexer


def T(value):
    t = lexer.Token()
    t.value = value
    return t


class TestParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_regex_parser(self):
        regexp = parser.RegExp('^foo$')
        self.assertTrue(parser.is_match(regexp.derive(T('foo'))))
        self.assertTrue(regexp.derive(T('foobar')) is parser.reject)

        token = T('foo')
        self.assertEquals(regexp.derive(token).ast()[0], token)

    def test_and_parser(self):
        left = parser.RegExp('^var$')
        right = parser.RegExp('^a$')
        and_ = parser.And(left, right)
        deriv = and_.derive(T('var')).derive(T('a'))

        self.assertTrue(parser.is_match(deriv))
        self.assertEquals(len(deriv.ast()), 2)
        self.assertEquals(deriv.ast()[0].value, 'var')
        self.assertEquals(deriv.ast()[1].value, 'a')

        and_and = parser.And(and_, right)
        deriv2 = and_and.derive(T('var')).derive(T('a')).derive(T('a'))

        self.assertTrue(parser.is_match(deriv2))
        self.assertEquals(len(deriv2.ast()), 3)
        self.assertEquals(deriv2.ast()[0].value, 'var')
        self.assertEquals(deriv2.ast()[1].value, 'a')
        self.assertEquals(deriv2.ast()[2].value, 'a')

    def test_or(self):
        left = parser.RegExp('^var$')
        right = parser.RegExp('^a$')
        or_ = parser.Or(left, right)
        deriv = or_.derive(T('var'))

        self.assertTrue(parser.is_match(deriv))
        self.assertEquals(len(deriv.ast()), 1)
        self.assertEquals(deriv.ast()[0].value, 'var')

        deriv = or_.derive(T('a'))

        self.assertTrue(parser.is_match(deriv))
        self.assertEquals(len(deriv.ast()), 1)
        self.assertEquals(deriv.ast()[0].value, 'a')


    def test_star(self):
        regex = parser.RegExp('^a$')
        star = parser.Star(regex)
        deriv = star.derive(T('a'))

        self.assertTrue(deriv.is_matchable())
        self.assertEquals(len(deriv.ast()), 1)
        self.assertEquals(deriv.ast()[0].value, 'a')

        deriv = deriv.derive(T('a'))

        self.assertTrue(deriv.is_matchable())
        self.assertEquals(len(deriv.ast()), 2)
        self.assertEquals(deriv.ast()[0].value, 'a')
        self.assertEquals(deriv.ast()[1].value, 'a')


    def test_optional(self):
        regex = parser.RegExp('^a$')
        optional = parser.Optional(regex)
        deriv = optional.derive(T('a'))

        self.assertTrue(optional.is_matchable())

        self.assertTrue(parser.is_match(deriv))
        self.assertEquals(len(deriv.ast()), 1)
        self.assertEquals(deriv.ast()[0].value, 'a')

    def test_reduce(self):
        def reduction(ast):
            return ' '.join([_.value for _ in ast])

        left = parser.RegExp('^var$')
        right = parser.RegExp('^a$')
        and_ = parser.And(left, right)
        reduce_ = parser.Reduce(and_, reduction)

        deriv = reduce_.derive(T('var')).derive(T('a'))

        self.assertTrue(parser.is_match(deriv))
        self.assertEquals(len(deriv.ast()), 1)
        self.assertEquals(deriv.ast()[0], 'var a')


if __name__ == '__main__':
    unittest.main()

