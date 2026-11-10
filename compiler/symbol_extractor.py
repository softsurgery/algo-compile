"""
Symbol and Object Extractor for Algorithms.
Extracts declared types (TDNT), global objects (TDOG), and all subprogram objects
and variables (parameters and TDOL) for IDE inspectors.
"""

import re
from compiler.utils import normalize_accents
from compiler.parser import SectionExtractor
from compiler.types import TypeHandler


def parse_subprogram_header(header: str) -> dict:
    """
    Parses a subprogram header line.
    Returns:
        dict with keys: 'name', 'kind', 'return_type', 'params', 'raw_params'
        where params is a list of {'name': str, 'type': str, 'is_ref': bool}
    """
    s = header.strip()
    m = re.match(
        r'^(fonction|procédure|procedure)\s+([a-zA-Z0-9_\u00C0-\u017F]+)\s*(?:\((.*?)\))?(?:\s*:\s*(.+))?$',
        s,
        re.IGNORECASE
    )
    if not m:
        return {
            'name': '',
            'kind': 'procedure',
            'return_type': None,
            'params': [],
            'raw_params': ''
        }

    kind_word = m.group(1).lower()
    kind = 'fonction' if 'fonc' in kind_word else 'procedure'
    name = m.group(2).strip()
    params_str = (m.group(3) or "").strip()
    return_type = (m.group(4) or "").strip() if m.group(4) else None

    params = []
    if params_str:
        # Split params into chunks by comma, handling potential commas inside brackets
        raw_chunks = [c.strip() for c in params_str.split(',') if c.strip()]
        
        # We handle both:
        # 1. p1 : Type1, p2 : Type2
        # 2. a, b : Entier (grouped types)
        # 3. @t : Tab (pass by reference)
        collected_names = []
        for chunk in raw_chunks:
            if ':' in chunk:
                pnames_part, ptype = chunk.split(':', 1)
                ptype = ptype.strip()
                pname = pnames_part.strip()
                if pname:
                    collected_names.append(pname)
                for pn in collected_names:
                    pn_clean = pn.strip()
                    is_ref = pn_clean.startswith('@')
                    clean_id = pn_clean.lstrip('@').strip()
                    if clean_id:
                        params.append({
                            'name': clean_id,
                            'type': ptype,
                            'is_ref': is_ref,
                            'display_name': ('@' if is_ref else '') + clean_id
                        })
                collected_names = []
            else:
                collected_names.append(chunk)

        # Any remaining untyped parameters
        for pn in collected_names:
            pn_clean = pn.strip()
            is_ref = pn_clean.startswith('@')
            clean_id = pn_clean.lstrip('@').strip()
            if clean_id:
                params.append({
                    'name': clean_id,
                    'type': 'Objet',
                    'is_ref': is_ref,
                    'display_name': ('@' if is_ref else '') + clean_id
                })

    return {
        'name': name,
        'kind': kind,
        'return_type': return_type,
        'params': params,
        'raw_params': params_str
    }


def parse_table_declaration_lines(lines: list) -> list:
    """
    Parses declaration lines from TDOG or TDOL tables.
    Preserves original casing for names.
    Returns:
        list of dicts: [{'name': str, 'type': str, 'is_subprogram': bool}, ...]
    """
    results = []
    seen = set()

    for item in lines:
        if isinstance(item, (tuple, list)):
            _, line = item
        else:
            line = item

        s = line.strip()
        if not s or re.match(r'^[\*\-=\/ ]+$', s):
            continue

        lower = s.lower()
        if lower.startswith(('objet', 'type', 'nom_objet', '---', '===', 'tdo', 'tdol', 'tdog')):
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
            if t_low in ('/', 'module') or not type_part:
                continue

            is_sub = t_low.startswith(('procedure', 'procédure', 'fonction'))
            names = [n.strip() for n in names_part.split(',') if n.strip()]
            for raw_name in names:
                clean_name = re.sub(r'[^a-zA-Z0-9_\u00C0-\u017F]', '', raw_name)
                if clean_name and clean_name != '/' and clean_name.lower() not in seen:
                    seen.add(clean_name.lower())
                    results.append({
                        'name': clean_name,
                        'type': type_part,
                        'is_subprogram': is_sub
                    })

    return results


