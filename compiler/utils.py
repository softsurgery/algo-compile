"""
Helper utilities for algorithmic code parsing and text processing.
"""

import unicodedata

def normalize_accents(text: str) -> str:
    """Normalize accented characters while preserving standard accents."""
    return unicodedata.normalize('NFC', text)

def split_arguments(s: str) -> list:
    """Splits arguments by comma outside of parentheses, brackets, braces, and quotes."""
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
