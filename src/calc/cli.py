from .parse import run


def main():
    calc = """
x = 11
y = -3
x * 2 + (y - 1) / (8 * 0.5)
"""

    expressions = [e for e in calc.splitlines() if len(e)]

    result = run(expressions)
    print(f"Result: {result}")
