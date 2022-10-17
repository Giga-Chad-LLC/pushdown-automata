import copy
import unittest
from transformer import Transformer
from parser import (
    Grammar,
    Empty,
    NonTerminal,
    Terminal,
    Single,
    Multiple,
    Rule,
    Ruleset,
    Start,
    Root,
    get_terminals,
    get_non_terminals,
)


class Test_TransformerFindEpsilonGeneratingNonterminals(unittest.TestCase):
    def test_simple_grammar(self):
        # S → ABC
        # S → DS
        # A → ε
        # B → AC
        # C → ε
        # D → d

        ANonTerm = NonTerminal("A")
        BNonTerm = NonTerminal("B")
        CNonTerm = NonTerminal("C")
        DNonTerm = NonTerminal("D")
        SNonTerm = NonTerminal("S")

        A = Single(ANonTerm)
        B = Single(BNonTerm)
        C = Single(CNonTerm)
        D = Single(DNonTerm)
        S = Single(SNonTerm)
        d = Single(Terminal("d"))
        eps = Single(Empty())

        ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [
                    Rule(SNonTerm, [Multiple([A, B, C]), Multiple([D, S])]),
                    Rule(ANonTerm, [Multiple([eps])]),
                    Rule(BNonTerm, [Multiple([A, C])]),
                    Rule(CNonTerm, [Multiple([eps])]),
                    Rule(DNonTerm, [Multiple([d])]),
                ]
            ),
        )

        grammar = Grammar(ast, get_terminals(ast), get_non_terminals(ast))

        result = Transformer()._get_epsilon_generating_nonterminals(grammar)

        self.assertEqual(["A", "B", "C", "S"], result)

    def test_right_bracket_sequence(self):
        # S → ASBS
        # S → ε
        # A → (
        # B → )

        ANonTerm = NonTerminal("A")
        BNonTerm = NonTerminal("B")
        SNonTerm = NonTerminal("S")

        A = Single(ANonTerm)
        B = Single(BNonTerm)
        S = Single(SNonTerm)

        lb = Single(Terminal("("))
        rb = Single(Terminal(")"))
        eps = Single(Empty())

        ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [
                    Rule(SNonTerm, [Multiple([A, S, B, S]), Multiple([eps])]),
                    Rule(ANonTerm, [Multiple([lb])]),
                    Rule(BNonTerm, [Multiple([rb])]),
                ]
            ),
        )

        grammar = Grammar(ast, get_terminals(ast), get_non_terminals(ast))

        result = Transformer()._get_epsilon_generating_nonterminals(grammar)

        self.assertEqual(["S"], result)


