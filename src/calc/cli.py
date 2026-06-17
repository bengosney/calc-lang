from pathlib import Path
import subprocess

import typer

from .codegen import compile_to_ir
from .parse import CaclError, run

app = typer.Typer()


@app.command()
def main(
    path: Path = typer.Argument(..., help="Path to .calc file"),
    debug: bool = typer.Option(False, "--debug", help="Print each expression and its result"),
    compile: bool = typer.Option(False, "--compile", "-c", help="Compile to LLVM IR and native binary"),
    optimization: int = typer.Option("0", "--optimization", "-O", help="Clang optimization level"),
):
    source = path.read_text()

    if compile:
        output_path = path.with_suffix("")
        ir_path = output_path.with_suffix(".ll")
        ir = compile_to_ir(source)
        ir_path.write_text(ir)
        typer.echo(f"IR written to {ir_path}")

        clang_args = ["clang", f"-O{optimization}", "runtime.c", str(ir_path), "-o", str(output_path)]
        typer.echo(f"Compiling IR with: {' '.join(clang_args)}")
        subprocess.run(clang_args)

        return

    try:
        result = run(
            source,
            input_resolver=lambda name: float(typer.prompt(f"Input {name}")),
            debug=debug,
        )
        print(f"Result: {result}")
    except CaclError as e:
        print(f"error: {e}")
