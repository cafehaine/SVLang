import re

import ply.lex as lex

tokens = (
    "COMMENT",
    "ASM",
    "ASM_OP",
    "DEF",
    "ARROW",
    "RETURN",
    "WHILE",
    "BREAK",
    "IF",
    "ELSE",
    "TYPE",
    "NUMBER",
    "NUMERIC_OPERATOR",
    "NUMERIC_COMPARATOR",
    "BOOLEAN",
    "BOOLEAN_OPERATOR",
    "BOOLEAN_NEGATION",
    "BINARY_OPERATOR",
    "BINARY_NEGATION",
    "COLOR",
    "FUNCTION_IDENTIFIER",
    "VARIABLE_IDENTIFIER",
)

literals = ["{", "}", "(", ")", ":", ",", "="]

t_NUMERIC_OPERATOR = r"[+\-*/]"
t_NUMERIC_COMPARATOR = r"<|>|<=|>=|==|!="


def t_ignore_COMMENT(t):
    r"//.*"
    pass  # ignore comment tokens


def t_ASM(t):
    r"ASM"
    return t


def t_ASM_OP(t):
    r"Set|GoTo|Skip|Add|Sub|Mul|Div|Cmp|Deref|Ref|Inst|Print|Read|Band|Xor|Sync"
    return t


def t_DEF(t):
    r"def"
    return t


def t_ARROW(t):
    r"->"
    return t


def t_RETURN(t):
    r"return"
    return t


def t_WHILE(t):
    r"while"
    return t


def t_BREAK(t):
    r"break"
    return t


def t_IF(t):
    r"if"
    return t


def t_ELSE(t):
    r"else"
    return t


def t_NUMBER(t):
    r"0b[01_]+|0x[a-fA-F\d_]+|[\d_]+"
    group_pattern = r"(?:0b(?P<binary>[01_]+))|(?:0x(?P<hexadecimal>[a-fA-F\d_]+))|(?P<decimal>[\d_]+)"
    match = re.match(group_pattern, t.value)
    assert match is not None
    groupdicts = match.groupdict()
    if groupdicts["binary"]:
        t.value = int(t.value, 2)
    elif groupdicts["hexadecimal"]:
        t.value = int(t.value, 16)
    elif groupdicts["decimal"]:
        t.value = int(t.value)
    else:
        raise RuntimeError("matched unknown group")
    return t


def t_TYPE(t):
    r"BOOL|UINT|COLOR"
    return t


def t_BOOLEAN(t):
    r"True|False"
    t.value = t.value == "True"
    return t


def t_BOOLEAN_OPERATOR(t):
    r"and|or"
    return t


def t_BOOLEAN_NEGATION(t):
    r"not"
    return t


def t_BINARY_OPERATOR(t):
    r"\^|&"
    return t


def t_BINARY_NEGATION(t):
    r"!"
    return t


def t_COLOR(t):
    r"[#][0-9a-fA-F]{4}"
    t.value = int(t.value[1:], 16)
    return t


def t_FUNCTION_IDENTIFIER(t):
    r"\w(\w|[0-9_])*"
    return t


def t_VARIABLE_IDENTIFIER(t):
    r"\$\w(\w|[0-9_])*"
    t.value = t.value[1:]
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


t_ignore = " \t\r"


def t_error(t):
    raise SyntaxError(f"Illegal character {t.value[0]!r}")


lexer = lex.lex()

if __name__ == "__main__":
    lex.runmain()
