from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto

from typing import Any, Literal


@dataclass
class Statement:
    lineno: int


class Expression(Statement): ...


@dataclass
class FunctionCall(Expression):
    identifier: str
    arguments: list[Expression]

    def __str__(self):
        return f"{self.identifier}({', '.join(str(arg) for arg in self.arguments)})"


class NumericOperator(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"

    def __str__(self):
        return self.value


@dataclass
class NumericExpression(Expression):
    left: Expression
    operator: NumericOperator
    right: Expression

    def __str__(self):
        return f"{self.left} {self.operator} {self.right}"


class NumericComparator(Enum):
    LT = "<"
    LEQ = "<="
    EQ = "=="
    NEQ = "!="
    GEQ = ">="
    GT = ">"

    def __str__(self):
        return self.value


@dataclass
class NumericComparison(Expression):
    left: Expression
    operator: NumericComparator
    right: Expression

    def __str__(self):
        return f"{self.left} {self.operator} {self.right}"


class BooleanOperator(Enum):
    OR = "or"
    AND = "and"

    def __str__(self):
        return self.value


@dataclass
class BooleanExpression(Expression):
    left: Expression
    operator: BooleanOperator
    right: Expression

    def __str__(self):
        return f"{self.left} {self.operator} {self.right}"


@dataclass
class BooleanNegation(Expression):
    expression: Expression

    def __str__(self):
        return f"!{self.expression}"


@dataclass
class VariableReference(Expression):
    identifier: str

    def __str__(self):
        return f"${self.identifier}"


@dataclass
class BooleanValue(Expression):
    value: bool

    def __str__(self):
        return str(self.value)


@dataclass
class NumericValue(Expression):
    value: int

    def __str__(self):
        return str(self.value)


@dataclass
class Color(Expression):
    color: int

    def __str__(self):
        return f"#{self.color:04x}"


class BinaryOP(Enum):
    AND = "&"
    XOR = "^"

    def __str__(self):
        return self.value


@dataclass
class BinaryExpression(Expression):
    left: NumericValue | VariableReference
    operator: BinaryOP
    right: NumericValue | VariableReference

    def __str__(self):
        return f"{self.left} {self.operator} {self.right}"


@dataclass
class BinaryNegation(Expression):
    operand: NumericValue | VariableReference

    def __str__(self):
        return f"!{self.operand}"


class ValueType(Enum):
    UINT = "UINT"
    BOOL = "BOOL"
    COLOR = "COLOR"

    def __str__(self):
        return self.value


@dataclass
class Declaration(Statement):
    identifier: str
    type: ValueType
    value: Expression

    def __str__(self):
        return f"${self.identifier}: {self.type} = {self.value}"


@dataclass
class Assignment(Statement):
    identifier: str
    value: Expression

    def __str__(self):
        return f"${self.identifier} = {self.value}"


@dataclass
class ArgumentDeclaration:
    identifier: str
    type: ValueType

    def __str__(self):
        return f"${self.identifier}: {self.type}"


@dataclass
class FunctionDeclaration(Statement):
    identifier: str
    arguments: list[ArgumentDeclaration]
    return_type: ValueType | None
    statements: list[Statement]

    def __str__(self):
        arguments = ", ".join(str(arg) for arg in self.arguments)
        statements = " ".join(str(st) for st in self.statements)
        if self.return_type:
            return f"def {self.identifier}({arguments}) -> {self.return_type} {{{statements}}}"
        else:
            return f"def {self.identifier}({arguments}) {{{statements}}}"


@dataclass
class Return(Statement):
    expression: Expression | None

    def __str__(self):
        return f"return {self.expression}" if self.expression else "return"


@dataclass
class While(Statement):
    expression: Expression
    statements: list[Statement]

    def __str__(self):
        return (
            f"while {self.expression} {{{' '.join(str(st) for st in self.statements)}}}"
        )


@dataclass
class Break(Statement):

    def __str__(self):
        return "break"


@dataclass
class If(Statement):
    expression: Expression
    statements: list[Statement]
    else_statements: list[Statement] | None = None

    def __str__(self):
        statements = " ".join(str(st) for st in self.statements)
        else_statements = (
            " ".join(str(st) for st in self.else_statements)
            if self.else_statements
            else None
        )
        if else_statements:
            return f"if {self.expression} {{{statements}}} else {{{else_statements}}}"
        return f"if {self.expression} {{{statements}}}"


# fmt: off

class ASMArgType(Enum):
    Reference = 0
    Value = 1
    Unused = 2

@dataclass
class ASMOp:
    opcode: int
    arg1_type : ASMArgType
    arg2_type : ASMArgType
    arg3_type : ASMArgType


class ASMOps(ASMOp, Enum):
    Set   = 0, ASMArgType.Reference, ASMArgType.Value, ASMArgType.Unused
    GoTo  = 1, ASMArgType.Reference, ASMArgType.Value, ASMArgType.Reference
    Skip  = 2, ASMArgType.Value, ASMArgType.Value, ASMArgType.Reference
    Add   = 3, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Reference
    Sub   = 4, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Reference
    Mul   = 5, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Reference
    Div   = 6, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Reference
    Cmp   = 7, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Reference
    Deref = 8, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Value
    Ref   = 9, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Value
    Inst  = 10, ASMArgType.Reference, ASMArgType.Unused, ASMArgType.Unused
    Print = 11, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Value
    Read  = 12, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Value
    Band  = 13, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Reference
    Xor   = 14, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Reference
    Sync  = 15, ASMArgType.Reference, ASMArgType.Reference, ASMArgType.Value

    def __str__(self):
        return self.name

# fmt: on


@dataclass
class ASMInstruction(Statement):
    op: ASMOp
    arg1: VariableReference | NumericValue
    arg2: VariableReference | NumericValue
    arg3: VariableReference | NumericValue

    def __str__(self):
        return f"ASM {self.op} {self.arg1} {self.arg2} {self.arg3}"


def pprint(statement: Statement, *, indent_level=0, indent="    "):
    """Pretty print a statement."""
    match statement:
        case While(_, expression, statements):
            print(f"{indent * indent_level}while {expression} {{")
            for st in statements:
                pprint(st, indent_level=indent_level + 1, indent=indent)
            print(f"{indent * indent_level}}}")
        case If(_, expression, statements, None):
            print(f"{indent * indent_level}if {expression} {{")
            for st in statements:
                pprint(st, indent_level=indent_level + 1, indent=indent)
            print(f"{indent * indent_level}}}")
        case If(_, expression, statements, else_statements):
            assert else_statements is not None
            print(f"{indent * indent_level}if {expression} {{")
            for st in statements:
                pprint(st, indent_level=indent_level + 1, indent=indent)
            print(f"{indent * indent_level}}} else {{")
            for st in else_statements:
                pprint(st, indent_level=indent_level + 1, indent=indent)
            print(f"{indent * indent_level}}}")
        case FunctionDeclaration(_, identifier, arguments, return_type, statements):
            arguments_string = ", ".join(str(argument) for argument in arguments)
            return_type_string = ""
            if return_type is not None:
                return_type_string = f" -> {return_type}"
            print(
                f"{indent * indent_level}def {identifier}({arguments_string}){return_type_string} {{"
            )
            for st in statements:
                pprint(st, indent_level=indent_level + 1, indent=indent)
            print(f"{indent * indent_level}}}\n")
        case st:
            print(f"{indent * indent_level}{st}")
