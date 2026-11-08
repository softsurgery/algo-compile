"""
Transpiler from Tunisian Algorithm Convention (2024/2025) to Python 3.
Complies with 'Convention Algorithmique 2024.pdf' and 'Implémention 2024-2025.pdf'.
"""

import re
import unicodedata

class CompileError(Exception):
    def __init__(self, message, line_num=None, column=None):
        super().__init__(message)
        self.message = message
        self.line_num = line_num
        self.column = column

    def __str__(self):
        if self.line_num is not None:
            return f"Ligne {self.line_num}: {self.message}"
        return self.message


def normalize_accents(text):
    """Normalize accented characters while preserving standard accents."""
    return unicodedata.normalize('NFC', text)


class AlgoTranspiler:
    def __init__(self):
        self.declared_objects = {}  # var_name -> type_desc
        self.custom_types = {}      # type_name -> type_def
        self.program_name = "Algorithme"
        self.subprograms = []
        self.main_code_lines = []
        self.errors = []
        self.warnings = []

    def compile(self, algo_code: str) -> str:
        """
        Main entry point: transpiles algorithmic code to Python 3.
        Returns the generated Python source string.
        """
        self.declared_objects = {}
        self.custom_types = {}
        self.program_name = "Algorithme"
        self.subprograms = []
        self.main_code_lines = []
        self.errors = []
        self.warnings = []

        code = normalize_accents(algo_code)
        
        # 1. Parse comments and isolate declaration sections vs code blocks
        raw_lines = code.splitlines()

        # Split into sections:
        # We may have:
        # - Header: ALGORITHME Nom
        # - Functions / Procedures
        # - Main block: DEBUT ... FIN
        # - Object declarations (TDO): Déclaration des objets ...
        # - Type declarations: Déclaration des nouveaux types ...
        
        blocks = self._extract_sections(raw_lines)
        
        # Parse type definitions first
        self._parse_type_declarations(blocks.get('types', []))
        
        # Parse object declarations (TDO)
        self._parse_object_declarations(blocks.get('objects', []))

        # Generate Python code header
        py_lines = [
            "# -*- coding: utf-8 -*-",
            "# Code généré conformément aux Conventions Algorithmiques 2024/2025",
            "# Ministère de l'Éducation - République Tunisienne",
            "",
            "from numpy import array",
            "from math import sqrt",
            "from random import randint",
            "from pickle import load, dump",
            "from compiler.runtime import (",
            "    Arrondi, RacineCarré, RacineCarre, Aléa, Alea, Ent, Abs,",
            "    Ord, Chr, Long, Pos, Convch, Estnum, Valeur, Sous_chaine,",
            "    Effacer, Majus, Enregistrement, _lire_valeur, _fin_fichier,",
            "    Vrai, Faux, vrai, faux",
            ")",
            "",
        ]

        # Process custom record type definitions into generator functions/classes
        for t_name, t_def in self.custom_types.items():
            if t_def['kind'] == 'enregistrement':
                fields = ", ".join(f"{f}=None" for f in t_def['fields'])
                fields_dict = ", ".join(f"'{f}': {f}" for f in t_def['fields'])
                py_lines.append(f"def _creer_{t_name}({fields}):")
                py_lines.append(f"    return Enregistrement({{{fields_dict}}})")
                py_lines.append("")

        # Process Subprograms (Fonction & Procédure)
        for subprog in blocks.get('subprograms', []):
            py_sub = self._translate_subprogram(subprog)
            py_lines.extend(py_sub)
            py_lines.append("")

        # Main algorithm body
        main_body = blocks.get('main', [])
        
        # Add main block wrapper
        py_lines.append(f"# --- Algorithme Principal: {self.program_name} ---")
        py_lines.append("def main():")

        # Initialize declared objects with defaults (numpy arrays, dicts, default values)
        init_lines = self._generate_object_initializations(self.declared_objects)
        if init_lines:
            for l in init_lines:
                py_lines.append(f"    {l}")
            py_lines.append("")

        # Translate main statements
        translated_main = self._translate_statements(main_body, indent_level=1)
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
    # Parsing Sections
    # -------------------------------------------------------------------------
    def _extract_sections(self, lines):
        """Categorize lines into header, subprograms, main, objects, types."""
        sections = {
            'header': [],
            'subprograms': [],
            'main': [],
            'objects': [],
            'types': []
        }

        # Normalize line tags
        current_section = 'header'
        current_subprog = None
        in_main = False
        in_tdo = False
        in_types = False

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            line_no = i + 1

            # Strip full-line comments or empty lines for classification
            if not stripped or stripped.startswith(("//", "#", "/*")):
                if in_main:
                    sections['main'].append((line_no, line))
                elif current_subprog is not None:
                    current_subprog['lines'].append((line_no, line))
                elif in_tdo:
                    sections['objects'].append((line_no, line))
                elif in_types:
                    sections['types'].append((line_no, line))
                i += 1
                continue

            # Check for section headers
            lower = stripped.lower()
            
            # Header: ALGORITHME Nom
            m_algo = re.match(r'^algorithme\s+([a-zA-Z0-9_]+)', stripped, re.IGNORECASE)
            if m_algo:
                self.program_name = m_algo.group(1)
                sections['header'].append((line_no, stripped))
                i += 1
                continue

            # Declarations section
            if re.match(r'^(déclaration|declaration)\s+des\s+objets', stripped, re.IGNORECASE) or \
               stripped.upper() == "T.D.O" or stripped.upper() == "TDO":
                in_tdo = True
                in_types = False
                in_main = False
                current_subprog = None
                i += 1
                continue

            if re.match(r'^(déclaration|declaration)\s+des\s+nouveaux\s+types', stripped, re.IGNORECASE) or \
               re.match(r'^(déclaration|declaration)\s+des\s+types', stripped, re.IGNORECASE) or \
               stripped.upper() == "T.D.N.T" or stripped.upper() == "TDNT":
                in_types = True
                in_tdo = False
                in_main = False
                current_subprog = None
                i += 1
                continue

            # Subprogram declaration: Fonction / Procédure
            m_fn = re.match(r'^(fonction|procédure|procedure)\s+([a-zA-Z0-9_]+)', stripped, re.IGNORECASE)
            if m_fn and not in_tdo and not in_types:
                kind = m_fn.group(1).lower()
                if 'proc' in kind:
                    kind = 'procedure'
                else:
                    kind = 'fonction'
                current_subprog = {
                    'kind': kind,
                    'header': stripped,
                    'start_line': line_no,
                    'lines': [(line_no, line)],
                    'tdo': []
                }
                sections['subprograms'].append(current_subprog)
                in_main = False
                i += 1
                continue

            # Check for DEBUT
            if stripped.upper() == "DEBUT" or stripped.upper() == "DÉBUT":
                if current_subprog is not None:
                    current_subprog['lines'].append((line_no, line))
                else:
                    in_main = True
                    in_tdo = False
                    in_types = False
                i += 1
                continue

            # Check for FIN
            if stripped.upper() == "FIN":
                if current_subprog is not None:
                    current_subprog['lines'].append((line_no, line))
                    current_subprog = None
                elif in_main:
                    in_main = False
                i += 1
                continue

            # Otherwise accumulate based on state
            if in_types:
                sections['types'].append((line_no, line))
            elif in_tdo:
                sections['objects'].append((line_no, line))
            elif current_subprog is not None:
                sections['subprograms'][-1]['lines'].append((line_no, line))
            elif in_main:
                sections['main'].append((line_no, line))
            else:
                # If neither main nor subprog has been explicitly triggered,
                # but statements exist outside (common when student omits ALGORITHME ... DEBUT)
                sections['main'].append((line_no, line))

            i += 1

        return sections

    # -------------------------------------------------------------------------
    # Parsing Declarations (TDO & Types)
    # -------------------------------------------------------------------------
    def _parse_type_declarations(self, lines):
        """Parse custom types (records, arrays, files)."""
        idx = 0
        while idx < len(lines):
            line_no, line = lines[idx]
            s = line.strip()
            idx += 1
            if not s or s.lower().startswith(('nouveau type', 'nom_type', 'objet', 'type / nature', '|')):
                continue

            # Check for record: Nom = Enregistrement ... Fin
            m_rec = re.match(r'^([a-zA-Z0-9_]+)\s*=\s*enregistrement', s, re.IGNORECASE)
            if m_rec:
                type_name = m_rec.group(1)
                fields = []
                while idx < len(lines):
                    l_no, l_text = lines[idx]
                    idx += 1
                    t_str = l_text.strip()
                    if t_str.upper() in ('FIN', 'FIN ENREGISTREMENT'):
                        break
                    if ':' in t_str:
                        fname, ftype = t_str.split(':', 1)
                        for f in fname.split(','):
                            f_clean = f.strip()
                            if f_clean:
                                fields.append(f_clean)
                self.custom_types[type_name] = {'kind': 'enregistrement', 'fields': fields}
                continue

            # Check for array type: Nom = Tableau de N Type
            m_arr1 = re.match(r'^([a-zA-Z0-9_]+)\s*=\s*tableau\s+de\s+(\d+|[a-zA-Z0-9_]+)\s+(.+)$', s, re.IGNORECASE)
            if m_arr1:
                t_name, size, elem_type = m_arr1.group(1), m_arr1.group(2), m_arr1.group(3).strip()
                self.custom_types[t_name] = {'kind': 'tableau_1d', 'size': size, 'elem_type': elem_type}
                continue

            # Check for 2D array: Nom = Tableau de N lignes * M colonnes Type
            m_arr2 = re.match(r'^([a-zA-Z0-9_]+)\s*=\s*tableau\s+de\s+(\d+|[a-zA-Z0-9_]+)\s*lignes?\s*\*\s*(\d+|[a-zA-Z0-9_]+)\s*colonnes?\s+(.+)$', s, re.IGNORECASE)
            if m_arr2:
                t_name, rows, cols, elem_type = m_arr2.group(1), m_arr2.group(2), m_arr2.group(3), m_arr2.group(4).strip()
                self.custom_types[t_name] = {'kind': 'tableau_2d', 'rows': rows, 'cols': cols, 'elem_type': elem_type}
                continue

    def _parse_object_declarations(self, lines):
        """Parse TDO lines (e.g. x, y, z : Entier or x, y | Entier or columns)."""
        for line_no, line in lines:
            s = line.strip()
            if not s:
                continue
            lower = s.lower()
            if lower.startswith(('objet', 'type', 'nom_objet', '---', '===')):
                continue

            parts = None
            if ':' in s:
                parts = s.split(':', 1)
            elif '|' in s:
                parts = s.split('|', 1)
            else:
                m = re.match(
                    r'^([a-zA-Z0-9_,\s]+?)\s+(Tableau\b.*|Enregistrement\b.*|Fichier\b.*|Entier\b.*|Réel\b.*|Reel\b.*|Booléen\b.*|Booleen\b.*|Caractère\b.*|Caractere\b.*|Chaîne\b.*|Chaine\b.*|[a-zA-Z0-9_]+)$',
                    s,
                    re.IGNORECASE
                )
                if m:
                    parts = [m.group(1), m.group(2)]
                elif re.search(r'\s{2,}|\t', s):
                    parts = re.split(r'\s{2,}|\t', s, 1)

            if parts and len(parts) == 2:
                names_part, type_part = parts[0].strip(), parts[1].strip()
                names = [n.strip() for n in names_part.split(',') if n.strip()]
                for name in names:
                    clean_name = re.sub(r'[^a-zA-Z0-9_]', '', name)
                    if clean_name:
                        self.declared_objects[clean_name] = type_part

    def _generate_object_initializations(self, objects_dict):
        """Generates Python initialization code for declared objects (numpy arrays, dicts)."""
        lines = []
        for var_name, type_str in objects_dict.items():
            t_lower = type_str.lower()

            # Check if type matches custom type
            if type_str in self.custom_types:
                t_def = self.custom_types[type_str]
                if t_def['kind'] == 'enregistrement':
                    lines.append(f"{var_name} = _creer_{type_str}()")
                    continue
                elif t_def['kind'] == 'tableau_1d':
                    init_val = self._default_value_for_type(t_def['elem_type'])
                    lines.append(f"{var_name} = array([{init_val}] * ({t_def['size']}))")
                    continue
                elif t_def['kind'] == 'tableau_2d':
                    init_val = self._default_value_for_type(t_def['elem_type'])
                    lines.append(f"{var_name} = array([[{init_val}] * ({t_def['cols']})] * ({t_def['rows']}))")
                    continue

            # Tableau 2D: Tableau de N lignes * M colonnes Type
            m_arr2 = re.match(r'tableau\s+de\s+(.+?)\s*lignes?\s*\*\s*(.+?)\s*colonnes?\s+(.+)', t_lower)
            if m_arr2:
                rows, cols, elem_type = m_arr2.group(1).strip(), m_arr2.group(2).strip(), m_arr2.group(3).strip()
                init_val = self._default_value_for_type(elem_type)
                lines.append(f"{var_name} = array([[{init_val}] * ({cols})] * ({rows}))")
                continue

            # Tableau 1D: Tableau de N Type
            m_arr1 = re.match(r'tableau\s+de\s+(.+?)\s+([a-zA-Z0-9_éèêà]+.*)', t_lower)
            if m_arr1:
                size, elem_type = m_arr1.group(1).strip(), m_arr1.group(2).strip()
                init_val = self._default_value_for_type(elem_type)
                lines.append(f"{var_name} = array([{init_val}] * ({size}))")
                continue

            # Enregistrement
            if 'enregistrement' in t_lower:
                lines.append(f"{var_name} = Enregistrement()")
                continue

        return lines

    def _default_value_for_type(self, elem_type):
        t = elem_type.lower()
        if 'entier' in t or 'int' in t:
            return "0"
        elif 'reel' in t or 'réel' in t or 'float' in t:
            return "0.0"
        elif 'bool' in t:
            return "False"
        elif 'caractere' in t or 'caractère' in t or 'char' in t or 'chaine' in t or 'chaîne' in t or 'str' in t:
            return "''"
        return "0"

    # -------------------------------------------------------------------------
    # Subprogram Translation
    # -------------------------------------------------------------------------
    def _translate_subprogram(self, subprog):
        """Translates Fonction or Procédure to def."""
        header_text = subprog['header']
        kind = subprog['kind']

        # Parse: Fonction Nom (p1: t1, @p2: t2) : Type_res
        # or Procédure Nom (p1: t1, @p2: t2)
        m = re.match(r'^(?:fonction|procédure|procedure)\s+([a-zA-Z0-9_]+)\s*(?:\((.*?)\))?(?:\s*:\s*([a-zA-Z0-9_]+))?', header_text, re.IGNORECASE)
        if not m:
            return [f"# Erreur de syntaxe dans l'en-tête: {header_text}"]

        sub_name = m.group(1)
        params_str = m.group(2) or ""
        return_type = m.group(3) or ""

        # Parse parameters
        py_params = []
        param_ref = set()
        if params_str.strip():
            raw_params = params_str.split(',')
            for p in raw_params:
                p = p.strip()
                if not p:
                    continue
                if ':' in p:
                    pname, ptype = p.split(':', 1)
                    pname = pname.strip()
                else:
                    pname = p
                
                # Check for @ pass-by-reference
                if pname.startswith('@'):
                    clean_pname = pname[1:].strip()
                    param_ref.add(clean_pname)
                    py_params.append(clean_pname)
                else:
                    py_params.append(pname)

        params_joined = ", ".join(py_params)
        py_lines = [f"def {sub_name}({params_joined}):"]

        # Filter out DEBUT and FIN lines from body
        body_lines = []
        for line_no, line in subprog['lines']:
            stripped = line.strip()
            if stripped.upper() in ('DEBUT', 'DÉBUT', 'FIN') or stripped == header_text:
                continue
            body_lines.append((line_no, line))

        sub_body = self._translate_statements(body_lines, indent_level=1)
        if not sub_body:
            sub_body = ["    pass"]
        py_lines.extend(sub_body)

        return py_lines

    # -------------------------------------------------------------------------
    # Statement Translation
    # -------------------------------------------------------------------------
    def _translate_statements(self, line_tuples, indent_level=1):
        """Translates a sequence of algorithmic lines to Python statements."""
        result = []
        base_indent = "    " * indent_level
        i = 0

        while i < len(line_tuples):
            line_no, line = line_tuples[i]
            s = line.strip()

            if not s:
                i += 1
                continue

            # Strip comments
            if s.startswith(("//", "#")):
                comment_text = s[2:].strip() if s.startswith("//") else s[1:].strip()
                result.append(f"{base_indent}# {comment_text}")
                i += 1
                continue

            # Check for DEBUT or FIN standalone
            if s.upper() in ('DEBUT', 'DÉBUT', 'FIN'):
                i += 1
                continue

            # 1. Conditionnelle: Si ... Alors
            m_si = re.match(r'^si\s+(.+?)\s+alors$', s, re.IGNORECASE)
            if m_si:
                cond = self._translate_expression(m_si.group(1))
                result.append(f"{base_indent}if {cond}:")
                
                # Collect then block, elifs, and else
                block_res, next_i = self._parse_si_block(line_tuples, i + 1, indent_level)
                result.extend(block_res)
                i = next_i
                continue

            # 2. Selon <Sélecteur> ... Fin Selon
            m_selon = re.match(r'^selon\s+(.+)$', s, re.IGNORECASE)
            if m_selon:
                selector = self._translate_expression(m_selon.group(1))
                result.append(f"{base_indent}match {selector}:")
                selon_res, next_i = self._parse_selon_block(line_tuples, i + 1, indent_level, selector)
                result.extend(selon_res)
                i = next_i
                continue

            # 3. Pour <compteur> de <debut> à <fin> [Pas = <p>] Faire ... Fin Pour
            m_pour = re.match(r'^pour\s+([a-zA-Z0-9_]+)\s+de\s+(.+?)\s+à\s+(.+?)(?:\s+pas\s*=\s*(.+?))?\s+faire$', s, re.IGNORECASE)
            if not m_pour:
                # also check without accent: 'a'
                m_pour = re.match(r'^pour\s+([a-zA-Z0-9_]+)\s+de\s+(.+?)\s+a\s+(.+?)(?:\s+pas\s*=\s*(.+?))?\s+faire$', s, re.IGNORECASE)
            
            if m_pour:
                counter = m_pour.group(1)
                start_val = self._translate_expression(m_pour.group(2))
                end_val = self._translate_expression(m_pour.group(3))
                step_val = m_pour.group(4)
                
                if step_val is not None:
                    step_expr = self._translate_expression(step_val)
                    # Support negative or positive step
                    range_expr = f"range({start_val}, ({end_val}) + 1 if ({step_expr}) > 0 else ({end_val}) - 1, {step_expr})"
                else:
                    range_expr = f"range({start_val}, ({end_val}) + 1)"

                result.append(f"{base_indent}for {counter} in {range_expr}:")
                
                # Collect loop body until Fin Pour
                body_lines, next_i = self._collect_block_until(line_tuples, i + 1, [r'^fin\s*pour$'])
                translated_body = self._translate_statements(body_lines, indent_level + 1)
                if not translated_body:
                    translated_body = [f"{base_indent}    pass"]
                result.extend(translated_body)
                i = next_i
                continue

            # 4. Tant que <Condition> Faire ... Fin Tant que
            m_tq = re.match(r'^tant\s*que\s+(.+?)\s+faire$', s, re.IGNORECASE)
            if m_tq:
                cond = self._translate_expression(m_tq.group(1))
                result.append(f"{base_indent}while {cond}:")
                body_lines, next_i = self._collect_block_until(line_tuples, i + 1, [r'^fin\s*tant\s*que$', r'^fintantque$'])
                translated_body = self._translate_statements(body_lines, indent_level + 1)
                if not translated_body:
                    translated_body = [f"{base_indent}    pass"]
                result.extend(translated_body)
                i = next_i
                continue

            # 5. Répéter ... Jusqu'à <Condition>
            if s.lower() in ('répéter', 'repeter'):
                result.append(f"{base_indent}while True:")
                # Collect until Jusqu'à
                body_lines, until_cond, next_i = self._collect_repeter_block(line_tuples, i + 1)
                translated_body = self._translate_statements(body_lines, indent_level + 1)
                if not translated_body:
                    translated_body = [f"{base_indent}    pass"]
                result.extend(translated_body)
                if until_cond:
                    until_py = self._translate_expression(until_cond)
                    result.append(f"{base_indent}    if {until_py}:")
                    result.append(f"{base_indent}        break")
                i = next_i
                continue

            # 6. Retourner <Expression>
            m_ret = re.match(r'^retourner\s+(.+)$', s, re.IGNORECASE)
            if m_ret:
                expr = self._translate_expression(m_ret.group(1))
                result.append(f"{base_indent}return {expr}")
                i += 1
                continue

            # 7. Single statement translation (Lire, Ecrire, Assignment, Procedure call)
            stmt = self._translate_single_statement(s, line_no)
            if stmt:
                result.append(f"{base_indent}{stmt}")
            i += 1

        return result

    # -------------------------------------------------------------------------
    # Parsing Conditionals (Si / Sinon Si / Sinon / FinSi)
    # -------------------------------------------------------------------------
    def _parse_si_block(self, line_tuples, start_idx, indent_level):
        """Parses if branches and returns translated lines and next index."""
        result = []
        base_indent = "    " * indent_level
        branch_body = []
        current_branch = 'if'
        idx = start_idx
        nesting = 0

        while idx < len(line_tuples):
            line_no, line = line_tuples[idx]
            s = line.strip()

            if re.match(r'^si\s+.+?\s+alors$', s, re.IGNORECASE):
                nesting += 1
                branch_body.append((line_no, line))
                idx += 1
                continue

            if nesting > 0:
                if re.match(r'^(?:fin\s*si|finsi)$', s, re.IGNORECASE):
                    nesting -= 1
                branch_body.append((line_no, line))
                idx += 1
                continue

            # Here nesting == 0, check for branch switches or end
            m_elif = re.match(r'^(?:sinon\s*si|sinonsi)\s+(.+?)\s+alors$', s, re.IGNORECASE)
            if m_elif:
                # Flush previous branch
                sub = self._translate_statements(branch_body, indent_level + 1)
                result.extend(sub if sub else [f"{base_indent}    pass"])
                branch_body = []
                cond = self._translate_expression(m_elif.group(1))
                result.append(f"{base_indent}elif {cond}:")
                idx += 1
                continue

            if re.match(r'^sinon$', s, re.IGNORECASE):
                sub = self._translate_statements(branch_body, indent_level + 1)
                result.extend(sub if sub else [f"{base_indent}    pass"])
                branch_body = []
                result.append(f"{base_indent}else:")
                idx += 1
                continue

            if re.match(r'^(?:fin\s*si|finsi)$', s, re.IGNORECASE):
                sub = self._translate_statements(branch_body, indent_level + 1)
                result.extend(sub if sub else [f"{base_indent}    pass"])
                idx += 1
                return result, idx

            branch_body.append((line_no, line))
            idx += 1

        # Reached end of file without FinSi
        sub = self._translate_statements(branch_body, indent_level + 1)
        result.extend(sub if sub else [f"{base_indent}    pass"])
        return result, idx

    # -------------------------------------------------------------------------
    # Parsing Selon
    # -------------------------------------------------------------------------
    def _parse_selon_block(self, line_tuples, start_idx, indent_level, selector):
        """Parses Selon choices into match/case."""
        result = []
        base_indent = "    " * indent_level
        idx = start_idx

        while idx < len(line_tuples):
            line_no, line = line_tuples[idx]
            s = line.strip()

            if re.match(r'^(?:fin\s*selon|finselon)$', s, re.IGNORECASE):
                idx += 1
                return result, idx

            if not s:
                idx += 1
                continue

            # Check for Sinon
            m_sinon = re.match(r'^sinon\s*(?::)?\s*(.*)$', s, re.IGNORECASE)
            if m_sinon:
                rest = m_sinon.group(1)
                result.append(f"{base_indent}    case _:")
                if rest:
                    stmt = self._translate_single_statement(rest, line_no)
                    result.append(f"{base_indent}        {stmt}")
                idx += 1
                continue

            # Case: pattern : treatment
            if ':' in s:
                pattern, action = s.split(':', 1)
                pattern = pattern.strip()
                action = action.strip()

                # Check if interval: val1 .. val2
                if '..' in pattern:
                    v1, v2 = pattern.split('..', 1)
                    v1_py = self._translate_expression(v1.strip())
                    v2_py = self._translate_expression(v2.strip())
                    result.append(f"{base_indent}    case s if ({v1_py} <= s <= {v2_py}):")
                else:
                    # Values list: v1, v2, v3
                    vals = [self._translate_expression(v.strip()) for v in pattern.split(',') if v.strip()]
                    pattern_py = " | ".join(vals)
                    result.append(f"{base_indent}    case {pattern_py}:")

                if action:
                    stmt = self._translate_single_statement(action, line_no)
                    result.append(f"{base_indent}        {stmt}")
                else:
                    result.append(f"{base_indent}        pass")
                idx += 1
                continue

            idx += 1

        return result, idx

    # -------------------------------------------------------------------------
    # Block collectors for Pour, Tant que, Répéter
    # -------------------------------------------------------------------------
    def _collect_block_until(self, line_tuples, start_idx, end_patterns):
        """Collects lines until a matching closing pattern is found at depth 0."""
        body = []
        nesting = 0
        idx = start_idx

        while idx < len(line_tuples):
            line_no, line = line_tuples[idx]
            s = line.strip()

            # Check nested open structures
            if re.match(r'^(?:pour\s+.+?\s+faire|tant\s*que\s+.+?\s+faire|si\s+.+?\s+alors|selon\s+.+|répéter|repeter)', s, re.IGNORECASE):
                nesting += 1
                body.append((line_no, line))
                idx += 1
                continue

            # Check closing patterns
            matched_end = any(re.match(pat, s, re.IGNORECASE) for pat in end_patterns)
            if matched_end:
                if nesting > 0:
                    nesting -= 1
                    body.append((line_no, line))
                    idx += 1
                    continue
                else:
                    return body, idx + 1

            # Check generic ends for nested constructs
            if re.match(r'^(?:fin\s*si|finsi|fin\s*pour|fin\s*tant\s*que|fintantque|fin\s*selon|jusqu[\'’]à|jusqu[\'’]a)', s, re.IGNORECASE):
                if nesting > 0:
                    nesting -= 1

            body.append((line_no, line))
            idx += 1

        return body, idx

    def _collect_repeter_block(self, line_tuples, start_idx):
        """Collects lines for Répéter until Jusqu'à."""
        body = []
        nesting = 0
        idx = start_idx

        while idx < len(line_tuples):
            line_no, line = line_tuples[idx]
            s = line.strip()

            if s.lower() in ('répéter', 'repeter'):
                nesting += 1
                body.append((line_no, line))
                idx += 1
                continue

            m_until = re.match(r'^jusqu[\'’]?(?:à|a)\s+(.+)$', s, re.IGNORECASE)
            if m_until:
                if nesting > 0:
                    nesting -= 1
                    body.append((line_no, line))
                    idx += 1
                    continue
                else:
                    until_cond = m_until.group(1).strip()
                    return body, until_cond, idx + 1

            body.append((line_no, line))
            idx += 1

        return body, None, idx

    # -------------------------------------------------------------------------
    # Single Statement Translation
    # -------------------------------------------------------------------------
    def _translate_single_statement(self, s, line_no=0):
        """Translates an assignment, Lire, Ecrire, or subprogram call."""
        s = s.strip()
        if not s:
            return ""

        # 1. Output: Écrire / Ecrire / Écrire_nl / Ecrire_nl
        m_ecrire = re.match(r'^(?:écrire_nl|ecrire_nl|écrire|ecrire)\s*\((.*)\)$', s, re.IGNORECASE)
        if m_ecrire:
            is_nl = 'nl' in s[:12].lower()
            args_str = m_ecrire.group(1).strip()
            args = self._split_arguments(args_str)
            
            # Check if first argument is a file logical name
            if len(args) >= 2 and args[0].isidentifier() and args[0] in self.declared_objects:
                t_obj = self.declared_objects[args[0]].lower()
                if 'fichier' in t_obj:
                    f_name = args[0]
                    content = self._translate_expression(args[1])
                    if 'texte' in t_obj:
                        if is_nl:
                            return f"{f_name}.write(str({content}) + '\\n')"
                        return f"{f_name}.write(str({content}))"
                    else:
                        return f"dump({content}, {f_name})"

            # Console output
            py_args = [self._translate_expression(arg) for arg in args]
            args_joined = ", ".join(py_args)
            if is_nl:
                return f"print({args_joined})" if args_joined else "print()"
            else:
                return f"print({args_joined}, end='')" if args_joined else "print(end='')"

        # 2. Input: Lire(...) or Lire_ligne(...)
        m_lire = re.match(r'^(?:lire_ligne|lire)\s*\((.*)\)$', s, re.IGNORECASE)
        if m_lire:
            is_line = 'ligne' in s[:12].lower()
            args_str = m_lire.group(1).strip()
            args = self._split_arguments(args_str)

            # Check if reading from file: Lire(f, obj) or Lire_ligne(f, ch)
            if len(args) == 2 and args[0].isidentifier() and args[0] in self.declared_objects:
                t_obj = self.declared_objects[args[0]].lower()
                if 'fichier' in t_obj:
                    f_name = args[0]
                    target_var = self._translate_target(args[1])
                    if 'texte' in t_obj:
                        if is_line:
                            return f"{target_var} = {f_name}.readline()"
                        return f"{target_var} = {f_name}.read()"
                    else:
                        return f"{target_var} = load({f_name})"

            # Interactive input from console: Lire(a, b, ...)
            assignments = []
            for arg in args:
                target_var = self._translate_target(arg.strip())
                # Lookup declared type for smart casting
                clean_id = re.sub(r'\[.*\]', '', arg.strip())
                vtype = self.declared_objects.get(clean_id, None)
                if vtype:
                    assignments.append(f"{target_var} = _lire_valeur('', {vtype!r})")
                else:
                    assignments.append(f"{target_var} = _lire_valeur('')")
            return "; ".join(assignments)

        # 3. File open: Ouvrir("path", f, "mode")
        m_open = re.match(r'^ouvrir\s*\((.+?)\)$', s, re.IGNORECASE)
        if m_open:
            args = self._split_arguments(m_open.group(1))
            if len(args) >= 3:
                path = self._translate_expression(args[0])
                f_name = args[1].strip()
                mode = self._translate_expression(args[2])
                return f"{f_name} = open({path}, {mode})"

        # 4. File close: Fermer(f)
        m_close = re.match(r'^fermer\s*\((.+?)\)$', s, re.IGNORECASE)
        if m_close:
            f_name = m_close.group(1).strip()
            return f"{f_name}.close()"

        # 5. Assignment: target <- expression (or , ←, :=)
        # Look for assignment symbols
        for sym in ['<-', '←', '\uf0e7', '', ':=']:
            if sym in s:
                parts = s.split(sym, 1)
                target = self._translate_target(parts[0].strip())
                expr = self._translate_expression(parts[1].strip())
                return f"{target} = {expr}"

        # If has bare '=', check if statement is assignment like `x = expr`
        if '=' in s and not s.startswith(('if', 'while', 'for')):
            # ensure not a comparison expression inside parens
            parts = s.split('=', 1)
            target = parts[0].strip()
            # check if target looks like a variable or index: name or name[i]
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\s*\[.+?\]|\.[a-zA-Z0-9_]+)?$', target):
                expr = self._translate_expression(parts[1].strip())
                target_py = self._translate_target(target)
                return f"{target_py} = {expr}"

        # 6. Procedure call or expression statement
        return self._translate_expression(s)

    # -------------------------------------------------------------------------
    # Target (LHS of assignment) Translation
    # -------------------------------------------------------------------------
    def _translate_target(self, target_str):
        """Translates target expression (e.g. M[i, j] or E.champ)."""
        target = target_str.strip()
        # Handle 2D index: M[i, j] -> M[i, j] (numpy) or M[i][j]
        m_2d = re.match(r'^([a-zA-Z0-9_]+)\s*\[\s*(.+?)\s*,\s*(.+?)\s*\]$', target)
        if m_2d:
            arr = m_2d.group(1)
            i_idx = self._translate_expression(m_2d.group(2))
            j_idx = self._translate_expression(m_2d.group(3))
            return f"{arr}[{i_idx}, {j_idx}]"

        # Handle 1D index: T[i]
        m_1d = re.match(r'^([a-zA-Z0-9_]+)\s*\[\s*(.+?)\s*\]$', target)
        if m_1d:
            arr = m_1d.group(1)
            i_idx = self._translate_expression(m_1d.group(2))
            return f"{arr}[{i_idx}]"

        # Handle record field: E.champ -> E['champ']
        if '.' in target:
            parts = target.split('.', 1)
            return f"{parts[0]}['{parts[1]}']"

        return target

    # -------------------------------------------------------------------------
    # Expression Translation
    # -------------------------------------------------------------------------
    def _translate_expression(self, expr_str):
        """
        Translates algorithmic expressions to Python expressions.
        - Operators: Div -> //, Mod -> %, Et -> and, Ou -> or, Non -> not
        - Equality: = -> ==, ≠ / <> -> !=, ≤ -> <=, ≥ -> >=
        - Sets & Intervals: x  [a .. b] -> a <= x <= b
        - Built-in functions mapping
        - Record dot access: E.champ -> E['champ']
        """
        if not expr_str:
            return ""

        # Protect string literals from token replacement
        tokens = []
        str_map = {}
        str_idx = 0

        # Replace strings with placeholders
        def save_str(m):
            nonlocal str_idx
            placeholder = f"__STR_{str_idx}__"
            str_map[placeholder] = m.group(0)
            str_idx += 1
            return placeholder

        # Match single or double quoted strings
        s = re.sub(r'("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')', save_str, expr_str)

        # Handle membership in intervals: expr  [a .. b] or expr dans [a .. b]
        m_int = re.search(r'(.+?)\s+(?:|∈|dans|in)\s+\[\s*(.+?)\s*\.\.\s*(.+?)\s*\]', s, re.IGNORECASE)
        if m_int:
            val = self._translate_expression(m_int.group(1).strip())
            low = self._translate_expression(m_int.group(2).strip())
            high = self._translate_expression(m_int.group(3).strip())
            replacement = f"({low} <= {val} <= {high})"
            s = s[:m_int.start()] + replacement + s[m_int.end():]

        # Handle membership in set: expr  {a, b, c}
        m_set = re.search(r'(.+?)\s+(?:|∈|dans|in)\s+\{\s*(.+?)\s*\}', s, re.IGNORECASE)
        if m_set:
            val = self._translate_expression(m_set.group(1).strip())
            items = [self._translate_expression(it.strip()) for it in m_set.group(2).split(',') if it.strip()]
            replacement = f"({val} in {{{', '.join(items)}}})"
            s = s[:m_set.start()] + replacement + s[m_set.end():]

        # Handle 2D index in expressions: M[i, j]
        s = re.sub(r'([a-zA-Z0-9_]+)\s*\[\s*(.+?)\s*,\s*(.+?)\s*\]', r'\1[\2, \3]', s)

        # Handle predefined function names (case-insensitive)
        fn_map = {
            'arrondi': 'Arrondi',
            'racinecarré': 'RacineCarré',
            'racinecarre': 'RacineCarré',
            'aléa': 'Aléa',
            'alea': 'Aléa',
            'ent': 'Ent',
            'abs': 'Abs',
            'ord': 'Ord',
            'chr': 'Chr',
            'long': 'Long',
            'pos': 'Pos',
            'convch': 'Convch',
            'estnum': 'Estnum',
            'valeur': 'Valeur',
            'sous_chaine': 'Sous_chaine',
            'effacer': 'Effacer',
            'majus': 'Majus',
            'fin_fichier': '_fin_fichier',
        }
        for fn_name, py_fn in fn_map.items():
            s = re.sub(rf'\b{fn_name}\s*\(', f'{py_fn}(', s, flags=re.IGNORECASE)

        # Handle Boolean literals
        s = re.sub(r'\bvrai\b', 'True', s, flags=re.IGNORECASE)
        s = re.sub(r'\bfaux\b', 'False', s, flags=re.IGNORECASE)

        # Handle arithmetic and logical operators
        s = re.sub(r'\bdiv\b', '//', s, flags=re.IGNORECASE)
        s = re.sub(r'\bmod\b', '%', s, flags=re.IGNORECASE)
        s = re.sub(r'\bet\b', 'and', s, flags=re.IGNORECASE)
        s = re.sub(r'\bou\b', 'or', s, flags=re.IGNORECASE)
        s = re.sub(r'\bnon\b', 'not', s, flags=re.IGNORECASE)
        s = re.sub(r'\bdans\b', 'in', s, flags=re.IGNORECASE)

        # Comparison operators
        s = s.replace('≠', '!=').replace('<>', '!=')
        s = s.replace('≤', '<=')
        s = s.replace('≥', '>=')
        s = s.replace('', ' in ').replace('∈', ' in ')

        # Handle equality '=' -> '==' (when not part of <=, >=, !=, ==)
        # Regex to match '=' that is not preceded or followed by '<', '>', '!', '='
        s = re.sub(r'(?<![<>!=])=(?![=])', '==', s)

        # Handle record dot access: E.champ -> E['champ']
        # Be careful not to replace decimal points like 3.14
        def replace_dot(m):
            obj = m.group(1)
            field = m.group(2)
            return f"{obj}['{field}']"

        s = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b', replace_dot, s)

        # Restore strings
        for placeholder, original in str_map.items():
            s = s.replace(placeholder, original)

        return s

    # -------------------------------------------------------------------------
    # Helper: Split arguments respecting nested parentheses and strings
    # -------------------------------------------------------------------------
    def _split_arguments(self, s):
        """Splits arguments by comma outside of parentheses and quotes."""
        args = []
        current = []
        depth = 0
        in_quote = None

        i = 0
        while i < len(s):
            ch = s[i]
            if in_quote:
                current.append(ch)
                if ch == in_quote:
                    in_quote = None
            elif ch in ('"', "'"):
                in_quote = ch
                current.append(ch)
            elif ch in ('(', '[', '{'):
                depth += 1
                current.append(ch)
            elif ch in (')', ']', '}'):
                depth -= 1
                current.append(ch)
            elif ch == ',' and depth == 0:
                args.append("".join(current).strip())
                current = []
            else:
                current.append(ch)
            i += 1

        if current:
            args.append("".join(current).strip())

        return args
