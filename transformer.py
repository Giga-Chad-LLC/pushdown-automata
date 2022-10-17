import copy
from queue import Queue
from typing import List, Set, Tuple
from parser import (
    Empty,
    Grammar,
    Multiple,
    NonTerminal,
    Terminal,
    Rule,
    Root,
    Ruleset,
    Single,
    Start,
    get_non_terminals,
    get_terminals,
)


class Transformer:
    def _greibah_iteration(self, grammar: Grammar) -> Tuple[bool, Grammar]:
        grammar = copy.deepcopy(grammar)
        nonterminals_rules: dict[str, List[Rule]] = self.get_rules_by_nonterminal(
            grammar
        )
        non_terminals_list = sorted(list(grammar.non_terminals))

        n = len(grammar.non_terminals)
        grammar_changed = False

        for i in range(n - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                # Aj → δ1 | … | δk
                # Ai → Aj γ         <- remove

                # Ai → δ1 γ | … | δk γ

                Ai = non_terminals_list[i]
                Aj = non_terminals_list[j]

                for rule in nonterminals_rules[Ai]:
                    # since grammar is flattened
                    assert (
                        len(rule.values) == 1
                    ), f"Grammar is not flattened: {grammar.to_string()}"

                    if rule.values[0].values[0].object.value == Aj:
                        grammar_changed = True
                        # remove old rule
                        # TODO: list.remove may throw!
                        grammar.ast.ruleset.rules.remove(rule)
                        # add new rules
                        gamma = rule.values[0].values[1:]
                        for delta_rule in nonterminals_rules[Aj]:
                            assert (
                                len(delta_rule.values) == 1
                            ), f"More than 1 multiple in `delta_rule`: {delta_rule.to_string()}"
                            delta = copy.deepcopy(delta_rule.values[0])

                            new_rule = Rule(
                                variable=NonTerminal(Ai),
                                values=[Multiple(delta.values + gamma)],
                            )
                            grammar.ast.ruleset.append(new_rule)

        return (grammar_changed, grammar)

    def to_greibah_weak_form(self, grammar: Grammar) -> Grammar:
        grammar = self._remove_left_recursion(
            self._remove_epsilon_rules(grammar)
        ).flatten()

        (changed, grammar) = self._greibah_iteration(grammar)

        while changed:
            (changed, grammar) = self._greibah_iteration(grammar)

        grammar = self._remove_isolated_rules(grammar)

        grammar.non_terminals = get_non_terminals(grammar.ast)
        grammar.terminals = get_terminals(grammar.ast)
        return grammar

    def _is_greibah_weak_form(self, grammar: Grammar) -> bool:
        # A → aγ: a - terminal
        for rule in grammar.ast.ruleset.rules:
            for multiple in rule.values:
                assert len(
                    multiple.values
                ), f"Length is less than 1 in `multiple.values`: {multiple.to_string()}"

                is_terminal = isinstance(multiple.values[0].object, Terminal)
                is_eps = isinstance(multiple.values[0].object, Empty)

                is_start_variable = (
                    rule.variable.value == grammar.ast.start.variable.value
                )

                if not (is_terminal or (is_start_variable and is_eps)):
                    return False

        # A ⇸ ε: if A != S
        for rule in grammar.ast.ruleset.rules:
            if (
                rule.variable.value != grammar.ast.start.variable.value
                and self._is_epsilon_generating_rule(rule)
            ):
                return False

        return not self._has_start_non_terminal_in_right_part(grammar)

    def _remove_epsilon_rules(self, grammar: Grammar) -> Grammar:
        grammar = grammar.flatten()
        epsilon_generating_nonterminals = self._get_epsilon_generating_nonterminals(
            grammar
        )

        rules = grammar.ast.ruleset.rules

        result_rules: List[Rule] = []

        for rule in rules:
            k = self._count_epsilon_generating_nonterminals_in_rule(
                rule, epsilon_generating_nonterminals
            )

            for bits in range(2**k):
                new_multiple = Multiple([])
                index = 0

                # since flatten made len(rule.values) == 1
                multiple = rule.values[0]
                for single in multiple.values:
                    should_append = True

                    if isinstance(
                        single.object, NonTerminal
                    ) and epsilon_generating_nonterminals.count(single.object.value):
                        if not (bits & (2**index)):
                            should_append = False
                        index += 1

                    if should_append:
                        new_multiple.append(single)

                new_rule = Rule(rule.variable, [new_multiple])

                # do not add epsilon generating rules according to the algorithm
                if not self._is_epsilon_generating_rule(new_rule):
                    result_rules.append(new_rule)

        # adding new rule (S' -> S | ε) if initial grammar appears to be epsilon-generating
        is_epsilon_generating_grammar = self._is_epsilon_generating_grammar(grammar)

        start_nonterminal: NonTerminal = grammar.ast.start.variable

        if is_epsilon_generating_grammar:
            start_nonterminal = self._create_unique_nonterminal(
                grammar.ast.start.variable.value,
                grammar.non_terminals | grammar.terminals,
            )

            # S' -> S | ε
            result_rules.append(
                Rule(
                    start_nonterminal,
                    [
                        Multiple([Single(Empty())]),
                        Multiple([Single(grammar.ast.start.variable)]),
                    ],
                )
            )

        new_grammar = Grammar(
            ast=Root(Start(start_nonterminal), Ruleset(result_rules)),
            non_terminals=grammar.non_terminals,
            terminals=grammar.terminals,
        )
        return new_grammar

    def _create_unique_nonterminal(
        self, start: str, used_names: Set[str]
    ) -> NonTerminal:
        new_start = start
        while new_start in used_names:
            new_start += "'"
        return NonTerminal(new_start)

    def _is_epsilon_generating_grammar(self, grammar: Grammar) -> bool:
        for rule in grammar.ast.ruleset.rules:
            # if left part of rule is start and rule generates epsilon
            if (
                rule.variable.value == grammar.ast.start.variable.value
                and self._is_epsilon_generating_rule(rule)
            ):
                return True
        return False

    def _get_epsilon_generating_nonterminals(self, grammar: Grammar) -> List[str]:
        grammar = grammar.flatten()
        rules = grammar.ast.ruleset.rules

        is_epsilon: dict[str, bool] = {}
        concerned_rules: dict[str, list[int]] = {}
        counter: dict[int, int] = {}

        queue: Queue[str] = Queue()

        for nonterm in grammar.non_terminals:
            is_epsilon[nonterm] = False
            concerned_rules[nonterm] = []

        # For each rule get the number of non-terminals in its description and fill `is_epsilon`
        for index in range(len(rules)):
            rule = rules[index]
            counter[index] = self._count_nonterminals_in_rule(rule)

            if counter[index] == 0 and self._is_epsilon_generating_rule(rule):
                # current rule has the form: nonterm -> EPS | EPS | ... | EPS
                queue.put(rule.variable.value)
                is_epsilon[rule.variable.value] = True

        # Collect `concerned_rules`: for each nonterm find the rules that contain it in description
        for nonterm in grammar.non_terminals:
            for rule_index in range(len(rules)):
                rule = rules[rule_index]

                for multiple in rule.values:
                    for single in multiple.values:
                        if (
                            isinstance(single.object, NonTerminal)
                            and single.object.value == nonterm
                        ):
                            concerned_rules[nonterm].append(rule_index)

        while not queue.empty():
            nonterm = queue.get()

            for rule_index in concerned_rules[nonterm]:
                counter[rule_index] -= 1

                if counter[rule_index] == 0:
                    rule = rules[rule_index]
                    is_epsilon[rule.variable.value] = True
                    queue.put(rule.variable.value)

        # creating result
        epsilon_generating_nonterminals = []

        for (nonterm, is_epsilon_generating) in is_epsilon.items():
            if is_epsilon_generating is True:
                epsilon_generating_nonterminals.append(nonterm)

        return sorted(epsilon_generating_nonterminals)

    def _count_nonterminals_in_rule(self, rule: Rule) -> int:
        result = 0

        for multiple in rule.values:
            for single in multiple.values:
                if isinstance(single.object, NonTerminal):
                    result += 1

        return result

    def _count_epsilon_generating_nonterminals_in_rule(
        self, rule: Rule, epsilon_generating_nonterms: List[str]
    ) -> int:
        count = 0

        for multiple in rule.values:
            for single in multiple.values:
                if isinstance(
                    single.object, NonTerminal
                ) and epsilon_generating_nonterms.count(single.object.value):
                    count += 1

        return count

    def has_immediate_epsilon_generating_evaluation(self, rule: Rule) -> bool:
        for multiple in rule.values:
            result = True
            for single in multiple.values:
                if not isinstance(single.object, Empty):
                    result = False

            if result:
                return True

        return False

    def _is_epsilon_generating_rule(self, rule: Rule) -> bool:
        for multiple in rule.values:
            for single in multiple.values:
                if not isinstance(single.object, Empty):
                    return False
        return True

    def get_rules_by_nonterminal(self, grammar: Grammar) -> dict[str, List[Rule]]:
        nonterminals_rules: dict[str, List[Rule]] = {}

        for rule in grammar.ast.ruleset.rules:
            nonterm = rule.variable.value

            if nonterm not in nonterminals_rules:
                nonterminals_rules[nonterm] = []

            nonterminals_rules[nonterm].append(copy.deepcopy(rule))

        return nonterminals_rules

    def _remove_left_recursion(self, grammar: Grammar) -> Grammar:
        grammar = grammar.flatten()

        nonterminals_rules: dict[str, List[Rule]] = self.get_rules_by_nonterminal(
            grammar
        )

        nonterminals: List[str] = sorted(list(copy.deepcopy(grammar.non_terminals)))

        # for Ai ∈ N
        for i in range(len(nonterminals)):
            Ai = nonterminals[i]
            # for Aj ∈ { N ∣ 1 <= j < i }
            for j in range(i):
                Aj = nonterminals[j]

                # for p ∈ { p ∣ Ai → Aj γ }
                for p_Ai in nonterminals_rules[Ai]:
                    multiple_Ai = copy.deepcopy(p_Ai.values[0])

                    if (
                        multiple_Ai.values[0].object.value != Aj
                    ):  # leading_token_in_rule != Aj
                        continue

                    # now we are dealing with rules of the form: `Ai → Aj γ`

                    # TODO: `remove()` may throw exception!
                    grammar.ast.ruleset.rules.remove(p_Ai)  # p_Ai = Ai → Aj γ

                    # Aj → δ1 ∣ … ∣ δk
                    # Ai → δ1 γ ∣ … ∣ δk γ, where p_Ai = Ai → Aj γ
                    for p_Aj in nonterminals_rules[Aj]:
                        delta = copy.deepcopy(p_Aj.values[0])
                        delta.values += multiple_Ai.values[1:]

                        new_rule_Ai = Rule(
                            variable=NonTerminal(Ai), values=[delta]
                        )  # Ai → δk γ
                        # TODO: should we add `new_rule_Ai` to the set of rules that we are iterating over?
                        grammar.ast.ruleset.append(new_rule_Ai)

            grammar = self._remove_immediate_left_recursion(grammar, NonTerminal(Ai))

        grammar.non_terminals = get_non_terminals(grammar.ast)
        grammar.terminals = get_terminals(grammar.ast)
        return grammar

    def _has_start_non_terminal_in_right_part(self, grammar: Grammar) -> bool:
        start_non_terminal = grammar.ast.start.variable

        for rule in grammar.ast.ruleset.rules:
            for multiple in rule.values:
                for single in multiple.values:
                    if single.object.value == start_non_terminal.value:
                        return True
        return False

    def _remove_start_non_terminal_from_right_part(self, grammar: Grammar) -> Grammar:
        start_non_terminal = grammar.ast.start.variable
        new_grammar = copy.deepcopy(grammar)

        if self._has_start_non_terminal_in_right_part(grammar):
            new_start_non_terminal = self._create_unique_nonterminal(
                start_non_terminal.value, grammar.terminals | grammar.non_terminals
            )

            new_grammar.ast.start.variable = new_start_non_terminal
            new_grammar.ast.ruleset.append(
                Rule(
                    variable=new_start_non_terminal,
                    values=[Multiple([Single(start_non_terminal)])],
                )
            )

        return new_grammar

    def _remove_immediate_left_recursion(
        self, grammar: Grammar, symbol: NonTerminal
    ) -> Grammar:
        symbol_rule = Rule(symbol, [])
        new_grammar = grammar.flatten()

        for rule in new_grammar.ast.ruleset.rules:
            if rule.variable.value == symbol.value:
                symbol_rule.values += copy.deepcopy(rule.values)

        # remove rules that are about to be changed
        new_grammar.ast.ruleset.rules = list(
            filter(
                lambda rule: rule.variable.value != symbol.value,
                new_grammar.ast.ruleset.rules,
            )
        )

        # A → A α1 ∣ … ∣ A αn ∣ β1 ∣ … ∣ βm

        # A → β1 A′ ∣ … ∣ βm A′ ∣ β1 ∣ … ∣ βm
        # A′ → α1 A′ ∣ … ∣ αn A′ ∣ α1 ∣ … ∣ αn

        is_symbol_included_immediately = (
            lambda multiple: isinstance(multiple.values[0].object, NonTerminal)
            and multiple.values[0].object.value == symbol.value
        )

        betas = list(
            filter(
                lambda multiple: not is_symbol_included_immediately(multiple),
                symbol_rule.values,
            )
        )

        alphas = list(
            map(
                lambda multiple: Multiple(multiple.values[1:]),
                list(filter(is_symbol_included_immediately, symbol_rule.values)),
            )
        )

        # if no immediate recursion exists
        if len(alphas) == 0:
            return grammar

        # creating symbol': S -> S'
        symbol_ = self._create_unique_nonterminal(
            symbol.value, new_grammar.non_terminals | new_grammar.terminals
        )

        # A → β1 A′ ∣ ... ∣ βm A′ ∣ β1 ∣ ... ∣ βm
        new_symbol_rule = Rule(
            symbol,
            [Multiple(beta.values + [Single(symbol_)]) for beta in betas] + betas,
        )

        # A′ → α1 A′ ∣ ... ∣ αn A′ ∣ α1 ∣ ... ∣ αn
        new_symbol__rule = Rule(
            symbol_,
            [Multiple(alpha.values + [Single(symbol_)]) for alpha in alphas] + alphas,
        )

        new_grammar.ast.ruleset.append(new_symbol_rule)
        new_grammar.ast.ruleset.append(new_symbol__rule)

        new_grammar.non_terminals = get_non_terminals(new_grammar.ast)
        new_grammar.terminals = get_terminals(new_grammar.ast)

        return new_grammar

    def _remove_isolated_rules(self, grammar: Grammar) -> Grammar:
        grammar = grammar.unflatten()

        rules_count = len(grammar.ast.ruleset.rules)

        isolated_rules: List[Rule] = []

        for i in range(rules_count):
            rule = grammar.ast.ruleset.rules[i]

            if rule.variable.value == grammar.ast.start.variable.value:
                continue

            is_isolated = True

            for j in range(rules_count):
                if i == j:
                    continue

                for multiple in grammar.ast.ruleset.rules[j].values:
                    for single in multiple.values:
                        if single.object.value == rule.variable.value:
                            is_isolated = False

            if is_isolated:
                isolated_rules.append(rule)

        for rule in isolated_rules:
            # TODO: `remove()` may throw!
            grammar.ast.ruleset.rules.remove(rule)

        grammar.non_terminals = get_non_terminals(grammar.ast)
        grammar.terminals = get_terminals(grammar.ast)

        return grammar
