"""
Tests for Ouvrir, Fermer, and file operations according to Tunisian algorithmic conventions.
"""

import os
import tempfile
import unittest
from compiler.transpiler import AlgoTranspiler
from compiler.validator import AlgoValidator
from compiler.runtime import Ouvrir, Fermer, Lire_ligne, Fin_fichier


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.transpiler = AlgoTranspiler()

    def test_ouvrir_text_file_conventions(self):
        """Verifies Ouvrir('chemin', F, 'r') compiles cleanly and generates Ouvrir()."""
        algo = """ALGORITHME TestFichierTexte
DEBUT
  Ouvrir("data.txt", F, "r")
  Lire_ligne(F, ligne)
  Fermer(F)
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
F              Fichier Texte
ligne          Chaîne
"""
        py_code = self.transpiler.compile(algo)
        self.assertIn('F = Ouvrir("data.txt", "r")', py_code)
        self.assertIn("ligne = F.readline().rstrip('\\r\\n')", py_code)
        self.assertIn('F.close()', py_code)
        self.assertIn('F = None', py_code)

    def test_ouvrir_alt_argument_order(self):
        """Verifies Ouvrir(F, 'chemin', 'w') is also handled gracefully."""
        algo = """ALGORITHME TestEcriture
DEBUT
  Ouvrir(F, "sortie.txt", "w")
  Ecrire_nl(F, "Bonjour le monde")
  Fermer(F)
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
F              Fichier Texte
"""
        py_code = self.transpiler.compile(algo)
        self.assertIn('F = Ouvrir("sortie.txt", "w")', py_code)
        self.assertIn('F.write(str("Bonjour le monde") + \'\\n\')', py_code)
        self.assertIn('F.close()', py_code)

    def test_ouvrir_data_file_conventions(self):
        """Verifies binary data file operations (wb/rb with pickle dump/load)."""
        algo = """ALGORITHME TestFichierDonnees
DEBUT
  Ouvrir("scores.dat", F, "wb")
  note <- 18
  Ecrire(F, note)
  Fermer(F)

  Ouvrir("scores.dat", F, "rb")
  Lire(F, note_lue)
  Fermer(F)
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
F              Fichier de Entier
note, note_lue Entier
"""
        py_code = self.transpiler.compile(algo)
        self.assertIn('F = Ouvrir("scores.dat", "wb")', py_code)
        self.assertIn('dump(note, F)', py_code)
        self.assertIn('F = Ouvrir("scores.dat", "rb")', py_code)
        self.assertIn('note_lue = load(F)', py_code)

    def test_fin_fichier_in_loop(self):
        """Verifies Tant que Non Fin_fichier(F) compiles to valid Python."""
        algo = """ALGORITHME ParcoursFichier
DEBUT
  Ouvrir("liste.txt", F, "r")
  Tant que Non Fin_fichier(F) Faire
    Lire_ligne(F, s)
  Fin Tant que
  Fermer(F)
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
F              Fichier Texte
s              Chaîne
"""
        py_code = self.transpiler.compile(algo)
        self.assertIn('while not _fin_fichier(F):', py_code)

    def test_runtime_file_helpers(self):
        """Tests that Ouvrir, Fermer, Lire_ligne, Fin_fichier execute correctly at runtime."""
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
            tmp.write("Ligne 1\nLigne 2\n")
            tmp_path = tmp.name

        try:
            # Ouvrir in read mode
            f = Ouvrir(tmp_path, "r")
            self.assertFalse(Fin_fichier(f))
            line1 = Lire_ligne(f)
            self.assertEqual(line1, "Ligne 1")
            line2 = Lire_ligne(f)
            self.assertEqual(line2, "Ligne 2")
            self.assertTrue(Fin_fichier(f))
            Fermer(f)
            self.assertTrue(f.closed)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_relative_path_resolved_in_algo_directory(self):
        """Verifies that relative file paths are opened in the algorithm's directory unless absolute."""
        with tempfile.TemporaryDirectory() as algo_dir:
            old_algo_dir = os.environ.get("ALGO_DIR")
            os.environ["ALGO_DIR"] = algo_dir
            try:
                # 1. Relative path: must be created inside algo_dir
                f_rel = Ouvrir("mon_fichier.txt", "w")
                f_rel.write("Données algorithme")
                Fermer(f_rel)

                expected_rel_path = os.path.join(algo_dir, "mon_fichier.txt")
                self.assertTrue(os.path.isfile(expected_rel_path), "Relative file should be located in algorithm's folder")

                # 2. Absolute path: must be created exactly at absolute path, not inside algo_dir
                with tempfile.NamedTemporaryFile("w+", delete=False) as abs_tmp:
                    abs_path = abs_tmp.name

                f_abs = Ouvrir(abs_path, "w")
                f_abs.write("Fichier absolu")
                Fermer(f_abs)

                with open(abs_path, "r", encoding="utf-8") as fp:
                    self.assertEqual(fp.read(), "Fichier absolu")
                if os.path.exists(abs_path):
                    os.remove(abs_path)
            finally:
                if old_algo_dir is not None:
                    os.environ["ALGO_DIR"] = old_algo_dir
                else:
                    os.environ.pop("ALGO_DIR", None)

    def test_docs_files_exist_and_cover_ouvrir(self):
        """Verifies that the markdown docs include files documentation detailing Ouvrir."""
        docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
        fichiers_doc = os.path.join(docs_dir, "06_Structures_Donnees", "04_Fichiers.md")
        self.assertTrue(os.path.isfile(fichiers_doc), "Missing docs/06_Structures_Donnees/04_Fichiers.md")

        with open(fichiers_doc, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Ouvrir", content)
        self.assertIn("Fichier Texte", content)
        self.assertIn("Fichier de", content)
        self.assertIn("Fermer", content)

    def test_subprogram_file_parameters_and_alias_types(self):
        """Tests that custom type aliases for files (e.g. Texte = Fichier Texte) and subprogram parameters work seamlessly."""
        algo = """
Procedure ecrireTexte(@fe:Texte, ch:Chaine)
DEBUT
  ecrire_nl(fe, ch)
FIN
Tableau de déclaration des objets locaux
/

Procedure lireTexte(@fe:Texte, @ch:Chaine)
DEBUT
  lire_ligne(fe, ch)
FIN
Tableau de déclaration des objets locaux
/

Procedure ecrireData(@fs:Fiche, e:Chif)
DEBUT
  ecrire(fs, e)
FIN
Tableau de déclaration des objets locaux
/

Procedure lireData(@fs:Fiche, @e:Chif)
DEBUT
  lire(fs, e)
FIN
Tableau de déclaration des objets locaux
/

ALGORITHME TestFichiersComplet
DEBUT
  ouvrir("test_txt.txt", fe, "w")
  ecrireTexte(fe, "Ligne de test")
  fermer(fe)

  ouvrir("test_txt.txt", fe, "r")
  lireTexte(fe, s)
  fermer(fe)

  item.val <- 42
  ouvrir("test_bin.dat", fs, "wb")
  ecrireData(fs, item)
  fermer(fs)

  ouvrir("test_bin.dat", fs, "rb")
  lireData(fs, item_lu)
  fermer(fs)
FIN

Tableau de déclaration des objets globaux
Objet            Type / Nature
fe               Texte
fs               Fiche
s                Chaine
item, item_lu    Chif
ecrireTexte      Procedure
lireTexte        Procedure
ecrireData       Procedure
lireData         Procedure

Tableau de déclaration des nouveaux types
Texte = Fichier Texte
Fiche = Fichier de Chif

Chif = Enregistrement
    val : Entier
Fin Enregistrement
"""
        py_code = self.transpiler.compile(algo)
        self.assertIn("fe.write(str(ch) + '\\n')", py_code)
        self.assertIn("ch = fe.readline().rstrip('\\r\\n')", py_code)
        self.assertIn("dump(e, fs)", py_code)
        self.assertIn("e = load(fs)", py_code)

        # Run end-to-end in temp directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            old_algo = os.environ.get("ALGO_DIR")
            os.environ["ALGO_DIR"] = tmp_dir
            try:
                ns = {'__name__': '__main__'}
                exec(py_code, ns)

                # Check text file
                txt_path = os.path.join(tmp_dir, "test_txt.txt")
                self.assertTrue(os.path.exists(txt_path))
                with open(txt_path, "r", encoding="utf-8") as f:
                    self.assertEqual(f.read().strip(), "Ligne de test")

                # Check binary file
                dat_path = os.path.join(tmp_dir, "test_bin.dat")
                self.assertTrue(os.path.exists(dat_path))
                import pickle
                with open(dat_path, "rb") as f:
                    obj = pickle.load(f)
                    self.assertEqual(obj['val'], 42)
            finally:
                if old_algo is not None:
                    os.environ["ALGO_DIR"] = old_algo
                else:
                    os.environ.pop("ALGO_DIR", None)

    def test_lire_ligne_removes_newline(self):
        """Verifies that Lire_ligne reads lines into strings without trailing newline characters."""
        algo = """
ALGORITHME TestNoNewline
DEBUT
  ouvrir("lines.txt", f, "r")
  lire_ligne(f, ch)
  dernier_car <- ch[long(ch) - 1]
  ecrire(ch, "|", dernier_car)
  fermer(f)
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
f              Fichier Texte
ch             Chaine
dernier_car    Caractere
"""
        py_code = self.transpiler.compile(algo)
        self.assertIn("ch = f.readline().rstrip('\\r\\n')", py_code)

        import io
        from contextlib import redirect_stdout

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, "lines.txt")
            with open(file_path, "w", encoding="utf-8") as fp:
                fp.write("123\n456\n")

            old_algo = os.environ.get("ALGO_DIR")
            os.environ["ALGO_DIR"] = tmp_dir
            try:
                buf = io.StringIO()
                ns = {'__name__': '__main__'}
                with redirect_stdout(buf):
                    exec(py_code, ns)
                self.assertEqual(buf.getvalue(), "123 | 3")
            finally:
                if old_algo is not None:
                    os.environ["ALGO_DIR"] = old_algo
                else:
                    os.environ.pop("ALGO_DIR", None)


if __name__ == "__main__":
    unittest.main()
