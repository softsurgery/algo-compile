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
        local_types = {}
        if params_str.strip():
            raw_params = params_str.split(',')
            for p in raw_params:
                p = p.strip()
                if not p:
                    continue
                if ':' in p:
                    pname, ptype = p.split(':', 1)
                    pname = pname.strip()
                    clean_p = pname.lstrip('@').strip()
                    local_types[clean_p] = ptype.strip()
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

        from compiler.validator import AlgoValidator

        # Extract local TDOL variables and combine with parameter types
        tdol_vars, _ = AlgoValidator.extract_table_declarations(subprog.get('tdo', []))
        all_locals = dict(tdol_vars)
        all_locals.update(local_types)

        prev_local = getattr(self.stmt_trans, 'local_objects', {})
        self.stmt_trans.local_objects = dict(all_locals)
        try:
            sub_body = self.stmt_trans.translate_statements(body_lines, indent_level=1)
        finally:
            self.stmt_trans.local_objects = prev_local
        if not sub_body:
            sub_body = ["    pass"]

        # Initialize local TDOL variables that are not parameters
        if hasattr(self.stmt_trans, 'type_handler') and self.stmt_trans.type_handler:
            param_lower = {p.lower() for p in py_params}
            non_param_locals = {k: v for k, v in tdol_vars.items() if k.lower() not in param_lower}
            if non_param_locals:
                inits = self.stmt_trans.type_handler.generate_object_initializations(non_param_locals)
                for init_l in reversed(inits):
                    sub_body.insert(0, f"    {init_l}")

        # If procedure has pass-by-reference params and doesn't explicitly return
        if kind == 'procedure' and param_ref:
            has_return = any('return' in l for l in sub_body)
            if not has_return:
                refs_ordered = [p for p in py_params if p in param_ref]
                sub_body.append(f"    return {', '.join(refs_ordered)}")

        py_lines.extend(sub_body)
        return py_lines
