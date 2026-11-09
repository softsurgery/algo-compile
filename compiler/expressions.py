"""
Algorithmic Expression and Target Translator.
"""

import re

class ExpressionTranslator:
    """Translates algorithmic expressions and assignment targets to valid Python 3 expressions."""

    def __init__(self):
        self.fn_map = {
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

    def translate_target(self, target_str: str) -> str:
        """Translates target expression for assignment LHS (e.g. M[i, j], E.champ, T[i].champ)."""
        target = target_str.strip()

        # Handle indexed record field: T[i].field -> T[i]['field']
        m_idx_dot = re.match(r'^([a-zA-Z0-9_]+\[.+?\])\.([a-zA-Z0-9_]+)$', target)
        if m_idx_dot:
            base = self.translate_target(m_idx_dot.group(1))
            return f"{base}['{m_idx_dot.group(2)}']"

        # Handle 2D index: M[i, j] -> M[i, j] (numpy array)
        m_2d = re.match(r'^([a-zA-Z0-9_]+)\s*\[\s*(.+?)\s*,\s*(.+?)\s*\]$', target)
        if m_2d:
            arr = m_2d.group(1)
            i_idx = self.translate_expression(m_2d.group(2))
            j_idx = self.translate_expression(m_2d.group(3))
            return f"{arr}[{i_idx}, {j_idx}]"

        # Handle 1D index: T[i]
        m_1d = re.match(r'^([a-zA-Z0-9_]+)\s*\[\s*(.+?)\s*\]$', target)
        if m_1d:
            arr = m_1d.group(1)
            i_idx = self.translate_expression(m_1d.group(2))
            return f"{arr}[{i_idx}]"

        # Handle record field: E.champ -> E['champ']
        if '.' in target:
            parts = target.split('.', 1)
            return f"{parts[0]}['{parts[1]}']"

        return target

    def translate_expression(self, expr_str: str) -> str:
        """
        Translates algorithmic expressions to Python expressions:
        - Operators: Div -> //, Mod -> %, Et -> and, Ou -> or, Non -> not
        - Equality: = -> ==, ≠ / <> -> !=, ≤ -> <=, ≥ -> >=
        - Sets & Intervals: x  [a .. b] -> (a <= x <= b), x  {a, b} -> (x in {a, b})
        - Built-in functions mapping
        - Record dot access: E.champ -> E['champ']
        """
        if not expr_str:
            return ""

        # Protect string literals from token replacement
        str_map = {}
        str_idx = 0

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
            val = self.translate_expression(m_int.group(1).strip())
            low = self.translate_expression(m_int.group(2).strip())
            high = self.translate_expression(m_int.group(3).strip())
            replacement = f"({low} <= {val} <= {high})"
            s = s[:m_int.start()] + replacement + s[m_int.end():]

        # Handle membership in set: expr  {a, b, c}
        m_set = re.search(r'(.+?)\s+(?:|∈|dans|in)\s+\{\s*(.+?)\s*\}', s, re.IGNORECASE)
        if m_set:
            val = self.translate_expression(m_set.group(1).strip())
            items = [self.translate_expression(it.strip()) for it in m_set.group(2).split(',') if it.strip()]
            replacement = f"({val} in {{{', '.join(items)}}})"
            s = s[:m_set.start()] + replacement + s[m_set.end():]

        # Handle 2D index in expressions: M[i, j]
        s = re.sub(r'([a-zA-Z0-9_]+)\s*\[\s*(.+?)\s*,\s*(.+?)\s*\]', r'\1[\2, \3]', s)

        # Handle predefined function names (case-insensitive)
        for fn_name, py_fn in self.fn_map.items():
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
        s = re.sub(r'(?<![<>!=])=(?![=])', '==', s)

        # Handle record dot access: E.champ -> E['champ']
        def replace_dot(m):
            obj = m.group(1)
            field = m.group(2)
            return f"{obj}['{field}']"

        s = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b', replace_dot, s)

        # Restore strings
        for placeholder, original in str_map.items():
            s = s.replace(placeholder, original)

        return s
