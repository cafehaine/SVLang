from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
from typing import Literal, Self

from .ast import *


@dataclass
class Symbols:
    variables: dict[str, ValueType]
    functions: dict[str, tuple[tuple[ValueType, ...], ValueType | None]]

    def clone(self) -> Self:
        return self.__class__(self.variables.copy(), self.functions.copy())


class TypeCheckLevel(Enum):
    ERROR = "\x1b[31m"
    WARN = "\x1b[33m"
    INFO = ""


@dataclass
class TypeCheckMessage:
    level: TypeCheckLevel
    message: str
    line: int

    def __str__(self):
        return f"{self.level.value}{self.level.name}: line {self.line}:\x1b[0m {self.message}"


encountered_type_check_messages: ContextVar[list[TypeCheckMessage]] = ContextVar(
    "encountered_type_check_messages"
)


def type_check_message(level: TypeCheckLevel, message: str, line: int) -> None:
    _type_check_message = TypeCheckMessage(level, message, line)
    encountered_type_check_messages.get().append(_type_check_message)


def _expression_type(expression: Expression, symbols: Symbols) -> ValueType | None:
    match expression:
        case VariableReference(lineno, identifier):
            if identifier not in symbols.variables:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Undefined reference to variable ${identifier}",
                    lineno,
                )
                return None
            return symbols.variables[identifier]

        case NumericValue():
            return ValueType.UINT

        case BooleanValue():
            return ValueType.BOOL

        case Color():
            return ValueType.COLOR

        case NumericExpression(lineno, left, _, right):
            left_type = _expression_type(left, symbols)
            if left_type != ValueType.UINT:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Invalid lefthand operand type {left_type} in numeric expression.",
                    lineno,
                )
            right_type = _expression_type(right, symbols)
            if right_type != ValueType.UINT:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Invalid lefthand operand type {right_type} in numeric expression.",
                    lineno,
                )
            return ValueType.UINT

        case NumericComparison(lineno, left, _, right):
            left_type = _expression_type(left, symbols)
            if left_type != ValueType.UINT:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Invalid lefthand operand type {left_type} in numeric comparison.",
                    lineno,
                )
            right_type = _expression_type(right, symbols)
            if right_type != ValueType.UINT:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Invalid lefthand operand type {right_type} in numeric comparison.",
                    lineno,
                )
            return ValueType.BOOL

        case BinaryExpression(lineno, left, _, right):
            left_type = _expression_type(left, symbols)
            if left_type != ValueType.UINT:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Invalid lefthand operand type {left_type} in binary expression.",
                    lineno,
                )
            right_type = _expression_type(right, symbols)
            if right_type != ValueType.UINT:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Invalid lefthand operand type {right_type} in binary expression.",
                    lineno,
                )
            return ValueType.UINT

        case FunctionCall(lineno, identifier, arguments):
            if identifier not in symbols.functions:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Undefined reference to function {identifier}",
                    lineno,
                )
                return None
            signature = symbols.functions[identifier]
            if len(signature[0]) != len(arguments):
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Function {identifier} was given {len(arguments)} arguments, but expected {len(signature[0])} arguments.",
                    lineno,
                )
                return signature[1]
            for arg_index, argument in enumerate(arguments):
                argument_type = _expression_type(argument, symbols)

            return signature[1]

            raise NotImplementedError()

        case _:
            raise RuntimeError(
                f"Unhandled expression type {type(expression)}: {expression}"
            )


class Sentinel(Enum):
    UNDEFINED = auto()


