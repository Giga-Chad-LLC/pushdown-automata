# Pushdown Automata

## What is this project?

This project is done as a formal languages course work for sophomore year at HSE SPb. Its goal is to implement pushdown automata with other various components such as context-free grammar syntax, grammar lexer and parser, and grammar conversion algorithm.

## Development requirements:
- Intall `python` and `pip`.
- Setup [virtual environment](https://docs.python-guide.org/dev/virtualenvs/):

    ```bash
    > pip3 install virtualenv
    > git clone https://github.com/Giga-Chad-LLC/pushdown-automata.git && cd pushdown-automata
    > python3 -m venv .venv
    > source .venv/bin/activate # on windows: .venv\Scripts\activate.bat
    ```
- Install project dependencies (make sure that the virtual environment is enabled):
    ```bash
    (.venv)> pip install -r requirements.txt
    ```

## How to use:
- **Lexer**: `python ./lexer.py <path/to/file/with/grammar>` - saves lexing results into the file with same name but adding suffix `.out`.
- **Parser**: `python ./parser.py <path/to/file/with/grammar>` - saves parsing results into the file with the same name but adding suffix `.out`.
- **Interpreter**: `python ./interpreter.py <path/to/file/with/grammar>` - loads grammar rules from the specified file and then starts the interpreter. Interpretor waits for user to input a single string which is analyzed if it is recognized by the provided grammar. Prints the results of the analysis into the file with same name but adding suffix `.out`.
- **Tests**: `python ./test_transformation.py` - runs tests with `unittest` python library.


## Distribution of tasks:

### Dmitrii Artiukhov:
- Implementation of algorithm that converts initial arbitrary context-free grammar into [Greibah Weak Form](https://neerc.ifmo.ru/wiki/index.php?title=%D0%9F%D1%80%D0%B8%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5_%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B8_%D0%BA_%D0%BE%D1%81%D0%BB%D0%B0%D0%B1%D0%BB%D0%B5%D0%BD%D0%BD%D0%BE%D0%B9_%D0%BD%D0%BE%D1%80%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B9_%D1%84%D0%BE%D1%80%D0%BC%D0%B5_%D0%93%D1%80%D0%B5%D0%B9%D0%B1%D0%B0%D1%85): created algorithm that removes left recursion from grammar according to the [article](https://neerc.ifmo.ru/wiki/index.php?title=%D0%A3%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5_%D0%BB%D0%B5%D0%B2%D0%BE%D0%B9_%D1%80%D0%B5%D0%BA%D1%83%D1%80%D1%81%D0%B8%D0%B8), completed the conversion algorithm with the help of other team members, added other various utility pieces of code.
- Simulation of pushdown automata work process: created class `Interpreter` which traverses states of automata (represented in pairs, e.g. `{ string, stack }`, where `string` is a suffix of the string that is is to be covered with grammar parts stored in `stack`) and evaluates if string is recognized by the grammar.
- Took part in covering the codebase with tests.
- Collaborated with other team members in VS Code via the [**Live Share**](https://code.visualstudio.com/learn/collaboration/live-share) and helped other team members.



### Vladislav Artiukhov:

 - Created concrete syntax for an abstract syntax: non-terminals, terminals, rules.
 - Implemented of removal of epsilon-generating rules from grammar using the modification with queue according to the [article](https://neerc.ifmo.ru/wiki/index.php?title=%D0%A3%D0%B4%D0%B0%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5_eps-%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB_%D0%B8%D0%B7_%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B8).
 - Developed evaluation algorithm of user input string as well as created output printing and formatting functionality.
 - Organized and maintained the collaborative work in the VS Code editor via the [**Live Share**](https://code.visualstudio.com/learn/collaboration/live-share) extension.


### Nikolai Vladimirov:

- Implementation of lexer: created tokenization of input context-free grammar description.
- Parser of context-free grammar parser: created class Grammar and others classes which help present a context-free grammar in a convenient way to present the operation of a pushdown automata.
- Tests were written to check the correctness of the simulation of the operation of the pushdown automata.
Checking the operation of the following functionalities:
    - Removing of left-hand recursion
    - Removing epsilon productions in a context-free grammar
    - Removing the start non-terminal
    - Checking the correctness of the reduction to the weak Greibach form
- Collaborated with other team members in VS Code via the [**Live Share**](https://code.visualstudio.com/learn/collaboration/live-share) extension and took part in realization and discussing of code.


## Concrete syntax:

### Terminals and non-terminals format:

- **Non-terminals** format: `🤯...🤯`
- **Terminals** format: `🥵...🥵`
- **Empty string** (aka `ε`) format: `😵`
- **Enumeration terminator** format: `🗿`
- **Start non-terminal** format: `start=🤯...🤯`. **Start** must be included **only once** and must not be followed by **enumeration terminator** `🗿`.


### Grammar rules format:

- Non-terminal is followed by **binding arrow** `👉`, which is followed by the **enumeration** of terminals and nonterminal separated by `🤌` sign.


### Examples:

- Palindromes over an alphabet `{ a, b }`:
    ```
    start=🤯str🤯
    🤯str🤯 👉 🥵a🥵 🤯str🤯 🥵a🥵 🤌 🥵b🥵 🤯str🤯 🥵b🥵 🤌 🥵a🥵 🤌 🥵b🥵 🤌 😵 🗿
    ```

- Right bracket sequence over an alphabet `{ (, ) }`:
    ```
    start=🤯S🤯
    🤯S🤯 👉 🥵(🥵 🤯S🤯 🥵)🥵 🤌 🥵(🥵 🤯S🤯 🥵)🥵 🤯S🤯 🤌 😵 🗿
    ```

- Basic arithmetics over digits `{ 0, 1, 2, 3 }`:
    ```
    start=🤯expr🤯
    🤯expr🤯 👉 🤯expr🤯 🥵+🥵 🤯term🤯 🤌 🤯expr🤯 🥵-🥵 🤯term🤯 🤌 🤯term🤯🗿
    🤯term🤯 👉 🤯term🤯 🥵*🥵 🤯mult🤯 🤌 🤯term🤯 🥵/🥵 🤯mult🤯 🤌 🤯mult🤯🗿
    🤯mult🤯 👉 🥵(🥵 🤯expr🤯 🥵)🥵   🤌 🥵0🥵 🤌 🥵1🥵 🤌 🥵2🥵 🤌 🥵3🥵🗿
    ```

## Lexing and parsing:

We used `ply.lex` and `ply.yacc` python libraries to implement lexer and parser. The abstract syntax tree that we generate when parsing the grammar is based on the following grammar-describing language:

Grammar Entity | Ruleset
------------   | -------------
Single   	   | EMPTY
&nbsp;	       | NON_TERMINAL
&nbsp;		   | TERMINAL
Multiple   	   | Single
&nbsp;	       | Multiple Single
Description	   | Multiple
&nbsp;	       | Description SEPARATOR Multiple
Rule           | NON_TERMINAL ARROW Description END
Ruleset        | Rule
&nbsp;         | Ruleset Rule
Start          | START
Root           | Start Ruleset


## Development issues:
We got our asses 🔥burned down🔥.
