import ply.lex as lex
from ply.lex import TOKEN
import sys
from tokens import (
    tokens,
    START_TOKEN_REGEX,
    ARROW_TOKEN_REGEX,
    SEPARATOR_TOKEN_REGEX,
    END_TOKEN_REGEX,
    EMPTY_TOKEN_REGEX,
    NON_TERMINAL_TOKEN_REGEX,
    TERMINAL_TOKEN_REGEX,
)

t_ignore = " \t"


def t_newline(token):
    r"\n+"
    token.lexer.lineno += len(token.value)


def t_error(token):
    if token is None:
        print("Lexer: Unexpected end of input")
    else:
        token_description = f"{token.type}({token.value}) at {token.lineno}:{token.lexpos}"
        print(f"Lexer: Syntax error: Unexpected {token_description}", token)
    exit()


@TOKEN(START_TOKEN_REGEX)
def t_START(token):
    token.value = token.value[7:-1]
    return token


t_ARROW = ARROW_TOKEN_REGEX

t_SEPARATOR = SEPARATOR_TOKEN_REGEX

t_END = END_TOKEN_REGEX

t_EMPTY = EMPTY_TOKEN_REGEX


@TOKEN(NON_TERMINAL_TOKEN_REGEX)
def t_NON_TERMINAL(token):
    print(token.value)
    token.value = token.value[1:-1]
    return token


@TOKEN(TERMINAL_TOKEN_REGEX)
def t_TERMINAL(token):
    print(token.value)
    token.value = token.value[1:-1]
    return token


lexer = lex.lex()


def main():
    lexer = lex.lex()

    if len(sys.argv) > 1:
        filename = sys.argv[1]

        with open(filename, "r", encoding="utf-8") as grammar, open(
            filename + ".out", "w", encoding="utf-8"
        ) as output_grammar:
            lexer.input("".join(grammar.readlines()))

            while token := lexer.token():
                print(token, file=output_grammar)
    else:
        while True:
            lexer.input(input("> "))

            while token := lexer.token():
                print(token)


if __name__ == "__main__":
    main()
