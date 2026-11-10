"""
Unit tests for the isolated compiler validator and algo errors module.
Verifies that:
- END is mandatory (algorithm, subprogram, and block structures).
- Types are mandatory (variables, parameters, return types, TDO entries).
- Every subprogram must have a Tableau de déclaration des objets locaux (TDOL) after it.
- The main algorithm must have a Tableau de déclaration des objets globaux (TDOG) under it.
"""

import unittest
from compiler.validator import AlgoValidator
from compiler.errors import (
    CompileError,
    MissingEndError,
    MissingTypeError,
    InvalidStructureError,
)
from compiler.transpiler import AlgoTranspiler


class TestAlgoValidator(unittest.TestCase):
    def setUp(self):
        self.transpiler = AlgoTranspiler(strict_types=True)
        self.validator = AlgoValidator(strict_types=True)

    # -------------------------------------------------------------------------
    # Mandatory END Tests
    # -------------------------------------------------------------------------
    def test_missing_fin_main_algorithm(self):
        code = """
        ALGORITHME SansFin
        DEBUT
          x <- 1
        Tableau de déclaration des objets globaux
        x : Entier
        """
        with self.assertRaises(MissingEndError) as cm:
            self.transpiler.compile(code)
        self.assertIn("FIN", str(cm.exception))

    def test_missing_fin_and_debut_main_algorithm(self):
        code = """
        ALGORITHME SansDebutNiFin
        x <- 1
        Tableau de déclaration des objets globaux
        x : Entier
        """
        with self.assertRaises(MissingEndError) as cm:
            self.transpiler.compile(code)
        self.assertIn("FIN", str(cm.exception))

    def test_missing_fin_subprogram(self):
        code = """
        Fonction Carre(x: Entier) : Entier
        DEBUT
          Retourner x * x

        Tableau de déclaration des objets locaux
        /

        ALGORITHME Principal
        DEBUT
          y <- Carre(5)
        FIN
        Tableau de déclaration des objets globaux
        y : Entier
        """
        with self.assertRaises(MissingEndError) as cm:
            self.transpiler.compile(code)
        self.assertIn("FIN", str(cm.exception))
        self.assertIn("Carre", str(cm.exception))

    def test_english_end_accepted(self):
        code = """
        ALGORITHME EnglishEnd
        DEBUT
          x <- 42
        END
        Tableau de déclaration des objets globaux
        x : Entier
        """
        py = self.transpiler.compile(code)
        self.assertIn("x = 42", py)

    def test_unclosed_si_block(self):
        code = """
        ALGORITHME TestSi
        DEBUT
          Si x > 0 Alors
            x <- x - 1
        FIN
        Tableau de déclaration des objets globaux
        x : Entier
        """
        with self.assertRaises(MissingEndError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Fin Si", str(cm.exception))

    def test_unclosed_pour_block(self):
        code = """
        ALGORITHME TestPour
        DEBUT
          Pour i de 1 à 10 Faire
            s <- s + i
        FIN
        Tableau de déclaration des objets globaux
        s, i : Entier
        """
        with self.assertRaises(MissingEndError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Fin Pour", str(cm.exception))

    def test_unclosed_tant_que_block(self):
        code = """
        ALGORITHME TestTantQue
        DEBUT
          Tant que x < 10 Faire
            x <- x + 1
        FIN
        Tableau de déclaration des objets globaux
        x : Entier
        """
        with self.assertRaises(MissingEndError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Fin Tant que", str(cm.exception))

    def test_unclosed_repeter_block(self):
        code = """
        ALGORITHME TestRepeter
        DEBUT
          Répéter
            x <- x + 1
        FIN
        Tableau de déclaration des objets globaux
        x : Entier
        """
        with self.assertRaises(MissingEndError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Jusqu'à", str(cm.exception))

    def test_unclosed_selon_block(self):
        code = """
        ALGORITHME TestSelon
        DEBUT
          Selon x
            1 : x <- 2
        FIN
        Tableau de déclaration des objets globaux
        x : Entier
        """
        with self.assertRaises(MissingEndError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Fin Selon", str(cm.exception))

    # -------------------------------------------------------------------------
    # Mandatory Tables Presence Tests (TDOL & TDOG)
    # -------------------------------------------------------------------------
    def test_subprogram_missing_tdol_rejected(self):
        code = """
        Procedure Saluer(nom: Chaine)
        DEBUT
          ecrire("Bonjour ", nom)
        FIN

        ALGORITHME MonProg
        DEBUT
          Saluer("Ali")
        FIN
        Tableau de déclaration des objets globaux
        /
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("TDOL", str(cm.exception))
        self.assertIn("Saluer", str(cm.exception))

    def test_main_missing_tdog_rejected(self):
        code = """
        ALGORITHME SansTDOG
        DEBUT
          x <- 10
        FIN
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("TDOG", str(cm.exception))

    def test_tdog_must_be_under_main(self):
        code = """
        Tableau de déclaration des objets globaux
        x : Entier

        ALGORITHME TDOGEnHaut
        DEBUT
          x <- 10
        FIN
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("TDOG", str(cm.exception))
        self.assertIn("placé sous l'algorithme", str(cm.exception))

    # -------------------------------------------------------------------------
    # Mandatory Types Tests
    # -------------------------------------------------------------------------
    def test_undeclared_variable_in_main(self):
        code = """
        ALGORITHME UndeclaredMain
        DEBUT
          valeur_inconnue <- 123
        FIN
        Tableau de déclaration des objets globaux
        /
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("valeur_inconnue", str(cm.exception))
        self.assertIn("non déclaré", str(cm.exception))

    def test_undeclared_variable_with_partial_tdo(self):
        code = """
        ALGORITHME PartialTDO
        DEBUT
          a <- 1
          b <- 2
        FIN
        Tableau de déclaration des objets globaux
        a : Entier
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("b", str(cm.exception))
        self.assertIn("non déclaré", str(cm.exception))

    def test_undeclared_variable_in_subprogram(self):
        code = """
        Procedure Test(a: Entier)
        DEBUT
          inconnu <- a * 2
        FIN
        Tableau de déclaration des objets locaux
        /
        ALGORITHME MonAlgo
        DEBUT
          Test(10)
        FIN
        Tableau de déclaration des objets globaux
        /
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("inconnu", str(cm.exception))
        self.assertIn("Test", str(cm.exception))

    def test_subprogram_parameter_missing_type(self):
        code = """
        Procedure Test(a, b: Entier)
        DEBUT
          ecrire(a, b)
        FIN
        Tableau de déclaration des objets locaux
        /
        ALGORITHME MonAlgo
        DEBUT
          Test(1, 2)
        FIN
        Tableau de déclaration des objets globaux
        /
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("paramètre 'a'", str(cm.exception))

    def test_function_missing_return_type(self):
        code = """
        Fonction Somme(x: Entier, y: Entier)
        DEBUT
          Retourner x + y
        FIN
        Tableau de déclaration des objets locaux
        /
        ALGORITHME MonAlgo
        DEBUT
          res <- Somme(2, 3)
        FIN
        Tableau de déclaration des objets globaux
        res : Entier
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Type de retour obligatoire", str(cm.exception))

    def test_tdo_item_missing_type_colon(self):
        code = """
        ALGORITHME BadTDO
        DEBUT
          x <- 10
        FIN
        Tableau de déclaration des objets globaux
        x :
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Type manquant pour l'objet 'x'", str(cm.exception))

    def test_tdo_item_missing_type_no_colon(self):
        code = """
        ALGORITHME BadTDO
        DEBUT
          x <- 10
        FIN
        Tableau de déclaration des objets globaux
        Objet Type
        x
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(code)
        self.assertIn("Type manquant", str(cm.exception))

    def test_record_fields_do_not_require_separate_variable_declarations(self):
        code = """
        ALGORITHME TestRec
        DEBUT
          E.nom <- "Alice"
          E.age <- 20
        FIN
        Déclaration des types
        Personne = Enregistrement
          nom : Chaine
          age : Entier
        Fin Enregistrement
        Tableau de déclaration des objets globaux
        E : Personne
        """
        py = self.transpiler.compile(code)
        self.assertIn('E[\'nom\'] = "Alice"', py)
        self.assertIn("E['age'] = 20", py)

    def test_local_tdol_subprogram_passes(self):
        code = """
        Procedure Calc(n: Entier)
        DEBUT
          Pour i de 1 à n Faire
            temp <- i * 2
          Fin Pour
        FIN
        Tableau de déclaration des objets locaux
        Objet Type
        i, temp : Entier

        ALGORITHME TestTDOL
        DEBUT
          Calc(5)
        FIN
        Tableau de déclaration des objets globaux
        /
        """
        py = self.transpiler.compile(code)
        self.assertIn("def Calc(n):", py)


if __name__ == '__main__':
    unittest.main()
