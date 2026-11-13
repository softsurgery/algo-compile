"""
Unit tests for:
1. Subprograms separate TDOG and TDOL tables detection in TDO view.
2. Verification that Variables tab is removed and only TDO and TDNT tabs remain.
3. The new TDNT (Tableau de Déclaration des Nouveaux Types) inspector tab.
"""

import unittest
from PyQt5.QtWidgets import QApplication
from compiler.transpiler import AlgoTranspiler
from compiler.symbol_extractor import extract_all_symbols
from ui.tdnt_view import TDNTView
from ui.tdo_view import TDOView
from ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])


class TestSubprogramsVariablesAndTDNT(unittest.TestCase):
    def setUp(self):
        self.transpiler = AlgoTranspiler(strict_types=True)

    def test_symbol_extractor_separates_tdog_and_tdol(self):
        code = """
        Procedure saisir(@n:entier)
        DEBUT
          lire(n)
        FIN
        Tableau de déclaration des objets locaux
        /        /

        Fonction verifIdent(id:chaine) : Booléen
        DEBUT
          verif <- Vrai
          i <- 0
          Retourner verif
        FIN
        Tableau de déclaration des objets locaux
        Objet        Type / Nature
        verif        Booléen
        i            Entier

        Procedure remplir(@IDENT:Tableau de 50 Chaine, @DATE:Tableau de 50 Chaine, n:entier)
        DEBUT
          i <- 0
        FIN
        Tableau de déclaration des objets locaux
        Objet        Type / Nature
        verifIdent   Fonction
        i            Entier

        ALGORITHME PROB2019
        DEBUT
          saisir(n)
          remplir(IDENT,DATE,n)
        FIN
        Tableau de déclaration des objets globaux
        Objet              Type / Nature
        saisir, remplir    Procédure
        n                  entier
        IDENT              Tableau de 50 Chaine
        DATE               Tableau de 50 Chaine
        """
        symbols = extract_all_symbols(code)

        # Verify separate tdo_tables
        self.assertIn('tdo_tables', symbols)
        tables = symbols['tdo_tables']
        self.assertEqual(len(tables), 4)

        # 1. TDOG table
        tdog = tables[0]
        self.assertEqual(tdog['kind'], 'tdog')
        tdog_obj_names = [o['name'] for o in tdog['objects']]
        self.assertIn('saisir', tdog_obj_names)
        self.assertIn('remplir', tdog_obj_names)
        self.assertIn('n', tdog_obj_names)
        self.assertIn('IDENT', tdog_obj_names)
        self.assertIn('DATE', tdog_obj_names)
        # Must not contain subprogram locals or parameters
        self.assertNotIn('verif', tdog_obj_names)
        self.assertNotIn('id', tdog_obj_names)

        # 2. TDOL saisir table
        tdol_saisir = next(t for t in tables if t.get('subprogram_name') == 'saisir')
        self.assertEqual(tdol_saisir['kind'], 'tdol')
        saisir_obj_names = [o['name'] for o in tdol_saisir['objects']]
        self.assertIn('@n', saisir_obj_names)
        self.assertNotIn('verif', saisir_obj_names)

        # 3. TDOL verifIdent table
        tdol_verif = next(t for t in tables if t.get('subprogram_name') == 'verifIdent')
        verif_obj_names = [o['name'] for o in tdol_verif['objects']]
        self.assertIn('id', verif_obj_names)
        self.assertIn('verif', verif_obj_names)
        self.assertIn('i', verif_obj_names)
        self.assertNotIn('n', verif_obj_names)

        # 4. TDOL remplir table
        tdol_remplir = next(t for t in tables if t.get('subprogram_name') == 'remplir')
        remplir_obj_names = [o['name'] for o in tdol_remplir['objects']]
        self.assertIn('@IDENT', remplir_obj_names)
        self.assertIn('@DATE', remplir_obj_names)
        self.assertIn('n', remplir_obj_names)
        self.assertIn('verifIdent', remplir_obj_names)
        self.assertIn('i', remplir_obj_names)

    def test_symbol_extractor_tdnt(self):
        code = """
        Tableau de déclaration des nouveaux types
        Eleve = Enregistrement
            nom : chaine
            note : réel
        Fin Enregistrement
        Tab = Tableau de 30 Eleve
        Mat = Tableau de 5 lignes * 5 colonnes Entier
        Age = Entier

        ALGORITHME Test
        DEBUT
          pass
        FIN
        Tableau de déclaration des objets globaux
        e : Eleve
        """
        symbols = extract_all_symbols(code)
        ct = symbols['custom_types']
        self.assertIn('Eleve', ct)
        self.assertEqual(ct['Eleve']['kind'], 'enregistrement')
        self.assertIn('nom', ct['Eleve']['fields'])
        self.assertIn('Tab', ct)
        self.assertEqual(ct['Tab']['kind'], 'tableau_1d')
        self.assertIn('Mat', ct)
        self.assertEqual(ct['Mat']['kind'], 'tableau_2d')
        self.assertIn('Age', ct)
        self.assertEqual(ct['Age']['kind'], 'alias')

    def test_tdnt_view_widget(self):
        view = TDNTView(is_dark=False)
        self.assertEqual(view.table.columnCount(), 3)
        self.assertEqual(view.table.horizontalHeaderItem(0).text(), "Nouveau Type")
        self.assertEqual(view.table.horizontalHeaderItem(1).text(), "Nature")
        self.assertEqual(view.table.horizontalHeaderItem(2).text(), "Définition / Structure")

        custom_types = {
            'Etud': {'kind': 'enregistrement', 'fields': {'nom': 'chaine', 'note': 'reel'}},
            'Scores': {'kind': 'tableau_1d', 'size': '50', 'elem_type': 'Entier'},
            'Grille': {'kind': 'tableau_2d', 'rows': '10', 'cols': '10', 'elem_type': 'Entier'},
            'AliasT': {'kind': 'alias', 'target_type': 'Entier'}
        }
        view.update_tdnt(custom_types)
        self.assertEqual(view.table.rowCount(), 4)
        self.assertEqual(view.lbl_count.text(), "4 types")

        # Test dark mode toggle
        view.set_dark_mode(True)
        view.set_dark_mode(False)

        # Clear
        view.clear_tdnt()
        self.assertEqual(view.table.rowCount(), 0)
        self.assertEqual(view.lbl_count.text(), "0 types")
        view.close()

    def test_tdo_view_separate_tables_rendering(self):
        view = TDOView(is_dark=False)

        tables = [
            {
                'id': 'tdog',
                'title': 'Tableau de Déclaration des Objets Globaux (T.D.O.G.)',
                'short_name': 'T.D.O.G. (Objets Globaux)',
                'kind': 'tdog',
                'objects': [
                    {'name': 'n', 'type': 'entier', 'py_equiv': 'int'},
                    {'name': 'Calcul', 'type': 'Procédure', 'py_equiv': 'def Calcul(...) -> None'}
                ]
            },
            {
                'id': 'tdol_Calcul',
                'title': 'T.D.O.L. — Procédure Calcul',
                'short_name': 'T.D.O.L. (Calcul)',
                'kind': 'tdol',
                'subprogram_name': 'Calcul',
                'objects': [
                    {'name': 'x', 'type': 'entier', 'py_equiv': 'int'},
                    {'name': 'y', 'type': 'réel', 'py_equiv': 'float'}
                ]
            }
        ]

        view.update_tdo(tables)

        # Selector has "Tous les tableaux", "T.D.O.G. (Objets Globaux)", "T.D.O.L. (Calcul)"
        selector_items = [view.table_selector.itemText(i) for i in range(view.table_selector.count())]
        self.assertIn("Tous les tableaux (T.D.O.G. & T.D.O.L.)", selector_items)
        self.assertIn("T.D.O.G. (Objets Globaux)", selector_items)
        self.assertIn("T.D.O.L. (Calcul)", selector_items)

        # In "Tous les tableaux", 2 cards rendered separately
        self.assertEqual(len(view._table_cards), 2)
        tdog_card = view._table_cards[0]
        tdol_card = view._table_cards[1]
        self.assertEqual(tdog_card.table.rowCount(), 2)
        self.assertEqual(tdol_card.table.rowCount(), 2)
        self.assertEqual(tdog_card.table.columnCount(), 2)
        self.assertEqual(tdol_card.table.columnCount(), 2)

        # Selecting T.D.O.G. shows only 1 card
        idx_tdog = view.table_selector.findText("T.D.O.G. (Objets Globaux)")
        view.table_selector.setCurrentIndex(idx_tdog)
        self.assertEqual(len(view._table_cards), 1)
        self.assertEqual(view._table_cards[0].table_info['kind'], 'tdog')

        # Selecting T.D.O.L. (Calcul) shows only 1 card
        idx_tdol = view.table_selector.findText("T.D.O.L. (Calcul)")
        view.table_selector.setCurrentIndex(idx_tdol)
        self.assertEqual(len(view._table_cards), 1)
        self.assertEqual(view._table_cards[0].table_info['kind'], 'tdol')

        # Clear
        view.clear_tdo()
        self.assertEqual(len(view._table_cards), 0)
        view.close()

    def test_main_window_has_no_variables_tab_and_has_tdo_and_tdnt(self):
        win = MainWindow()
        tab_titles = [win.side_tabs.tabText(i) for i in range(win.side_tabs.count())]

        # Variables tab MUST be removed
        self.assertNotIn("Variables", tab_titles)
        self.assertFalse(hasattr(win, "variables_view"))

        # Must have Code Python, Tableau T.D.O., Tableau T.D.N.T., Guide et Aide
        self.assertIn("Code Python", tab_titles)
        self.assertIn("Tableau T.D.O.", tab_titles)
        self.assertIn("Tableau T.D.N.T.", tab_titles)
        self.assertIn("Guide et Aide", tab_titles)

        # Verify Affichage menu does NOT contain "Variables"
        menubar = win.menuBar()
        menus = menubar.findChildren(type(menubar.addMenu("")))
        view_menu = next((m for m in menus if "Affichage" in m.title()), None)
        self.assertIsNotNone(view_menu)
        actions = [a.text() for a in view_menu.actions()]
        self.assertNotIn("Variables", actions)
        self.assertIn("Tableau T.D.O.", actions)
        self.assertIn("Tableau T.D.N.T.", actions)

        win.close()


if __name__ == '__main__':
    unittest.main()
