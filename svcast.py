from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto

from typing import Any, Literal


class ASTNode(ABC): ...


class Expression(ASTNode): ...


@dataclass
class FunctionCall(Expression):
    identifier: str
    arguments: list[Expression]


class NumericOperator(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()


@dataclass
class NumericExpression(Expression):
    left: Expression
    operator: NumericOperator
    right: Expression


class NumericComparator(Enum):
    LT = auto()
    LEQ = auto()
    EQ = auto()
    NEQ = auto()
    GEQ = auto()
    GT = auto()


@dataclass
class NumericComparision(Expression):
    left: Expression
    operator: NumericComparator
    right: Expression


class BooleanOperator(Enum):
    OR = auto()
    AND = auto()


@dataclass
class BooleanExpression(Expression):
    left: Expression
    operator: BooleanOperator
    right: Expression


@dataclass
class BooleanNegation(Expression):
    expression: Expression


@dataclass
class VariableReference(Expression):
    identifier: str


@dataclass
class BooleanValue(Expression):
    value: bool


@dataclass
class NumericValue(Expression):
    value: int


class Statement(ASTNode): ...


class ValueType(Enum):
    UINT = auto()
    BOOL = auto()
    COLOR = auto()


@dataclass
class Declaration(Statement):
    identifier: str
    type: ValueType
    value: Expression


@dataclass
class Assignment(Statement):
    identifier: str
    value: Expression


@dataclass
class While(Statement):
    expression: Expression
    statements: list[Statement]


@dataclass
class If(Statement):
    expression: Expression
    statements: list[Statement]
