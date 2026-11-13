"""
Algorithmic Code Error Validator.
Isolates and enforces algorithmic compilation requirements:
1. END is mandatory:
   - The main algorithm MUST end with 'FIN' or 'END'.
   - All subprograms (Fonctions & Procédures) MUST end with 'FIN' or 'END'.
   - Block structures (Si, Pour, Tant que, Selon, Répéter, Enregistrement) must be closed.
2. Tables are mandatory:
   - Every subprogram MUST have a Tableau de déclaration des objets locaux (TDOL) after it.
   - The main algorithm MUST have a Tableau de déclaration des objets globaux (TDOG) under it.
3. Types are mandatory:
   - All variables used in the main algorithm must be declared with a type in TDOG.
   - All variables used in subprograms must be declared with a type (parameters, TDOL, or TDOG).
   - Any function or procedure used in another function/procedure or the main algorithm must be declared.
   - Subprogram parameters must have explicit types (e.g., param: Type).
   - Functions must have an explicit return type (e.g., Fonction Nom(...) : Type).
   - Declared objects in TDOG/TDOL cannot be left without a type.
"""

import re
from compiler.errors import (
    CompileError,
    MissingEndError,
    MissingTypeError,
    InvalidStructureError,
)

# Standard builtin functions and constants in algorithmic language
BUILTIN_FUNCTIONS = {
    'arrondi', 'racinecarré', 'racinecarre', 'aléa', 'alea', 'ent', 'abs',
    'ord', 'chr', 'long', 'pos', 'convch', 'estnum', 'valeur', 'sous_chaine',
    'effacer', 'majus', 'vrai', 'faux', 'true', 'false', 'pi', 'null', 'none',
    '_lire_valeur', '_fin_fichier',
    'ouvrir', 'fermer', 'fin_fichier', 'finfichier', 'lire_ligne', 'lireligne'
}

# Algorithmic syntax keywords
KEYWORDS = {
    'si', 'alors', 'sinon', 'finsi', 'fin', 'debut', 'début', 'pour', 'de',
    'a', 'à', 'faire', 'finpour', 'tant', 'que', 'tantque', 'fintantque',
    'fintanqtue', 'repeter', 'répéter', 'jusqu', 'jusqua', "jusqu'a", "jusqu'à",
    'selon', 'finselon', 'retourner', 'lire', 'ecrire', 'ecrire_nl', 'écrire',
    'écrire_nl', 'algorithme', 'fonction', 'procedure', 'procédure',
    'enregistrement', 'tableau', 'div', 'mod', 'et', 'ou', 'non', 'in',
    'dans', 'pas', 'end', 'begin', 'true', 'false', 'match', 'case',
    'ouvrir', 'fermer', 'lire_ligne', 'fin_fichier', 'finfichier'
}

# Known standard primitive and composite type keywords
STANDARD_TYPES = {
    'entier', 'reel', 'réel', 'booleen', 'booléen', 'caractere', 'caractère',
    'chaine', 'chaîne', 'tableau', 'fichier', 'texte', 'int', 'float',
    'bool', 'str', 'char', 'void'
}