def get_python_equivalent(typ: str, custom_types: dict = None, name: str = None) -> str:
    """Returns explanatory Python equivalent for an algorithmic type."""
    if not typ:
        return "Objet Python"

    custom_types = custom_types or {}
    t_clean = typ.strip()
    id_name = name or "nom"

    # Look up in custom types (case-insensitive)
    match_custom = None
    for c_name, c_def in custom_types.items():
        if c_name.lower() == t_clean.lower():
            match_custom = (c_name, c_def)
            break

    if match_custom:
        c_name, c_def = match_custom
        kind = c_def.get('kind')
        if kind == 'enregistrement':
            fields_str = ", ".join(f"{f}=..." for f in c_def.get('fields', {}).keys())
            return f"_creer_{c_name}() (dict({fields_str}))"
        elif kind == 'tableau_1d':
            return f"array([...]*{c_def.get('size', 'N')})"
        elif kind == 'tableau_2d':
            return f"array([[...]*{c_def.get('cols', 'M')}]*{c_def.get('rows', 'N')})"
        elif kind == 'alias':
            return get_python_equivalent(c_def.get('target_type', ''), custom_types, name)

    t = t_clean.lower()
    if 'tableau' in t:
        if '*' in t or 'lignes' in t or 'colonnes' in t:
            return "from numpy import array; array([[...]*C]*L)"
        return "from numpy import array; array([...]*N)"
    elif 'enregistrement' in t:
        return "dict(champ1=..., champ2=...)"
    elif 'fichier' in t:
        if 'texte' in t:
            return "open(..., 'r'/'w'/'a')"
        return "open(..., 'rb'/'wb'/'ab') + pickle load/dump"
    elif 'entier' in t:
        return "int"
    elif 'réel' in t or 'reel' in t:
        return "float"
    elif 'bool' in t:
        return "bool (True / False)"
    elif 'caractère' in t or 'caractere' in t or 'chaîne' in t or 'chaine' in t:
        return "str"
    elif 'procédure' in t or 'procedure' in t:
        return f"def {id_name}(...) -> None"
    elif 'fonction' in t:
        return f"def {id_name}(...) -> valeur"
    elif 'constante' in t:
        return "Constante Python"
    return "Objet Python dynamique"


def get_default_val(typ: str, custom_types: dict = None) -> str:
    """Returns placeholder initial value for Variables View."""
    if not typ:
        return "-"

    custom_types = custom_types or {}
    t_clean = typ.strip()

    match_custom = None
    for c_name, c_def in custom_types.items():
        if c_name.lower() == t_clean.lower():
            match_custom = (c_name, c_def)
            break

    if match_custom:
        _, c_def = match_custom
        kind = c_def.get('kind')
        if kind == 'enregistrement':
            return "{...}"
        elif kind in ('tableau_1d', 'tableau_2d'):
            return "[...]"
        elif kind == 'alias':
            return get_default_val(c_def.get('target_type', ''))

    t = t_clean.lower()
    if 'tableau' in t:
        return "[...]"
    elif 'enregistrement' in t:
        return "{...}"
    elif 'entier' in t:
        return "0"
    elif 'réel' in t or 'reel' in t:
        return "0.0"
    elif 'bool' in t:
        return "Faux"
    elif 'caractère' in t or 'caractere' in t or 'chaîne' in t or 'chaine' in t:
        return "''"
    return "-"