class Test_TransformerRemoveEpsilonGeneratingRules(unittest.TestCase):
    def test_simple_grammar(self):
        # S → ABCd
        # A → a | ε
        # B → AC
        # C → c | ε

        ANonTerm = NonTerminal("A")
        BNonTerm = NonTerminal("B")
        CNonTerm = NonTerminal("C")
        SNonTerm = NonTerminal("S")

        A = Single(ANonTerm)
        B = Single(BNonTerm)
        C = Single(CNonTerm)
        S = Single(SNonTerm)

        a = Single(Terminal("a"))
        c = Single(Terminal("c"))
        d = Single(Terminal("d"))
        eps = Single(Empty())

        ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        SNonTerm,
                        [
                            Multiple([A, B, C, d]),
                        ],
                    ),
                    Rule(
                        ANonTerm,
                        [
                            Multiple([a]),
                            Multiple([eps]),
                        ],
                    ),
                    Rule(BNonTerm, [Multiple([A, C])]),
                    Rule(
                        CNonTerm,
                        [
                            Multiple([c]),
                            Multiple([eps]),
                        ],
                    ),
                ]
            ),
        )

        # S → Ad | ABd | ACd | ABCd | Bd | BCd | Cd | d
        # A → a
        # B → A | AC | C
        # C → c
        result_grammar = Grammar(
            ast=Root(
                start=Start(SNonTerm),
                ruleset=Ruleset(
                    [
                        Rule(
                            SNonTerm,
                            [
                                Multiple([A, d]),
                                Multiple([A, B, d]),
                                Multiple([A, C, d]),
                                Multiple([A, B, C, d]),
                                Multiple([B, d]),
                                Multiple([B, C, d]),
                                Multiple([C, d]),
                                Multiple([d]),
                            ],
                        ),
                        Rule(
                            ANonTerm,
                            [
                                Multiple([a]),
                            ],
                        ),
                        Rule(
                            BNonTerm,
                            [
                                Multiple([A]),
                                Multiple([A, C]),
                                Multiple([C]),
                            ],
                        ),
                        Rule(
                            CNonTerm,
                            [
                                Multiple([c]),
                            ],
                        ),
                    ]
                ),
            ),
            non_terminals=set(),
            terminals=set(),
        )
        result_grammar = result_grammar.flatten()
        result_grammar.ast.ruleset.sort()

        grammar = Grammar(ast, get_terminals(ast), get_non_terminals(ast))
        grammar = Transformer()._remove_epsilon_rules(grammar)
        grammar = grammar.flatten()
        grammar.ast.ruleset.sort()

        self.assertEqual(result_grammar.ast.ruleset, grammar.ast.ruleset)

    def test_simple_grammar_with_unique_name(self):
        # S → S'BCd | ε
        # S' → a | ε
        # B → S'C
        # C → c | ε

        S_NonTerm = NonTerminal("S'")
        S__NonTerm = NonTerminal("S''")
        BNonTerm = NonTerminal("B")
        CNonTerm = NonTerminal("C")
        SNonTerm = NonTerminal("S")

        S_ = Single(S_NonTerm)
        B = Single(BNonTerm)
        C = Single(CNonTerm)
        S = Single(SNonTerm)

        a = Single(Terminal("a"))
        c = Single(Terminal("c"))
        d = Single(Terminal("d"))
        eps = Single(Empty())

        ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        SNonTerm,
                        [
                            Multiple([S_, B, C, d]),
                            Multiple([eps]),
                        ],
                    ),
                    Rule(
                        S_NonTerm,
                        [
                            Multiple([a]),
                            Multiple([eps]),
                        ],
                    ),
                    Rule(BNonTerm, [Multiple([S_, C])]),
                    Rule(
                        CNonTerm,
                        [
                            Multiple([c]),
                            Multiple([eps]),
                        ],
                    ),
                ]
            ),
        )

        # S → S'd | S'Bd | S'Cd | S'BCd | Bd | BCd | Cd | d
        # S' → a
        # B → S' | S'C | C
        # C → c
        result_grammar = Grammar(
            ast=Root(
                start=Start(S__NonTerm),
                ruleset=Ruleset(
                    [
                        Rule(
                            S__NonTerm,
                            [
                                Multiple([S]),
                                Multiple([eps]),
                            ],
                        ),
                        Rule(
                            SNonTerm,
                            [
                                Multiple([S_, d]),
                                Multiple([S_, B, d]),
                                Multiple([S_, C, d]),
                                Multiple([S_, B, C, d]),
                                Multiple([B, d]),
                                Multiple([B, C, d]),
                                Multiple([C, d]),
                                Multiple([d]),
                            ],
                        ),
                        Rule(
                            S_NonTerm,
                            [
                                Multiple([a]),
                            ],
                        ),
                        Rule(
                            BNonTerm,
                            [
                                Multiple([S_]),
                                Multiple([S_, C]),
                                Multiple([C]),
                            ],
                        ),
                        Rule(
                            CNonTerm,
                            [
                                Multiple([c]),
                            ],
                        ),
                    ]
                ),
            ),
            non_terminals=set(),
            terminals=set(),
        )
        result_grammar = result_grammar.flatten()
        result_grammar.ast.ruleset.sort()

        grammar = Grammar(ast, get_terminals(ast), get_non_terminals(ast))
        grammar = Transformer()._remove_epsilon_rules(grammar)
        grammar = grammar.flatten()
        grammar.ast.ruleset.sort()

        self.assertEqual(result_grammar.ast.ruleset, grammar.ast.ruleset)
        self.assertEqual(result_grammar.ast.start.variable.value, S__NonTerm.value)


