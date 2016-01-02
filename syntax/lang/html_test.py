import unittest
from html import Output, Main, Void, Start, End, Comment
from syntax import Lexer


VOID_ELEMENTS = ['area', 'base', 'br', 'col', 'command', 'embed',
                 'hr', 'img', 'input', 'link', 'keygen', 'meta',
                 'param', 'source', 'track', 'wbr', '!DOCTYPE']

class HtmlLexerTest(unittest.TestCase):

    def setUp(self):
        self.out = Output()
        self.lexer = Lexer(initial_state=Main, output=self.out)


    def test_link_tag(self):
        for ele in VOID_ELEMENTS:
            self.lexer.lex('<link>')
            self.assertTrue(isinstance(self.out.tokens[0], Void))


    def test_comment_tag(self):
        self.lexer.lex('<!-- -->')
        self.assertTrue(isinstance(self.out.tokens[0], Comment))


    def test_start_tag(self):
        self.lexer.lex('<start>')
        self.assertTrue(isinstance(self.out.tokens[0], Start))


    def test_end_tag(self):
        self.lexer.lex('</start>')
        self.assertTrue(isinstance(self.out.tokens[0], End))



if __name__ == '__main__':
    unittest.main()


