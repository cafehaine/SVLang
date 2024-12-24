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
    p[0] = Declaration(p.lineno(1), p[1], p[3], p[5])


def p_assignment(p):
    """
    assignment : VARIABLE_IDENTIFIER '=' expression
    """
    assert isinstance(p[1], str)
    assert isinstance(p[3], Expression)
    p[0] = Assignment(p.lineno(1), p[1], p[3])


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
    p[0] = FunctionCall(p.lineno(1), p[1], p[3])


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
        p[0] = NumericExpression(p.lineno(1), p[1], operator, p[3])
    else:
        assert isinstance(p[1], int)
        p[0] = NumericValue(p.lineno(1), p[1])


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
    p[0] = NumericComparison(p.lineno(1), p[1], comparator, p[3])


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
        p[0] = BooleanExpression(p.lineno(1), p[1], operator, p[3])
    elif len(p) == 3:
        assert isinstance(p[2], Expression)
        p[0] = BooleanNegation(p.lineno(1), p[2])
    else:
        assert isinstance(p[1], bool)
        p[0] = BooleanValue(p.lineno(1), p[1])


def p_binary_expression(p):
    """
    binary_expression : NUMBER BINARY_OPERATOR NUMBER
                      | NUMBER BINARY_OPERATOR variable_reference
                      | variable_reference BINARY_OPERATOR NUMBER
                      | variable_reference BINARY_OPERATOR variable_reference
    """
    left: NumericValue | VariableReference
    right: NumericValue | VariableReference

    if isinstance(p[1], VariableReference):
        left = p[1]
    elif isinstance(p[1], int):
        left = NumericValue(p.lineno(1), p[1])
    else:
        raise ValueError(
            f"Invalid type {type(p[1])} for lefthand operand, expected variable reference or int"
        )

    if isinstance(p[3], VariableReference):
        right = p[3]
    elif isinstance(p[3], int):
        right = NumericValue(p.lineno(1), p[3])
    else:
        raise ValueError(
            f"Invalid type {type(p[3])} for righthand operand, expected variable reference or int"
        )

    p[0] = BinaryExpression(
        p.lineno(1),
        left,
        {
            "&": BinaryOP.AND,
            "^": BinaryOP.XOR,
        }[p[2]],
        right,
    )


def p_binary_negation(p):
    """
    binary_negation : '!' NUMBER
                    | '!' variable_reference
    """
    if isinstance(p[2], int):
        p[0] = BinaryNegation(p.lineno(1), NumericValue(p.lineno(1), p[2]))
    elif isinstance(p[2], VariableReference):
        p[0] = BinaryNegation(p.lineno(1), p[2])
    else:
        raise ValueError("Invalid type for operand, expected variable reference or int")


def p_variable_reference(p):
    "variable_reference : VARIABLE_IDENTIFIER"
    p[0] = VariableReference(p.lineno(1), p[1])


def p_color_expression(p):
    "color_expression : COLOR"
    p[0] = Color(p.lineno(1), p[1])


def p_expression(p):
    """
    expression : variable_reference
               | function_call
               | numeric_expression
               | numeric_comparison
               | boolean_expression
               | binary_expression
               | color_expression
    """
    p[0] = p[1]


def p_while(p):
    "while : WHILE expression '{' statements '}'"
    assert isinstance(p[2], Expression)
    assert isinstance(p[4], list)
    p[0] = While(p.lineno(1), p[2], p[4])


def p_if(p):
    """
    if : IF expression '{' statements '}' ELSE '{' statements '}'
       | IF expression '{' statements '}'
    """
    if len(p) == 6:
        assert isinstance(p[2], Expression)
        assert isinstance(p[4], list)
        p[0] = If(p.lineno(1), p[2], p[4])
    else:
        assert isinstance(p[2], Expression)
        assert isinstance(p[4], list)
        assert isinstance(p[8], list)
        p[0] = If(p.lineno(1), p[2], p[4], p[8])


def p_function_declare_arguments(p):
    """
    function_declare_arguments : VARIABLE_IDENTIFIER ':' type_reference ',' function_declare_arguments
                               | VARIABLE_IDENTIFIER ':' type_reference
                               |
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 4:
        assert isinstance(p[1], str)
        assert isinstance(p[3], ValueType)
        p[0] = [ArgumentDeclaration(p[1], p[3])]
    elif len(p) == 6:
        assert isinstance(p[1], str)
        assert isinstance(p[3], ValueType)
        assert isinstance(p[5], list)
        p[0] = [ArgumentDeclaration(p[1], p[3]), *p[5]]


def p_function_declaration(p):
    """
    function_declaration : DEF FUNCTION_IDENTIFIER '(' function_declare_arguments ')' ARROW type_reference '{' statements '}'
                         | DEF FUNCTION_IDENTIFIER '(' function_declare_arguments ')' '{' statements '}'
    """
    if len(p) == 11:
        assert isinstance(p[2], str)
        assert isinstance(p[4], list)
        assert isinstance(p[7], ValueType)
        assert isinstance(p[9], list)
        p[0] = FunctionDeclaration(p.lineno(1), p[2], p[4], p[7], p[9])
    else:
        assert isinstance(p[2], str)
        assert isinstance(p[4], list)
        assert isinstance(p[7], list)
        p[0] = FunctionDeclaration(p.lineno(1), p[2], p[4], None, p[7])


def p_return(p):
    """
    return : RETURN expression
           | RETURN
    """
    if len(p) == 3:
        assert isinstance(p[2], Expression)
        p[0] = Return(p.lineno(1), p[2])
    else:
        p[0] = Return(p.lineno(1), None)


def p_break(p):
    """
    break : BREAK
    """
    p[0] = Break(p.lineno(1))


def p_asm_arg(p):
    """
    asm_arg : variable_reference
            | NUMBER
    """
    if isinstance(p[1], int):
        p[0] = NumericValue(p.lineno(1), p[1])
    else:
        p[0] = p[1]


def p_asm(p):
    """
    asm : ASM ASM_OP asm_arg asm_arg asm_arg
    """
    assert isinstance(p[3], (VariableReference, NumericValue))
    assert isinstance(p[4], (VariableReference, NumericValue))
    assert isinstance(p[5], (VariableReference, NumericValue))
    p[0] = ASMInstruction(p.lineno(1), ASMOps[p[2]], p[3], p[4], p[5])


def p_statement(p):
    """
    statement : declaration
              | assignment
              | expression
              | while
              | if
              | function_declaration
              | return
              | break
              | asm
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
        for statement in parse(source_file.read()):
            pprint(statement)
