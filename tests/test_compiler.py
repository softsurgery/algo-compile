import unittest
from compiler.transpiler import AlgoTranspiler
from compiler.errors import (
    CompileError,
    MissingEndError,
    MissingTypeError,
)

class TestAlgoTranspiler(unittest.TestCase):
    def setUp(self):
        self.transpiler = AlgoTranspiler()

    def test_simple_sum(self):
        algo = """
        ALGORITHME Somme
        DEBUT
          s <- 0
          Pour i de 1 à 10 Faire
            s <- s + i
          Fin Pour
          Ecrire_nl("Somme = ", s)
        FIN
        Déclaration des objets
        Objet  Type / Nature
        s, i   Entier
        """
        py = self.transpiler.compile(algo)
        ns = {'__name__': '__main__'}
        exec(py, ns)

    def test_repeat_until(self):
        algo = """
        ALGORITHME TestRepeter
        DEBUT
          x <- 1
          Répéter
            x <- x * 2
          Jusqu'à x >= 16
        FIN
        Déclaration des objets
        Objet  Type / Nature
        x      Entier
        """
        py = self.transpiler.compile(algo)
        ns = {'__name__': '__main__'}
        exec(py, ns)

    def test_selon_choices(self):
        algo = """
        ALGORITHME TestSelon
        DEBUT
          mois <- 2
          Selon mois
            1, 3, 5, 7, 8, 10, 12 : j <- 31
            4, 6, 9, 11 : j <- 30
            2 : j <- 28
            Sinon j <- 0
          Fin Selon
        FIN
        Déclaration des objets
        Objet  Type / Nature
        mois, j Entier
        """
        py = self.transpiler.compile(algo)
        ns = {'__name__': '__main__'}
        exec(py, ns)

    def test_predefined_functions(self):
        algo = """
        ALGORITHME TestBuiltins
        DEBUT
          a <- Abs(-10)
          b <- RacineCarré(25)
          c <- Arrondi(4.6)
          ch <- "Informatique"
          l <- Long(ch)
          sub <- Sous_chaine(ch, 0, 4)
          maj <- Majus(sub)
          num <- Estnum("1234")
          val <- Valeur("42")
        FIN
        Déclaration des objets
        Objet  Type / Nature
        a, l, num, val : Entier
        b, c : Réel
        ch, sub, maj : Chaîne
        """
        py = self.transpiler.compile(algo)
        ns = {'__name__': '__main__'}
        exec(py, ns)

    def test_array_operations(self):
        algo = """
        ALGORITHME TestTableau
        DEBUT
          T[0] <- 100
          T[1] <- 200
          T[2] <- T[0] + T[1]
        FIN
        Déclaration des objets
        Objet  Type / Nature
        T      Tableau de 10 Entier
        """
        py = self.transpiler.compile(algo)
        ns = {'__name__': '__main__'}
        exec(py, ns)

    def test_procedure_saisir_jusqua(self):
        algo = """
        Procedure saisir(@n:entier)
        Debut
          Repeter
          ecrire("N =")
          n <- 10
          jusqu'a(2 <= n <= 30)
        Fin

        ALGORITHME SommeDiviseurs
        DEBUT
          saisir(n)
          ecrire(n)
        FIN
        Déclaration des objets
        Objet  Type / Nature
        n      Entier
        """
        py = self.transpiler.compile(algo)
        self.assertIn("while True:", py)
        self.assertIn("if (2 <= n <= 30):", py)
        self.assertIn("break", py)
        self.assertIn("n = saisir(n)", py)
        ns = {'__name__': '__main__'}
        exec(py, ns)

    def test_players_ranking_compilation(self):
        with open("examples/players_ranking.algo", "r", encoding="utf-8") as f:
            algo = f.read()
        py = self.transpiler.compile(algo)
        self.assertIn("def _creer_Player", py)
        self.assertIn("def saisir(n):", py)
        self.assertIn("def registerPlayers(T, n):", py)
        self.assertIn("def playRounds(T, n, p):", py)
        self.assertIn("def determineRanking(T, n):", py)
        self.assertIn("T = array([_creer_Player() for _ in range(30)], dtype=object)", py)

    def test_string_array_preserves_full_strings(self):
        algo = """
        Procedure remplir(@T: Tableau de 5 Chaine)
        Debut
          T[0] <- "Hello World"
          T[1] <- "12345678"
        Fin

        ALGORITHME TestStringArray
        DEBUT
          remplir(T)
        FIN
        Déclaration des objets
        Objet  Type / Nature
        T      Tableau de 5 Chaine
        """
        py = self.transpiler.compile(algo)
        self.assertIn("T = array([''] * (5), dtype=object)", py)
        ns = {'__name__': '__main__'}
        exec(py, ns)

    def test_missing_end_blocks(self):
        # Missing Fin Pour
        with self.assertRaises(CompileError) as cm:
            self.transpiler.compile("ALGORITHME T\nDEBUT\nPour i de 1 à 10 Faire\nx <- i\nFIN\nDéclaration des objets\nx, i : Entier")
        self.assertIn("Fin Pour", str(cm.exception))

        # Missing Fin Tant que
        with self.assertRaises(CompileError) as cm:
            self.transpiler.compile("ALGORITHME T\nDEBUT\nTant que x < 10 Faire\nx <- x + 1\nFIN\nDéclaration des objets\nx : Entier")
        self.assertIn("Fin Tant que", str(cm.exception))

        # Missing Fin Si
        with self.assertRaises(CompileError) as cm:
            self.transpiler.compile("ALGORITHME T\nDEBUT\nSi x > 0 Alors\nx <- 0\nFIN\nDéclaration des objets\nx : Entier")
        self.assertIn("Fin Si", str(cm.exception))

        # Missing Jusqu'à
        with self.assertRaises(CompileError) as cm:
            self.transpiler.compile("ALGORITHME T\nDEBUT\nRépéter\nx <- x + 1\nFIN\nDéclaration des objets\nx : Entier")
        self.assertIn("Jusqu'à", str(cm.exception))

        # Missing Fin Selon
        with self.assertRaises(CompileError) as cm:
            self.transpiler.compile("ALGORITHME T\nDEBUT\nSelon x\n1 : x <- 2\nFIN\nDéclaration des objets\nx : Entier")
        self.assertIn("Fin Selon", str(cm.exception))

        # Missing FIN in subprogram
        with self.assertRaises(CompileError) as cm:
            self.transpiler.compile("Procedure p()\nDEBUT\nx <- 1\nALGORITHME T\nDEBUT\np()\nFIN\nDéclaration des objets\nx : Entier")
        self.assertIn("FIN", str(cm.exception))

        # Missing FIN in ALGORITHME
        with self.assertRaises(CompileError) as cm:
            self.transpiler.compile("ALGORITHME T\nDEBUT\nx <- 1\nDéclaration des objets\nx : Entier")
        self.assertIn("FIN", str(cm.exception))

        # Missing Fin Enregistrement
        with self.assertRaises(CompileError) as cm:
            self.transpiler.compile("ALGORITHME T\nDEBUT\nFIN\nDéclaration des types\nRec = Enregistrement\na: Entier")
        self.assertIn("Fin Enregistrement", str(cm.exception))

    def test_mandatory_end_enforcement(self):
        # Missing FIN without DEBUT
        with self.assertRaises(MissingEndError):
            self.transpiler.compile("ALGORITHME MonAlgo\nx <- 1\nDéclaration des objets\nx : Entier")

        # Missing FIN with DEBUT
        with self.assertRaises(MissingEndError):
            self.transpiler.compile("ALGORITHME MonAlgo\nDEBUT\nx <- 1\nDéclaration des objets\nx : Entier")

        # English END is accepted
        py = self.transpiler.compile("ALGORITHME MonAlgo\nDEBUT\nx <- 1\nEND\nDéclaration des objets\nx : Entier")
        self.assertIn("x = 1", py)

    def test_mandatory_types_enforcement(self):
        # Undeclared variable in main
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile("ALGORITHME MonAlgo\nDEBUT\nx <- 1\nFIN")
        self.assertIn("non déclaré", str(cm.exception))

        # Undeclared variable in subprogram
        algo_sub = """
        Procedure test(n: Entier)
        DEBUT
          y <- n + 1
        FIN
        ALGORITHME MonAlgo
        DEBUT
          test(5)
        FIN
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(algo_sub)
        self.assertIn("non déclaré", str(cm.exception))

        # Subprogram parameter missing type
        algo_param = """
        Procedure test(n)
        DEBUT
          ecrire(n)
        FIN
        ALGORITHME MonAlgo
        DEBUT
          test(5)
        FIN
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(algo_param)
        self.assertIn("Type manquant pour le paramètre", str(cm.exception))

        # Function missing return type
        algo_fn = """
        Fonction carre(x: Entier)
        DEBUT
          retourner x * x
        FIN
        ALGORITHME MonAlgo
        DEBUT
          y <- carre(5)
        FIN
        Déclaration des objets
        y : Entier
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(algo_fn)
        self.assertIn("Type de retour obligatoire", str(cm.exception))

        # TDO item missing type
        algo_tdo = """
        ALGORITHME MonAlgo
        DEBUT
          x <- 1
        FIN
        Déclaration des objets
        Objet Type
        x
        """
        with self.assertRaises(MissingTypeError) as cm:
            self.transpiler.compile(algo_tdo)
        self.assertIn("Type manquant", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
