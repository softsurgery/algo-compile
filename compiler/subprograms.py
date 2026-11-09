"""
Subprogram (Fonction & Procédure) Translator.
"""

import re

class SubprogramTranslator:
    """Translates Fonction and Procédure blocks to Python functions with pass-by-reference handling."""

    def __init__(self, statement_translator):
        self.stmt_trans = statement_translator

    def translate_subprogram(self, subprog: dict) -> list:
        """Translates a Fonction or Procédure block into Python def."""
        header_text = subprog['header']
        kind = subprog['kind']

        # Parse: Fonction Nom (p1: t1, @p2: t2) : Type_res
        # or Procédure Nom (p1: t1, @p2: t2)
        m = re.match(
            r'^(?:fonction|procédure|procedure)\s+([a-zA-Z0-9_]+)\s*(?:\((.*?)\))?(?:\s*:\s*([a-zA-Z0-9_]+))?',
            header_text,
            re.IGNORECASE
        )
        if not m:
            return [f"# Erreur de syntaxe dans l'en-tête: {header_text}"]

        sub_name = m.group(1)
        params_str = m.group(2) or ""

        # Parse parameters and track @ pass-by-reference
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

        sub_body = self.stmt_trans.translate_statements(body_lines, indent_level=1)
        if not sub_body:
            sub_body = ["    pass"]

        # If procedure has pass-by-reference params and doesn't explicitly return
        if kind == 'procedure' and param_ref:
            has_return = any('return' in l for l in sub_body)
            if not has_return:
                refs_ordered = [p for p in py_params if p in param_ref]
                sub_body.append(f"    return {', '.join(refs_ordered)}")

        py_lines.extend(sub_body)
        return py_lines