class Test_TransformerRemoveImmidiateLeftRecursion(unittest.TestCase):
    def test_nothing_to_remove(self):
        # A → S a | a
        # S → b | a
        ANonTerm = NonTerminal("A")
        SNonTerm = NonTerminal("S")

        A = Single(ANonTerm)
        S = Single(SNonTerm)

        a = Single(Terminal("a"))
        b = Single(Terminal("b"))

        ast = Root(
            start=Start(ANonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        ANonTerm,
                        [
                            Multiple([S, a]),
                            Multiple([a]),
                        ],
                    ),
                    Rule(
                        SNonTerm,
                        [
                            Multiple([b]),
                            Multiple([a]),
                        ],
                    ),
                ]
            ),
        )

        result_ast = Root(
            start=Start(ANonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        ANonTerm,
                        [
                            Multiple([S, a]),
                            Multiple([a]),
                        ],
                    ),
                    Rule(
                        SNonTerm,
                        [
                            Multiple([b]),
                            Multiple([a]),
                        ],
                    ),
                ]
            ),
        )

        result_grammar = Grammar(
            ast=result_ast,
            terminals=get_terminals(result_ast),
            non_terminals=get_non_terminals(result_ast),
        ).flatten()

        result_grammar.ast.ruleset.sort()

        grammar = Grammar(
            ast=ast, terminals=get_terminals(ast), non_terminals=get_non_terminals(ast)
        )

        grammar = (
            Transformer()._remove_immediate_left_recursion(grammar, ANonTerm).flatten()
        )
        grammar.ast.ruleset.sort()

        self.assertEqual(result_grammar.ast.ruleset, grammar.ast.ruleset)

    def test_simple_grammar(self):
        # A → S a ∣ A a
        # S → A b
        ANonTerm = NonTerminal("A")
        A_NonTerm = NonTerminal("A'")
        SNonTerm = NonTerminal("S")

        A = Single(ANonTerm)
        A_ = Single(A_NonTerm)
        S = Single(SNonTerm)

        a = Single(Terminal("a"))
        b = Single(Terminal("b"))
        eps = Single(Empty())

        ast = Root(
            start=Start(ANonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        ANonTerm,
                        [
                            Multiple([S, a]),
                            Multiple([A, a]),
                        ],
                    ),
                    Rule(
                        SNonTerm,
                        [
                            Multiple([A, b]),
                        ],
                    ),
                ]
            ),
        )

        # A → S a A' ∣ S a
        # A' → a A' ∣ a
        # S → A b

        result_ast = Root(
            start=Start(ANonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        ANonTerm,
                        [
                            Multiple([S, a, A_]),
                            Multiple([S, a]),
                        ],
                    ),
                    Rule(
                        A_NonTerm,
                        [
                            Multiple([a, A_]),
                            Multiple([a]),
                        ],
                    ),
                    Rule(
                        SNonTerm,
                        [
                            Multiple([A, b]),
                        ],
                    ),
                ]
            ),
        )

        result_grammar = Grammar(
            ast=result_ast,
            terminals=get_terminals(result_ast),
            non_terminals=get_non_terminals(result_ast),
        ).flatten()

        result_grammar.ast.ruleset.sort()

        grammar = Grammar(
            ast=ast, terminals=get_terminals(ast), non_terminals=get_non_terminals(ast)
        )

        grammar = (
            Transformer()._remove_immediate_left_recursion(grammar, ANonTerm).flatten()
        )
        grammar.ast.ruleset.sort()

        self.assertEqual(result_grammar.ast.ruleset, grammar.ast.ruleset)

    def test_multiple_immidiate_left_recursion(self):
        # A → S a | S b ∣ A a | A b
        # S → A b
        ANonTerm = NonTerminal("A")
        A_NonTerm = NonTerminal("A'")
        SNonTerm = NonTerminal("S")

        A = Single(ANonTerm)
        A_ = Single(A_NonTerm)
        S = Single(SNonTerm)

        a = Single(Terminal("a"))
        b = Single(Terminal("b"))
        eps = Single(Empty())

        ast = Root(
            start=Start(ANonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        ANonTerm,
                        [
                            Multiple([S, a]),
                            Multiple([S, b]),
                            Multiple([A, a]),
                            Multiple([A, b]),
                        ],
                    ),
                    Rule(
                        SNonTerm,
                        [
                            Multiple([A, b]),
                        ],
                    ),
                ]
            ),
        )

        # A → S a A' | S b A' ∣ S a | S b
        # A' → a A' | b A' ∣ a | b
        # S → A b

        result_ast = Root(
            start=Start(ANonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        ANonTerm,
                        [
                            Multiple([S, a, A_]),
                            Multiple([S, b, A_]),
                            Multiple([S, a]),
                            Multiple([S, b]),
                        ],
                    ),
                    Rule(
                        A_NonTerm,
                        [
                            Multiple([a, A_]),
                            Multiple([b, A_]),
                            Multiple([a]),
                            Multiple([b]),
                        ],
                    ),
                    Rule(
                        SNonTerm,
                        [
                            Multiple([A, b]),
                        ],
                    ),
                ]
            ),
        )

        result_grammar = Grammar(
            ast=result_ast,
            terminals=get_terminals(result_ast),
            non_terminals=get_non_terminals(result_ast),
        ).flatten()

        result_grammar.ast.ruleset.sort()

        grammar = Grammar(
            ast=ast, terminals=get_terminals(ast), non_terminals=get_non_terminals(ast)
        )

        grammar = (
            Transformer()._remove_immediate_left_recursion(grammar, ANonTerm).flatten()
        )
        grammar.ast.ruleset.sort()

        self.assertEqual(result_grammar.ast.ruleset, grammar.ast.ruleset)


