"""
Type and Object Declarations Handler for the Tunisian Algorithmic Convention.
Complies with 'Convention Algorithmique 2024.pdf' and 'Implémention 2024-2025.pdf'.
"""

import re

class TypeHandler:
    """Manages custom types (TDNT) and declared objects (TDO/TDOG)."""

    def __init__(self):
        self.custom_types = {}       # type_name -> dict(kind=..., ...)
        self.declared_objects = {}   # var_name -> type_str

    def reset(self):
        self.custom_types.clear()
        self.declared_objects.clear()

    def parse_type_declarations(self, lines: list):
        """Parse custom types from TDNT lines (records, 1D/2D arrays)."""
        idx = 0
        while idx < len(lines):
            line_no, line = lines[idx]
            s = line.strip()
            idx += 1
            if not s or s.lower().startswith(('nouveau type', 'nom_type', 'objet', 'type / nature', '|')):
                continue

            # Record: Nom = Enregistrement ... Fin [Enregistrement]
            m_rec = re.match(r'^([a-zA-Z0-9_]+)\s*=\s*enregistrement', s, re.IGNORECASE)
            if m_rec:
                type_name = m_rec.group(1)
                fields = {}
                while idx < len(lines):
                    l_no, l_text = lines[idx]
                    idx += 1
                    t_str = l_text.strip()
                    if t_str.upper() in ('FIN', 'FIN ENREGISTREMENT') or re.match(r'^fin\s*(?:enregistrement)?$', t_str, re.IGNORECASE):
                        break
                    if ':' in t_str:
                        fname, ftype = t_str.split(':', 1)
                        for f in fname.split(','):
                            f_clean = f.strip()
                            if f_clean:
                                fields[f_clean] = ftype.strip()
                self.custom_types[type_name] = {'kind': 'enregistrement', 'fields': fields}
                continue

            # 1D Array: Nom = Tableau de N Type
            m_arr1 = re.match(r'^([a-zA-Z0-9_]+)\s*=\s*tableau\s+de\s+(\d+|[a-zA-Z0-9_]+)\s+(.+)$', s, re.IGNORECASE)
            if m_arr1:
                t_name, size, elem_type = m_arr1.group(1), m_arr1.group(2), m_arr1.group(3).strip()
                self.custom_types[t_name] = {'kind': 'tableau_1d', 'size': size, 'elem_type': elem_type}
                continue

            # 2D Array: Nom = Tableau de N lignes * M colonnes Type
            m_arr2 = re.match(r'^([a-zA-Z0-9_]+)\s*=\s*tableau\s+de\s+(\d+|[a-zA-Z0-9_]+)\s*lignes?\s*\*\s*(\d+|[a-zA-Z0-9_]+)\s*colonnes?\s+(.+)$', s, re.IGNORECASE)
            if m_arr2:
                t_name, rows, cols, elem_type = m_arr2.group(1), m_arr2.group(2), m_arr2.group(3), m_arr2.group(4).strip()
                self.custom_types[t_name] = {'kind': 'tableau_2d', 'rows': rows, 'cols': cols, 'elem_type': elem_type}
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
                t_low = type_part.lower()
                if t_low in ('procedure', 'procédure', 'fonction', 'module', '/'):
                    continue
                names = [n.strip() for n in names_part.split(',') if n.strip()]
                for name in names:
                    clean_name = re.sub(r'[^a-zA-Z0-9_]', '', name)
                    if clean_name and clean_name != '/':
                        self.declared_objects[clean_name] = type_part

    def default_value_for_type(self, elem_type: str) -> str:
        """Returns standard Python literal default for algorithmic type."""
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

    def generate_object_initializations(self, objects_dict: dict = None) -> list:
        """Generates Python initialization code for declared objects (NumPy arrays, dicts, scalars)."""
        if objects_dict is None:
            objects_dict = self.declared_objects
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
                    elem_t = t_def['elem_type']
                    if elem_t in self.custom_types and self.custom_types[elem_t]['kind'] == 'enregistrement':
                        lines.append(f"{var_name} = array([_creer_{elem_t}() for _ in range({t_def['size']})], dtype=object)")
                    else:
                        init_val = self.default_value_for_type(elem_t)
                        lines.append(f"{var_name} = array([{init_val}] * ({t_def['size']}))")
                    continue
                elif t_def['kind'] == 'tableau_2d':
                    init_val = self.default_value_for_type(t_def['elem_type'])
                    lines.append(f"{var_name} = array([[{init_val}] * ({t_def['cols']})] * ({t_def['rows']}))")
                    continue

            # Tableau 2D inline: Tableau de N lignes * M colonnes Type
            m_arr2 = re.match(r'tableau\s+de\s+(.+?)\s*lignes?\s*\*\s*(.+?)\s*colonnes?\s+(.+)', t_lower)
            if m_arr2:
                rows, cols, elem_type = m_arr2.group(1).strip(), m_arr2.group(2).strip(), m_arr2.group(3).strip()
                init_val = self.default_value_for_type(elem_type)
                lines.append(f"{var_name} = array([[{init_val}] * ({cols})] * ({rows}))")
                continue

            # Tableau 1D inline: Tableau de N Type
            m_arr1 = re.match(r'tableau\s+de\s+(.+?)\s+([a-zA-Z0-9_éèêà]+.*)', t_lower)
            if m_arr1:
                size, elem_type = m_arr1.group(1).strip(), m_arr1.group(2).strip()
                if elem_type in self.custom_types and self.custom_types[elem_type]['kind'] == 'enregistrement':
                    lines.append(f"{var_name} = array([_creer_{elem_type}() for _ in range({size})], dtype=object)")
                else:
                    init_val = self.default_value_for_type(elem_type)
                    lines.append(f"{var_name} = array([{init_val}] * ({size}))")
                continue

            # Enregistrement inline
            if 'enregistrement' in t_lower:
                lines.append(f"{var_name} = Enregistrement()")
                continue

            # Simple scalar types (Entier, Réel, Booléen, Chaîne)
            init_val = self.default_value_for_type(type_str)
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
