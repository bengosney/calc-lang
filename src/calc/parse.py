from collections.abc import Callable

from lark import Lark, Transformer

parser = Lark.open("./grammars/calc.lark", rel_to=__file__, parser="earley")


class CaclError(Exception):
    pass


class CalcTransformer(Transformer):
    def __init__(self, input_resolver: Callable[[str], float]):
        super().__init__()
        self.vars = {}
        self._input_resolver = input_resolver

    def number(self, items):
        return float(items[0])

    def neg(self, items):
        return -items[0]

    def add(self, items):
        return items[0] + items[1]

    def sub(self, items):
        return items[0] - items[1]

    def mul(self, items):
        return items[0] * items[1]

    def div(self, items):
        return items[0] / items[1]

    def var(self, items):
        name = str(items[0])
        if name not in self.vars:
            raise NameError(f"Undefined variable: {name}")
        return self.vars[name]

    def assign_var(self, items):
        name, value = str(items[0]), items[1]
        self.vars[name] = value
        return value

    def define_var(self, items):
        name = str(items[0])
        self.vars[name] = self._input_resolver(name)
        return self.vars[name]

    def expr(self, items):
        return items[0]

    def start(self, items):
        return [v for v in items]


def run(source: str, input_resolver: Callable[[str], float], debug: bool = False) -> float:
    transformer = CalcTransformer(input_resolver)
    results = transformer.transform(parser.parse(source))

    if not results:
        raise CaclError("expressions returned no result")

    if debug:
        lines = [line for line in (s.strip() for s in source.splitlines()) if line and not line.startswith("#")]
        for line, result in zip(lines, results):
            print(f"{line} => {result}")

    return results[-1]
