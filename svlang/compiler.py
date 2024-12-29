from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum, auto
from io import BytesIO, StringIO
import sys
from typing import Literal, Self

from .grammar import parse
from .ast import *
from .typecheck import type_check, encountered_type_check_messages, TypeCheckLevel


@dataclass
class Symbols:
    """
    A mapping of variables/functions to their addresses.

    For functions, the address is the position of the first "real" instruction.
    """

    variables: dict[str, int]
    functions: dict[str, int]

    def clone(self) -> Self:
        return self.__class__(self.variables.copy(), self.functions.copy())


def _compile_statement(statement: Statement, *, symbols: Symbols, offset: int) -> bytes:
    # TODO group all declaration of variables at the start of the scope (main/function)
    output = BytesIO()
    match statement:
        case ASMInstruction(_, op, arg1, arg2, arg3):
            ...
        case unhandled:
            raise NotImplementedError(
                f"Compilation of {type(unhandled)} {unhandled} is not yet implemented"
            )
    raise NotImplementedError("TODO")


def compile(source: str) -> bytes:
    statements = parse(source)

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

    symbols = Symbols({}, {})
    output = BytesIO()
    offset = 0
    for statement in statements:
        statement_output = _compile_statement(statement, symbols=symbols, offset=offset)
        offset += len(statement_output)
        output.write(statement_output)
    return output.getvalue()
