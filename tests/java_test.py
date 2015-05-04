
import syntax.lang.java as java
import syntax
import sys

if __name__ == '__main__':
    out = java.Output()
    lexer = syntax.Lexer(initial_state=java.Main, output=out)
    lexer.lex(open(sys.argv[1]).read())

    g = java.JavaGrammar()
    tokens = out.tokens #filter(lambda _: not isinstance(_, (Whitespace, NewLine, Comment)), out.tokens)
    g.derive(tokens)
