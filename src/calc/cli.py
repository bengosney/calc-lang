from collections.abc import Iterator
from pathlib import Path

import typer

from .parse import run, CaclError

app = typer.Typer()


def load(path: Path) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            if (stripped := line.strip()) != "":
                yield stripped


@app.command()
def main(
    path: Path = typer.Argument(..., help="Path to .calc file"),
    debug: bool = typer.Option(False, "--debug", help="Print each expression and its result"),
):
    expressions = load(path)
    try:
        result = run(expressions, debug=debug)
        print(f"Result: {result}")
    except CaclError as e:
        print(f"error: {e}")
