from lark import Lark, Transformer
from collections.abc import Iterable
import typer

parser = Lark.open("./grammars/calc.lark", rel_to=__file__, parser="earley")


class CaclError(Exception):
    pass


class CalcTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.vars = {}

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
        self.vars[name] = float(typer.prompt(f"Input {name}"))


def run(expressions: Iterable[str], debug: bool = False) -> float:
    transformer = CalcTransformer()
    result = None

    for expr in expressions:
        result = transformer.transform(parser.parse(expr))
        if debug:
            print(f"{expr} => {result}")

    if result is None:
        raise CaclError("expressions returned no result")

    return result
