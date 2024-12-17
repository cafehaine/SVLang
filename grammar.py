import ply.yacc as yacc

from svcast import *
from tokens import tokens

start = "statements"


def p_type_reference(p):
    """
    type_reference : TYPE
    """
    match p[1]:
        case "BOOL":
            p[0] = ValueType.BOOL
        case "UINT":
            p[0] = ValueType.UINT
        case "COLOR":
            p[0] = ValueType.COLOR
        case _:
            raise ValueError(f"Invalid type reference: Unknown type {p[1]!r}")


def p_declaration(p):
    """
    declaration : VARIABLE_IDENTIFIER ':' type_reference '=' expression
    """
    assert isinstance(p[1], str)
    assert isinstance(p[3], ValueType)
    assert isinstance(p[5], Expression)
    p[0] = Declaration(p[1], p[3], p[5])


def p_assignment(p):
    """
    assignment : VARIABLE_IDENTIFIER '=' expression
    """
    assert isinstance(p[1], str)
    assert isinstance(p[3], Expression)
    p[0] = Assignment(p[1], p[3])


def p_function_arguments(p):
    """
    function_arguments : expression ',' function_arguments
                       | expression
                       |
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        assert isinstance(p[1], Expression)
        p[0] = [p[1]]
    else:
        assert isinstance(p[1], Expression)
        assert isinstance(p[3], list)
        p[0] = [p[1]] + p[3]


def p_function_call(p):
    """
    function_call : FUNCTION_IDENTIFIER '(' function_arguments ')'
    """
    assert isinstance(p[1], str)
    assert isinstance(p[3], list)
    p[0] = FunctionCall(p[1], p[3])


def p_numeric_expression(p):
    """
    numeric_expression : expression NUMERIC_OPERATOR expression
                       | NUMBER
    """
    if len(p) == 4:
        assert isinstance(p[1], Expression)
        assert isinstance(p[3], Expression)
        operator: NumericOperator
        match p[2]:
            case "+":
                operator = NumericOperator.ADD
            case "-":
                operator = NumericOperator.SUB
            case "*":
                operator = NumericOperator.MUL
            case "/":
                operator = NumericOperator.DIV
            case _:
                raise ValueError(
                    f"Invalid numeric expression: Unknown operator {p[2]!r}"
                )
        p[0] = NumericExpression(p[1], operator, p[3])
    else:
        assert isinstance(p[1], int)
        p[0] = NumericValue(p[1])


def p_numeric_comparison(p):
    """
    numeric_comparison : expression NUMERIC_COMPARATOR expression
    """
    assert isinstance(p[1], Expression)
    assert isinstance(p[3], Expression)
    comparator: NumericComparator
    match p[2]:
        case "<":
            comparator = NumericComparator.LT
        case "<=":
            comparator = NumericComparator.LEQ
        case "==":
            comparator = NumericComparator.EQ
        case "!=":
            comparator = NumericComparator.NEQ
        case ">=":
            comparator = NumericComparator.GEQ
        case ">":
            comparator = NumericComparator.GT
        case _:
            raise ValueError(f"Invalid numeric comparison: Unknown operator {p[2]!r}")
    p[0] = NumericComparision(p[1], comparator, p[3])


def p_boolean_expression(p):
    """
    boolean_expression : expression BOOLEAN_OPERATOR expression
                       | BOOLEAN_NEGATION expression
                       | BOOLEAN
    """
    if len(p) == 4:
        assert isinstance(p[1], Expression)
        assert isinstance(p[3], Expression)
        operator: BooleanOperator
        match p[2]:
            case "and":
                operator = BooleanOperator.AND
            case "or":
                operator = BooleanOperator.OR
            case _:
                raise ValueError(
                    f"Invalid boolean expression: Unknown operator {p[2]!r}"
                )
        p[0] = BooleanExpression(p[1], operator, p[3])
    elif len(p) == 3:
        assert isinstance(p[2], Expression)
        p[0] = BooleanNegation(p[2])
    else:
        assert isinstance(p[1], bool)
        p[0] = BooleanValue(p[1])


def p_variable_reference(p):
    "variable_reference : VARIABLE_IDENTIFIER"
    p[0] = VariableReference(p[1])


def p_expression(p):
    """
    expression : variable_reference
               | function_call
               | numeric_expression
               | numeric_comparison
               | boolean_expression
    """
    p[0] = p[1]


def p_while(p):
    "while : WHILE expression '{' statements '}'"
    assert isinstance(p[2], Expression)
    assert isinstance(p[4], list)
    p[0] = While(p[2], p[4])


def p_if(p):
    """
    if : IF expression '{' statements '}'
    """
    assert isinstance(p[2], Expression)
    assert isinstance(p[4], list)
    p[0] = If(p[2], p[4])


def p_statement(p):
    """
    statement : declaration
              | assignment
              | expression
              | while
              | if
    """
    p[0] = p[1]


def p_statements(p):
    """
    statements : statement statements
               | statement
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


# Error rule for syntax errors
def p_error(p):
    if p:
        raise SyntaxError(f"Unexpected {p.type} token {p.value} at line {p.lineno}")
    else:
        raise SyntaxError("Unexpected end of file")


# Build the parser
parser = yacc.yacc()


def parse(source: str) -> list[Statement]:
    return parser.parse(source, tracking=True)


if __name__ == "__main__":
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument("source")
    args = p.parse_args()
    with open(args.source, "r") as source_file:
        print(parse(source_file.read()))