def extract_all_symbols(algo_code: str, custom_types_extra: dict = None) -> dict:
    """
    Extracts all symbols from algorithmic source code:
    - Custom Types (TDNT)
    - TDO Objects (both global and all subprogram local objects & parameters)
    - Variables (both global variables and all subprogram parameters & local variables)
    - Subprograms metadata
    """
    code = normalize_accents(algo_code or "")
    lines = code.splitlines()

    extractor = SectionExtractor()
    blocks = extractor.extract_sections(lines)

    type_handler = TypeHandler()
    type_handler.parse_type_declarations(blocks.get('types', []))
    custom_types = dict(type_handler.custom_types)
    if custom_types_extra:
        custom_types.update(custom_types_extra)

    tdo_objects = []
    tdo_tables = []
    variables = []
    subprograms_meta = []

    # 1. Global Objects (TDOG)
    tdog_table = {
        'id': 'tdog',
        'title': 'Tableau de Déclaration des Objets Globaux (T.D.O.G.)',
        'short_name': 'T.D.O.G. (Objets Globaux)',
        'kind': 'tdog',
        'subprogram_name': None,
        'header': None,
        'objects': []
    }

    global_items = parse_table_declaration_lines(blocks.get('objects', []))
    for item in global_items:
        name = item['name']
        typ = item['type']
        is_sub = item['is_subprogram']
        py_equiv = get_python_equivalent(typ, custom_types, name=name)
        def_val = get_default_val(typ, custom_types)

        obj_entry = {
            'name': name,
            'type': typ,
            'scope': 'Globale',
            'scope_display': 'Globale (TDOG)',
            'role': 'sous_programme' if is_sub else 'variable_globale',
            'is_subprogram': is_sub,
            'py_equiv': py_equiv
        }
        tdo_objects.append(obj_entry)
        tdog_table['objects'].append(obj_entry)

        if not is_sub:
            variables.append({
                'name': name,
                'type': typ,
                'scope': 'Globale',
                'scope_display': 'Globale',
                'role': 'variable_globale',
                'value': def_val
            })

    tdo_tables.append(tdog_table)

    # 2. Subprograms (Parameters + TDOL)
    for subprog in blocks.get('subprograms', []):
        header_info = parse_subprogram_header(subprog.get('header', ''))
        sub_name = subprog.get('name') or header_info['name']
        sub_kind = subprog.get('kind') or header_info['kind']
        sub_title = sub_kind.capitalize()

        tdol_table = {
            'id': f"tdol_{sub_name}",
            'title': f"T.D.O.L. — {sub_title} {sub_name}",
            'short_name': f"T.D.O.L. ({sub_name})",
            'kind': 'tdol',
            'subprogram_name': sub_name,
            'header': subprog.get('header', ''),
            'objects': []
        }

        sub_info = {
            'name': sub_name,
            'kind': sub_kind,
            'header': subprog.get('header', ''),
            'return_type': header_info.get('return_type'),
            'params': header_info.get('params', []),
            'tdol_objects': []
        }

        # Parameters
        seen_local_names = set()
        for p in header_info.get('params', []):
            p_name = p['name']
            p_type = p['type']
            p_ref = p['is_ref']
            seen_local_names.add(p_name.lower())

            py_equiv = get_python_equivalent(p_type, custom_types, name=p['display_name'])
            def_val = get_default_val(p_type, custom_types)
            ref_label = " (@réf)" if p_ref else ""

            param_entry = {
                'name': p['display_name'],
                'type': p_type,
                'scope': sub_name,
                'scope_display': f"{sub_name} (Paramètre{ref_label})",
                'role': 'paramètre_ref' if p_ref else 'paramètre',
                'is_subprogram': False,
                'is_param': True,
                'is_ref': p_ref,
                'py_equiv': py_equiv
            }
            tdo_objects.append(param_entry)
            tdol_table['objects'].append(param_entry)

            variables.append({
                'name': p['display_name'],
                'type': p_type,
                'scope': sub_name,
                'scope_display': f"Locale ({sub_name})",
                'role': 'paramètre_ref' if p_ref else 'paramètre',
                'value': def_val
            })

        # Local Declarations (TDOL)
        tdol_items = parse_table_declaration_lines(subprog.get('tdo', []))
        for item in tdol_items:
            name = item['name']
            typ = item['type']
            is_sub = item['is_subprogram']

            # If parameter was re-declared in TDOL, don't duplicate
            if name.lower() in seen_local_names:
                continue
            seen_local_names.add(name.lower())

            sub_info['tdol_objects'].append(item)
            py_equiv = get_python_equivalent(typ, custom_types, name=name)
            def_val = get_default_val(typ, custom_types)

            local_entry = {
                'name': name,
                'type': typ,
                'scope': sub_name,
                'scope_display': f"{sub_name} (TDOL)",
                'role': 'sous_programme' if is_sub else 'variable_locale',
                'is_subprogram': is_sub,
                'is_param': False,
                'is_ref': False,
                'py_equiv': py_equiv
            }
            tdo_objects.append(local_entry)
            tdol_table['objects'].append(local_entry)

            if not is_sub:
                variables.append({
                    'name': name,
                    'type': typ,
                    'scope': sub_name,
                    'scope_display': f"Locale ({sub_name})",
                    'role': 'variable_locale',
                    'value': def_val
                })

        tdo_tables.append(tdol_table)
        subprograms_meta.append(sub_info)

    return {
        'blocks': blocks,
        'custom_types': custom_types,
        'tdo_objects': tdo_objects,
        'tdo_tables': tdo_tables,
        'variables': variables,
        'subprograms': subprograms_meta
    }
