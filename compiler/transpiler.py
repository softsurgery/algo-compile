"""
Main Transpiler Pipeline for Algorithm to Python 3.
"""

from compiler.errors import (
    CompileError,
    MissingEndError,
    MissingTypeError,
    InvalidStructureError,
)
from compiler.validator import AlgoValidator
from compiler.utils import normalize_accents, split_arguments
from compiler.types import TypeHandler
from compiler.parser import SectionExtractor
from compiler.expressions import ExpressionTranslator
from compiler.statements import StatementTranslator
from compiler.subprograms import SubprogramTranslator
from compiler.symbol_extractor import extract_all_symbols

__all__ = [
    "AlgoTranspiler",
    "CompileError",
    "MissingEndError",
    "MissingTypeError",
    "InvalidStructureError",
]


class AlgoTranspiler:
    """
    Main Compiler / Transpiler Pipeline.
    Coordinates section extraction, error validation, type/object analysis,
    expression parsing, control flow structure compilation, and subprogram generation.
    """

    def __init__(self, strict_types: bool = True):
        self.subprogram_meta = {}   # name -> {'kind': kind, 'ref_params': [...], 'all_params': [...]}
        self.errors = []
        self.warnings = []
        self.strict_types = strict_types

        # Modular components
        self.section_extractor = SectionExtractor()
        self.type_handler = TypeHandler()
        self.validator = AlgoValidator(strict_types=strict_types)
        self.expr_trans = ExpressionTranslator()
        self.stmt_trans = StatementTranslator(self.expr_trans, self.type_handler, self.subprogram_meta)
        self.subprog_trans = SubprogramTranslator(self.stmt_trans)
        self.last_blocks = {}
        self.last_symbols = {}

    @property
    def declared_objects(self):
        return self.type_handler.declared_objects

    @declared_objects.setter
    def declared_objects(self, val):
        self.type_handler.declared_objects = val

    @property
    def custom_types(self):
        return self.type_handler.custom_types

    @custom_types.setter
    def custom_types(self, val):
        self.type_handler.custom_types = val

    @property
    def program_name(self):
        return self.section_extractor.program_name

    @program_name.setter
    def program_name(self, val):
        self.section_extractor.program_name = val

    def compile(self, algo_code: str, strict_types: bool = None) -> str:
        """
        Main entry point: transpiles algorithmic code to Python 3 with NumPy.
        Returns the generated Python source string.
        """
        # Reset state
        self.type_handler.reset()
        self.subprogram_meta.clear()
        self.section_extractor.program_name = "Algorithme"
        self.errors = []
        self.warnings = []

        if strict_types is not None:
            self.validator.strict_types = strict_types
        else:
            self.validator.strict_types = self.strict_types

        code = normalize_accents(algo_code)
        raw_lines = code.splitlines()

        # 1. Extract structural sections
        blocks = self.section_extractor.extract_sections(raw_lines)
        self.last_blocks = blocks
        self.last_symbols = extract_all_symbols(algo_code)

        # 2. Validate mandatory END structure
        self.validator.validate_end_structure(raw_lines, blocks)
        
        # 3. Parse type definitions first (TDNT)
        self.type_handler.parse_type_declarations(blocks.get('types', []))
        
        # 4. Parse object declarations (TDO / TDOG)
        self.type_handler.parse_object_declarations(blocks.get('objects', []))

        # 5. Pre-scan subprograms headers to register signatures and @ ref params
        for subprog in blocks.get('subprograms', []):
            self.section_extractor.register_subprogram_signature(subprog, self.subprogram_meta)

        # 6. Validate TDNT rules and Enregistrement type constraints
        self.validator.validate_tdnt_rules(blocks)
        self.validator.validate_no_direct_enregistrement(blocks)

        # 7. Validate subprogram headers and TDO syntax
        self.validator.validate_subprogram_headers(blocks.get('subprograms', []))
        if self.validator.strict_types:
            self.validator.validate_tables_presence(raw_lines, blocks)
            self.validator.validate_subprogram_declarations(blocks, self.subprogram_meta)
        self.validator.validate_tdo_syntax(blocks.get('objects', []))

        # 8. Validate mandatory types (cannot pass without)
        if self.validator.strict_types:
            self.validator.validate_mandatory_types(
                blocks,
                self.declared_objects,
                self.custom_types,
                self.subprogram_meta
            )

        # 5. Generate standard Python header & runtime imports
        py_lines = [
            "# -*- coding: utf-8 -*-",
            "# Code généré par Algoo",
            "",
            "from numpy import array",
            "from math import sqrt",
            "from random import randint",
            "from pickle import load, dump",
            "from compiler.runtime import (",
            "    Arrondi, RacineCarré, RacineCarre, Aléa, Alea, Ent, Abs,",
            "    Ord, Chr, Long, Pos, Convch, Estnum, Valeur, Sous_chaine,",
            "    Effacer, Majus, Enregistrement, _lire_valeur, _fin_fichier,",
            "    Fin_fichier, fin_fichier, Ouvrir, ouvrir, Fermer, fermer,",
            "    Lire_ligne, lire_ligne, Vrai, Faux, vrai, faux",
            ")",
            "",
        ]

        # 6. Generate custom record factory functions (_creer_Nom)
        py_lines.extend(self.type_handler.generate_record_constructors())

        # 7. Process Subprograms (Fonctions & Procédures)
        for subprog in blocks.get('subprograms', []):
            py_sub = self.subprog_trans.translate_subprogram(subprog)
            py_lines.extend(py_sub)
            py_lines.append("")

        # 8. Main algorithm body
        main_body = blocks.get('main', [])
        
        py_lines.append(f"# --- Algorithme Principal: {self.program_name} ---")
        py_lines.append("def main():")

        # Initialize declared objects with defaults (numpy arrays, dicts, default values)
        init_lines = self.type_handler.generate_object_initializations()
        if init_lines:
            for l in init_lines:
                py_lines.append(f"    {l}")
            py_lines.append("")

        # Translate main statements
        translated_main = self.stmt_trans.translate_statements(main_body, indent_level=1)
        if not translated_main:
            translated_main = ["    pass"]
        py_lines.extend(translated_main)

        py_lines.extend([
            "",
            "if __name__ == '__main__':",
            "    main()",
            ""
        ])

        return "\n".join(py_lines)

    # -------------------------------------------------------------------------
    # Backward-compatible helper delegates
    # -------------------------------------------------------------------------
    def _extract_sections(self, lines):
        return self.section_extractor.extract_sections(lines)

    def _register_subprogram_signature(self, subprog):
        return self.section_extractor.register_subprogram_signature(subprog, self.subprogram_meta)

    def _parse_type_declarations(self, lines):
        return self.type_handler.parse_type_declarations(lines)

    def _parse_object_declarations(self, lines):
        return self.type_handler.parse_object_declarations(lines)

    def _generate_object_initializations(self, objects_dict):
        return self.type_handler.generate_object_initializations(objects_dict)

    def _default_value_for_type(self, elem_type):
        return self.type_handler.default_value_for_type(elem_type)

    def _translate_subprogram(self, subprog):
        return self.subprog_trans.translate_subprogram(subprog)

    def _translate_statements(self, line_tuples, indent_level=1):
        return self.stmt_trans.translate_statements(line_tuples, indent_level)

    def _translate_single_statement(self, s, line_no=0):
        return self.stmt_trans.translate_single_statement(s, line_no)

    def _translate_target(self, target_str):
        return self.expr_trans.translate_target(target_str)

    def _translate_expression(self, expr_str):
        return self.expr_trans.translate_expression(expr_str)

    def _split_arguments(self, s):
        return split_arguments(s)

    def extract_symbols(self, algo_code: str = None) -> dict:
        """
        Extracts all symbols (TDNT, TDOG, and all subprograms variables & objects).
        If algo_code is None, uses last extracted symbols.
        """
        if algo_code is not None:
            self.last_symbols = extract_all_symbols(algo_code, self.custom_types)
        elif not self.last_symbols and hasattr(self, 'last_blocks'):
            self.last_symbols = extract_all_symbols("", self.custom_types)
        return self.last_symbols

    def get_all_variables(self, algo_code: str = None) -> list:
        """Returns list of all variables across global scope and all subprograms."""
        symbols = self.extract_symbols(algo_code)
        return symbols.get('variables', [])

    def get_all_tdo_objects(self, algo_code: str = None) -> list:
        """Returns list of all TDO objects (TDOG + all subprogram TDOL & parameters)."""
        symbols = self.extract_symbols(algo_code)
        return symbols.get('tdo_objects', [])

    def get_all_tdo_tables(self, algo_code: str = None) -> list:
        """Returns list of separated TDO tables (TDOG and each subprogram TDOL)."""
        symbols = self.extract_symbols(algo_code)
        return symbols.get('tdo_tables', [])

    def get_all_custom_types(self, algo_code: str = None) -> dict:
        """Returns dict of all TDNT custom types."""
        symbols = self.extract_symbols(algo_code)
        return symbols.get('custom_types', self.custom_types)
