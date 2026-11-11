"""
Type and Object Declarations Handler.
"""

import re
from compiler.errors import MissingEndError, MissingTypeError

class TypeHandler:
    """Manages custom types (TDNT) and declared objects (TDO/TDOG)."""

    def __init__(self):
        self.custom_types = {}       # type_name -> dict(kind=..., ...)
        self.declared_objects = {}   # var_name -> type_str

    def reset(self):
        self.custom_types.clear()
        self.declared_objects.clear()

    def resolve_type(self, type_str: str) -> str:
        """Resolves type aliases recursively (like typedef in C), case-insensitively."""
        curr = type_str.strip()
        visited = set()
        while True:
            found = False
            for k, v in self.custom_types.items():
                if k.lower() == curr.lower() and v.get('kind') == 'alias':
                    if curr.lower() in visited:
                        break
                    visited.add(curr.lower())
                    curr = v.get('target_type', curr).strip()
                    found = True
                    break
            if not found:
                break
        return curr

    def parse_type_declarations(self, lines: list):
        """Parse custom types from TDNT lines (records, 1D/2D arrays, aliases)."""
        idx = 0
        while idx < len(lines):
            line_no, line = lines[idx]
            s = line.strip()
            idx += 1
            if not s or s.lower().startswith(('nouveau type', 'nom_type', 'objet', 'type / nature', 'type / definition', 'type / définition', '|', '---', '===')):
                continue
            if s.lower() in ('type', 'types', 'nouveaux types'):
                continue

            # Record: Nom = Enregistrement ... Fin [Enregistrement]
            m_rec = re.match(r'^([a-zA-Z0-9_\u00C0-\u017F]+)\s*(?:=|:|\s)\s*enregistrement\b', s, re.IGNORECASE)
            if m_rec:
                type_name = m_rec.group(1).strip()
                rec_line_no = line_no
                fields = {}
                closed = False
                while idx < len(lines):
                    l_no, l_text = lines[idx]
                    idx += 1
                    t_str = l_text.strip()
                    if not t_str:
                        continue
                    if t_str.upper() in ('FIN', 'FIN ENREGISTREMENT') or re.match(r'^fin[\s_]*(?:enregistrement)?$', t_str, re.IGNORECASE):
                        closed = True
                        break

                    # Check for direct Enregistrement in fields
                    if re.search(r'\benregistrement\b', t_str, re.IGNORECASE) and not re.match(r'^fin\b', t_str, re.IGNORECASE):
                        raise MissingTypeError(
                            f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type de champ dans '{type_name}'. Déclarez un type séparé dans le TDNT.",
                            line_num=l_no
                        )

                    parts = None
                    if ':' in t_str:
                        parts = t_str.split(':', 1)
                    elif '|' in t_str:
                        parts = t_str.split('|', 1)
                    elif re.search(r'\s{2,}|\t', t_str):
                        parts = re.split(r'\s{2,}|\t', t_str, 1)

                    if parts and len(parts) == 2:
                        fnames_part, ftype = parts[0].strip(), parts[1].strip()
                        for f in fnames_part.split(','):
                            f_clean = f.strip()
                            if f_clean:
                                fields[f_clean] = ftype
                if not closed:
                    raise MissingEndError(f"Enregistrement '{type_name}' ouvert à la ligne {rec_line_no} non fermé : 'Fin Enregistrement' manquant", line_num=rec_line_no)
                self.custom_types[type_name] = {'kind': 'enregistrement', 'fields': fields}
                continue

            # 2D Array: Nom = Tableau de N lignes * M colonnes Type
            m_arr2 = re.match(r'^([a-zA-Z0-9_\u00C0-\u017F]+)\s*(?:=|:|\s)\s*tableau\s+de\s+(\d+|[a-zA-Z0-9_\u00C0-\u017F]+)\s*lignes?\s*\*\s*(\d+|[a-zA-Z0-9_\u00C0-\u017F]+)\s*colonnes?\s+(.+)$', s, re.IGNORECASE)
            if m_arr2:
                t_name, rows, cols, elem_type = m_arr2.group(1).strip(), m_arr2.group(2).strip(), m_arr2.group(3).strip(), m_arr2.group(4).strip()
                if elem_type.lower() == 'enregistrement':
                    raise MissingTypeError(
                        f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type d'élément pour '{t_name}'. Déclarez un type d'enregistrement dans le TDNT.",
                        line_num=line_no
                    )
                self.custom_types[t_name] = {'kind': 'tableau_2d', 'rows': rows, 'cols': cols, 'elem_type': elem_type}
                continue

            # 1D Array: Nom = Tableau de N Type
            m_arr1 = re.match(r'^([a-zA-Z0-9_\u00C0-\u017F]+)\s*(?:=|:|\s)\s*tableau\s+de\s+(\d+|[a-zA-Z0-9_\u00C0-\u017F]+)\s+(.+)$', s, re.IGNORECASE)
            if m_arr1:
                t_name, size, elem_type = m_arr1.group(1).strip(), m_arr1.group(2).strip(), m_arr1.group(3).strip()
                if elem_type.lower() == 'enregistrement':
                    raise MissingTypeError(
                        f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type d'élément pour '{t_name}'. Déclarez un type d'enregistrement dans le TDNT.",
                        line_num=line_no
                    )
                self.custom_types[t_name] = {'kind': 'tableau_1d', 'size': size, 'elem_type': elem_type}
                continue

            # Type Alias / Typedef / File type: Nom = Type or Nom = Fichier ...
            m_alias = re.match(r'^([a-zA-Z0-9_\u00C0-\u017F]+)\s*(?:=|:)\s*(.+)$', s, re.IGNORECASE)
            if m_alias:
                t_name, target = m_alias.group(1).strip(), m_alias.group(2).strip()
                if target.lower() == 'enregistrement':
                    raise MissingTypeError(
                        f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type. Déclarez la structure complète de l'enregistrement avec ses champs (ex: {t_name} = Enregistrement ... Fin).",
                        line_num=line_no
                    )
                self.custom_types[t_name] = {'kind': 'alias', 'target_type': target}
                continue

    def parse_object_declarations(self, lines: list):
        """Parse TDO/TDOG lines (e.g. x, y, z : Entier or x, y | Entier)."""
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
                    r'^([a-zA-Z0-9_,\s\u00C0-\u017F]+?)\s+(Tableau\b.*|Enregistrement\b.*|Fichier\b.*|Entier\b.*|Réel\b.*|Reel\b.*|Booléen\b.*|Booleen\b.*|Caractère\b.*|Caractere\b.*|Chaîne\b.*|Chaine\b.*|[a-zA-Z0-9_\u00C0-\u017F]+)$',
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
                if t_low in ('procedure', 'procédure', 'fonction', 'module', '/'):
                    continue
                names = [n.strip() for n in names_part.split(',') if n.strip()]
                for name in names:
                    clean_name = re.sub(r'[^a-zA-Z0-9_\u00C0-\u017F]', '', name)
                    if clean_name and clean_name != '/':
                        self.declared_objects[clean_name] = type_part

    def default_value_for_type(self, elem_type: str) -> str:
        """Returns standard Python literal default for algorithmic type."""
        resolved = self.resolve_type(elem_type)
        if resolved in self.custom_types:
            c_def = self.custom_types[resolved]
            if c_def.get('kind') == 'enregistrement':
                return f"_creer_{resolved}()"
            elif c_def.get('kind') == 'tableau_1d':
                el_t = self.resolve_type(c_def.get('elem_type', 'entier'))
                init_val = self.default_value_for_type(el_t)
                dtype = ", dtype=object" if self.is_string_type(el_t) or el_t in self.custom_types else ""
                return f"array([{init_val}] * ({c_def['size']}){dtype})"
            elif c_def.get('kind') == 'tableau_2d':
                el_t = self.resolve_type(c_def.get('elem_type', 'entier'))
                init_val = self.default_value_for_type(el_t)
                dtype = ", dtype=object" if self.is_string_type(el_t) or el_t in self.custom_types else ""
                return f"array([[{init_val}] * ({c_def['cols']})] * ({c_def['rows']}){dtype})"

        t = resolved.lower()
        if 'fichier' in t:
            return "None"
        elif 'entier' in t or 'int' in t:
            return "0"
        elif 'reel' in t or 'réel' in t or 'float' in t:
            return "0.0"
        elif 'bool' in t:
            return "False"
        elif 'caractere' in t or 'caractère' in t or 'char' in t or 'chaine' in t or 'chaîne' in t or 'str' in t:
            return "''"
        return "0"

    def is_string_type(self, elem_type: str) -> bool:
        """Returns True if the type represents a string (Chaine)."""
        resolved = self.resolve_type(elem_type)
        t = resolved.lower()
        return 'chaine' in t or 'chaîne' in t or 'str' in t

    def generate_object_initializations(self, objects_dict: dict = None) -> list:
        """Generates Python initialization code for declared objects (NumPy arrays, dicts, scalars)."""
        if objects_dict is None:
            objects_dict = self.declared_objects
        lines = []
        for var_name, type_str in objects_dict.items():
            t_lower = type_str.lower().strip()
            resolved_type = self.resolve_type(type_str)

            # Enregistrement cannot be used directly as a type
            if t_lower == 'enregistrement':
                raise MissingTypeError(
                    f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type pour l'objet '{var_name}'. "
                    f"Déclarez un nouveau type dans le Tableau de déclaration des nouveaux types (TDNT) "
                    f"(ex: NomType = Enregistrement ... Fin) et utilisez ce nom de type."
                )

            # Check if resolved type matches custom type from TDNT
            if resolved_type in self.custom_types:
                t_def = self.custom_types[resolved_type]
                if t_def['kind'] == 'enregistrement':
                    lines.append(f"{var_name} = _creer_{resolved_type}()")
                    continue
                elif t_def['kind'] == 'tableau_1d':
                    elem_t = self.resolve_type(t_def['elem_type'])
                    if elem_t in self.custom_types and self.custom_types[elem_t]['kind'] == 'enregistrement':
                        lines.append(f"{var_name} = array([_creer_{elem_t}() for _ in range({t_def['size']})], dtype=object)")
                    else:
                        init_val = self.default_value_for_type(elem_t)
                        if self.is_string_type(elem_t):
                            lines.append(f"{var_name} = array([{init_val}] * ({t_def['size']}), dtype=object)")
                        else:
                            lines.append(f"{var_name} = array([{init_val}] * ({t_def['size']}))")
                    continue
                elif t_def['kind'] == 'tableau_2d':
                    elem_t = self.resolve_type(t_def['elem_type'])
                    init_val = self.default_value_for_type(elem_t)
                    if self.is_string_type(elem_t):
                        lines.append(f"{var_name} = array([[{init_val}] * ({t_def['cols']})] * ({t_def['rows']}), dtype=object)")
                    else:
                        lines.append(f"{var_name} = array([[{init_val}] * ({t_def['cols']})] * ({t_def['rows']}))")
                    continue

            # Tableau 2D inline: Tableau de N lignes * M colonnes Type
            m_arr2 = re.match(r'tableau\s+de\s+(.+?)\s*lignes?\s*\*\s*(.+?)\s*colonnes?\s+(.+)', t_lower)
            if m_arr2:
                rows, cols, elem_type = m_arr2.group(1).strip(), m_arr2.group(2).strip(), m_arr2.group(3).strip()
                if elem_type.lower() == 'enregistrement':
                    raise MissingTypeError(
                        f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type d'élément pour '{var_name}'. Déclarez un type d'enregistrement dans le TDNT."
                    )
                elem_t = self.resolve_type(elem_type)
                init_val = self.default_value_for_type(elem_t)
                if self.is_string_type(elem_t):
                    lines.append(f"{var_name} = array([[{init_val}] * ({cols})] * ({rows}), dtype=object)")
                else:
                    lines.append(f"{var_name} = array([[{init_val}] * ({cols})] * ({rows}))")
                continue

            # Tableau 1D inline: Tableau de N Type
            m_arr1 = re.match(r'tableau\s+de\s+(.+?)\s+([a-zA-Z0-9_éèêà\u00C0-\u017F]+.*)', t_lower)
            if m_arr1:
                size, elem_type = m_arr1.group(1).strip(), m_arr1.group(2).strip()
                if elem_type.lower() == 'enregistrement':
                    raise MissingTypeError(
                        f"Le mot-clé 'Enregistrement' ne peut pas être utilisé directement comme type d'élément pour '{var_name}'. Déclarez un type d'enregistrement dans le TDNT."
                    )
                elem_t = self.resolve_type(elem_type)
                if elem_t in self.custom_types and self.custom_types[elem_t]['kind'] == 'enregistrement':
                    lines.append(f"{var_name} = array([_creer_{elem_t}() for _ in range({size})], dtype=object)")
                else:
                    init_val = self.default_value_for_type(elem_t)
                    if self.is_string_type(elem_t):
                        lines.append(f"{var_name} = array([{init_val}] * ({size}), dtype=object)")
                    else:
                        lines.append(f"{var_name} = array([{init_val}] * ({size}))")
                continue

            # Simple scalar types (Entier, Réel, Booléen, Chaîne, etc.)
            init_val = self.default_value_for_type(resolved_type)
            lines.append(f"{var_name} = {init_val}")

        return lines

    def generate_record_constructors(self) -> list:
        """Generates helper functions _creer_Nom(...) for custom records."""
        py_lines = []
        for t_name, t_def in self.custom_types.items():
            if t_def['kind'] == 'enregistrement':
                param_defs = []
                dict_entries = []
                for f, ftype in t_def['fields'].items():
                    def_val = self.default_value_for_type(ftype)
                    param_defs.append(f"{f}={def_val}")
                    dict_entries.append(f"'{f}': {f}")
                params_str = ", ".join(param_defs)
                entries_str = ", ".join(dict_entries)
                py_lines.append(f"def _creer_{t_name}({params_str}):")
                py_lines.append(f"    return Enregistrement({{{entries_str}}})")
                py_lines.append("")
        return py_lines
