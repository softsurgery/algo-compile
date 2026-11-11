"""
Unit tests for the modular compiler components:
- compiler.utils
- compiler.types
- compiler.parser
- compiler.expressions
- compiler.statements
- compiler.subprograms
"""

import unittest
from compiler.utils import normalize_accents, split_arguments
from compiler.types import TypeHandler
from compiler.parser import SectionExtractor
from compiler.expressions import ExpressionTranslator
from compiler.statements import StatementTranslator
from compiler.subprograms import SubprogramTranslator


class TestModularCompiler(unittest.TestCase):
    def test_utils(self):
        text = "Répéter Jusqu'à Élève"
        self.assertEqual(normalize_accents(text), text)

        args = split_arguments('a, b, [1, 2, 3], "hello, world", f(x, y)')
        self.assertEqual(args, ['a', 'b', '[1, 2, 3]', '"hello, world"', 'f(x, y)'])

    def test_type_handler(self):
        th = TypeHandler()
        tdnt_lines = [
            (1, "Player = Enregistrement"),
            (2, "    nom: Chaine"),
            (3, "    score: Entier"),
            (4, "Fin Enregistrement"),
            (5, "Tab = Tableau de 20 Player")
        ]
        th.parse_type_declarations(tdnt_lines)
        self.assertIn("Player", th.custom_types)
        self.assertEqual(th.custom_types["Player"]["kind"], "enregistrement")
        self.assertIn("Tab", th.custom_types)
        self.assertEqual(th.custom_types["Tab"]["kind"], "tableau_1d")

        tdo_lines = [
            (1, "p : Player"),
            (2, "T : Tab"),
            (3, "n : Entier")
        ]
        th.parse_object_declarations(tdo_lines)
        self.assertEqual(th.declared_objects["p"], "Player")
        self.assertEqual(th.declared_objects["T"], "Tab")
        self.assertEqual(th.declared_objects["n"], "Entier")

        inits = th.generate_object_initializations()
        self.assertIn("p = _creer_Player()", inits)
        self.assertIn("T = array([_creer_Player() for _ in range(20)], dtype=object)", inits)
        self.assertIn("n = 0", inits)

        record_funcs = th.generate_record_constructors()
        self.assertTrue(any("def _creer_Player" in l for l in record_funcs))

    def test_section_extractor(self):
        extractor = SectionExtractor()
        lines = [
            "ALGORITHME TestProg",
            "Fonction carre(x: Entier): Entier",
            "Debut",
            "  retourner x * x",
            "Fin",
            "DEBUT",
            "  y <- carre(5)",
            "FIN"
        ]
        sections = extractor.extract_sections(lines)
        self.assertEqual(extractor.program_name, "TestProg")
        self.assertEqual(len(sections["subprograms"]), 1)
        self.assertEqual(sections["subprograms"][0]["kind"], "fonction")
        self.assertTrue(len(sections["main"]) > 0)

        meta = {}
        extractor.register_subprogram_signature(sections["subprograms"][0], meta)
        self.assertIn("carre", meta)
        self.assertEqual(meta["carre"]["kind"], "fonction")
        self.assertEqual(meta["carre"]["all_params"], ["x"])

    def test_expression_translator(self):
        expr = ExpressionTranslator()
        # Operators
        self.assertEqual(expr.translate_expression("a Div b Mod c"), "a // b % c")
        self.assertEqual(expr.translate_expression("x Et y Ou Non z"), "x and y or not z")
        self.assertEqual(expr.translate_expression("a ≠ b Et c ≤ d Et e ≥ f"), "a != b and c <= d and e >= f")
        self.assertEqual(expr.translate_expression("a = b"), "a == b")

        # Intervals
        self.assertEqual(expr.translate_expression("x dans [2 .. 30]"), "(2 <= x <= 30)")
        self.assertEqual(expr.translate_expression("ch dans {'A', 'B'}"), "(ch in {'A', 'B'})")

        # Builtins
        self.assertEqual(expr.translate_expression("RacineCarré(16) + Arrondi(3.2)"), "RacineCarré(16) + Arrondi(3.2)")

        # Target translation
        self.assertEqual(expr.translate_target("T[i].nom"), "T[i]['nom']")
        self.assertEqual(expr.translate_target("M[i, j]"), "M[i, j]")
        self.assertEqual(expr.translate_target("obj.champ"), "obj['champ']")

    def test_subprogram_and_statement_translator(self):
        th = TypeHandler()
        expr = ExpressionTranslator()
        meta = {}
        stmt = StatementTranslator(expr, th, meta)
        subp = SubprogramTranslator(stmt)

        subprog_dict = {
            'kind': 'procedure',
            'header': 'Procedure swap(@a: Entier, @b: Entier)',
            'lines': [
                (1, 'Procedure swap(@a: Entier, @b: Entier)'),
                (2, 'Debut'),
                (3, '  temp <- a'),
                (4, '  a <- b'),
                (5, '  b <- temp'),
                (6, 'Fin')
            ]
        }
        meta['swap'] = {'kind': 'procedure', 'ref_params': ['a', 'b'], 'all_params': ['a', 'b']}
        py_lines = subp.translate_subprogram(subprog_dict)
        joined = "\n".join(py_lines)

        self.assertIn("def swap(a, b):", joined)
        self.assertIn("temp = a", joined)
        self.assertIn("a = b", joined)
        self.assertIn("b = temp", joined)
        self.assertIn("return a, b", joined)

        # Call-site translation for swap(x, y)
        call_code = stmt.translate_single_statement("swap(x, y)")
        self.assertEqual(call_code, "x, y = swap(x, y)")

    def test_string_array_and_input(self):
        import io, sys
        from compiler.runtime import _lire_valeur

        th = TypeHandler()
        tdo = [
            (1, "IDENT : Tableau de 50 Chaine"),
            (2, "M : Tableau de 3 lignes * 3 colonnes Chaine")
        ]
        th.parse_object_declarations(tdo)
        inits = th.generate_object_initializations()
        self.assertIn("IDENT = array([''] * (50), dtype=object)", inits)
        self.assertIn("M = array([[''] * (3)] * (3), dtype=object)", inits)

        # Test _lire_valeur does not truncate chaine de caractere
        orig_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO("12345678\n")
            val = _lire_valeur("", "Chaine de caractere")
            self.assertEqual(val, "12345678")
        finally:
            sys.stdin = orig_stdin


if __name__ == '__main__':
    unittest.main()