class Test_TransformerRemoveLeftRecursion(unittest.TestCase):
    def test_simple_grammar(self):
        # A → S a
        # S → S b ∣ A c ∣ b

        ANonTerm = NonTerminal("A")
        SNonTerm = NonTerminal("S")
        S_NonTerm = NonTerminal("S'")

        A = Single(ANonTerm)
        S = Single(SNonTerm)
        S_ = Single(S_NonTerm)

        a = Single(Terminal("a"))
        b = Single(Terminal("b"))
        c = Single(Terminal("c"))

        ast = Root(
            start=Start(ANonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        ANonTerm,
                        [
                            Multiple([S, a]),
                        ],
                    ),
                    Rule(
                        SNonTerm,
                        [
                            Multiple([S, b]),
                            Multiple([A, c]),
                            Multiple([b]),
                        ],
                    ),
                ]
            ),
        )

        # A → S a
        # S  → b S' ∣ b
        # S' → b S' ∣ a c S' ∣ b ∣ a c
        result_ast = Root(
            start=Start(ANonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        ANonTerm,
                        [
                            Multiple([S, a]),
                        ],
                    ),
                    Rule(
                        SNonTerm,
                        [
                            Multiple([b, S_]),
                            Multiple([b]),
                        ],
                    ),
                    Rule(
                        S_NonTerm,
                        [
                            Multiple([b, S_]),
                            Multiple([a, c, S_]),
                            Multiple([b]),
                            Multiple([a, c]),
                        ],
                    ),
                ]
            ),
        )

        result_grammar = Grammar(
            ast=result_ast,
            terminals=get_terminals(result_ast),
            non_terminals=get_non_terminals(result_ast),
        ).flatten()

        result_grammar.ast.ruleset.sort()

        grammar = Grammar(
            ast=ast, terminals=get_terminals(ast), non_terminals=get_non_terminals(ast)
        )

        grammar = Transformer()._remove_left_recursion(grammar).flatten()
        grammar.ast.ruleset.sort()

        self.assertEqual(result_grammar.ast.ruleset, grammar.ast.ruleset)

    def test_nothing_to_remove(self):
        # A → a | b | c
        # S → a b

        ANonTerm = NonTerminal("A")
        SNonTerm = NonTerminal("S")
        # S_NonTerm = NonTerminal("S'")

        # S = Single(SNonTerm)

        a = Single(Terminal("a"))
        b = Single(Terminal("b"))
        c = Single(Terminal("c"))

        ast = Root(
            start=Start(ANonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        ANonTerm,
                        [
                            Multiple([a]),
                            Multiple([b]),
                            Multiple([c]),
                        ],
                    ),
                    Rule(
                        SNonTerm,
                        [
                            Multiple([a, b]),
                        ],
                    ),
                ]
            ),
        )

        # A → a | b | c
        # S → a b
        result_ast = copy.deepcopy(ast)

        result_grammar = Grammar(
            ast=result_ast,
            terminals=get_terminals(result_ast),
            non_terminals=get_non_terminals(result_ast),
        ).flatten()
        result_grammar.ast.ruleset.sort()

        grammar = Grammar(
            ast=ast, terminals=get_terminals(ast), non_terminals=get_non_terminals(ast)
        )

        grammar = Transformer()._remove_left_recursion(grammar).flatten()
        grammar.ast.ruleset.sort()

        self.assertEqual(result_grammar.ast.ruleset, grammar.ast.ruleset)


