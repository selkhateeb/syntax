#! /usr/bin/env python
import StringIO
import os

output = StringIO.StringIO()

# ( var foo bar ) <=> foo = bar
foo = 'bar'

z = [
    ['meta',
     ('\n', 0, 1),
     ('\n', 12, 1),],

    ['var', 1,
     ('foo', 0),
     ('bar', 6),
     ['meta', ('=', 5, 1)]],  # variable identification


    ['def', 13, ('buffer_size', 17),
     ['args', ['positional', ('buf', 29) ]],
     ['body', ['return', 39, ('None', 46)]],
     ['meta',
      ('\n', 50, 1),
      ('(', 28, 1),
      (')', 32, 1),
      (':', 33, 1),
      ('\n', 34, 1),
      ],
     ],
    ]


def buffer_size(buf):
    buf.seek(0, os.SEEK_END)
    return buf.tell()

def buffer_fill_spaces_if_needed(buf, position):
    diff = buffer_size(buf) - position
    if diff < 0:
        offset = diff * -1
        buf.write(''.rjust(offset, ' '))

    # Reset to the initial position
    buf.seek(position)



def write_tuple(tup, offset, buf):
    value, position = tup
    buffer_fill_spaces_if_needed(buf, position + offset)
    buf.write(value)


def var(sexp, out):
    offset = sexp[1]
    name = sexp[2]
    value = sexp[3]
    meta = sexp[4]

    write_tuple(name, offset, out)
    write_tuple(value, offset, out)
    character(meta, out)
    return out

def character(sexp, out):
    for ch, start, length in sexp[1:]:
        buffer_fill_spaces_if_needed(out, start)
        out.write(''.ljust(length, ch))
    return out

def function(sexp, out):
    '''
    ['def', ('buffer_size', 31),
     ['args', ['positional', ('buf', 44) ]],
     ['body', ['return', ('None', 54)]]],
    '''
    start = sexp[1]
    name = sexp[2]
    args = sexp[3]
    body = sexp[4]
    meta = sexp[5]

    buffer_fill_spaces_if_needed(out, start)
    out.write('def')

    write_tuple(name, 0, out)
    for arg in args[1:]:
        args_map[arg[0]](arg, out)

    for stmt in body[1:]:
        body_map[stmt[0]](stmt, out)

    character(meta, out)

    return out


def arg_positional(sexp, out):
    write_tuple(sexp[1], 0, out)
    return out

def return_statement(sexp, out):
    buffer_fill_spaces_if_needed(out, sexp[1])
    out.write('return')
    write_tuple(sexp[2], 0, out)
    return out

map = {
    'var': var,
    'character': character,
    'def': function,
    'meta': character,
}

args_map = {
    'positional': arg_positional,
    'meta': character,
}

body_map = {
    'return': return_statement,
    'meta': character,
}

def print_sexp(sexp):
    for i in sexp:
        map[i[0]](i, output)
    print(output.getvalue())


if __name__ == '__main__':
    for i in z:
        map[i[0]](i, output)

    print(output.getvalue())
    output.close()
