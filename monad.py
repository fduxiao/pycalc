from functools import wraps


class Either:
    type = None
    LEFT = "Left"
    RIGHT = "Right"

    def __init__(self, value):
        self.value = value

    @property
    def left(self):
        return self.type == self.LEFT

    @property
    def right(self):
        return self.type == self.RIGHT

    def __repr__(self):
        return f"{self.type} {self.value.__repr__()}"


class Left(Either):
    type = Either.LEFT


class Right(Either):
    type = Either.RIGHT


class State:
    def __init__(self, string, pos=0):
        self.pos = pos
        self.string = string

    def copy(self):
        return State(self.string, pos=self.pos)

    def next(self):
        return State(self.string, pos=self.pos+1)

    def prev(self):
        return State(self.string, pos=self.pos-1)

    @staticmethod
    def err(reason):
        return Parser.err(reason)

    def __repr__(self):
        return f"{self.string[:self.pos]}[{self.string[self.pos:self.pos+1]}]{self.string[self.pos+1:]}"


class Parser:
    def __init__(self, run):
        self.run = run

    @staticmethod
    def ret(value):
        return Parser(lambda state: Right((value, state)))

    @staticmethod
    def err(reason):
        return Parser(lambda state: Left((reason, state)))

    def bind(self, f) -> "Parser":
        def bound_parser(state) -> Either:
            either: Either = self.run(state)
            if either.left:
                return either
            value, new_state = either.value
            return f(value).run(new_state)
        return Parser(bound_parser)

    def raw(self) -> "Parser":
        def raw_parser(state):
            result = self.run(state)
            if result.right:
                state = result.value[1]
            return Right((result, state))
        return Parser(raw_parser)

    @staticmethod
    def get() -> "Parser":
        return Parser(lambda state: Right((state, state)))

    @staticmethod
    def put(state) -> "Parser":
        return Parser(lambda _state: Right((None, state)))

    def __or__(self, other):
        def or_parser(state):
            either: Either = self.run(state)
            if either.right:
                return either
            return other.run(state)
        return Parser(or_parser)


class _Null:
    pass


Generator = type((x for x in []))


def reduce(generator, value=_Null):
    if not isinstance(generator, Generator):
        return generator  # that should be a value
    try:
        if value is _Null:
            m_a = next(generator)
        else:
            m_a = generator.send(value)
    except StopIteration as err:
        return err.value

    return m_a.bind(lambda a: reduce(generator, a))


def do(generator_func):
    @wraps(generator_func)
    def wrapper(*args, **kwargs):
        return reduce(generator_func(*args, **kwargs))
    return wrapper