class Test_TransformerReplaceStartNonTerminal(unittest.TestCase):
    def test_simple_grammar(self):
        # S → BB
        # B → b | SB

        SNonTerm = NonTerminal("S")
        S_NonTerm = NonTerminal("S'")
        BNonTerm = NonTerminal("B")

        S = Single(SNonTerm)
        B = Single(BNonTerm)

        b = Single(Terminal("b"))

        ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [
                    Rule(SNonTerm, [Multiple([B, B])]),
                    Rule(BNonTerm, [Multiple([b]), Multiple([S, B])]),
                ]
            ),
        )

        # S' → S
        # S  → BB
        # B  → b | SB

        result_ast = Root(
            start=Start(S_NonTerm),
            ruleset=Ruleset(
                [
                    Rule(S_NonTerm, [Multiple([S])]),
                    Rule(SNonTerm, [Multiple([B, B])]),
                    Rule(BNonTerm, [Multiple([b]), Multiple([S, B])]),
                ]
            ),
        )

        grammar = (
            Transformer()
            ._remove_start_non_terminal_from_right_part(
                Grammar(
                    ast=ast,
                    terminals=get_terminals(ast),
                    non_terminals=get_non_terminals(ast),
                )
            )
            .flatten()
        )
        result_grammar = Grammar(
            ast=result_ast,
            terminals=get_terminals(result_ast),
            non_terminals=get_non_terminals(result_ast),
        ).flatten()

        grammar.ast.ruleset.sort()
        result_grammar.ast.ruleset.sort()

        self.assertEqual(result_grammar.ast.ruleset, grammar.ast.ruleset)

    def test_nothing_to_change(self):
        # S → BB
        # B → b

        SNonTerm = NonTerminal("S")
        BNonTerm = NonTerminal("B")

        B = Single(BNonTerm)

        b = Single(Terminal("b"))

        ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [Rule(SNonTerm, [Multiple([B, B])]), Rule(BNonTerm, [Multiple([b])])]
            ),
        )

        # S → BB
        # B → b
        result_ast = copy.deepcopy(ast)

        grammar = (
            Transformer()
            ._remove_start_non_terminal_from_right_part(
                Grammar(
                    ast=ast,
                    terminals=get_terminals(ast),
                    non_terminals=get_non_terminals(ast),
                )
            )
            .flatten()
        )
        result_grammar = Grammar(
            ast=result_ast,
            terminals=get_terminals(result_ast),
            non_terminals=get_non_terminals(result_ast),
        ).flatten()

        grammar.ast.ruleset.sort()
        result_grammar.ast.ruleset.sort()

        self.assertEqual(result_grammar.ast.ruleset, grammar.ast.ruleset)


