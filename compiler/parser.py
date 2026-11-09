"""
Structural Section Extractor and Header Parser for Algorithmic Code.
"""

import re

class SectionExtractor:
    """Categorizes algorithmic source lines into structured sections."""

    def __init__(self):
        self.program_name = "Algorithme"

    def extract_sections(self, lines: list) -> dict:
        """
        Categorizes lines into header, subprograms, main, objects (TDO/TDOG),
        types (TDNT), and local objects (TDOL).
        """
        sections = {
            'header': [],
            'subprograms': [],
            'main': [],
            'objects': [],
            'types': [],
            'tdol': []
        }

        current_subprog = None
        in_main = False
        in_tdo = False
        in_types = False
        in_tdol = False

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            line_no = i + 1

            if not stripped:
                i += 1
                continue

            # Strip comments
            if stripped.startswith(("//", "#", "/*")):
                i += 1
                continue

            # Decorative border lines like *******, -------, ======, //////
            if re.match(r'^[\*\-=\/ ]{3,}$', stripped):
                i += 1
                continue

            lower = stripped.lower()

            # Check for TDOL / TDOL- (Local TDO) -> ignore so it does not spill into main
            if re.match(r'^t\.?d\.?o\.?l(?:-|\s|$)', stripped, re.IGNORECASE):
                in_tdol = True
                in_tdo = False
                in_types = False
                in_main = False
                current_subprog = None
                i += 1
                continue

            # Check for TDOG / TDO (Global or standard TDO)
            if re.match(r'^(?:t\.?d\.?o\.?g|t\.?d\.?o)\b', stripped, re.IGNORECASE) or \
               re.match(r'^(?:déclaration|declaration)\s+des\s+objets', stripped, re.IGNORECASE):
                in_tdo = True
                in_tdol = False
                in_types = False
                in_main = False
                current_subprog = None
                i += 1
                continue

            # Check for TDNT / Declarations des types
            if re.match(r'^t\.?d\.?n\.?t\b', stripped, re.IGNORECASE) or \
               re.match(r'^(?:déclaration|declaration)\s+des\s+(?:nouveaux\s+)?types', stripped, re.IGNORECASE):
                in_types = True
                in_tdo = False
                in_tdol = False
                in_main = False
                current_subprog = None
                i += 1
                continue

            # Check for Subprogram declaration: Fonction / Procédure
            m_fn = re.match(r'^(fonction|procédure|procedure)\s+([a-zA-Z0-9_]+)', stripped, re.IGNORECASE)
            if m_fn:
                in_tdo = False
                in_types = False
                in_tdol = False
                in_main = False
                kind = 'procedure' if 'proc' in m_fn.group(1).lower() else 'fonction'
                current_subprog = {
                    'kind': kind,
                    'header': stripped,
                    'start_line': line_no,
                    'lines': [(line_no, line)],
                    'tdo': []
                }
                sections['subprograms'].append(current_subprog)
                i += 1
                continue

            # Header: ALGORITHME Nom
            m_algo = re.match(r'^algorithme\s+([a-zA-Z0-9_]+)', stripped, re.IGNORECASE)
            if m_algo:
                self.program_name = m_algo.group(1)
                sections['header'].append((line_no, stripped))
                in_tdo = False
                in_types = False
                in_tdol = False
                in_main = False
                current_subprog = None
                i += 1
                continue

            # Inside TDNT (types), accumulate all lines
            if in_types:
                sections['types'].append((line_no, line))
                i += 1
                continue

            # Inside TDOL (local declarations), accumulate
            if in_tdol:
                sections['tdol'].append((line_no, line))
                i += 1
                continue

            # Inside TDOG / TDO, accumulate
            if in_tdo:
                sections['objects'].append((line_no, line))
                i += 1
                continue

            # Check for DEBUT
            if stripped.upper() in ("DEBUT", "DÉBUT"):
                if current_subprog is not None:
                    current_subprog['lines'].append((line_no, line))
                else:
                    in_main = True
                i += 1
                continue

            # Check for FIN of subprogram or main algorithm (excluding block closures like Fin Si, Fin Pour, Fin Selon, Fin Tant que)
            is_block_end = bool(re.match(r'^fin\s*(?:si|pour|selon|tant|enregistrement)\b', stripped, re.IGNORECASE))
            if not is_block_end and (
                stripped.upper() == "FIN" or
                re.match(r'^fin\s+(?:procedure|procédure|fonction|[a-zA-Z0-9_]+)$', stripped, re.IGNORECASE)
            ):
                if current_subprog is not None:
                    current_subprog['lines'].append((line_no, line))
                    current_subprog = None
                elif in_main:
                    in_main = False
                i += 1
                continue
            elif current_subprog is not None:
                sections['subprograms'][-1]['lines'].append((line_no, line))
            elif in_main:
                sections['main'].append((line_no, line))
            else:
                # If outside of marked sections, check if it looks like code or declarations
                if not re.match(r'^objet\b', lower):
                    sections['main'].append((line_no, line))

            i += 1

        return sections

    @staticmethod
    def register_subprogram_signature(subprog: dict, subprogram_meta: dict):
        """Extracts and registers metadata for a subprogram (params, ref params, kind)."""
        header = subprog['header']
        m = re.match(r'^(?:fonction|procédure|procedure)\s+([a-zA-Z0-9_]+)\s*(?:\((.*?)\))?', header, re.IGNORECASE)
        if m:
            sub_name = m.group(1)
            params_str = m.group(2) or ""
            py_params = []
            ref_params = []
            if params_str.strip():
                for p in params_str.split(','):
                    p = p.strip()
                    if not p:
                        continue
                    pname = p.split(':', 1)[0].strip() if ':' in p else p
                    if pname.startswith('@'):
                        clean_name = pname[1:].strip()
                        ref_params.append(clean_name)
                        py_params.append(clean_name)
                    else:
                        py_params.append(pname)
            subprogram_meta[sub_name] = {
                'kind': subprog['kind'],
                'ref_params': ref_params,
                'all_params': py_params
            }
