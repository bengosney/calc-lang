from collections.abc import Iterator
from pathlib import Path

import typer

from .parse import run

app = typer.Typer()


def load(path: Path) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            if (stripped := line.strip()) != "":
                yield stripped


@app.command()
def main(path: Path = typer.Argument(..., help="Path to .calc file")):
    expressions = load(path)
    result = run(expressions)
    print(f"Result: {result}")