class Test_TransformerRemoveIsolatedRules(unittest.TestCase):
    def test_several_isolated_rules(self):
        # S → A | B
        # B → b | aB
        # A → a
        # X → x
        # Y → y

        SNonTerm = NonTerminal("S")
        ANonTerm = NonTerminal("A")
        BNonTerm = NonTerminal("B")
        XNonTerm = NonTerminal("X")
        YNonTerm = NonTerminal("Y")

        A = Single(ANonTerm)
        B = Single(BNonTerm)

        a = Single(Terminal("a"))
        b = Single(Terminal("b"))
        x = Single(Terminal("x"))
        y = Single(Terminal("y"))

        ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        SNonTerm,
                        [
                            Multiple([A]),
                            Multiple([B]),
                        ],
                    ),
                    Rule(
                        BNonTerm,
                        [
                            Multiple([b]),
                            Multiple([a, B]),
                        ],
                    ),
                    Rule(
                        ANonTerm,
                        [
                            Multiple([a]),
                        ],
                    ),
                    Rule(
                        XNonTerm,
                        [
                            Multiple([x]),
                        ],
                    ),
                    Rule(
                        YNonTerm,
                        [
                            Multiple([y]),
                        ],
                    ),
                ]
            ),
        )

        expected_ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        SNonTerm,
                        [
                            Multiple([A]),
                            Multiple([B]),
                        ],
                    ),
                    Rule(
                        BNonTerm,
                        [
                            Multiple([b]),
                            Multiple([a, B]),
                        ],
                    ),
                    Rule(
                        ANonTerm,
                        [
                            Multiple([a]),
                        ],
                    ),
                ]
            ),
        )

        expected_grammar = Grammar(
            ast=expected_ast,
            non_terminals=get_non_terminals(expected_ast),
            terminals=get_terminals(expected_ast),
        )
        expected_grammar.ast.ruleset.sort()

        result_grammar = Transformer()._remove_isolated_rules(
            Grammar(
                ast=ast,
                non_terminals=get_non_terminals(ast),
                terminals=get_terminals(ast),
            )
        )
        result_grammar.ast.ruleset.sort()

        self.assertEqual(expected_grammar, result_grammar)


class Test_TransformerApplyGreibahForm(unittest.TestCase):
    def test_to_greibah_form(self):
        # S → XA | BB
        # B → b | SB
        # X → b
        # A → a

        SNonTerm = NonTerminal("S")
        XNonTerm = NonTerminal("X")
        BNonTerm = NonTerminal("B")
        ANonTerm = NonTerminal("A")
        S_NonTerm = NonTerminal("S'")

        S = Single(SNonTerm)
        S_ = Single(S_NonTerm)
        X = Single(XNonTerm)
        B = Single(BNonTerm)
        A = Single(ANonTerm)

        a = Single(Terminal("a"))
        b = Single(Terminal("b"))

        ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [
                    Rule(SNonTerm, [Multiple([X, A]), Multiple([B, B])]),
                    Rule(BNonTerm, [Multiple([b]), Multiple([S, B])]),
                    Rule(XNonTerm, [Multiple([b])]),
                    Rule(ANonTerm, [Multiple([a])]),
                ]
            ),
        )

        # S → bA | bABB | bB | bABS'B | bS'B
        # B → bAB | b | bABS' | bS'
        # S' → bABB | bB | bABS'B | bS'B | bABBS' | bBS' | bABS'BS' | bS'BS'
        # X → b
        # A → a

        tr = Transformer()

        grammar = tr.to_greibah_weak_form(
            Grammar(
                ast=ast,
                terminals=get_terminals(ast),
                non_terminals=get_non_terminals(ast),
            )
        )

        self.assertEqual(tr._is_greibah_weak_form(grammar), True)

    def test_convert_simple_grammar_to_greibah_form(self):
        # S → ASBS | ε
        # A → (
        # B → )

        SNonTerm = NonTerminal("S")
        ANonTerm = NonTerminal("A")
        BNonTerm = NonTerminal("B")

        S = Single(SNonTerm)
        A = Single(ANonTerm)
        B = Single(BNonTerm)

        lb = Single(Terminal("("))
        rb = Single(Terminal(")"))
        eps = Single(Empty())

        ast = Root(
            start=Start(SNonTerm),
            ruleset=Ruleset(
                [
                    Rule(
                        SNonTerm,
                        [
                            Multiple([A, S, B, S]),
                            Multiple([eps]),
                        ],
                    ),
                    Rule(
                        ANonTerm,
                        [
                            Multiple([lb]),
                        ],
                    ),
                    Rule(
                        BNonTerm,
                        [
                            Multiple([rb]),
                        ],
                    ),
                ]
            ),
        )

        tr = Transformer()

        grammar = tr.to_greibah_weak_form(
            Grammar(
                ast=ast,
                terminals=get_terminals(ast),
                non_terminals=get_non_terminals(ast),
            )
        )

        self.assertEqual(tr._is_greibah_weak_form(grammar), True)


if __name__ == "__main__":
    unittest.main()
