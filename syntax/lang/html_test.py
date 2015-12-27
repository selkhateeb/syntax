import unittest
from html import Output, Main, Void, Start, End, Comment
from syntax import Lexer


class LexerTest(unittest.TestCase):

    def setUp(self):
        self.out = Output()
        self.lexer = Lexer(initial_state=Main, output=self.out)


    def test_link_tag(self):
        self.lexer.lex('<link>')
        self.assertTrue(isinstance(self.out.tokens[0], Void))


    def test_comment(self):
        self.lexer.lex('<!-- -->')
        print self.out.tokens
        self.assertTrue(isinstance(self.out.tokens[0], Comment))


if __name__ == '__main__':
    unittest.main()
