from collections.abc import Iterator
from pathlib import Path

from .parse import run


def load(path: Path) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            if (stripped := line.strip()) != "":
                yield stripped


def main():
    expressions = load(Path("./math.calc"))

    result = run(expressions)
    print(f"Result: {result}")
