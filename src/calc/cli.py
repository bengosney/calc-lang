from collections.abc import Iterator
from pathlib import Path
import subprocess

import typer

from .codegen import compile_to_ir
from .parse import CaclError, run

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
    compile: Path | None = typer.Option(None, "--compile", help="Compile to LLVM IR and write to this path"),
):
    if compile is not None:
        ir = compile_to_ir(load(path))
        compile.with_suffix(".ll").write_text(ir)
        typer.echo(f"IR written to {compile}")
        typer.echo("Compiling IR")
        subprocess.run(["clang", "runtime.c", compile.with_suffix(".ll"), "-o", compile])
        return

    try:
        result = run(
            load(path),
            input_resolver=lambda name: float(typer.prompt(f"Input {name}")),
            debug=debug,
        )
        print(f"Result: {result}")
    except CaclError as e:
        print(f"error: {e}")
