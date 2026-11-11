"""
Statement and Control Flow Translator.
"""

import re
from compiler.utils import split_arguments
from compiler.errors import  MissingEndError

class StatementTranslator:
    """Translates algorithmic statements and structured control blocks into Python 3."""

    def __init__(self, expression_translator, type_handler, subprogram_meta):
        self.expr_trans = expression_translator
        self.type_handler = type_handler
        self.subprogram_meta = subprogram_meta
        self.local_objects = {}

    @property
    def declared_objects(self):
        combined = dict(self.type_handler.declared_objects)
        if hasattr(self, 'local_objects') and self.local_objects:
            combined.update(self.local_objects)
        return combined

    def _get_var_type(self, var_name: str) -> str:
        """Looks up the declared or local type of var_name case-insensitively and resolves aliases."""
        if not var_name:
            return ""
        target = var_name.strip().lower()
        found_type = None
        # Check local objects first
        if hasattr(self, 'local_objects') and self.local_objects:
            for k, v in self.local_objects.items():
                if k.lower() == target:
                    found_type = v
                    break
        # Check declared objects
        if not found_type and hasattr(self, 'declared_objects') and self.declared_objects:
            for k, v in self.declared_objects.items():
                if k.lower() == target:
                    found_type = v
                    break
        if found_type:
            if hasattr(self, 'type_handler') and hasattr(self.type_handler, 'resolve_type'):
                found_type = self.type_handler.resolve_type(found_type)
            return found_type
        return ""

    def _is_file_var(self, var_name: str) -> tuple[bool, bool]:
        """Returns (is_file, is_text) for a variable name."""
        t_obj = self._get_var_type(var_name).lower()
        if 'fichier' in t_obj:
            return True, ('texte' in t_obj)
        return False, False

    def translate_statements(self, line_tuples: list, indent_level: int = 1) -> list:
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
                cond = self.expr_trans.translate_expression(m_si.group(1))
                result.append(f"{base_indent}if {cond}:")
                
                # Collect then block, elifs, and else
                block_res, next_i = self.parse_si_block(line_tuples, i + 1, indent_level, si_line_no=line_no)
                result.extend(block_res)
                i = next_i
                continue

            # 2. Selon <Sélecteur> ... Fin Selon
            m_selon = re.match(r'^selon\s+(.+)$', s, re.IGNORECASE)
            if m_selon:
                selector = self.expr_trans.translate_expression(m_selon.group(1))
                result.append(f"{base_indent}match {selector}:")
                selon_res, next_i = self.parse_selon_block(line_tuples, i + 1, indent_level, selector, selon_line_no=line_no)
                result.extend(selon_res)
                i = next_i
                continue

            # 3. Pour <compteur> de <debut> à <fin> [Pas = <p>] Faire ... Fin Pour
            m_pour = re.match(r'^pour\s+([a-zA-Z0-9_]+)\s+de\s+(.+?)\s+à\s+(.+?)(?:\s+pas\s*=\s*(.+?))?\s+faire$', s, re.IGNORECASE)
            if not m_pour:
                m_pour = re.match(r'^pour\s+([a-zA-Z0-9_]+)\s+de\s+(.+?)\s+a\s+(.+?)(?:\s+pas\s*=\s*(.+?))?\s+faire$', s, re.IGNORECASE)
            
            if m_pour:
                counter = m_pour.group(1)
                start_val = self.expr_trans.translate_expression(m_pour.group(2))
                end_val = self.expr_trans.translate_expression(m_pour.group(3))
                step_val = m_pour.group(4)
                
                if step_val is not None:
                    step_expr = self.expr_trans.translate_expression(step_val)
                    range_expr = f"range({start_val}, ({end_val}) + 1 if ({step_expr}) > 0 else ({end_val}) - 1, {step_expr})"
                else:
                    range_expr = f"range({start_val}, ({end_val}) + 1)"

                result.append(f"{base_indent}for {counter} in {range_expr}:")
                
                # Collect loop body until Fin Pour
                body_lines, next_i = self.collect_block_until(
                    line_tuples, i + 1, [r'^(?:fin[\s_]*pour|finpour)$'],
                    block_name="Pour", start_line_no=line_no
                )
                translated_body = self.translate_statements(body_lines, indent_level + 1)
                if not translated_body:
                    translated_body = [f"{base_indent}    pass"]
                result.extend(translated_body)
                i = next_i
                continue

            # 4. Tant que <Condition> Faire ... Fin Tant que
            m_tq = re.match(r'^tant\s*que\s+(.+?)\s+faire$', s, re.IGNORECASE)
            if m_tq:
                cond = self.expr_trans.translate_expression(m_tq.group(1))
                result.append(f"{base_indent}while {cond}:")
                body_lines, next_i = self.collect_block_until(
                    line_tuples, i + 1, [r'^(?:fin[\s_]*tan.*|fintan.*)$'],
                    block_name="Tant que", start_line_no=line_no
                )
                translated_body = self.translate_statements(body_lines, indent_level + 1)
                if not translated_body:
                    translated_body = [f"{base_indent}    pass"]
                result.extend(translated_body)
                i = next_i
                continue

            # 5. Répéter ... Jusqu'à <Condition>
            if s.lower() in ('répéter', 'repeter'):
                result.append(f"{base_indent}while True:")
                body_lines, until_cond, next_i = self.collect_repeter_block(line_tuples, i + 1, start_line_no=line_no)
                translated_body = self.translate_statements(body_lines, indent_level + 1)
                if not translated_body:
                    translated_body = [f"{base_indent}    pass"]
                result.extend(translated_body)
                if until_cond:
                    until_py = self.expr_trans.translate_expression(until_cond)
                    result.append(f"{base_indent}    if {until_py}:")
                    result.append(f"{base_indent}        break")
                i = next_i
                continue

            # 6. Retourner <Expression>
            m_ret = re.match(r'^retourner\s+(.+)$', s, re.IGNORECASE)
            if m_ret:
                expr = self.expr_trans.translate_expression(m_ret.group(1))
                result.append(f"{base_indent}return {expr}")
                i += 1
                continue

            # 7. Single statement translation (Lire, Ecrire, Assignment, Procedure call)
            stmt = self.translate_single_statement(s, line_no)
            if stmt:
                result.append(f"{base_indent}{stmt}")
            i += 1

        return result

    def parse_si_block(self, line_tuples: list, start_idx: int, indent_level: int, si_line_no: int = None):
        """Parses if branches and returns translated lines and next index."""
        result = []
        base_indent = "    " * indent_level
        branch_body = []
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
                if re.match(r'^(?:fin[\s_]*si|finsi)$', s, re.IGNORECASE):
                    nesting -= 1
                branch_body.append((line_no, line))
                idx += 1
                continue

            # Nesting == 0: check for branch switches or end
            m_elif = re.match(r'^(?:sinon\s*si|sinonsi)\s+(.+?)\s+alors$', s, re.IGNORECASE)
            if m_elif:
                sub = self.translate_statements(branch_body, indent_level + 1)
                result.extend(sub if sub else [f"{base_indent}    pass"])
                branch_body = []
                cond = self.expr_trans.translate_expression(m_elif.group(1))
                result.append(f"{base_indent}elif {cond}:")
                idx += 1
                continue

            if re.match(r'^sinon$', s, re.IGNORECASE):
                sub = self.translate_statements(branch_body, indent_level + 1)
                result.extend(sub if sub else [f"{base_indent}    pass"])
                branch_body = []
                result.append(f"{base_indent}else:")
                idx += 1
                continue

            if re.match(r'^(?:fin[\s_]*si|finsi)$', s, re.IGNORECASE):
                sub = self.translate_statements(branch_body, indent_level + 1)
                result.extend(sub if sub else [f"{base_indent}    pass"])
                idx += 1
                return result, idx

            branch_body.append((line_no, line))
            idx += 1

        line_info = f" à la ligne {si_line_no}" if si_line_no is not None else ""
        raise MissingEndError(f"Bloc 'Si' ouvert{line_info} non fermé : 'Fin Si' manquant", line_num=si_line_no)

    def parse_selon_block(self, line_tuples: list, start_idx: int, indent_level: int, selector: str, selon_line_no: int = None):
        """Parses Selon choices into match/case."""
        result = []
        base_indent = "    " * indent_level
        idx = start_idx

        while idx < len(line_tuples):
            line_no, line = line_tuples[idx]
            s = line.strip()

            if re.match(r'^(?:fin[\s_]*selon|finselon)$', s, re.IGNORECASE):
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
                    stmt = self.translate_single_statement(rest, line_no)
                    result.append(f"{base_indent}        {stmt}")
                idx += 1
                continue

            # Case: pattern : action
            if ':' in s:
                pattern, action = s.split(':', 1)
                pattern = pattern.strip()
                action = action.strip()

                if '..' in pattern:
                    v1, v2 = pattern.split('..', 1)
                    v1_py = self.expr_trans.translate_expression(v1.strip())
                    v2_py = self.expr_trans.translate_expression(v2.strip())
                    result.append(f"{base_indent}    case s if ({v1_py} <= s <= {v2_py}):")
                else:
                    vals = [self.expr_trans.translate_expression(v.strip()) for v in pattern.split(',') if v.strip()]
                    pattern_py = " | ".join(vals)
                    result.append(f"{base_indent}    case {pattern_py}:")

                if action:
                    stmt = self.translate_single_statement(action, line_no)
                    result.append(f"{base_indent}        {stmt}")
                else:
                    result.append(f"{base_indent}        pass")
                idx += 1
                continue

            idx += 1

        line_info = f" à la ligne {selon_line_no}" if selon_line_no is not None else ""
        raise MissingEndError(f"Bloc 'Selon' ouvert{line_info} non fermé : 'Fin Selon' manquant", line_num=selon_line_no)

    def collect_block_until(self, line_tuples: list, start_idx: int, end_patterns: list, block_name: str = "Bloc", start_line_no: int = None):
        """Collects lines until a matching closing pattern is found at depth 0."""
        body = []
        nesting = 0
        idx = start_idx

        while idx < len(line_tuples):
            line_no, line = line_tuples[idx]
            s = line.strip()

            if re.match(r'^(?:pour\s+.+?\s+faire|tant\s*que\s+.+?\s+faire|si\s+.+?\s+alors|selon\s+.+|répéter|repeter)', s, re.IGNORECASE):
                nesting += 1
                body.append((line_no, line))
                idx += 1
                continue

            matched_end = any(re.match(pat, s, re.IGNORECASE) for pat in end_patterns)
            if matched_end:
                if nesting > 0:
                    nesting -= 1
                    body.append((line_no, line))
                    idx += 1
                    continue
                else:
                    return body, idx + 1

            if re.match(r'^(?:fin[\s_]*si|finsi|fin[\s_]*pour|finpour|fin[\s_]*tant[\s_]*que|fintantque|fintanqtue|fin[\s_]*selon|jusqu[\'’]?(?:à|a))', s, re.IGNORECASE):
                if nesting > 0:
                    nesting -= 1

            body.append((line_no, line))
            idx += 1

        line_info = f" à la ligne {start_line_no}" if start_line_no is not None else ""
        end_desc = f"'Fin {block_name}'" if block_name else "délimiteur de fin"
        raise MissingEndError(f"Bloc '{block_name}' ouvert{line_info} non fermé : {end_desc} manquant", line_num=start_line_no)

    def collect_repeter_block(self, line_tuples: list, start_idx: int, start_line_no: int = None):
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

            m_until = re.match(r'^jusqu[\'’\s]?(?:à|a|e)?\s*(.+)$', s, re.IGNORECASE)
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

        line_info = f" à la ligne {start_line_no}" if start_line_no is not None else ""
        raise MissingEndError(f"Bloc 'Répéter' ouvert{line_info} non fermé : 'Jusqu\'à' manquant", line_num=start_line_no)

    def translate_single_statement(self, s: str, line_no: int = 0) -> str:
        """Translates an assignment, Lire, Ecrire, or subprogram call."""
        s = s.strip()
        if not s:
            return ""

        # 1. Output: Écrire / Ecrire / Écrire_nl / Ecrire_nl
        m_ecrire = re.match(r'^(?:écrire_nl|ecrire_nl|écrire|ecrire)\s*\((.*)\)$', s, re.IGNORECASE)
        if m_ecrire:
            is_nl = 'nl' in s[:12].lower()
            args_str = m_ecrire.group(1).strip()
            args = split_arguments(args_str)
            
            # File logical name check: Ecrire(f, obj...) or Ecrire_nl(f, obj...)
            if len(args) >= 2 and args[0].isidentifier():
                is_file, is_text = self._is_file_var(args[0])
                if is_file:
                    f_name = args[0]
                    if is_text:
                        if len(args) == 2:
                            content = self.expr_trans.translate_expression(args[1])
                            if is_nl:
                                return f"{f_name}.write(str({content}) + '\\n')"
                            return f"{f_name}.write(str({content}))"
                        else:
                            py_items = [f"str({self.expr_trans.translate_expression(a)})" for a in args[1:]]
                            content = " + ".join(py_items)
                            if is_nl:
                                return f"{f_name}.write({content} + '\\n')"
                            return f"{f_name}.write({content})"
                    else:
                        # Binary data file: pickle dump
                        dumps = []
                        for a in args[1:]:
                            content = self.expr_trans.translate_expression(a)
                            dumps.append(f"dump({content}, {f_name})")
                        return "; ".join(dumps)

            # Console output
            py_args = [self.expr_trans.translate_expression(arg) for arg in args]
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
            args = split_arguments(args_str)

            # File read: Lire(f, obj...) or Lire_ligne(f, ch...)
            if len(args) >= 2 and args[0].isidentifier():
                is_file, is_text = self._is_file_var(args[0])
                if is_file or is_line:
                    f_name = args[0]
                    if is_text or is_line:
                        reads = []
                        for a in args[1:]:
                            target_var = self.expr_trans.translate_target(a)
                            if is_line:
                                reads.append(f"{target_var} = {f_name}.readline().rstrip('\\r\\n')")
                            else:
                                reads.append(f"{target_var} = {f_name}.read()")
                        return "; ".join(reads)
                    else:
                        # Binary data file: pickle load
                        reads = []
                        for a in args[1:]:
                            target_var = self.expr_trans.translate_target(a)
                            reads.append(f"{target_var} = load({f_name})")
                        return "; ".join(reads)

            # Interactive input from console: Lire(a, b, ...)
            assignments = []
            for arg in args:
                target_var = self.expr_trans.translate_target(arg.strip())
                clean_id = re.sub(r'\[.*\]', '', arg.strip())
                clean_id = clean_id.split('.')[0].strip()
                vtype = self._get_var_type(clean_id)
                if vtype:
                    target_type = vtype
                    # If reading an array element (e.g. IDENT[i]), get the element type
                    if '[' in arg:
                        if vtype in self.type_handler.custom_types:
                            c_def = self.type_handler.custom_types[vtype]
                            if c_def.get('kind') in ('tableau_1d', 'tableau_2d'):
                                target_type = c_def.get('elem_type', vtype)
                        else:
                            m_arr = re.match(r'tableau\s+de\s+(?:.+?\s*lignes?\s*\*\s*.+?\s*colonnes?\s+|.+?\s+)(.+)', vtype, re.IGNORECASE)
                            if m_arr:
                                target_type = m_arr.group(1).strip()
                    # If reading a record field (e.g. E.nom or T[i].nom)
                    if '.' in arg:
                        field_name = arg.split('.')[-1].strip()
                        rec_type = target_type
                        if rec_type in self.type_handler.custom_types and self.type_handler.custom_types[rec_type].get('kind') == 'enregistrement':
                            target_type = self.type_handler.custom_types[rec_type].get('fields', {}).get(field_name, target_type)
                    assignments.append(f"{target_var} = _lire_valeur('', {target_type!r})")
                else:
                    assignments.append(f"{target_var} = _lire_valeur('')")
            return "; ".join(assignments)

        # 3. File open: Ouvrir("path", f, "mode")
        m_open = re.match(r'^ouvrir\s*\((.+?)\)$', s, re.IGNORECASE)
        if m_open:
            args = split_arguments(m_open.group(1))
            if len(args) >= 3:
                arg0 = args[0].strip()
                arg1 = args[1].strip()
                arg2 = args[2].strip()
                all_objs_lower = {k.lower(): v for k, v in {**self.declared_objects, **self.local_objects}.items()}
                if arg0.lower() in all_objs_lower and arg1.lower() not in all_objs_lower:
                    f_name = arg0
                    path = self.expr_trans.translate_expression(arg1)
                    mode = self.expr_trans.translate_expression(arg2)
                else:
                    path = self.expr_trans.translate_expression(arg0)
                    f_name = arg1
                    mode = self.expr_trans.translate_expression(arg2)
                return f"{f_name} = Ouvrir({path}, {mode})"
            elif len(args) == 2:
                path = self.expr_trans.translate_expression(args[0])
                mode = self.expr_trans.translate_expression(args[1])
                return f"Ouvrir({path}, {mode})"

        # 4. File close: Fermer(f)
        m_close = re.match(r'^fermer\s*\((.+?)\)$', s, re.IGNORECASE)
        if m_close:
            f_name = m_close.group(1).strip()
            return f"{f_name}.close()"

        # 5. Assignment: target <- expression (or , ←, :=)
        for sym in ['<-', '←', '\uf0e7', '', ':=']:
            if sym in s:
                parts = s.split(sym, 1)
                target = self.expr_trans.translate_target(parts[0].strip())
                expr = self.expr_trans.translate_expression(parts[1].strip())
                return f"{target} = {expr}"

        # If has bare '=', check if assignment: target = expr
        if '=' in s and not s.startswith(('if', 'while', 'for')):
            parts = s.split('=', 1)
            target = parts[0].strip()
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\s*\[.+?\]|\.[a-zA-Z0-9_]+)?$', target):
                expr = self.expr_trans.translate_expression(parts[1].strip())
                target_py = self.expr_trans.translate_target(target)
                return f"{target_py} = {expr}"

        # 6. Procedure call with @ reference parameters
        m_call = re.match(r'^([a-zA-Z0-9_]+)\s*\((.*)\)$', s)
        if m_call:
            callee = m_call.group(1)
            args_str = m_call.group(2)
            if callee in self.subprogram_meta:
                meta = self.subprogram_meta[callee]
                ref_p = meta.get('ref_params', [])
                all_p = meta.get('all_params', [])
                if ref_p:
                    args = split_arguments(args_str)
                    assigned_targets = []
                    for ref_name in ref_p:
                        if ref_name in all_p:
                            idx = all_p.index(ref_name)
                            if idx < len(args):
                                arg_target = args[idx].strip()
                                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\[.*\]|\.[a-zA-Z0-9_]+)?$', arg_target):
                                    assigned_targets.append(arg_target)
                    if assigned_targets:
                        trans_args = [self.expr_trans.translate_expression(a) for a in args]
                        targets_str = ", ".join(assigned_targets)
                        return f"{targets_str} = {callee}({', '.join(trans_args)})"

        return self.expr_trans.translate_expression(s)
