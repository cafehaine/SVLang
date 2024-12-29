from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum, auto
from io import BytesIO, StringIO
import sys
from typing import Literal, Self

from grammar import parse
from svcast import *
from typecheck import type_check, encountered_type_check_messages, TypeCheckLevel


def compile_statements(statements: list[Statement]) -> bytes:
    output = BytesIO()

    type_check_messages = []
    encountered_type_check_messages.set(type_check_messages)
    type_check(statements)
    errors_found = False
    for message in type_check_messages:
        if message.level == TypeCheckLevel.ERROR:
            errors_found = True
        print(message)
    if errors_found:
        raise RuntimeError("Errors found while type checking, aborting compilation")

    raise NotImplementedError("TODO")


def compile(source: str) -> bytes:
    statements = parse(source)
    return compile_statements(statements)


if __name__ == "__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(
        description="Compile SVLang programs into SVC16 binaries.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "source", default="-", nargs="?", help="The source file ('-' for stdin)"
    )
    parser.add_argument("output", help="The output file ('-' for stdout)")
    args = parser.parse_args()

    # Read input data from stdin or a file.
    input_data: str
    if args.source == "-":
        buffer = StringIO()
        try:
            while True:
                buffer.write(input("> "))
        except EOFError:
            pass
        input_data = buffer.getvalue()
    else:
        with open(args.source, "r") as input_file:
            input_data = input_file.read()

    statements = parse(input_data)
    binary = compile_statements(statements)

    if args.output == "-":
        sys.stdout.buffer.write(binary)
    else:
        with open(args.output, "wb") as binary_output_file:
            binary_output_file.write(binary)