class AlgoValidator:
    """
    Validator component that isolates algorithmic validation rules.
    Verifies mandatory 'FIN' (END) presence, mandatory tables (TDOL/TDOG),
    and mandatory type declarations for variables and subprograms.
    """

    def __init__(self, strict_types: bool = True):
        self.strict_types = strict_types

    def validate(
        self,
        raw_lines: list,
        sections: dict,
        declared_objects: dict,
        custom_types: dict,
        subprogram_meta: dict
    ):
        """
        Runs full validation on parsed algorithmic sections and declared objects.
        Raises MissingEndError or MissingTypeError if constraints are violated.
        """
        # 1. Structural END validation (Mandatory)
        self.validate_end_structure(raw_lines, sections)

        # 2. Subprogram headers (return types & parameter types)
        self.validate_subprogram_headers(sections.get('subprograms', []))

        # 3. TDNT rules & Enregistrement usage
        self.validate_tdnt_rules(sections)
        self.validate_no_direct_enregistrement(sections)

        # 4. Mandatory tables presence (TDOL after subprograms, TDOG under main)
        if self.strict_types:
            self.validate_tables_presence(raw_lines, sections)

        # 5. TDO/TDOG/TDOL syntax: objects cannot be declared without a type
        self.validate_tdo_syntax(sections.get('objects', []))

        # 6. Subprogram declarations validation (functions/procedures called must be declared)
        if self.strict_types:
            self.validate_subprogram_declarations(sections, subprogram_meta)

        # 7. Mandatory types verification (Variables used must have declared types)
        if self.strict_types:
            self.validate_mandatory_types(
                sections,
                declared_objects,
                custom_types,
                subprogram_meta
            )

    def validate_end_structure(self, raw_lines: list, sections: dict):
        """
        Validates that END ('FIN' / 'END') is present and mandatory.
        - The algorithm MUST have a closing FIN/END.
        - Every subprogram MUST have a closing FIN/END.
        - All blocks (Si, Pour, Tant que, Selon, Répéter) must have their closing END.
        """
        # First validate block-level closures inside subprograms and main
        for subprog in sections.get('subprograms', []):
            self.validate_block_closures(subprog.get('lines', []))

        self.validate_block_closures(sections.get('main', []))

        # Ensure main algorithm has mandatory FIN / END
        has_main_fin = sections.get('has_main_fin', False)
        if not has_main_fin:
            main_start = sections.get('main_start_line')
            if not main_start:
                if sections.get('header'):
                    main_start = sections['header'][0][0]
                elif sections.get('main'):
                    main_start = sections['main'][0][0]
                else:
                    main_start = len(raw_lines) or 1
            raise MissingEndError(
                "Mot-clé 'FIN' manquant : la fin de l'algorithme est obligatoire",
                line_num=main_start
            )

        # Ensure every subprogram has mandatory FIN / END
        for subprog in sections.get('subprograms', []):
            if not subprog.get('has_fin', False):
                sub_name = subprog.get('name', 'Sous-programme')
                sub_line = subprog.get('start_line', 1)
                raise MissingEndError(
                    f"Sous-programme '{sub_name}' ouvert à la ligne {sub_line} non fermé : 'FIN' manquant",
                    line_num=sub_line
                )

    def validate_tables_presence(self, raw_lines: list, sections: dict):
        """
        Validates mandatory presence and placement of objects tables:
        1. Every subprogram MUST have a 'Tableau de déclaration des objets locaux' (TDOL) after it.
        2. The main algorithm MUST have a 'Tableau de déclaration des objets globaux' (TDOG) under it.
        """
        # 1. Validate subprogram TDOL tables
        for subprog in sections.get('subprograms', []):
            if not subprog.get('has_tdol', False):
                sub_name = subprog.get('name', 'Sous-programme')
                sub_line = subprog.get('start_line', 1)
                raise MissingTypeError(
                    f"Tableau de déclaration des objets locaux (TDOL) manquant pour le sous-programme '{sub_name}' (doit être placé après le sous-programme)",
                    line_num=sub_line
                )

        # 2. Validate main algorithm TDOG table under main
        has_main_debut = sections.get('has_main_debut', False)
        has_main_fin = sections.get('has_main_fin', False)
        main_lines = sections.get('main', [])
        has_header = bool(sections.get('header', []))

        # If there is a main program body or header
        if has_main_debut or has_main_fin or main_lines or has_header:
            if not sections.get('has_tdog_under_main', False):
                main_start = sections.get('main_start_line')
                if not main_start:
                    if sections.get('header'):
                        main_start = sections['header'][0][0]
                    elif main_lines:
                        main_start = main_lines[0][0]
                    else:
                        main_start = len(raw_lines) or 1
                raise MissingTypeError(
                    "Tableau de déclaration des objets globaux (TDOG) manquant pour l'algorithme principal (doit être placé sous l'algorithme)",
                    line_num=main_start
                )

        # 3. Validate TDNT (at most one TDNT table in the program)
        self.validate_tdnt_rules(sections)

    def validate_block_closures(self, line_tuples: list):
        """
        Validates that control flow blocks (Si, Pour, Tant que, Selon, Répéter)
        within a sequence of lines have their mandatory closing statements.
        """
        stack = []

        for line_no, raw_line in line_tuples:
            s = raw_line.strip()
            if not s or s.startswith("#"):
                continue

            # Check block openings
            if re.match(r'^si\s+.+?\s+alors$', s, re.IGNORECASE):
                stack.append(('Si', line_no))
                continue
            if re.match(r'^pour\s+[a-zA-Z0-9_\u00C0-\u017F]+\s+de\s+.+?\s+(?:à|a)\s+.+?\s+faire$', s, re.IGNORECASE):
                stack.append(('Pour', line_no))
                continue
            if re.match(r'^(?:tant\s*que|tantque)(?:\s+|\s*(?=\()).+?(?:\s+|(?<=\)))faire$', s, re.IGNORECASE):
                stack.append(('Tant que', line_no))
                continue
            if re.match(r'^selon\s+.+$', s, re.IGNORECASE):
                stack.append(('Selon', line_no))
                continue
            if re.match(r'^(?:répéter|repeter)\b', s, re.IGNORECASE):
                stack.append(('Répéter', line_no))
                continue

            # Check block closings
            if re.match(r'^(?:fin[\s_]*si|finsi|end[\s_]*if)$', s, re.IGNORECASE):
                self._pop_matching_block(stack, 'Si')
                continue
            if re.match(r'^(?:fin[\s_]*pour|finpour|end[\s_]*for)$', s, re.IGNORECASE):
                self._pop_matching_block(stack, 'Pour')
                continue
            if re.match(r'^(?:fin[\s_]*tant[\s_]*que|fintantque|fintanqtue|end[\s_]*while)$', s, re.IGNORECASE):
                self._pop_matching_block(stack, 'Tant que')
                continue
            if re.match(r'^(?:fin[\s_]*selon|finselon|end[\s_]*select|end[\s_]*match)$', s, re.IGNORECASE):
                self._pop_matching_block(stack, 'Selon')
                continue
            if re.match(r'^(?:jusqu[\'’\s]?(?:à|a|e)?\b|until\b)', s, re.IGNORECASE):
                self._pop_matching_block(stack, 'Répéter')
                continue

        if stack:
            block_name, start_line = stack[-1]
            end_names = {
                'Si': "'Fin Si'",
                'Pour': "'Fin Pour'",
                'Tant que': "'Fin Tant que'",
                'Selon': "'Fin Selon'",
                'Répéter': "'Jusqu\'à'",
            }
            end_desc = end_names.get(block_name, "délimiteur de fin")
            raise MissingEndError(
                f"Bloc '{block_name}' ouvert à la ligne {start_line} non fermé : {end_desc} manquant",
                line_num=start_line
            )

    @staticmethod
    def _pop_matching_block(stack: list, expected_name: str):
        """Pops the most recent matching block from the stack."""
        for i in range(len(stack) - 1, -1, -1):
            if stack[i][0] == expected_name:
                stack.pop(i)
                return

    def validate_subprogram_headers(self, subprograms: list):
        """
        Validates that all subprogram parameters have types and functions have return types.
        """
        for subprog in subprograms:
            header = subprog.get('header', '')
            line_no = subprog.get('start_line', 1)
            name = subprog.get('name', 'sous-programme')
            kind = subprog.get('kind', 'procedure')

            # Match: (fonction|procedure) Name (params) [: ReturnType]
            m = re.match(
                r'^(?:fonction|procédure|procedure)\s+([a-zA-Z0-9_\u00C0-\u017F]+)\s*(?:\((.*?)\))?(?:\s*:\s*([a-zA-Z0-9_\u00C0-\u017F]+))?',
                header,
                re.IGNORECASE
            )
            if not m:
                continue

            params_str = m.group(2) or ""
            ret_type = m.group(3)

            # Functions must have an explicit return type
            if kind == 'fonction':
                if not ret_type or not ret_type.strip():
                    raise MissingTypeError(
                        f"Type de retour obligatoire pour la fonction '{name}'",
                        line_num=line_no
                    )
                if ret_type.strip().lower() == 'enregistrement':
                    raise MissingTypeError(
                        f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type de retour pour la fonction '{name}'. "
                        f"Déclarez un nouveau type dans le Tableau de déclaration des nouveaux types (TDNT).",
                        line_num=line_no
                    )

            # Subprogram parameters must have explicit types
            if params_str.strip():
                for p in params_str.split(','):
                    p = p.strip()
                    if not p:
                        continue
                    if ':' not in p:
                        pname = p.lstrip('@').strip()
                        raise MissingTypeError(
                            f"Type manquant pour le paramètre '{pname}' du sous-programme '{name}'",
                            line_num=line_no
                        )
                    pname, ptype = p.split(':', 1)
                    if not ptype.strip():
                        clean_pname = pname.lstrip('@').strip()
                        raise MissingTypeError(
                            f"Type manquant pour le paramètre '{clean_pname}' du sous-programme '{name}'",
                            line_num=line_no
                        )
                    if ptype.strip().lower() == 'enregistrement':
                        clean_pname = pname.lstrip('@').strip()
                        raise MissingTypeError(
                            f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type pour le paramètre '{clean_pname}' du sous-programme '{name}'. "
                            f"Déclarez un nouveau type dans le Tableau de déclaration des nouveaux types (TDNT).",
                            line_num=line_no
                        )

    def validate_tdnt_rules(self, sections: dict):
        """
        Validates TDNT (Tableau de déclaration des nouveaux types):
        - There can be at most one TDNT in the entire program.
        """
        tdnt_count = sections.get('tdnt_count', 0)
        if tdnt_count > 1:
            lines = sections.get('tdnt_start_lines', [1, 1])
            err_line = lines[1] if len(lines) > 1 else 1
            raise InvalidStructureError(
                f"Il ne peut y avoir qu'un seul Tableau de déclaration des nouveaux types (TDNT) dans tout le programme (trouvé {tdnt_count})",
                line_num=err_line
            )

    def validate_no_direct_enregistrement(self, sections: dict):
        """
        Ensures 'Enregistrement' is never used directly as a variable type in TDOG or TDOL.
        """
        # 1. Check TDOG
        for line_no, line in sections.get('objects', []):
            self._check_line_no_direct_enregistrement(line, line_no, "TDOG")

        # 2. Check each subprogram TDOL
        for sp in sections.get('subprograms', []):
            sp_name = sp.get('name', 'sous-programme')
            for line_no, line in sp.get('tdo', []):
                self._check_line_no_direct_enregistrement(line, line_no, f"TDOL de '{sp_name}'")

    def _check_line_no_direct_enregistrement(self, line: str, line_no: int, context: str):
        s = line.strip()
        if not s or s.lower().startswith(('objet', 'type', 'nom_objet', '---', '===')):
            return
        parts = None
        if ':' in s:
            parts = s.split(':', 1)
        elif '|' in s:
            parts = s.split('|', 1)
        else:
            m = re.match(
                r'^([a-zA-Z0-9_,\s\u00C0-\u017F]+?)\s+(Tableau\b.*|Enregistrement\b.*|Fichier\b.*|Entier\b.*|Réel\b.*|Reel\b.*|Booléen\b.*|Booleen\b.*|Caractère\b.*|Caractere\b.*|Chaîne\b.*|Chaine\b.*|Procédure\b.*|Procedure\b.*|Fonction\b.*|[a-zA-Z0-9_\u00C0-\u017F]+)$',
                s,
                re.IGNORECASE
            )
            if m:
                parts = [m.group(1), m.group(2)]
            elif re.search(r'\s{2,}|\t', s):
                parts = re.split(r'\s{2,}|\t', s, 1)

        if parts and len(parts) == 2:
            obj_name = parts[0].strip()
            type_str = parts[1].strip()
            if type_str.lower() == 'enregistrement':
                raise MissingTypeError(
                    f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type pour l'objet '{obj_name}' dans le {context}. "
                    f"Vous devez définir un nouveau type dans le Tableau de déclaration des nouveaux types (TDNT) "
                    f"(ex: NomType = Enregistrement ... Fin) et utiliser ce nom de type.",
                    line_num=line_no
                )

    def validate_tdo_syntax(self, tdo_lines: list):
        """
        Validates that every object declared in TDO/TDOG has a specified type.
        Objects cannot be listed without a type.
        """
        for line_no, line in tdo_lines:
            s = line.strip()
            if not s or re.match(r'^[\*\-=\/ ]+$', s):
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
                words = s.split()
                if len(words) == 1:
                    clean_w = re.sub(r'[^a-zA-Z0-9_\u00C0-\u017F]', '', words[0])
                    if clean_w and clean_w != '/':
                        raise MissingTypeError(
                            f"Type manquant pour l'objet '{clean_w}' dans la déclaration des objets",
                            line_num=line_no
                        )
                elif len(words) >= 2:
                    parts = [words[0], " ".join(words[1:])]

            if parts and len(parts) == 2:
                name = parts[0].strip()
                type_part = parts[1].strip()
                if not type_part:
                    raise MissingTypeError(
                        f"Type manquant pour l'objet '{name}' dans la déclaration des objets",
                        line_num=line_no
                    )
                if type_part.lower() == 'enregistrement':
                    raise MissingTypeError(
                        f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type pour l'objet '{name}'. "
                        f"Vous devez définir un nouveau type dans le Tableau de déclaration des nouveaux types (TDNT) "
                        f"(ex: NomType = Enregistrement ... Fin) et utiliser ce nom de type.",
                        line_num=line_no
                    )

    def validate_subprogram_declarations(
        self,
        sections: dict,
        subprogram_meta: dict
    ):
        """
        Validates that:
        1. Any subprogram called by the main program is declared in TDOG (as Fonction or Procédure).
        2. Any subprogram called by another subprogram is declared in that subprogram's TDOL (or TDOG).
        """
        known_subprograms = {sp['name'].lower(): sp for sp in sections.get('subprograms', [])}
        for name, meta in subprogram_meta.items():
            if name.lower() not in known_subprograms:
                known_subprograms[name.lower()] = {'name': name, 'kind': meta.get('kind', 'procedure')}

        # Parse TDOG declarations
        _, tdog_subprogs = self.extract_table_declarations(sections.get('objects', []))

        # 1. Main algorithm subprogram calls
        main_calls = self.extract_called_subprograms(sections.get('main', []), set(known_subprograms.keys()))
        for called_name, line_no in main_calls:
            called_low = called_name.lower()
            if called_low not in tdog_subprogs:
                sub_info = known_subprograms.get(called_low, {})
                kind = sub_info.get('kind', 'procedure')
                nature = "Procédure" if 'proc' in kind.lower() else "Fonction"
                raise MissingTypeError(
                    f"Le sous-programme '{called_name}' appelé à la ligne {line_no} doit être déclaré dans le Tableau de déclaration des objets globaux (TDOG) avec la nature '{nature}'",
                    line_num=line_no
                )

        # 2. Subprogram calls inside other subprograms
        for subprog in sections.get('subprograms', []):
            caller_name = subprog['name']
            caller_low = caller_name.lower()

            # Parse TDOL for this caller subprogram
            _, tdol_subprogs = self.extract_table_declarations(subprog.get('tdo', []))
            allowed_subprogs = set(tdol_subprogs.keys()) | set(tdog_subprogs.keys()) | {caller_low}

            sub_calls = self.extract_called_subprograms(subprog.get('lines', []), set(known_subprograms.keys()))
            for called_name, line_no in sub_calls:
                called_low = called_name.lower()
                if called_low not in allowed_subprogs:
                    sub_info = known_subprograms.get(called_low, {})
                    kind = sub_info.get('kind', 'procedure')
                    nature = "Procédure" if 'proc' in kind.lower() else "Fonction"
                    raise MissingTypeError(
                        f"Le sous-programme '{called_name}' appelé dans '{caller_name}' à la ligne {line_no} doit être déclaré dans son TDOL (nature: '{nature}')",
                        line_num=line_no
                    )

    def extract_called_subprograms(
        self,
        line_tuples: list,
        known_subprograms: set
    ) -> list:
        """
        Extracts subprogram invocations as list of (called_name, line_no).
        """
        calls = []
        for line_no, raw_line in line_tuples:
            s = raw_line.strip()
            if not s or s.startswith("#"):
                continue
            if re.match(r'^[\*\-=\/ ]{3,}$', s):
                continue
            if re.match(r'^(?:fonction|procédure|procedure)\b', s, re.IGNORECASE):
                continue

            # Remove string literals
            clean = re.sub(r'("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')', ' ', s)

            # Check: identifier followed by (
            for m in re.finditer(r'\b([a-zA-Z_\u00C0-\u017F][a-zA-Z0-9_\u00C0-\u017F]*)\s*\(', clean):
                ident = m.group(1)
                low = ident.lower()
                if low in KEYWORDS or low in BUILTIN_FUNCTIONS:
                    continue
                if low in known_subprograms:
                    calls.append((ident, line_no))

            # Check: standalone procedure call statement e.g. "proc_name"
            m_single = re.match(r'^([a-zA-Z_\u00C0-\u017F][a-zA-Z0-9_\u00C0-\u017F]*)$', clean.strip())
            if m_single:
                ident = m_single.group(1)
                low = ident.lower()
                if low in known_subprograms and (ident, line_no) not in calls:
                    calls.append((ident, line_no))

        return calls

    def validate_mandatory_types(
        self,
        sections: dict,
        declared_objects: dict,
        custom_types: dict,
        subprogram_meta: dict
    ):
        """
        Ensures all variables used in algorithmic code have declared types.
        Variables cannot pass without types!
        """
        known_subprograms = set(subprogram_meta.keys())
        for sp in sections.get('subprograms', []):
            known_subprograms.add(sp['name'].lower())
        for obj_name, obj_type in declared_objects.items():
            if obj_type.lower() in ('procedure', 'procédure', 'fonction'):
                known_subprograms.add(obj_name.lower())

        custom_type_names = {t.lower() for t in custom_types.keys()}

        # 1. Main algorithm variable validation
        main_lines = sections.get('main', [])
        main_vars = self.extract_variables_from_lines(
            main_lines,
            known_subprograms,
            custom_type_names
        )

        tdog_vars, _ = self.extract_table_declarations(sections.get('objects', []))
        declared_lower = {k.lower(): k for k in declared_objects.keys()}
        declared_lower.update(tdog_vars)

        if main_vars and not declared_lower:
            first_var, first_line = main_vars[0]
            raise MissingTypeError(
                f"Objet '{first_var}' non déclaré : les types sont obligatoires (section 'Déclaration des objets' manquante)",
                line_num=first_line
            )

        for var_name, line_no in main_vars:
            if var_name.lower() not in declared_lower:
                raise MissingTypeError(
                    f"Objet '{var_name}' non déclaré : la déclaration de type est obligatoire dans le TDOG",
                    line_num=line_no
                )

        # 2. Subprograms variable validation
        for subprog in sections.get('subprograms', []):
            sub_name = subprog['name']
            sub_meta = subprogram_meta.get(sub_name, {})
            sub_params = {p.lower() for p in sub_meta.get('all_params', [])}

            # Parse TDOL attached to this subprogram
            tdol_vars, tdol_subprogs = self.extract_table_declarations(subprog.get('tdo', []))
            tdol_lower = set(tdol_vars.keys())

            # Allowed identifiers for this subprogram:
            # parameters, local TDOL objects, global declared objects, and function's own name
            allowed_vars = sub_params | tdol_lower | set(declared_lower.keys()) | {sub_name.lower()}

            sub_vars = self.extract_variables_from_lines(
                subprog.get('lines', []),
                known_subprograms,
                custom_type_names
            )

            for var_name, line_no in sub_vars:
                if var_name.lower() not in allowed_vars:
                    raise MissingTypeError(
                        f"Objet '{var_name}' dans le sous-programme '{sub_name}' non déclaré : déclaration de type obligatoire (paramètres ou TDOL)",
                        line_num=line_no
                    )

    def extract_variables_from_lines(
        self,
        line_tuples: list,
        known_subprograms: set,
        custom_types: set
    ) -> list:
        """
        Extracts all variable occurrences as (var_name, line_no) from code lines.
        Excludes keywords, builtin functions, string literals, numbers, and record field names.
        """
        variables = []
        for line_no, raw_line in line_tuples:
            s = raw_line.strip()
            if not s or s.startswith("#"):
                continue
            # Border lines
            if re.match(r'^[\*\-=\/ ]{3,}$', s):
                continue
            # Header lines
            if re.match(r'^(?:fonction|procédure|procedure|algorithme)\b', s, re.IGNORECASE):
                continue

            extracted = self.extract_variables_from_text(
                s,
                line_no,
                known_subprograms,
                custom_types
            )
            variables.extend(extracted)

        return variables

    def extract_variables_from_text(
        self,
        text: str,
        line_no: int,
        known_subprograms: set,
        custom_types: set
    ) -> list:
        """
        Extracts variable identifiers from a single statement or expression string.
        """
        # Remove comments from line
        if "#" in text:
            text = text.split("#", 1)[0]

        # Remove string literals
        clean_text = re.sub(r'("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')', ' ', text)

        # Normalize dot field access so that 'E . champ' becomes 'E.champ'
        clean_text = re.sub(r'\.\s+([a-zA-Z0-9_\u00C0-\u017F])', r'.\1', clean_text)

        # Find all identifiers NOT preceded by a dot
        pattern = r'(?<!\.)\b([a-zA-Z_\u00C0-\u017F][a-zA-Z0-9_\u00C0-\u017F]*)\b'

        results = []
        for match in re.finditer(pattern, clean_text):
            ident = match.group(1)
            low = ident.lower()

            if low in KEYWORDS:
                continue
            if low in BUILTIN_FUNCTIONS:
                continue
            if low in STANDARD_TYPES:
                continue
            if low in known_subprograms:
                continue
            if low in custom_types:
                continue

            results.append((ident, line_no))

        return results

    @staticmethod
    def extract_table_declarations(lines: list) -> tuple:
        """
        Parses declaration lines from TDOG or TDOL.
        Returns:
            (variables_dict, subprograms_dict)
            where variables_dict maps name.lower() -> type_part
            and subprograms_dict maps name.lower() -> 'procedure' | 'fonction'
        """
        variables = {}
        subprograms = {}

        for line_no, line in lines:
            s = line.strip()
            if not s or re.match(r'^[\*\-=\/ ]+$', s):
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
                    r'^([a-zA-Z0-9_,\s\u00C0-\u017F]+?)\s+(Tableau\b.*|Enregistrement\b.*|Fichier\b.*|Entier\b.*|Réel\b.*|Reel\b.*|Booléen\b.*|Booleen\b.*|Caractère\b.*|Caractere\b.*|Chaîne\b.*|Chaine\b.*|Procédure\b.*|Procedure\b.*|Fonction\b.*|[a-zA-Z0-9_\u00C0-\u017F]+)$',
                    s,
                    re.IGNORECASE
                )
                if m:
                    parts = [m.group(1), m.group(2)]
                elif re.search(r'\s{2,}|\t', s):
                    parts = re.split(r'\s{2,}|\t', s, 1)

            if parts and len(parts) == 2:
                names_part, type_part = parts[0].strip(), parts[1].strip()
                t_low = type_part.lower()
                if t_low in ('/', 'module'):
                    continue
                names = [n.strip() for n in names_part.split(',') if n.strip()]
                for name in names:
                    clean_name = re.sub(r'[^a-zA-Z0-9_\u00C0-\u017F]', '', name)
                    if clean_name and clean_name != '/':
                        if t_low.startswith(('procedure', 'procédure', 'fonction')):
                            subprograms[clean_name.lower()] = t_low
                        else:
                            variables[clean_name.lower()] = type_part

        return variables, subprograms

    @staticmethod
    def extract_objects_from_lines(lines: list) -> dict:
        """Backward-compatible helper returning variables dict."""
        variables, _ = AlgoValidator.extract_table_declarations(lines)
        return variables