def _type_check(
    statement: Statement, symbols: Symbols, output_type: ValueType | None
) -> ValueType | None | Literal[Sentinel.UNDEFINED]:
    return_type = Sentinel.UNDEFINED
    match statement:
        case FunctionDeclaration(
            lineno, identifier, arguments, function_return_type, statements
        ):
            signature = (
                tuple(argument.type for argument in arguments),
                function_return_type,
            )
            if identifier in symbols.functions:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Shadowing existing definition of {identifier}",
                    lineno,
                )
            symbols.functions[identifier] = signature

            internal_scope = symbols.clone()
            for argument in arguments:
                if argument.identifier in symbols.variables:
                    type_check_message(
                        TypeCheckLevel.ERROR,
                        f"Argument {argument} shadows existing definition of variable",
                        lineno,
                    )
                internal_scope.variables[argument.identifier] = argument.type

            for st in statements:
                st_return_type = _type_check(st, internal_scope, function_return_type)
            # TODO verify that there is a return type matching the function definition

        case Declaration(lineno, identifier, variable_type, value):
            if identifier in symbols.variables:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Variable {identifier} shadows existing definition of variable",
                    lineno,
                )
            symbols.variables[identifier] = variable_type
            value_type = _expression_type(value, symbols)
            if value_type != variable_type:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Assigning incompatible value {value} of type {value_type} to variable ${identifier} of type {variable_type}",
                    lineno,
                )

        case Assignment(lineno, identifier, value):
            if identifier not in symbols.variables:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Assigning to undefined variable ${identifier}",
                    lineno,
                )
            else:
                variable_type = symbols.variables[identifier]
                value_type = _expression_type(value, symbols)
                if value_type != variable_type:
                    type_check_message(
                        TypeCheckLevel.ERROR,
                        f"Assigning incompatible value {value} of type {value_type} to variable ${identifier} of type {variable_type}",
                        lineno,
                    )

        case Return(lineno, expression):
            if expression is not None:
                expression_type = _expression_type(expression, symbols)
            else:
                expression_type = None
            if output_type != expression_type:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"Invalid return type {expression_type}, expected {output_type}",
                    lineno,
                )
            return_type = expression_type

        case ASMInstruction(lineno, op, arg1, arg2, arg3):

            def _check_arg_type(arg_type, arg, index):
                match arg_type:
                    case ASMArgType.Reference:
                        if isinstance(arg, NumericValue):
                            type_check_message(
                                TypeCheckLevel.ERROR,
                                f"Argument {index} of asm instruction {op.name} expected reference, not numeric value",  # type: ignore
                                lineno,
                            )
                        elif arg.identifier not in symbols.variables:
                            type_check_message(
                                TypeCheckLevel.ERROR,
                                f"Argument {index} of asm instruction {op.name} references undefined variable ${arg.identifier}",  # type: ignore
                                lineno,
                            )
                    case ASMArgType.Value:
                        if isinstance(arg, VariableReference):
                            type_check_message(
                                TypeCheckLevel.ERROR,
                                f"Argument {index} of asm instruction {op.name} expected numeric value, not reference",  # type: ignore
                                lineno,
                            )
                    case ASMArgType.Unused:
                        if isinstance(arg, VariableReference):
                            type_check_message(
                                TypeCheckLevel.WARN,
                                f"Argument {index} of asm instruction {op.name} was given a variable reference, but the argument is unused. Consider passing a zero value.",  # type: ignore
                                lineno,
                            )
                            if arg.identifier not in symbols.variables:
                                type_check_message(
                                    TypeCheckLevel.ERROR,
                                    f"Argument {index} of asm instruction {op.name} references undefined variable ${arg.identifier}",  # type: ignore
                                    lineno,
                                )
                        elif arg.value != 0:
                            type_check_message(
                                TypeCheckLevel.WARN,
                                f"Argument {index} of asm instruction {op.name} was given a non-zero numeric value, but the argument is unused. Consider passing a zero value.",  # type: ignore
                                lineno,
                            )

            _check_arg_type(op.arg1_type, arg1, 1)
            _check_arg_type(op.arg2_type, arg2, 2)
            _check_arg_type(op.arg3_type, arg3, 3)

        case While(lineno, expression, statements):
            expression_type = _expression_type(expression, symbols)
            if expression_type != ValueType.BOOL:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"While loop expression expects BOOL, but the expression is of type {expression_type}",
                    lineno,
                )
            for st in statements:
                _type_check(st, symbols, output_type)
                # TODO check for return type

        case If(lineno, expression, statements, else_statements):
            expression_type = _expression_type(expression, symbols)
            if expression_type != ValueType.BOOL:
                type_check_message(
                    TypeCheckLevel.ERROR,
                    f"If statement condition expectes BOOL, but the expression is of type {expression_type}",
                    lineno,
                )
            for st in statements:
                _type_check(st, symbols, output_type)
                # TODO check for return type
            if else_statements:
                for st in else_statements:
                    _type_check(st, symbols, output_type)
                    # TODO check for return type

        case Break(lineno):
            pass  # TODO check if contained in while loop

        case FunctionCall(lineno) as expression:
            if _expression_type(expression, symbols) != None:
                type_check_message(
                    TypeCheckLevel.INFO,
                    f"Unused return value for function call {expression}",
                    lineno,
                )

        case statement:
            type_check_message(
                TypeCheckLevel.WARN,
                f"Unchecked statement type {type(statement).__name__}: {statement}",
                statement.lineno,
            )

    return return_type


def type_check(statements: list[Statement]) -> None:
    symbols = Symbols({}, {})
    for statement in statements:
        return_type = _type_check(statement, symbols, None)
        if return_type not in (None, Sentinel.UNDEFINED):
            type_check_message(
                TypeCheckLevel.WARN,
                f"Returning a value of type {return_type} from the main scope isn't supported",
                statement.lineno,
            )


if __name__ == "__main__":
    from argparse import ArgumentParser
    from grammar import parse

    parser = ArgumentParser()
    parser.add_argument("source")
    args = parser.parse_args()

    with open(args.source, "r") as source_file:
        statements = parse(source_file.read())
        type_check_messages = []
        encountered_type_check_messages.set(type_check_messages)
        type_check(statements)
        errors_found = False
        for message in type_check_messages:
            print(message)
        if not type_check_messages:
            print("Nothing to fix :)")
