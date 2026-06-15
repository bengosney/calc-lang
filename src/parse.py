from lark import Lark, Transformer

parser = Lark.open("./grammars/calc.lark", rel_to=__file__, parser="earley")


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
        return self.vars[name]

    def assign_var(self, items):
        name, value = str(items[0]), items[1]
        self.vars[name] = value
        return value


transformer = CalcTransformer()

calc = """
x = 11
y = -3
x * 2 + (y - 1) / (8 * 0.5)
"""

expressions = [e for e in calc.splitlines() if len(e)]

for expr in expressions:
    result = transformer.transform(parser.parse(expr))
    print(f"{expr} => {result}")
