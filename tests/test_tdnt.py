"""
Unit tests for Tableau de Déclaration des Nouveaux Types (TDNT),
typedef / alias substitutions (e.g. Tab = Tableau de 100 Entier),
and prohibition of direct 'Enregistrement' as a type.
"""

import unittest
from compiler.transpiler import AlgoTranspiler
from compiler.errors import MissingTypeError, InvalidStructureError, MissingEndError


class TestTDNT(unittest.TestCase):
    def setUp(self):
        self.transpiler = AlgoTranspiler(strict_types=True)

    def test_direct_enregistrement_as_type_rejected_in_tdog(self):
        code = """
        ALGORITHME TestDirectEnreg
        DEBUT
          e.x <- 10
        FIN
        Tableau de déclaration des objets globaux
        e : Enregistrement
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Enregistrement", str(cm.exception))
        self.assertIn("ne peut pas être utilisé directement", str(cm.exception))

    def test_direct_enregistrement_as_type_rejected_in_tdol(self):
        code = """
        ALGORITHME TestDirectTDOL
        DEBUT
          Calcul()
        FIN
        Tableau de déclaration des objets globaux
        Calcul : Procédure
        
        Procédure Calcul()
        DEBUT
          e.val <- 5
        FIN
        Tableau de déclaration des objets locaux
        e : Enregistrement
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Enregistrement", str(cm.exception))
        self.assertIn("ne peut pas être utilisé directement", str(cm.exception))

    def test_direct_enregistrement_rejected_in_parameter(self):
        code = """
        ALGORITHME TestParamEnreg
        DEBUT
          Traiter(e)
        FIN
        Tableau de déclaration des objets globaux
        Traiter : Procédure
        e : Etud
        
        Tableau de déclaration des nouveaux types
        Etud = Enregistrement
          note : Entier
        Fin Enregistrement
        
        Procédure Traiter(item : Enregistrement)
        DEBUT
          Ecrire(item.note)
        FIN
        Tableau de déclaration des objets locaux
        item : Etud
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Enregistrement", str(cm.exception))
        self.assertIn("paramètre", str(cm.exception))

    def test_direct_enregistrement_rejected_in_return_type(self):
        code = """
        ALGORITHME TestReturnEnreg
        DEBUT
          e <- Fabriquer()
        FIN
        Tableau de déclaration des objets globaux
        Fabriquer : Fonction
        e : Etud
        
        Tableau de déclaration des nouveaux types
        Etud = Enregistrement
          note : Entier
        Fin Enregistrement
        
        Fonction Fabriquer() : Enregistrement
        DEBUT
          Retourner e
        FIN
        Tableau de déclaration des objets locaux
        e : Etud
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Enregistrement", str(cm.exception))
        self.assertIn("type de retour", str(cm.exception))

    def test_multiple_tdnt_rejected(self):
        code = """
        ALGORITHME TestMultipleTDNT
        Tableau de déclaration des nouveaux types
        Tab1 = Tableau de 10 Entier
        
        TDNT
        Tab2 = Tableau de 20 Entier
        
        DEBUT
          t[0] <- 1
        FIN
        Tableau de déclaration des objets globaux
        t : Tab1
        """
        with self.assertRaises(InvalidStructureError) as cm:
            self.transpiler.compile(code)
        self.assertIn("un seul Tableau de déclaration des nouveaux types", str(cm.exception))

    def test_single_tdnt_with_enregistrement_compiles_successfully(self):
        code = """
        ALGORITHME TestRecordTDNT
        Tableau de déclaration des nouveaux types
        Etudiant = Enregistrement
          nom : Chaine
          age : Entier
          moyenne : Reel
        Fin Enregistrement

        DEBUT
          e.nom <- "Sami"
          e.age <- 18
          e.moyenne <- 15.5
          Ecrire_nl(e.nom, e.age, e.moyenne)
        FIN
        Tableau de déclaration des objets globaux
        e : Etudiant
        """
        py = self.transpiler.compile(code)
        self.assertIn("def _creer_Etudiant(", py)
        self.assertIn("e = _creer_Etudiant()", py)
        self.assertIn("e['nom'] = \"Sami\"", py)
        self.assertIn("e['age'] = 18", py)
        self.assertIn("e['moyenne'] = 15.5", py)

    def test_tdnt_typedef_array_substitution(self):
        # Substitution like in C: Tab for Tableau de 100 Entier
        code = """
        ALGORITHME TestTypedefArray
        Tableau de déclaration des nouveaux types
        Tab = Tableau de 100 Entier

        DEBUT
          T[0] <- 99
          Ecrire_nl(T[0])
        FIN
        Tableau de déclaration des objets globaux
        T : Tab
        """
        py = self.transpiler.compile(code)
        # Should initialize T as an array of 100 integers
        self.assertIn("T = array([0] * (100))", py)
        self.assertIn("T[0] = 99", py)

    def test_tdnt_typedef_2d_array_substitution(self):
        code = """
        ALGORITHME TestTypedef2D
        Tableau de déclaration des nouveaux types
        Mat = Tableau de 10 lignes * 20 colonnes Reel

        DEBUT
          M[0, 0] <- 3.14
        FIN
        Tableau de déclaration des objets globaux
        M : Mat
        """
        py = self.transpiler.compile(code)
        self.assertIn("M = array([", py)
        self.assertIn("* (20)] * (10))", py)

    def test_tdnt_typedef_in_subprogram_tdol(self):
        code = """
        ALGORITHME TestLocalTypedef
        Tableau de déclaration des nouveaux types
        Tab = Tableau de 50 Entier
        
        DEBUT
          Traiter()
        FIN
        Tableau de déclaration des objets globaux
        Traiter : Procédure

        Procédure Traiter()
        DEBUT
          local_tab[0] <- 10
        FIN
        Tableau de déclaration des objets locaux
        local_tab : Tab
        """
        py = self.transpiler.compile(code)
        self.assertIn("def Traiter():", py)
        self.assertIn("local_tab = array([0] * (50))", py)

    def test_tdnt_array_of_records(self):
        code = """
        ALGORITHME TestArrayOfRecords
        Tableau de déclaration des nouveaux types
        Article = Enregistrement
          code : Entier
          prix : Reel
        Fin
        Stock = Tableau de 20 Article

        DEBUT
          catalogue[0].code <- 1001
          catalogue[0].prix <- 49.9
        FIN
        Tableau de déclaration des objets globaux
        catalogue : Stock
        """
        py = self.transpiler.compile(code)
        self.assertIn("def _creer_Article(", py)
        self.assertIn("catalogue = array([_creer_Article() for _ in range(20)], dtype=object)", py)

    def test_tdnt_type_alias(self):
        code = """
        ALGORITHME TestAlias
        Tableau de déclaration des nouveaux types
        MonEntier = Entier

        DEBUT
          x <- 42
        FIN
        Tableau de déclaration des objets globaux
        x : MonEntier
        """
        py = self.transpiler.compile(code)
        self.assertIn("x = 0", py)
        self.assertIn("x = 42", py)

    def test_symbols_bar_has_tdnt_button(self):
        from PyQt5.QtWidgets import QApplication, QPushButton
        from ui.symbols_bar import SymbolsBar
        app = QApplication.instance() or QApplication([])
        sb = SymbolsBar()
        buttons = sb.findChildren(QPushButton)
        btn_texts = [b.text() for b in buttons]
        self.assertIn("TDNT", btn_texts)
        self.assertIn("TDOG", btn_texts)
        self.assertIn("TDOL", btn_texts)

        # Test clicking TDNT button
        received = []
        sb.insert_requested.connect(lambda text: received.append(text))
        tdnt_btn = next(b for b in buttons if b.text() == "TDNT")
        tdnt_btn.click()
        self.assertTrue(len(received) > 0)
        self.assertIn("Tableau de déclaration des nouveaux types", received[0])
        self.assertIn("Enregistrement", received[0])
        self.assertIn("Tableau de 100 Entier", received[0])

    def test_symbols_bar_symbols_and_separate_groups(self):
        from PyQt5.QtWidgets import QApplication, QPushButton
        from ui.symbols_bar import SymbolsBar
        app = QApplication.instance() or QApplication([])
        sb = SymbolsBar()
        buttons = sb.findChildren(QPushButton)
        btn_dict = {b.text(): b for b in buttons}

        # Check all required symbol shortcuts exist
        for sym_name in ["LT", "LTE", "GT", "GTE", "NEQ", "MOD", "DIV", "IN", "ASSIGN"]:
            self.assertIn(sym_name, btn_dict)

        # Check all required structure shortcuts exist
        for struct_name in ["SI", "POUR", "TANTQUE", "REPETER", "SELON"]:
            self.assertIn(struct_name, btn_dict)

        # Check all shortcut buttons have bold text
        for b in buttons:
            self.assertIn("font-weight: bold", b.styleSheet())

        # Check emission for each symbol
        expected_inserts = {
            "LT": "<",
            "LTE": "≤",
            "GT": ">",
            "GTE": "≥",
            "NEQ": "≠",
            "MOD": " Mod ",
            "DIV": " Div ",
            "IN": " ∈ ",
            "ASSIGN": "←",
        }
        for sym_name, expected_text in expected_inserts.items():
            received = []
            sb.insert_requested.connect(lambda t: received.append(t))
            btn_dict[sym_name].click()
            self.assertEqual(received[-1], expected_text)

        # Check separate group label and separator exist
        self.assertEqual(sb.lbl_tables.text(), "Tableaux :")
        self.assertIsNotNone(sb.sep2)

        # Check theme styling on the new group elements
        sb.set_dark_mode(True)
        self.assertIn("#a6adc8", sb.lbl_tables.styleSheet())
        self.assertIn("#45475a", sb.sep2.styleSheet())
        sb.set_dark_mode(False)
        self.assertIn("#64748b", sb.lbl_tables.styleSheet())
        self.assertIn("#cbd5e1", sb.sep2.styleSheet())

    def test_all_examples_compile_cleanly(self):
        import os
        examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")
        for fname in os.listdir(examples_dir):
            if fname.endswith(".algo"):
                with open(os.path.join(examples_dir, fname), "r", encoding="utf-8") as f:
                    code = f.read()
                # Should compile cleanly without errors
                py = self.transpiler.compile(code)
                self.assertTrue(len(py) > 0, f"Example {fname} failed to generate code")


if __name__ == '__main__':
    unittest.main()
