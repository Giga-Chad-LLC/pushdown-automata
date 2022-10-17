import sys
import copy
from typing import List, Tuple
from parser import (
    parser,
    Grammar,
    Single,
    NonTerminal,
    Terminal,
    Empty,
    Rule,
    Root,
    get_terminals,
    get_non_terminals,
)
from transformer import Transformer


class Interpreter:
    grammar: Grammar

    def set_grammar(self, grammar: Grammar):
        print("Grammar set: ")
        print(grammar.to_string())

        self.grammar = Transformer().to_greibah_weak_form(grammar)
        print("Convert grammar to Greibah weak form:")
        print(self.grammar.to_string())

    def evaluate(self, string: str) -> Tuple[bool, List[Tuple[str, List[Single]]]]:
        evaluation_trace: List[Tuple[str, List[Single]]] = []
        result = self._traverse(
            string, [Single(self.grammar.ast.start.variable)], evaluation_trace
        )
        return (result, evaluation_trace)

    def stack_to_string(self, stack: List[Single]) -> str:
        result = "["
        index = 0
        for elem in stack:
            index += 1
            result += elem.to_string()
            if len(stack) != index:
                result += ", "
        result += "]"
        return result

    def _traverse(
        self,
        string: str,
        stack: List[Single],
        evaluation_trace: List[Tuple[str, List[Single]]],
    ):
        evaluation_trace.append((string, copy.deepcopy(stack)))

        if len(string) == 0:
            # removing epsilon generating non-terminals from stack
            while len(stack) and isinstance(stack[-1].object, NonTerminal):
                rules = Transformer().get_rules_by_nonterminal(self.grammar)[
                    stack[-1].object.value
                ]

                able_to_generate_epsilon = False
                for rule in rules:
                    if Transformer().has_immediate_epsilon_generating_evaluation(rule):
                        able_to_generate_epsilon = True
                        break

                if able_to_generate_epsilon:
                    stack.pop()
                    evaluation_trace.append((string, copy.deepcopy(stack)))
                else:
                    break

            result = len(stack) == 0

            if result is False:
                evaluation_trace.pop()

            return result

        if len(stack) == 0:
            evaluation_trace.pop()
            return False

        tr = Transformer()
        rules_by_nonterminals: dict[str, List[Rule]] = tr.get_rules_by_nonterminal(
            self.grammar
        )
        a = stack.pop().object

        if isinstance(a, NonTerminal):
            for rule in rules_by_nonterminals[a.value]:
                for multiple in rule.values:
                    if self._traverse(
                        string,
                        stack + list(reversed(multiple.values)),
                        evaluation_trace,
                    ):
                        return True
        elif isinstance(a, Terminal):
            if string[0] == a.value:
                result = self._traverse(string[1:], stack, evaluation_trace)

                if result is False:
                    evaluation_trace.pop()
                return result
            else:
                evaluation_trace.pop()
                return False
        else:
            result = self._traverse(string, stack, evaluation_trace)

            if result is False:
                evaluation_trace.pop()
            return result

        evaluation_trace.pop()
        return False


interpreter = Interpreter()


def write_evaluation_steps_to_file(
    filename: str,
    provided_grammar: Grammar,
    greibah_weak_formed_grammar: Grammar,
    string: str,
    evaluation_result: bool,
    evaluation_trace: List[Tuple[str, List[Single]]],
) -> None:
    with open(filename, "w", encoding="utf-8") as output:

        print("Provided Grammar:", file=output)
        print(provided_grammar.to_string(), file=output)
        print(file=output)

        print("Grammar in Greibah weak form:", file=output)
        print(greibah_weak_formed_grammar.to_string(), file=output)
        print(file=output)

        print("-- Evaluation --", file=output)
        print(f"Grammar contains '{string}': {evaluation_result}\n", file=output)

        if evaluation_result:
            print(f"Evaluation trace:", file=output)
            for (s, stack) in evaluation_trace:
                trace_step: str = (
                    "{ " + f"'{s}', {interpreter.stack_to_string(stack)}" + " }"
                )
                print(trace_step, file=output)
        else:
            print(f"No evaluation trace", file=output)


def main():
    if len(sys.argv) > 1:
        filepath: str = sys.argv[1]

        with open(filepath, "r", encoding="utf-8") as grammar_description:
            ast: Root = parser.parse("".join(grammar_description.readlines()))
            grammar = Grammar(ast, get_terminals(ast), get_non_terminals(ast))
            print(grammar.to_string())
            interpreter.set_grammar(grammar)

        print("Enter string to evaluate with grammar:")
        while True:
            string = input("> ")
            (result, evaluation_trace) = interpreter.evaluate(string)
            output_file = f"{filepath}.out"
            write_evaluation_steps_to_file(
                output_file,
                grammar,
                interpreter.grammar,
                string,
                result,
                evaluation_trace,
            )

            print(f"Result has been printed into '{output_file}' file")

    else:
        while True:
            print(parser.parse(input("> ")))


if __name__ == "__main__":
    main()
