#! /usr/bin/env python

import sys
from lexer import LETTER, DIGIT, _, State, RegExp, Lexer, Token, Character
from lexer import Optional, HEX
from parser import Grammar, TokenClass, _, language
import parser


class FileHeaderRecord(object):
    def __init__(self, args):
        self.type_code             = args[0].value
        self.priority_code         = args[1].value
        self.immediate_destination = args[2].value
        self.immediate_origin      = args[3].value
        self.transmission_date     = args[4].value
        self.transmission_time     = args[5].value
        self.file_id_modifier      = args[6].value
        self.record_size           = args[7].value
        self.blocking_factor       = args[8].value
        self.format_code           = args[9].value
        self.destination_name      = args[10].value
        self.origin_name           = args[11].value
        self.reference_code        = args[12].value

    def __repr__(self):
        return 'FileHeaderRecord(%s)' % '|'.join([
            self.type_code,
            self.priority_code,
            self.immediate_destination,
            self.immediate_origin,
            self.transmission_date,
            self.transmission_time,
            self.file_id_modifier,
            self.record_size,
            self.blocking_factor,
            self.format_code,
            self.destination_name,
            self.origin_name,
            self.reference_code
        ])

class Main(State):
    def __init__(self):
        super(Main, self).__init__()
        self / RegExp('.') / (lambda: Token())


class Output(object):
    def __init__(self):
        self.tokens = []

    def add(self, token):
        self.tokens.append(token)
        #sys.stdout.write(token.value)
        #print("%s:'%s':%s" % (token.__class__.__name__, token.value, token.position))


A = parser.RegExp('^[a-zA-Z0-9]$')
N = parser.RegExp('^[0-9]$')


class PriorityCode(object):
    def __init__(self, tokens):
        self.value = ''.join([_.value for _ in tokens])

    def __repr__(self):
        return "PC(%s)" % self.code


def foo(args):
    return args


class FileHeaderRecordGrammar(object):

    @language
    def file_header_record(self):
        return ('=>', FileHeaderRecord,
                ('+',
                 '1',
                 self.priority_code,
                 self.immediate_destination,
                 self.immediate_origin,
                 self.transmission_date,
                 self.transmission_time,
                 self.file_id_modifier,
                 self.record_size,
                 self.blocking_factor,
                 self.format_code,
                 self.destination_name,
                 self.origin_name,
                 self.reference_code
             ))

    @language
    def priority_code(self):
        return ('=>', PriorityCode,
                ('+', N, N))

    @language
    def immediate_destination(self):
        return ('=>', PriorityCode,
                self._repeat(N, 10))

    @language
    def immediate_origin(self):
        return ('=>', PriorityCode,
                self._repeat(N, 10))

    @language
    def transmission_date(self):
        return ('=>', PriorityCode,
                self._repeat(N, 6))

    @language
    def transmission_time(self):
        return ('=>', PriorityCode,
                self._repeat(N, 4))

    @language
    def file_id_modifier(self):
        return ('=>', PriorityCode,
                ('+', A))

    @language
    def record_size(self):
        return ('=>', PriorityCode,
                ('+', '0', '9', '4'))

    @language
    def blocking_factor(self):
        return ('=>', PriorityCode,
                ('+', '1', '0'))

    @language
    def format_code(self):
        return ('=>', PriorityCode,
                '1')

    @language
    def destination_name(self):
        return ('=>', PriorityCode,
                self._repeat(A, 23))

    @language
    def origin_name(self):
        return ('=>', PriorityCode,
                self._repeat(A, 23))

    @language
    def reference_code(self):
        return ('=>', PriorityCode,
                self._repeat(A, 8))


class NachaGrammar(Grammar, FileHeaderRecordGrammar):
    def __init__(self):
        super(NachaGrammar, self).__init__()

    def main(self):
        return self.file_header_record()

    # TODO(Sam): Should we move this to the builder? do we have more use cases?
    def _repeat(self, language, times):
        return tuple(['+'] + [language] * times)



if __name__ == '__main__':
    record_type = '1'
    priority_code = '12'
    immediate_destination = '1234567890'
    immediate_origin = '1234567890'
    transmission_date = '123456'
    transmission_time = '1234'
    file_id_modifier = 'A'
    record_size = '094'
    blocking_factor = '10'
    format_code = '1'
    destination_name = 'ABCDEFGHIJKLMNOPQRSTUVW'
    origin_name = 'ABCDEFGHIJKLMNOPQRSTUVW'
    reference_code = 'ABCDEFGH'

    out = Output()
    lexer = Lexer(initial_state=Main, output=out)

    in_ = (record_type + priority_code + immediate_destination +
           immediate_origin + transmission_date + transmission_time +
           file_id_modifier + record_size + blocking_factor + format_code +
           destination_name + origin_name + reference_code)

    print in_, len(in_)
    lexer.lex(in_)
    g = NachaGrammar()
    tokens = out.tokens #filter(lambda _: not isinstance(_, (Whitespace, NewLine, Comment)), out.tokens)
    a = g.derive(tokens)
    if a.is_matchable():
        print a.ast()
    else:
        print "Error"


        # ('1', RecordTypeCode),
        # ('##', PriorityCode),
        # ('#' * 10, ImmediateDestination),
        # ('#' * 10, ImmediateOrigin),
        # ('#' * 6, TransmissionDate),
        # ('#' * 4, TransmissionTime),
        # ('A', FileIdModifier),
        # ('094', RecordSize),
        # ('10', BlockingFactor),
        # ('1', FormatCode),
        # ('A' * 23, DestinationName),
        # ('A' * 23, OriginName),
        # ('A' * 8, ReferenceCode)
'112123456789012345678901234561234A094101ABCDEFGHIJKLMNOPQRSTUVWABCDEFGHIJKLMNOPQRSTUVWABCDEFGH'
