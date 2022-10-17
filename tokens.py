tokens = [
    "START",
    "ARROW",
    "SEPARATOR",
    "END",
    "EMPTY",
    "NON_TERMINAL",
    "TERMINAL",
]

token_to_symbol = {
    "START": "=",
    "ARROW": "👉",
    "SEPARATOR": "🤌",
    "END": "🗿",
    "EMPTY": "😵",
    "NON_TERMINAL": "🤯",
    "TERMINAL": "🥵",
}

START_TOKEN = rf"{token_to_symbol['START']}"
NON_TERMINAL_TOKEN = rf"{token_to_symbol['NON_TERMINAL']}"
TERMINAL_TOKEN = rf"{token_to_symbol['TERMINAL']}"

START_TOKEN_REGEX = (
    r"start" + START_TOKEN + NON_TERMINAL_TOKEN + r"[\x00-\x7F]+" + NON_TERMINAL_TOKEN
)
ARROW_TOKEN_REGEX = rf"{token_to_symbol['ARROW']}"
SEPARATOR_TOKEN_REGEX = rf"{token_to_symbol['SEPARATOR']}"
END_TOKEN_REGEX = rf"{token_to_symbol['END']}"
EMPTY_TOKEN_REGEX = rf"{token_to_symbol['EMPTY']}"
NON_TERMINAL_TOKEN_REGEX = NON_TERMINAL_TOKEN + r"[\x00-\x7F]+" + NON_TERMINAL_TOKEN
TERMINAL_TOKEN_REGEX = TERMINAL_TOKEN + r"[\x00-\x7F]+" + TERMINAL_TOKEN
