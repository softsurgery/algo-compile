import unittest
from compiler.transpiler import AlgoTranspiler

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

if __name__ == '__main__':
    unittest.main()
