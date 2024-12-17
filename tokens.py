import ply.lex as lex

tokens = (
    "WHILE",
    "IF",
    "TYPE",
    "NUMBER",
    "NUMERIC_OPERATOR",
    "NUMERIC_COMPARATOR",
    "BOOLEAN",
    "BOOLEAN_OPERATOR",
    "BOOLEAN_NEGATION",
    "FUNCTION_IDENTIFIER",
    "VARIABLE_IDENTIFIER",
)

literals = ["{", "}", "(", ")", ":", ",", "="]

t_NUMERIC_OPERATOR = r"[+\-*/]"
t_NUMERIC_COMPARATOR = r"<|>|<=|>=|==|!="


def t_WHILE(t):
    r"while"
    return t


def t_IF(t):
    r"if"
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
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


t_ignore = " \t"


def t_error(t):
    raise SyntaxError(f"Illegal character {t.value[0]!r}")


lexer = lex.lex()

if __name__ == "__main__":
    lex.runmain()
