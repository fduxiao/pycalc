from monad import *


@do
def item():
    state = yield Parser.get()
    if state.pos == len(state.string):
        return state.err("Unexpected EOF")
    ch = state.string[state.pos]
    yield Parser.put(state.next())
    return Parser.ret(ch)


@do
def sat(p):
    state = yield Parser.get()
    c = yield item()
    if p(c):
        return Parser.ret(c)
    yield Parser.put(state)
    return Parser.err(f"Unexpected char: {c}")


def char(c):
    return sat(lambda x: x == c)


@do
def string(s):
    for x in s:
        yield char(x)
    return Parser.ret(s)


@do
def space():
    result = list()
    while True:
        state = yield Parser.get()
        either = yield sat(lambda x: x in "\r\n \t").raw()
        if either.left:
            yield Parser.put(state)
            break
        result.append(either.value[0])
    return Parser.ret(result)


@do
def token(parser):
    a = yield parser
    yield space()
    return Parser.ret(a)


@do
def symb(s):
    x = yield string(s)
    yield space()
    return Parser.ret(x)


@do
def plus():
    yield symb("+")
    return Parser.ret(lambda x, y: x+y)


@do
def minus():
    yield symb("-")
    return Parser.ret(lambda x, y: x-y)


@do
def times():
    yield symb("*")
    return Parser.ret(lambda x, y: x*y)


@do
def div():
    yield symb("/")
    return Parser.ret(lambda x, y: y != 0 and x/y)


@do
def digit():
    v = yield token(sat(lambda x: x in '0123456789'))
    return Parser.ret(ord(v) - ord('0'))


@do
def add_op(n1, n2):
    a = yield n1()
    op = yield plus() | minus()
    b = yield n2()
    return Parser.ret(op(a, b))


@do
def mul_op(n1, n2):
    a = yield n1()
    op = yield times() | div()
    b = yield n2()
    return Parser.ret(op(a, b))


@do
def parenthesis():
    yield symb('(')
    n = yield expr()
    yield symb(')')
    return Parser.ret(n)


def factor():
    return digit() | parenthesis()


def term():
    return mul_op(factor, term) | factor()


def expr():
    return add_op(term, expr) | term()


@do
def trim(parser):
    yield space()
    n = yield parser
    yield space()
    state = yield Parser.get()
    if state.pos < len(state.string):
        return Parser.err(f"Unexpected char: {state.string[state.pos]}")
    return Parser.ret(n)


def parse(s):
    return trim(expr()).run(State(s))
